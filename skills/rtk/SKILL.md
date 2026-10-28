---
name: rtk
description: Use RTK to reduce shell output while preserving failures, exit codes, and verification evidence during stack work.
---

# RTK

Use the installed `rtk` CLI where it supports the intended command. Consult `rtk --help` rather than inventing wrapper syntax. Retain errors, test outcomes and exit codes; use complete native output when compact output would hide necessary evidence. Prefer `rg` for literal searches.

[Setup](../setup/SKILL.md) checks the version from [versions.json](../../assets/versions.json) and can install an official platform binary after checksum verification. Unsupported OS/architecture or missing checksum blocks repair. Installation does not silently approve hooks or change trust settings.
