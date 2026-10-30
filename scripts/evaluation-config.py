#!/usr/bin/env python3
"""Resolve project workflow and evaluation switches without changing files or running commands."""
import argparse
import json
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    try:
        if not args.project.is_dir():
            raise ValueError("Project must be an existing directory")
        path = args.project / "kiss-chris-stack.config.json"
        settings = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object) if path.exists() else {}
        configuration = resolve_settings(settings, DEFAULTS)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(configuration, indent=2))


if __name__ == "__main__":
    main()
