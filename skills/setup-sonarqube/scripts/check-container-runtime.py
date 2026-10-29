#!/usr/bin/env python3
"""Read-only optional check for a reachable Linux Docker or Podman engine."""
import json
import shutil
import subprocess


def engine_os(info, engine):
    if not isinstance(info, dict):
        return None
    if engine == "docker":
        return info.get("OSType")
    host = info.get("host")
    return host.get("os") if isinstance(host, dict) else None


def check_runtime():
    attempts = []
    for engine in ("docker", "podman"):
        executable = shutil.which(engine)
        if not executable:
            attempts.append({"engine": engine, "reason": "CLI missing"})
            continue
        try:
            result = subprocess.run(
                [executable, "info", "--format", "{{json .}}"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode:
                attempts.append({"engine": engine, "reason": "Engine unavailable or access denied"})
                continue
            info = json.loads(result.stdout)
            if engine_os(info, engine) == "linux":
                return {"available": True, "engine": engine, "reason": "Reachable Linux engine", "attempts": attempts}
            reason = "Linux engine not confirmed"
        except (OSError, ValueError, subprocess.SubprocessError):
            reason = "Engine check failed or timed out"
        attempts.append({"engine": engine, "reason": reason})
    return {"available": False, "engine": None, "reason": "Install or start a Linux container runtime; /setup-sonarqube can run later", "attempts": attempts}


if __name__ == "__main__":
    print(json.dumps(check_runtime(), indent=2))
