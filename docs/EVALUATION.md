# Workflow and evaluation configuration

The separate evaluation agent follows [evaluate](../skills/evaluate/SKILL.md). The root resolves project configuration before defining acceptance criteria, and evaluation re-reads it before goal completion. The project-local [kiss-chris-stack.config.json](../kiss-chris-stack.config.json) controls routed interviews/Wayfinder, goal approval and two independent evaluation gates:

```json
{
  "grill-me": true,
  "grill-with-docs": true,
  "wayfinder": true,
  "wayfinder-tracker": { "provider": "local", "directory": ".scratch" },
  "plan-mode": false,
  "evaluation": {
    "live": { "enabled": true },
    "sonarqube": { "enabled": true }
  }
}
```

## Settings reference

The JSON root is an object. `evaluation` is an object grouping the two independent gates; `evaluation.live` and `evaluation.sonarqube` are objects containing their `enabled` boolean. These containers are not booleans themselves. Workflow/evaluation switches are strict booleans. Their supported leaves are:

| Setting | Default | `true` | `false` |
| --- | --- | --- | --- |
| `grill-me` | `true` | Compatibility key for explicit invocation; no additional automatic legacy interview. | Explicit invocation remains available. |
| `grill-with-docs` | `true` | Enable delegated interview/domain documentation for unclear normal work before goal. | Skip automatic skill use; unresolved decisions still need answers or a routing choice. |
| `wayfinder` | `true` | Map large work and schedule all unblocked tickets in parallel through stack goals. | Skip automatic skill use; proceed only with settled requirements and a safe bounded route. |
| `plan-mode` | `false` | Present the registered goal, request explicit approval and yield before dispatching test, implementation or evaluation roles. | Continue automatically after goal registration. |
| `evaluation.live.enabled` | `true` | Require applicable functional proof against the actual project; use document/contract checks for documentation-only work. | Skip the live evaluation gate; keep ordinary goal tests. |
| `evaluation.sonarqube.enabled` | `true` | Require fresh current-source, analysis-specific green quality gates for every relevant configured SonarQube project. | Skip scanner, readback and token operations; preserve service configuration, credentials and data. |

Defaults apply independently to omitted settings and containers. Only literal JSON `true` and `false` are accepted for these switches: strings such as `"false"`, numbers such as `0`, and `null` are invalid. Unknown keys and duplicate keys at any depth are rejected by the [resolver](../scripts/evaluation-config.py). Feedback learning follows the [project feedback workflow](LEARNING.md); there is no supported learning switch in this file.

For example, to review each goal before implementation while retaining live proof and deliberately skipping SonarQube:

```json
{
  "plan-mode": true,
  "evaluation": {
    "live": { "enabled": true },
    "sonarqube": { "enabled": false }
  }
}
```

This is an optional example, not this repository's active configuration. Routing, approval and gate switches are independent; disabling a gate does not disable tests, readiness checks or feedback review. Agents must not change a value merely to bypass a failing check.

## Wayfinder target

The independent `wayfinder-tracker` selected-variant object defaults to `{ "provider": "local", "directory": ".scratch" }`. Supported variants are local `directory` (safe project-relative path), GitHub `repository` (`OWNER/REPO` on github.com) and GitLab `project` (explicit HTTPS project URL). A present object must name `provider`; only local can omit its directory to use `.scratch`. Hosted target fields are required and never default from remotes. Unknown/provider-mismatched keys, unsafe paths/hosts, credentials/query/fragment URLs and missing targets are invalid, even if automatic Wayfinder is disabled. See [storage/setup](WAYFINDER.md).

The resolver preserves explicit provider/location values; no local fields are injected into hosted variants. First initialization and every explicit `/setup` ask the storage choice and target, display any current selection, and wait for the user's answer before dependent writes; defaults/backfill do not answer that question. Ordinary per-task readiness reuses validated config without another prompt. Required setup wiring prepares/checks the selected root and managed operations doc, before config-last creation with exact pending first-init settings or as targeted ordinary reconciliation. It creates no effort/map/tickets and preserves old artifacts and user document content. Read-only hosted prerequisites block missing/auth/Issues/access targets without fallback or automatic installation/login; they never authorize writes.

## Approval, initialization and updates

The root selects a semantic route before setup or configuration backfill: tiny bounded low-risk fixes use a delegated direct worker without setup/goal/triad overhead; clear normal features/bugs use stack with goal; unclear normal work uses [grill-with-docs](../skills/grill-with-docs/SKILL.md) before goal; large work uses [Wayfinder](../skills/wayfinder/SKILL.md), followed by every unblocked ticket in parallel through stack goals within host capacity and isolated write ownership. Scope/risk/uncertainty emerging on the direct route escalates before wider edits.

`grill-with-docs` and `wayfinder` are independent strict JSON booleans defaulting to `true`. They enable only the selected automatic route. Legacy `grill-me` remains supported/default `true` for explicit invocation, with no automatic legacy interview. Explicit skill requests remain available even when automatic switches are false. Disabled selected skills are reported skipped, never permission to implement unresolved requirements. Interviews wait for actual user answers/pending research, resume across replies and continue automatically without a closing confirmation when settled. Clear requests need no invented questions.

All pure context gathering, including before interviews/goals, uses fresh `gpt-6-luna` low-reasoning agents, facts and source-linked notes only, no source/configuration changes, implementation or design decisions. The root delegates substantive interviewing/planning, documentation, tests, implementation and evaluation, retaining lifecycle coordination and evidence review. Unsupported requested research controls are visible blockers without silent fallback. For large work root schedules separate phases per ticket, records prerequisite completion and evaluates integrated source. One-active-native-goal hosts keep one umbrella with explicitly textual/unregistered strong ticket goals.

