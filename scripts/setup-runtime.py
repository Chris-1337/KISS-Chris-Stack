#!/usr/bin/env python3
"""Check local plugin prerequisites; --repair performs authorized local setup only."""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = json.loads((ROOT / "assets/versions.json").read_text(encoding="utf-8"))
BEGIN, END = "<!-- kiss-chris-stack:start -->", "<!-- kiss-chris-stack:end -->"
POLICY = (ROOT / "assets/global-stack-policy.md").read_text(encoding="utf-8").strip()
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", CODEGRAPH_NO_DOWNLOAD="1", PYTHONIOENCODING="utf-8")
MAX_RTK_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_RTK_BINARY_BYTES = 128 * 1024 * 1024
MAX_RTK_EXPANDED_BYTES = 256 * 1024 * 1024
MAX_RTK_MEMBERS = 10000


def command(name, *args):
    executable = shutil.which(name)
    if not executable:
        raise RuntimeError(f"{name} not found on PATH; install it or reload the host environment.")
    # Run npm's JavaScript entrypoints directly on Windows, without a command shell.
    if os.name == "nt" and Path(executable).suffix.lower() in (".cmd", ".bat"):
        entries = {"npm": "npm/bin/npm-cli.js", "codegraph": "@colbymchenry/codegraph/npm-shim.js", "codex": "@openai/codex/bin/codex.js"}
        entry = Path(executable).parent / "node_modules" / entries[name]
        node = shutil.which("node")
        if not entry.is_file() or not node:
            raise RuntimeError(f"Cannot resolve the native Node entrypoint for {name}; repair its installation.")
        argv = [node, str(entry), *args]
    else:
        argv = [executable, *args]
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV, timeout=90)
    if result.returncode:
        raise RuntimeError(f"{name} {' '.join(args[:2])} failed ({result.returncode}): {(result.stderr or result.stdout).strip()[:600]}")
    return result.stdout.strip()


def policy_current(path):
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return text.count(BEGIN) == text.count(END) == 1 and text.index(BEGIN) < text.index(END) and text.split(BEGIN)[1].split(END)[0].strip() == POLICY


def update_policy(path):
    content = path.read_bytes().decode("utf-8") if path.exists() else ""
    if content.count(BEGIN) != content.count(END) or content.count(BEGIN) > 1 or (BEGIN in content and content.index(BEGIN) > content.index(END)):
        raise RuntimeError(f"Ambiguous managed markers in {path}; resolve without discarding foreign content.")
    newline = "\r\n" if "\r\n" in content else "\n"
    block = (BEGIN + "\n" + POLICY + "\n" + END).replace("\n", newline)
    if BEGIN in content:
        updated = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, content, flags=re.S)
    else:
        separator = ""
        if content:
            separator = newline if content.endswith(newline) else newline * 2
        updated = content + separator + block + newline
    path.parent.mkdir(parents=True, exist_ok=True)
    if updated != content:
        path.write_bytes(updated.encode("utf-8"))


def mcp_config():
    try:
        return json.loads(command("codex", "mcp", "get", "codegraph", "--json"))
    except (RuntimeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"CodeGraph MCP registration unavailable: {error}") from error


def mcp_matches(config):
    transport = config.get("transport", {})
    name = Path(transport.get("command", "")).stem.lower()
    return config.get("enabled") is True and transport.get("type") == "stdio" and name == "codegraph" and transport.get("args") == ["serve", "--mcp"]


def read_bounded(stream, limit):
    data = stream.read(limit + 1)
    if len(data) > limit:
        raise RuntimeError("RTK artifact exceeds its resource limit; nothing installed.")
    return data


def read_zip_binary(archive, filename):
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len(entries) > MAX_RTK_MEMBERS or sum(member.file_size for member in entries) > MAX_RTK_EXPANDED_BYTES:
            raise RuntimeError("RTK archive exceeds its resource limit; nothing installed.")
        members = [member for member in entries if Path(member.filename).name == filename]
        if len(members) != 1:
            raise RuntimeError("RTK archive must contain exactly one binary.")
        member = members[0]
        if member.is_dir() or stat.S_IFMT(member.external_attr >> 16) not in (0, stat.S_IFREG):
            raise RuntimeError("RTK archive binary must be a regular file.")
        if member.file_size > MAX_RTK_BINARY_BYTES:
            raise RuntimeError("RTK binary exceeds its resource limit; nothing installed.")
        with bundle.open(member) as stream:
            return read_bounded(stream, MAX_RTK_BINARY_BYTES)


