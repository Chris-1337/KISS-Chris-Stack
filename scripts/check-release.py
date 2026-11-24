#!/usr/bin/env python3
"""Check local candidate bytes; never install, publish, or authorize delivery."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
RELEASE_EXTRAS = ("LICENSE", "docs/THIRD-PARTY.md", "docs/DELIVERY.md", "docs/GITHUB-PUBLICATION.md",
                  "SECURITY.md", ".github/CODEOWNERS", ".github/main-ruleset.json", "README.md",
                  "CONTRIBUTING.md", "AGENTS.md", "docs/OPERATIONS.md", "docs/LIFECYCLE.md",
                  "docs/EVALUATION.md", "docs/WAYFINDER.md", "docs/ARCHITEKTUR.md", "docs/HOST-TESTS.md",
                  "docs/SONARQUBE.md", "docs/REMOTE-CONTAINER.md", "docs/PRODUKT-ONBOARDING.md", "docs/LEARNING.md",
                  "docs/adr/0001-dokumentation-und-agentenrollen.md", "docs/adr/0002-codex-marketplace-und-lifecycle.md",
                  "docs/adr/0003-documentation-language.md", "docs/adr/0004-proportionate-routing-and-delegation.md",
                  ".github/workflows/tests.yml", "sonar-project.properties")


def host_helpers():
    # Candidate Python is untrusted data; load helpers only from this checker's checkout.
    spec = importlib.util.spec_from_file_location("release_host_helpers", ROOT / "scripts/test-host-workflows.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resource(root, relative, *, directory=False):
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError("Invalid candidate resource path")
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Candidate resource path escapes root")
    target = root
    for part in path.parts:
        target /= part
        if target.is_symlink() or target.is_junction():
            raise ValueError("Linked candidate resources are unsupported")
    if not target.resolve().is_relative_to(root):
        raise ValueError("Candidate resource path escapes root")
    if not (target.is_dir() if directory else target.is_file()):
        raise ValueError("Required candidate resource is missing")
    return target


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def json_resource(root, relative):
    path = resource(root, relative)
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    except ValueError:
        raise ValueError("Malformed candidate JSON resource") from None
    if not isinstance(data, dict) or not data:
        raise ValueError("Candidate JSON resource must be a nonempty object")
    return data


def matching_identity(data, name, version):
    if data.get("name") != name or ("version" in data and data["version"] != version):
        raise ValueError("Candidate name or version mismatch")


def valid_identifiers(value):
    return re.fullmatch(r"[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*", value) is not None


def valid_version(value):
    if not isinstance(value, str) or len(value) > 64:
        return False
    base, has_build, build = value.partition("+")
    if has_build and not valid_identifiers(build):
        return False
    core, has_prerelease, prerelease = base.partition("-")
    parts = core.split(".")
    if len(parts) != 3 or any(re.fullmatch(r"0|[1-9]\d*", part, re.ASCII) is None for part in parts):
        return False
    if not has_prerelease:
        return True
    if not valid_identifiers(prerelease):
        return False
    return all(not (part.isdigit() and len(part) > 1 and part.startswith("0"))
               for part in prerelease.split("."))


def metadata(root):
    native = json_resource(root, ".codex-plugin/plugin.json")
    name, version = native.get("name"), native.get("version")
    if name != "kiss-chris-stack" or not valid_version(version):
        raise ValueError("Invalid native candidate identity or version")
    matching_identity(json_resource(root, "plugin.json"), name, version)
    catalog = json_resource(root, ".agents/plugins/marketplace.json")
    matching_identity(catalog, name, version)
    entries = catalog.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
        raise ValueError("Marketplace must identify this candidate once")
    entry = entries[0]
    matching_identity(entry, name, version)
    source = entry.get("source")
    if not isinstance(source, dict) or source.get("source") != "local":
        raise ValueError("Marketplace candidate source must be local")
    if resource(root, source.get("path"), directory=True) != root:
        raise ValueError("Marketplace source must resolve to candidate root")
    resource(root, native.get("skills"), directory=True)
    json_resource(root, native.get("hooks"))
    extension = native.get("extensions", {}).get("com.openai", {})
    resource(root, extension.get("onboardingSkill"))
    return {"name": name, "version": version}


def check_bundle(root):
    hashes = json_resource(root, "assets/bundle-manifest.json").get("sha256")
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("Missing bundled resource hashes")
    for relative, digest in hashes.items():
        path = resource(root, relative)
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid bundled resource hash")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Bundled resource hash mismatch")
    licenses = resource(root, "licenses", directory=True)
    files = list(licenses.iterdir())
    if not files or any(path.relative_to(root).as_posix() not in hashes for path in files):
        raise ValueError("Licenses must retain bundled provenance hashes")
    json_resource(root, "assets/versions.json")


def source_identity(root):
    helpers = host_helpers()
    provenance = {}
    for relative in RELEASE_EXTRAS:
        content = resource(root, relative).read_bytes()
        if not content.strip():
            raise ValueError("Empty candidate release resource")
        provenance[relative] = hashlib.sha256(content).hexdigest()
    provenance["runtime"] = helpers.fingerprint(root)
    fingerprint = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel", "HEAD"],
                            capture_output=True, text=True, timeout=15, check=False)
    lines = result.stdout.splitlines()
    revision = lines[1] if result.returncode == 0 and len(lines) == 2 and Path(lines[0]).resolve() == root else None
    return {"revision": revision, "fingerprint": fingerprint}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--expect-source")
    args = parser.parse_args(argv)
    receipt = {"status": "failed", "published": False}
    try:
        root = args.project.resolve(strict=True)
        receipt["candidate"] = metadata(root)
        check_bundle(root)
        receipt["source"] = source_identity(root)
        if args.expect_source is not None and args.expect_source != receipt["source"]["fingerprint"]:
            raise ValueError("Candidate source fingerprint does not match expectation")
        receipt["status"] = "passed"
    except ValueError as error:
        receipt["errors"] = [str(error)]
    except (OSError, TypeError, AttributeError, subprocess.SubprocessError):
        receipt["errors"] = ["Candidate inspection failed; check local resources and Git availability"]
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
