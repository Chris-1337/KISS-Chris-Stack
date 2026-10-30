"""Prepare an isolated SSH target without using Docker or host credentials."""
import base64
import importlib.util
import runpy
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest


HELPER = Path(__file__).parents[1] / "containers/remote/prepare.py"
REAL_RUN = subprocess.run


def public_key():
    algorithm = b"ssh-ed25519"
    blob = struct.pack(">I", len(algorithm)) + algorithm + struct.pack(">I", 32) + b"k" * 32
    return "ssh-ed25519 " + base64.b64encode(blob).decode() + " container-host"


@pytest.fixture
def helper():
    assert HELPER.is_file(), "The isolated target needs its bootstrap helper"
    spec = importlib.util.spec_from_file_location("remote_environment_under_test", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def target(tmp_path, monkeypatch):
    monkeypatch.delenv("KISS_SSH_PORT", raising=False)
    home = tmp_path / "host-home"
    (home / ".ssh").mkdir(parents=True)
    (home / ".ssh/config").write_text("Host personal\n  HostName example.invalid\n")
    (home / ".ssh/id_ed25519").write_text("host private credential")
    (home / ".git-credentials").write_text("host git credential")
    monkeypatch.setenv("HOME", str(home))
    root = tmp_path / 'remote workspace "quoted"'
    root.mkdir()
    (root / "compose.yaml").write_text("services: {}\n")
    return root, home


def mock_commands(monkeypatch, root, host_key=None, docker_failure=False):
    calls = []

    def run(argv, **kwargs):
        argv = list(map(str, argv))
        calls.append(argv)
        assert not kwargs.get("shell"), "Paths and commands must use argv, never a shell"
        if argv[0] == "ssh-keygen":
            key = Path(argv[argv.index("-f") + 1])
            assert key.parent == root / ".runtime"
            if "-y" in argv:
                assert key.is_file(), "Public-key recovery must read the existing private key"
                return subprocess.CompletedProcess(argv, 0, public_key() + "\n", "")
            key.write_text("new dedicated private key")
            key.with_suffix(key.suffix + ".pub").write_text(public_key() + "\n")
            return subprocess.CompletedProcess(argv, 0, "", "")
        compose = ["docker", "compose", "-f", str(root / "compose.yaml")]
        if argv == compose + ["up", "-d", "--build"]:
            if docker_failure:
                raise subprocess.CalledProcessError(17, argv, stderr="Docker is unavailable")
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv == compose + ["exec", "-T", "agent", "cat", "/var/lib/kiss-ssh/ssh_host_ed25519_key.pub"]:
            return subprocess.CompletedProcess(argv, 0, (public_key() if host_key is None else host_key) + "\n", "")
        pytest.fail(f"Unexpected external command: {argv}")

    monkeypatch.setattr(subprocess, "run", run)
    return calls


def snapshot(root):
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def test_fresh_preparation_creates_dedicated_key_and_pinned_target(helper, target, monkeypatch):
    root, home = target
    original_credentials = snapshot(home)
    calls = mock_commands(monkeypatch, root)

    helper.prepare(root)

    runtime = root / ".runtime"
    assert (runtime / "id_ed25519").read_text() == "new dedicated private key"
    assert (runtime / "id_ed25519.pub").is_file()
    assert (runtime / "known_hosts").read_text() == "[127.0.0.1]:2222 " + " ".join(public_key().split()[:2]) + "\n"
    assert (runtime / "ssh_config").is_file()
    assert (runtime.stat().st_mode & 0o077) == 0
    assert ((runtime / "id_ed25519").stat().st_mode & 0o077) == 0
    assert snapshot(home) == original_credentials
    assert all(b"host private credential" not in data and b"host git credential" not in data for data in snapshot(root).values())
    assert sum(argv[0] == "ssh-keygen" for argv in calls) == 1
    assert calls.index(["docker", "compose", "-f", str(root / "compose.yaml"), "up", "-d", "--build"]) < len(calls) - 1


def test_ssh_config_is_usable_with_space_and_quote_paths(helper, target, monkeypatch):
    root, _ = target
    mock_commands(monkeypatch, root)
    helper.prepare(root)
    ssh = shutil.which("ssh")
    assert ssh, "OpenSSH is required to validate the generated SSH config"

    result = REAL_RUN([ssh, "-G", "-F", str(root / ".runtime/ssh_config"), "kiss-container"], check=True, capture_output=True, text=True)
    settings = dict(line.split(" ", 1) for line in result.stdout.splitlines())

    assert settings["hostname"] == "127.0.0.1"
    assert settings["port"] == "2222"
    assert settings["user"] == "node"
    assert settings["identityagent"] == "none"
    assert settings["identitiesonly"] == "yes"
    assert settings["stricthostkeychecking"] == "true"
    assert settings["identityfile"] == str(root / ".runtime/id_ed25519")
    assert settings["userknownhostsfile"].strip('"') == str(root / ".runtime/known_hosts")


@pytest.mark.parametrize("public_key_exists", [True, False])
def test_repeated_preparation_preserves_existing_private_key(helper, target, monkeypatch, public_key_exists):
    root, _ = target
    runtime = root / ".runtime"
    runtime.mkdir(mode=0o700)
    private_key = runtime / "id_ed25519"
    private_key.write_bytes(b"existing dedicated private key\n")
    private_key.chmod(0o600)
    if public_key_exists:
        private_key.with_suffix(".pub").write_text(public_key() + "\n")
    calls = mock_commands(monkeypatch, root)

    helper.prepare(root)
    first = snapshot(runtime)
    helper.prepare(root)

    assert private_key.read_bytes() == b"existing dedicated private key\n"
    assert private_key.with_suffix(".pub").is_file()
    assert snapshot(runtime) == first
    assert all("-y" in argv for argv in calls if argv[0] == "ssh-keygen")


@pytest.mark.parametrize("host_key", ["not a public key", "ssh-ed25519 !!!", "ssh-rsa AAAA", public_key() + "\nssh-ed25519 AAAA"])
def test_malformed_host_key_cannot_publish_ssh_target(helper, target, monkeypatch, host_key):
    root, _ = target
    mock_commands(monkeypatch, root, host_key=host_key)

    with pytest.raises((ValueError, RuntimeError)):
        helper.prepare(root)

    assert not (root / ".runtime/known_hosts").exists()
    assert not (root / ".runtime/ssh_config").exists()


def test_docker_start_failure_propagates_without_publishing_ssh_target(helper, target, monkeypatch):
    root, _ = target
    calls = mock_commands(monkeypatch, root, docker_failure=True)

    with pytest.raises(subprocess.CalledProcessError) as error:
        helper.prepare(root)

    assert error.value.returncode == 17
    assert not any("exec" in argv for argv in calls)
    assert not (root / ".runtime/known_hosts").exists()
    assert not (root / ".runtime/ssh_config").exists()


def test_explicit_port_is_pinned_in_generated_ssh_target(helper, target, monkeypatch):
    root, _ = target
    monkeypatch.setenv("KISS_SSH_PORT", "2223")
    mock_commands(monkeypatch, root)

    helper.prepare(root)

    assert (root / ".runtime/known_hosts").read_text().startswith("[127.0.0.1]:2223 ")
    ssh = shutil.which("ssh")
    assert ssh, "OpenSSH is required to validate the generated SSH config"
    result = REAL_RUN([ssh, "-G", "-F", str(root / ".runtime/ssh_config"), "kiss-container"], check=True, capture_output=True, text=True)
    assert "port 2223\n" in result.stdout


@pytest.mark.parametrize("port", ["", "0", "65536", "abc", "22.5"])
def test_invalid_port_fails_before_side_effects(helper, target, monkeypatch, port):
    root, _ = target
    monkeypatch.setenv("KISS_SSH_PORT", port)
    calls = mock_commands(monkeypatch, root)

    with pytest.raises(ValueError):
        helper.prepare(root)

    assert calls == []
    assert not (root / ".runtime").exists()


def test_cli_defaults_to_script_directory(helper, target, tmp_path, monkeypatch):
    root, _ = target
    script = root / "prepare.py"
    shutil.copyfile(HELPER, script)
    mock_commands(monkeypatch, root)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [str(script)])

    runpy.run_path(str(script), run_name="__main__")

    assert (root / ".runtime/ssh_config").is_file()
    assert not (tmp_path / ".runtime").exists()
