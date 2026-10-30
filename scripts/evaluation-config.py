#!/usr/bin/env python3
"""Resolve project switches; optionally backfill missing defaults in existing configuration."""
import argparse
import json
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path


DEFAULTS = {"plan-mode": False, "evaluation": {"live": {"enabled": True}, "sonarqube": {"enabled": True}}}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate configuration key")
        result[key] = value
    return result


def resolve_settings(settings, defaults, location="configuration"):
    if not isinstance(settings, dict) or settings.keys() - defaults.keys():
        raise ValueError(f"{location} must be an object containing only supported keys")
    result = {}
    for key, default in defaults.items():
        value = settings.get(key, default)
        if isinstance(default, dict):
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
