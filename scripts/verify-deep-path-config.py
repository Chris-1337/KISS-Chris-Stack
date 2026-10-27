#!/usr/bin/env python3
"""Verify the bounded KISS-Chris-Stack Ouroboros settings."""

from ouroboros.config.loader import load_config


EXPECTED = {
    "clarification.max_interview_rounds": 3,
    "execution.max_iterations_per_ac": 3,
    "execution.auto_evolve": False,
    "execution.auto_evolve_max_generations": 1,
    "execution.verify_command_timeout_seconds": 600,
    "evaluation.stage1_enabled": True,
    "evaluation.stage2_enabled": True,
    "evaluation.stage3_enabled": False,
    "runtime_controls.generation_idle_timeout_seconds": 600.0,
    "runtime_controls.generation_no_progress_timeout_seconds": 900.0,
    "runtime_controls.generation_safety_timeout_seconds": 3600.0,
    "orchestrator.default_max_turns": 6,
    "seed.verify_command_gate": "block",
}


def nested_value(config, path):
    value = config
    for segment in path.split("."):
        value = getattr(value, segment)
    return value


def main():
    config = load_config()
    mismatches = [
        f"{path}: expected {expected!r}, got {nested_value(config, path)!r}"
        for path, expected in EXPECTED.items()
        if nested_value(config, path) != expected
    ]
    if mismatches:
        raise SystemExit("ERROR: Deep Path configuration mismatch\n" + "\n".join(mismatches))
    print("OK  bounded Ouroboros Deep Path configuration")


if __name__ == "__main__":
    main()