def read_tar_binary(archive, filename):
    binary, expanded = None, 0
    with gzip.open(archive, "rb") as compressed:
        tar_bytes = read_bounded(compressed, MAX_RTK_EXPANDED_BYTES)
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r|") as bundle:
        for count, member in enumerate(bundle, 1):
            expanded += member.size
            if count > MAX_RTK_MEMBERS or expanded > MAX_RTK_EXPANDED_BYTES:
                raise RuntimeError("RTK archive exceeds its resource limit; nothing installed.")
            if Path(member.name).name != filename:
                continue
            if binary is not None or not member.isfile():
                raise RuntimeError("RTK archive must contain exactly one binary, a regular file.")
            if member.size > MAX_RTK_BINARY_BYTES:
                raise RuntimeError("RTK binary exceeds its resource limit; nothing installed.")
            with bundle.extractfile(member) as stream:
                binary = read_bounded(stream, MAX_RTK_BINARY_BYTES)
    if binary is None:
        raise RuntimeError("RTK archive must contain exactly one binary.")
    return binary


def read_rtk_binary(archive, filename):
    if archive.suffix == ".zip":
        return read_zip_binary(archive, filename)
    return read_tar_binary(archive, filename)


def install_rtk():
    version = VERSIONS["rtk"]["version"]
    machine = platform.machine().lower()
    architecture = {"arm64": "aarch64", "aarch64": "aarch64", "amd64": "x86_64", "x86_64": "x86_64"}.get(machine)
    targets = {("Windows", "x86_64"): "x86_64-pc-windows-msvc.zip", ("Darwin", "x86_64"): "x86_64-apple-darwin.tar.gz", ("Darwin", "aarch64"): "aarch64-apple-darwin.tar.gz", ("Linux", "x86_64"): "x86_64-unknown-linux-musl.tar.gz", ("Linux", "aarch64"): "aarch64-unknown-linux-gnu.tar.gz"}
    target = targets.get((platform.system(), architecture))
    if target is None:
        raise RuntimeError("No pinned RTK binary for this OS/architecture; obtain a supported upstream build.")
    asset = "rtk-" + target
    base = VERSIONS["rtk"]["releaseBase"] + "/v" + version + "/"
    with tempfile.TemporaryDirectory(prefix="kiss-rtk-") as directory:
        archive = Path(directory) / asset
        with urllib.request.urlopen(base + asset, timeout=60) as response:
            archive.write_bytes(read_bounded(response, MAX_RTK_ARCHIVE_BYTES))
        with urllib.request.urlopen(base + "checksums.txt", timeout=30) as response:
            checksums = read_bounded(response, 1024 * 1024).decode("utf-8")
        hashes = [line.split()[0] for line in checksums.splitlines() if line.split() and line.split()[-1].lstrip("*") == asset]
        if len(hashes) != 1 or hashlib.sha256(archive.read_bytes()).hexdigest().lower() != hashes[0].lower():
            raise RuntimeError("RTK archive checksum missing, ambiguous or mismatched; nothing installed.")
        filename = "rtk.exe" if platform.system() == "Windows" else "rtk"
        # Read one bounded regular binary without expanding archive paths.
        binary = read_rtk_binary(archive, filename)
        destination = Path.home() / ".local" / "bin" / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        staged = destination.with_suffix(destination.suffix + ".new")
        staged.write_bytes(binary)
        staged.chmod(0o755)
        staged.replace(destination)
    # Process-local only; the setup agent must prove visibility in its own shell.
    os.environ["PATH"] = str(destination.parent) + os.pathsep + os.environ.get("PATH", "")
    ENV["PATH"] = os.environ["PATH"]


def resources():
    manifest = json.loads((ROOT / "assets/bundle-manifest.json").read_text(encoding="utf-8"))
    for relative, digest in manifest["sha256"].items():
        source = (ROOT / relative).resolve()
        if not source.is_relative_to(ROOT) or hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"bundled resource missing or changed: {relative}")
    return f"{len(manifest['sha256'])} bundled resources verified"


