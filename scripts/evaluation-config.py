#!/usr/bin/env python3
"""Resolve workflow/evaluation switches and Wayfinder target; optionally backfill missing defaults."""
import argparse
import ipaddress
import json
import ntpath
import os
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import urlsplit


DEFAULTS = {"grill-me": True, "grill-with-docs": True, "wayfinder": True, "wayfinder-tracker": {"provider": "local", "directory": ".scratch"}, "plan-mode": False, "evaluation": {"live": {"enabled": True}, "sonarqube": {"enabled": True}}}
IS_RESERVED = getattr(ntpath, "isreserved", lambda value: PureWindowsPath(value).is_reserved())


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate configuration key")
        result[key] = value
    return result


def valid_gitlab_authority(parsed):
    host = parsed.hostname or ""
    if ":" in host:
        if not re.fullmatch(r"[0-9A-Fa-f:]+", host):
            return False
        ipaddress.IPv6Address(host)
        authority = rf"\[{re.escape(host)}\](?::[0-9]+)?"
    else:
        labels = host.split(".")
        if len(host) > 253 or any(not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label) for label in labels):
            return False
        if "." in host and host.replace(".", "").isdigit():
            ipaddress.IPv4Address(host)
        authority = rf"{re.escape(host)}(?::[0-9]+)?"
    return bool(re.fullmatch(authority, parsed.netloc, re.IGNORECASE)) and (parsed.port is None or 1 <= parsed.port <= 65535)


def validate_tracker_directory(target):
    parts = target.split("/")
    if (PurePosixPath(target).is_absolute() or PureWindowsPath(target).drive or "\\" in target
            or any(part.casefold() in ("", ".", "..", ".git", ".codegraph", ".scannerwork", ".sonar-evidence", ".env")
                   or part.endswith((".", " ")) or IS_RESERVED(part) for part in parts)
            or any(char in target for char in "`<>:*?\"|")):
        raise ValueError("wayfinder-tracker.directory must be a safe project-relative directory")


def validate_github_repository(target):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", target) or target.split("/")[1] in (".", ".."):
        raise ValueError("wayfinder-tracker.repository must be github.com OWNER/REPO")


def validate_gitlab_project(target):
    parsed = urlsplit(target)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username is not None or parsed.password is not None
            or "?" in target or "#" in target or not valid_gitlab_authority(parsed)
            or not re.fullmatch(r"(?:/[A-Za-z0-9_.-]+){2,}", parsed.path)
            or any(part in (".", "..") for part in parsed.path.split("/"))):
        raise ValueError("wayfinder-tracker.project must be an HTTPS project URL without credentials, query or fragment")


def resolve_tracker(value):
    if not isinstance(value, dict) or value.get("provider") not in ("local", "github", "gitlab"):
        raise ValueError("wayfinder-tracker must select provider local, github or gitlab")
    provider = value["provider"]
    field = {"local": "directory", "github": "repository", "gitlab": "project"}[provider]
    if value.keys() - {"provider", field}:
        raise ValueError("wayfinder-tracker contains unsupported provider-specific keys")
    target = value.get(field, ".scratch" if provider == "local" else None)
    if not isinstance(target, str) or not target or target != target.strip() or any(ord(char) < 32 for char in target):
        raise ValueError(f"wayfinder-tracker.{field} must be a nonempty string")
    validators = {"local": validate_tracker_directory, "github": validate_github_repository, "gitlab": validate_gitlab_project}
    validators[provider](target)
    return {"provider": provider, field: target}


def resolve_settings(settings, defaults, location="configuration"):
    if not isinstance(settings, dict) or settings.keys() - defaults.keys():
        raise ValueError(f"{location} must be an object containing only supported keys")
    result = {}
    for key, default in defaults.items():
        value = settings.get(key, default)
        if location == "configuration" and key == "wayfinder-tracker":
            result[key] = resolve_tracker(value)
        elif isinstance(default, dict):
            result[key] = resolve_settings(value, default, f"{location}.{key}")
        elif type(value) is bool:
            result[key] = value
        else:
            raise ValueError(f"{location}.{key} must be a JSON boolean")
    return result


def preserve_permissions(source, destination):
    shutil.copymode(source, destination)
    if os.name == "nt":
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if not powershell:
            raise OSError("PowerShell is required to preserve configuration permissions")
        result = subprocess.run(
            [powershell, "-NoProfile", "-NonInteractive", "-Command",
             "$ErrorActionPreference = 'Stop'; Set-Acl -LiteralPath $env:KISS_CONFIG_TEMP -AclObject (Get-Acl -LiteralPath $env:KISS_CONFIG_SOURCE)"],
            env={**os.environ, "KISS_CONFIG_SOURCE": str(source.absolute()), "KISS_CONFIG_TEMP": str(destination.absolute())},
            capture_output=True, timeout=30,
        )
        if result.returncode:
            raise OSError("Could not preserve configuration permissions")


def update_configuration(path, original, previous, configuration):
    if os.name == "nt" and not previous.st_mode & stat.S_IWRITE:
        raise PermissionError("Read-only configuration cannot be updated")
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    staging = Path(name)
    try:
        preserve_permissions(path, staging)
        with staging.open("w", encoding="utf-8", newline="\n") as output:
            json.dump(configuration, output, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        current = path.lstat()
        identity = ("st_dev", "st_ino", "st_mtime_ns", "st_size")
        if (not stat.S_ISREG(current.st_mode)
                or any(getattr(current, field) != getattr(previous, field) for field in identity)
                or path.read_bytes() != original):
            raise ValueError("Configuration changed concurrently; update refused")
        # shortcut: a noncooperating writer can race this final check; use shared locking if concurrent writers become a supported workflow.
        os.replace(staging, path)
    finally:
        staging.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--update", action="store_true", help="Add missing defaults to an existing valid configuration")
    args = parser.parse_args()
    try:
        if not args.project.is_dir():
            raise ValueError("Project must be an existing directory")
        path = args.project / "kiss-chris-stack.config.json"
        if args.update and path.is_symlink():
            raise ValueError("Configuration update target must be a regular file, not a symlink")
        previous = path.lstat() if path.exists() else None
        if args.update and previous and not stat.S_ISREG(previous.st_mode):
            raise ValueError("Configuration update target must be a regular file")
        original = path.read_bytes() if previous else None
        settings = json.loads(original.decode("utf-8-sig"), object_pairs_hook=unique_object) if original is not None else {}
        configuration = resolve_settings(settings, DEFAULTS)
        if args.update and original is not None and settings != configuration:
            update_configuration(path, original, previous, configuration)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.error(str(error))
    print(json.dumps(configuration, indent=2))


if __name__ == "__main__":
    main()
