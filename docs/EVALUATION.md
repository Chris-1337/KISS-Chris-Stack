# Configurable evaluation

The separate evaluation agent follows [evaluate](../skills/evaluate/SKILL.md). The root resolves project configuration before defining acceptance criteria, and evaluation re-reads it before goal completion. The project-local [kiss-chris-stack.config.json](../kiss-chris-stack.config.json) controls two independent gates:

```json
{
  "evaluation": {
    "live": { "enabled": true },
    "sonarqube": { "enabled": true }
  }
}
```

Set either `enabled` to `false` to deliberately skip that gate. Ordinary goal tests still apply. Disabled checks are reported as skipped, never passed. Agents must not disable a check to evade a failure. Both defaults are `true` if the file or nested settings are absent; SonarQube applies only to already configured projects, with no implicit provisioning. Missing/stopped services or credentials do not disable configured enforcement. Invalid JSON, duplicate/unknown keys, wrong types and unreadable configuration block evaluation. UTF-8 BOM files are accepted. The configuration contains no executable startup commands or secrets.

Resolve the effective settings without modifying any files:

```powershell
python "<plugin-root>/scripts/evaluation-config.py" --project "<project-root>"
```

The resolver only reads and validates switches. The agent executes the evaluation workflow; this is not an unattended test runner. In particular, enabling a flag does not itself start a process or install dependencies.

## Live behavior

When enabled, run the actual affected project directly or with its existing Docker Compose setup, using the evaluated working tree and fresh builds. Start required components, wait for bounded readiness and exercise the changed behavior with meaningful assertions. A running process or a healthy endpoint alone cannot satisfy the gate. Record commands, runtime identity, source revision/dirty fingerprint, exit codes, assertions and useful artifacts without secrets. Any subsequent affected source change requires fresh proof.

Affected frontend behavior requires a real browser and/or Playwright against the running application, including actual interactions and user-visible assertions. The agent automatically installs missing test dependencies, Playwright CLI and a matching headless Chromium browser within host permissions, without another confirmation. Existing pinned runners/caches take precedence; otherwise use an isolated tool cache and record the resolved version. The [skill](../skills/evaluate/SKILL.md#live-functional-proof) links official installation commands, compatibility checks and Linux dependency options. A real browser launch and workflow assertions establish readiness; successful package installation alone does not. Required network, permission or browser failures block the enabled gate.

Projects with no frontend do not install browser dependencies. Backend/API/CLI/plugin behavior is exercised through the real interface. Documentation-only tasks use applicable contract/document checks and explicitly explain why runtime checks are inapplicable. This repository is a plugin without its own frontend: real helper and hook subprocesses provide its runtime verification, rather than an invented web application.

Use local test environments/data. Local evaluation grants no production writes, remote-engine mutation, security-setting changes or approval bypass. Cleanup stops only evaluation-owned processes, sessions and containers; reused services, volumes and data remain intact.

## SonarQube

When enabled and configured, preserve the existing renewal preflight, measured coverage requirements and fresh analysis-specific green gates for every relevant project/component. See [SonarQube operations](SONARQUBE.md). An explicit disabled switch skips automatic scanner/readback/token operations but preserves services, credentials and scanner configuration. The switch does not weaken server thresholds or remove existing quality configuration. The repository keeps both gates enabled.