def check(project, codex_home):
    checks, errors = [], []
    def probe(name, action):
        try:
            detail = action()
            if detail is False:
                raise RuntimeError("required state is missing or outdated")
            checks.append({"name": name, "ok": True, "detail": detail})
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
            checks.append({"name": name, "ok": False})
            errors.append(f"{name}: {error}")
    probe("project", lambda: project.is_dir())
    probe("Python", lambda: sys.version.split()[0] if sys.version_info >= (3, 10) else False)
    probe("Node", lambda: command("node", "--version"))
    probe("Codex", lambda: command("codex", "--version"))
    probe("CodeGraph CLI", lambda: command("codegraph", "--version"))
    def codegraph_package():
        global_root = Path(command("npm", "root", "-g"))
        package = json.loads((global_root / VERSIONS["codegraph"]["package"] / "package.json").read_text(encoding="utf-8"))
        if package["version"] != VERSIONS["codegraph"]["version"]:
            raise RuntimeError("installed npm package differs from assets/versions.json pin")
        return package["version"]
    probe("CodeGraph npm package", codegraph_package)
    probe("RTK", lambda: command("rtk", "--version") if VERSIONS["rtk"]["version"] in command("rtk", "--version").split() else False)
    probe("bundled skills/resources", resources)
    def uiux_query():
        result = subprocess.run([sys.executable, str(ROOT / "skills/ui-ux-pro-max/scripts/search.py"), "accessible dashboard", "--domain", "ux", "--max-results", "1", "--json"], capture_output=True, text=True, encoding="utf-8", env=ENV, timeout=30)
        output = json.loads(result.stdout) if result.returncode == 0 else {}
        if not output.get("results"):
            raise RuntimeError("bundled UIUX query returned no results: " + result.stderr[:300])
        return "bundled search/data query returned results"
    probe("UIUX real query", uiux_query)
    probe("global AGENTS policy", lambda: policy_current(codex_home / "AGENTS.md"))
    override = codex_home / "AGENTS.override.md"
    if override.exists():
        probe("existing AGENTS.override policy", lambda: policy_current(override))
    index = project / ".codegraph"
    probe("CodeGraph index", index.is_dir)
    if index.is_dir():
        probe("CodeGraph status", lambda: command("codegraph", "status", str(project)))
    probe("CodeGraph MCP registration", lambda: mcp_matches(mcp_config()))
    return checks, errors


def repair(project, codex_home):
    if not project.is_dir():
        raise RuntimeError("Project directory does not exist; choose the intended workspace.")
    command("node", "--version")
    command("npm", "--version")
    pin = VERSIONS["codegraph"]
    global_root = Path(command("npm", "root", "-g"))
    installed = global_root / pin["package"] / "package.json"
    if not installed.is_file() or json.loads(installed.read_text(encoding="utf-8"))["version"] != pin["version"]:
        command("npm", "install", "-g", pin["package"] + "@" + pin["version"])
    try:
        correct_rtk = VERSIONS["rtk"]["version"] in command("rtk", "--version").split()
    except RuntimeError:
        correct_rtk = False
    if not correct_rtk:
        install_rtk()
    update_policy(codex_home / "AGENTS.md")
    override = codex_home / "AGENTS.override.md"
    if override.exists():
        update_policy(override)
    # Inspect all entries first: an unreadable configuration is not proof of absence.
    entries = json.loads(command("codex", "mcp", "list", "--json"))
    existing = next((entry for entry in entries if entry.get("name") == "codegraph"), None)
    if existing is None:
        command("codex", "mcp", "add", "codegraph", "--", "codegraph", "serve", "--mcp")
    elif not mcp_matches(mcp_config()):
        raise RuntimeError("Existing CodeGraph MCP entry conflicts; ask the user instead of overwriting it.")
    command("codegraph", "sync", str(project)) if (project / ".codegraph").is_dir() else command("codegraph", "init", "-i", str(project))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--repair", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).resolve()
    repair_errors = []
    if args.repair:
        try:
            repair(project, codex_home)
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
            repair_errors.append(str(error))
    checks, errors = check(project, codex_home)
    errors = repair_errors + errors
    runtime_ready = not errors
    report = {"ready": False, "runtime_ready": runtime_ready, "session_verification_required": True, "checks": checks, "errors": errors, "next_step": "After runtime_ready=true, invoke actual CodeGraph MCP status/context in this agent session. CLI registration alone does not prove loaded tools. Reload/review hook trust if unavailable; never self-approve trust."}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if runtime_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
