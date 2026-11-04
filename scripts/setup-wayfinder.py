#!/usr/bin/env python3
"""Check or prepare the configured Wayfinder directory and managed operations document."""
import argparse
import json
import os
import re
import runpy
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CONFIG = runpy.run_path(str(ROOT / "scripts/evaluation-config.py"))
BEGIN = "<!-- kiss-chris-stack:wayfinder-tracker:start -->"
END = "<!-- kiss-chris-stack:wayfinder-tracker:end -->"
DOCUMENT = "docs/agents/issue-tracker.md"
CONFIGURATION_FILE = "kiss-chris-stack.config.json"
GITHUB_REPOSITORY_PREFIX = "github.com/"


def safe_target(project, relative, directory=False):
    target = project / relative
    for candidate in [*reversed(target.relative_to(project).parents), target.relative_to(project)]:
        path = project / candidate
        try:
            entry = path.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(entry.st_mode) or getattr(entry, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError(f"Unsafe symlink/reparse target: {path}")
        want_directory = path != target or directory
        if not (stat.S_ISDIR(entry.st_mode) if want_directory else stat.S_ISREG(entry.st_mode)):
            raise ValueError(f"Unexpected file type at {path}")
    return target


def load_configuration(project, supplied):
    if supplied:
        raw = sys.stdin.read()
    else:
        path = safe_target(project, CONFIGURATION_FILE)
        raw = path.read_text(encoding="utf-8-sig") if path.exists() else "{}"
    settings = json.loads(raw, object_pairs_hook=CONFIG["unique_object"])
    return CONFIG["resolve_settings"](settings, CONFIG["DEFAULTS"])


def render_operations(tracker):
    provider = tracker["provider"]
    template = ROOT / f"skills/setup-matt-pocock-skills/issue-tracker-{provider}.md"
    text = template.read_text(encoding="utf-8")
    if provider == "local":
        text = text.replace(".scratch", tracker["directory"])
        location = tracker["directory"]
    else:
        location = tracker["repository"] if provider == "github" else tracker["project"]
        executable = "gh" if provider == "github" else "glab"
        target = GITHUB_REPOSITORY_PREFIX + location if provider == "github" else location
        quoted_target = shlex.quote(target)
        text = re.sub(rf"\b{executable} (issue|pr|mr|label) ([a-z-]+)\b", rf"{executable} \1 \2 --repo {quoted_target}", text)
        text = text.replace(f"{executable} repo view ", f"{executable} repo view {quoted_target} ")
        host = "github.com" if provider == "github" else urlsplit(location).netloc
        text = text.replace(f"{executable} api ", f"{executable} api --hostname {shlex.quote(host)} ")
        if provider == "github":
            text = text.replace("repos/<owner>/<repo>", "repos/" + location).replace("repos/{owner}/{repo}", "repos/" + location)
        else:
            project_id = quote(urlsplit(location).path.strip("/"), safe="")
            text = text.replace("projects/:id", "projects/" + project_id)
        text = re.sub(r"Infer the repo from `git remote -v`;[^\n]+", "Use only the configured explicit target in every command; never infer a target from cwd, a remote or environment defaults.", text)
    text = text.replace("[Wayfinder](../wayfinder/SKILL.md)", "bundled `skills/wayfinder/SKILL.md`")
    text = text.replace("[MIT notice](../../licenses/mattpocock-skills-LICENSE)", "bundled `licenses/mattpocock-skills-LICENSE`")
    text = text.replace("see `triage-labels.md` for the role strings", "see bundled `skills/setup-matt-pocock-skills/triage-labels.md` for optional triage role strings")
    return (f"{BEGIN}\n# Configured Wayfinder operations\n\n"
            f"Authoritative configuration: project-root `kiss-chris-stack.config.json`, `wayfinder-tracker`.\n"
            f"Provider: `{provider}`\nLocation: `{location}`\n\n"
            "Setup prepares this binding only; it creates no effort, map or ticket. External writes require separate authorization.\n\n"
            f"{text.rstrip()}\n{END}\n")


def document_update(original, expected):
    if original is None:
        return expected.encode("utf-8")
    text = original.decode("utf-8")
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) >= text.index(END):
        raise ValueError("Unmanaged or malformed operations document; preserve it and resolve the managed-block conflict")
    start, end = text.index(BEGIN), text.index(END) + len(END)
    newline = "\r\n" if "\r\n" in text else "\n"
    block = expected.rstrip("\n").replace("\n", newline)
    return (text[:start] + block + text[end:]).encode("utf-8")


def check_configuration_binding(project, configuration):
    path = safe_target(project, CONFIGURATION_FILE)
    if path.exists():
        settings = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=CONFIG["unique_object"])
        if CONFIG["resolve_settings"](settings, CONFIG["DEFAULTS"]) != configuration:
            raise ValueError("Existing or concurrently changed configuration differs from the selected pending settings; setup refused")