Top-level `plan-mode` defaults to `false`, preserving automatic execution after goal registration, including for existing files without this key. Set it to `true` to have the root present the strong registered goal, request explicit user approval and end its turn before dispatching test, implementation or evaluation agents. Approval resumes the same goal; a changed goal requires renewed approval. Rejection, silence, elapsed time and pending replies do not authorize implementation. An interview's automatic completion or a disabled routing switch never replaces this separate `plan-mode=true` goal approval. These are agent workflow rules, not switches for the host's collaboration mode; live and SonarQube evaluation remain independent.

This root file is also the project's initialization indicator. First-time [setup](../skills/setup/SKILL.md) creates it with the validated user-selected settings, using defaults only for omitted non-choice settings, after successful runtime readiness, a real session MCP call and documentation bootstrap. Existing configuration is strictly validated and updated only by adding missing current defaults; explicit values are preserved unless the user changes them. After onboarding and task route selection, stack hooks use its absence to select initialization and its presence to supply an updater argv for the root before current readiness checks without reinitialization; documentation folders are not setup markers. First initialization and explicit `/setup` must resolve the required storage question before dependent writes; ordinary readiness does not ask again. Explicit `/setup` can still fill documentation gaps. A failed/reload-required initial setup leaves the file absent. Installation [onboarding](../skills/onboarding/SKILL.md) asks for consent and then an explicit existing project path before setup begins.

Set either `enabled` to `false` to deliberately skip that gate. Ordinary goal tests still apply. Disabled checks are reported as skipped, never passed. Agents must not disable a check to evade a failure. Both defaults are `true` if the file or nested settings are absent; SonarQube applies only to already configured projects, with no implicit provisioning. Missing/stopped services or credentials do not disable configured enforcement. Invalid JSON, duplicate/unknown keys, wrong types and unreadable configuration block evaluation. UTF-8 BOM files are accepted. The configuration contains no executable startup commands or secrets.

Resolve the effective settings without modifying any files:

```powershell
python "<plugin-root>/scripts/evaluation-config.py" --project "<project-root>"
```

Without `--update`, the resolver only reads and validates workflow/evaluation switches and tracker target; its defaults for an absent file do not initialize a project or create that file. The agent executes the evaluation workflow; this is not an unattended test runner. In particular, enabling a flag does not itself start a process or install dependencies.

For an initialized stack root task, the hook supplies a JSON argv array for the root to execute with its actual Python interpreter after onboarding/task routing and before runtime readiness:

```powershell
python "<plugin-root>/scripts/evaluation-config.py" --project "<project-root>" --update
```

This explicit updater compares the valid existing configuration with the current bundled defaults and adds only missing fields, including nested ones. It preserves all explicit values, removes or renames no fields, and creates no absent configuration. A complete file is a byte/mtime-preserving no-op. Invalid configuration, unsafe nonregular/symlink targets, Windows read-only files needing changes, permission failures and detected concurrent edits block updates without replacing the original. Changed configuration uses a same-directory staging file with copied permissions (including Windows ACL before content is written), then atomic replacement and cleanup of its own staging file. A final noncooperating-writer race between the last check and replacement remains; shared locking is outside this workflow's scope.

The bare hook itself remains read-only. It cannot determine installation consent from arbitrary prompt text, so only the root assigns execution of the supplied argv after selecting a stack route. Tiny direct tasks skip it. Pending or declined installation onboarding never executes it; evaluation and other delegated roles continue using read-only resolution, except an explicitly root-assigned setup/preparation worker executing the supplied updater argv. Default backfill is not project reinitialization and cannot override a user's explicit interview/Wayfinder, evaluation gate or approval setting.

## Live behavior

When enabled, run the actual affected project directly or with its existing Docker Compose setup, using the evaluated working tree and fresh builds. Start required components, wait for bounded readiness and exercise the changed behavior with meaningful assertions. A running process or a healthy endpoint alone cannot satisfy the gate. Record commands, runtime identity, source revision/dirty fingerprint, exit codes, assertions and useful artifacts without secrets. Any subsequent affected source change requires fresh proof.

Affected frontend behavior requires a real browser and/or Playwright against the running application, including actual interactions and user-visible assertions. The agent automatically installs missing test dependencies, Playwright CLI and a matching headless Chromium browser within host permissions, without another confirmation. Existing pinned runners/caches take precedence; otherwise use an isolated tool cache and record the resolved version. The [skill](../skills/evaluate/SKILL.md#live-functional-proof) links official installation commands, compatibility checks and Linux dependency options. A real browser launch and workflow assertions establish readiness; successful package installation alone does not. Required network, permission or browser failures block the enabled gate.

Projects with no frontend do not install browser dependencies. Backend/API/CLI/plugin behavior is exercised through the real interface. Documentation-only tasks use applicable contract/document checks and explicitly explain why runtime checks are inapplicable. This repository is a plugin without its own frontend: real helper and hook subprocesses provide its runtime verification, rather than an invented web application.

Use local test environments/data. Local evaluation grants no production writes, remote-engine mutation, security-setting changes or approval bypass. Cleanup stops only evaluation-owned processes, sessions and containers; reused services, volumes and data remain intact.

## SonarQube

When enabled and configured, preserve the existing renewal preflight, measured coverage requirements and fresh analysis-specific green gates for every relevant project/component. See [SonarQube operations](SONARQUBE.md). An explicit disabled switch skips automatic scanner/readback/token operations but preserves services, credentials and scanner configuration. The switch does not weaken server thresholds or remove existing quality configuration. The repository keeps both gates enabled.
