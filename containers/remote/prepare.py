#!/usr/bin/env python3
"""Create a dedicated SSH identity and pin this Compose target's host key."""

import base64
import binascii
import os
from pathlib import Path
import shlex
import subprocess
import time


def _quote_path(path: Path) -> str:
    value = str(path)
    if any(character in value for character in "\n\r\0$"):
        raise ValueError("SSH config paths cannot contain newlines, NUL, or dollar signs")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%") + '"'


def _host_key(output: str) -> str:
    lines = output.strip().splitlines()
    fields = lines[0].split() if len(lines) == 1 else []
    if len(fields) < 2 or fields[0] != "ssh-ed25519":
        raise ValueError("Container did not return one Ed25519 SSH host key")
    try:
        blob = base64.b64decode(fields[1], validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError("Container returned an invalid SSH host key") from error
    if len(blob) != 51 or not blob.startswith(b"\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20"):
        raise ValueError("Container returned an invalid Ed25519 SSH host key")
    return " ".join(fields[:2])


def prepare(root: Path) -> Path:
    """Prepare containers/remote and return its standalone SSH config path."""
    root = root.resolve()
    port_value = os.environ.get("KISS_SSH_PORT", "2222")
    if not port_value.isascii() or not port_value.isdecimal() or not 1 <= int(port_value) <= 65535:
        raise ValueError("KISS_SSH_PORT must be an integer from 1 to 65535")
    port = int(port_value)
    runtime = root / ".runtime"
    identity = runtime / "id_ed25519"
    known_hosts = runtime / "known_hosts"
    config = runtime / "ssh_config"
    identity_path, hosts_path = _quote_path(identity), _quote_path(known_hosts)
    runtime.mkdir(mode=0o700, exist_ok=True)
    runtime.chmod(0o700)
    if not identity.exists():
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(identity)], check=True)
    identity.chmod(0o600)
    public = identity.with_suffix(".pub")
    if not public.exists():
        result = subprocess.run(["ssh-keygen", "-y", "-f", str(identity)], check=True, capture_output=True, text=True)
        public.write_text(result.stdout, encoding="utf-8")

    compose = ["docker", "compose", "-f", str(root / "compose.yaml")]
    subprocess.run(compose + ["up", "-d", "--build"], check=True)
    for attempt in range(10):
        try:
            result = subprocess.run(
                compose + ["exec", "-T", "agent", "cat", "/var/lib/kiss-ssh/ssh_host_ed25519_key.pub"],
                check=True, capture_output=True, text=True, timeout=5,
            )
            key = _host_key(result.stdout)
            break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            if attempt == 9:
                raise RuntimeError("Container SSH host key was unavailable after 10 attempts") from error
            time.sleep(1)

    known_hosts.write_text(f"[127.0.0.1]:{port} {key}\n", encoding="utf-8")
    config.write_text(
        "Host kiss-container\n"
        "  HostName 127.0.0.1\n"
        f"  Port {port}\n"
        "  User node\n"
        f"  IdentityFile {identity_path}\n"
        f"  UserKnownHostsFile {hosts_path}\n"
        "  IdentitiesOnly yes\n"
        "  IdentityAgent none\n"
        "  ForwardAgent no\n"
        "  StrictHostKeyChecking yes\n",
        encoding="utf-8",
    )
    known_hosts.chmod(0o600)
    config.chmod(0o600)
    return config


if __name__ == "__main__":
    config = prepare(Path(__file__).resolve().parent)
    print(f"SSH target ready. Test: ssh -F {shlex.quote(str(config))} kiss-container")
    print(f"Review and copy the Host block from {config} into your SSH config, preserving existing entries.")
    print("Add the kiss-container SSH connection in Codex, open /work, and complete login and hook review there.")