def write_document(path, original, updated):
    if original is None:
        with path.open("xb") as output:
            output.write(updated)
        return
    previous = path.lstat()
    descriptor, name = tempfile.mkstemp(prefix=".issue-tracker-", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    staging = Path(name)
    try:
        CONFIG["preserve_permissions"](path, staging)
        staging.write_bytes(updated)
        current = path.lstat()
        if (not stat.S_ISREG(current.st_mode) or current.st_mtime_ns != previous.st_mtime_ns
                or current.st_ino != previous.st_ino or path.read_bytes() != original):
            raise ValueError("Operations document changed concurrently; update refused")
        os.replace(staging, path)
    finally:
        staging.unlink(missing_ok=True)


def remote_json(executable, arguments, environment):
    command = shutil.which(executable)
    if not command:
        raise ValueError(f"Selected tracker requires {executable}; install/authenticate it explicitly, no local fallback")
    if Path(command).suffix.lower() in (".cmd", ".bat"):
        raise ValueError(f"Use a native {executable} executable, not a shell wrapper")
    result = subprocess.run([command, *arguments], capture_output=True, text=True, timeout=30, env=environment, stdin=subprocess.DEVNULL)
    if result.returncode:
        raise ValueError(f"{executable} read-only tracker preflight failed; check authentication, target and access")
    return json.loads(result.stdout)


def check_github(tracker, environment):
    repository = tracker["repository"]
    environment.update(GH_HOST="github.com", GH_REPO=GITHUB_REPOSITORY_PREFIX + repository)
    metadata = remote_json("gh", ["repo", "view", GITHUB_REPOSITORY_PREFIX + repository, "--json",
                                 "nameWithOwner,hasIssuesEnabled,isArchived,viewerPermission,url"], environment)
    if not isinstance(metadata, dict):
        raise ValueError("GitHub preflight did not return repository metadata")
    if (str(metadata.get("nameWithOwner", "")).casefold() != repository.casefold()
            or str(metadata.get("url", "")).casefold() != ("https://github.com/" + repository).casefold()):
        raise ValueError("GitHub preflight target identity does not match configuration")
    if (metadata.get("hasIssuesEnabled") is not True or metadata.get("isArchived") is not False
            or metadata.get("viewerPermission") not in ("TRIAGE", "WRITE", "MAINTAIN", "ADMIN")):
        raise ValueError("GitHub tracker requires enabled Issues, an unarchived repository and visible TRIAGE-or-higher access")


def check_gitlab(tracker, environment):
    target = urlsplit(tracker["project"])
    identity = target.path.strip("/")
    metadata = remote_json("glab", ["api", "--hostname", target.netloc,
                                   "projects/" + quote(identity, safe="")], environment)
    if not isinstance(metadata, dict):
        raise ValueError("GitLab preflight did not return project metadata")
    observed = urlsplit(str(metadata.get("web_url", "")))
    if (metadata.get("path_with_namespace") != identity
            or (observed.scheme, observed.netloc.casefold(), observed.path, observed.query, observed.fragment)
            != (target.scheme, target.netloc.casefold(), target.path, target.query, target.fragment)):
        raise ValueError("GitLab preflight target identity does not match configuration")
    permissions = metadata.get("permissions")
    permissions = permissions if isinstance(permissions, dict) else {}
    levels = [value["access_level"] for key in ("project_access", "group_access") for value in [permissions.get(key)]
              if isinstance(value, dict) and type(value.get("access_level")) is int]
    issues = metadata.get("issues_access_level") in ("enabled", "private") if "issues_access_level" in metadata else metadata.get("issues_enabled") is True
    if metadata.get("archived") is not False or not issues or max(levels, default=0) < 30:
        raise ValueError("GitLab tracker requires enabled Issues, an unarchived project and visible Developer-or-higher access")


def check_remote(tracker):
    environment = dict(os.environ, GH_PROMPT_DISABLED="1")
    if tracker["provider"] == "github":
        check_github(tracker, environment)
    else:
        check_gitlab(tracker, environment)


def reconcile_tracker(project, configuration, prepare):
    tracker = configuration["wayfinder-tracker"]
    directory = tracker.get("directory", "").casefold()
    outputs = (CONFIGURATION_FILE, "agents.md", DOCUMENT.casefold())
    if any(directory == name or directory.startswith(name + "/") for name in outputs):
        raise ValueError("Wayfinder local directory collides with a setup output file")
    document = safe_target(project, DOCUMENT)
    target = safe_target(project, tracker["directory"], directory=True) if tracker["provider"] == "local" else None
    original = document.read_bytes() if document.exists() else None
    updated = document_update(original, render_operations(tracker))
    check_configuration_binding(project, configuration)
    if tracker["provider"] != "local":
        check_remote(tracker)
    check_configuration_binding(project, configuration)
    changed = []
    if prepare:
        if target is not None and not target.exists():
            target.mkdir(parents=True)
            changed.append(str(target))
        if original != updated:
            document.parent.mkdir(parents=True, exist_ok=True)
            write_document(document, original, updated)
            changed.append(str(document))
    elif original != updated or target is not None and not target.is_dir():
        raise ValueError("Wayfinder tracker binding is missing or stale; run assigned setup --prepare, no fallback")
    return {"ready": True, "configuration": configuration, "provider": tracker["provider"],
                      "location": str(target) if target is not None else tracker.get("repository", tracker.get("project")),
                      "operations_document": str(document), "changed": changed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--check", action="store_true", help="Read-only check (the default)")
    parser.add_argument("--config-stdin", action="store_true", help="Validate full pending settings from stdin without creating a config marker")
    args = parser.parse_args()
    try:
        if not args.project.is_dir():
            raise ValueError("Project must be an existing directory")
        project = args.project.resolve()
        configuration = load_configuration(project, args.config_stdin)
        report = reconcile_tracker(project, configuration, args.prepare)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
