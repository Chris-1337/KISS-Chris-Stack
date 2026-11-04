# KISS-Chris-Stack

A complete Codex plugin for context-first goals and separate test, implementation, and evaluation agents. It bundles the orchestrator, setup, six Ponytail skills, grill-with-docs, Wayfinder and their skill/resource dependencies, Grilling, Caveman, UI-UX-Pro-Max with search code/data, and CodeGraph/RTK guides. See [architecture](docs/ARCHITEKTUR.md), [onboarding](docs/PRODUKT-ONBOARDING.md), and [provenance](docs/THIRD-PARTY.md).

Project-original material is [MIT licensed](LICENSE). Bundled third-party components retain their [own licenses and notices](docs/THIRD-PARTY.md). See [contributing](CONTRIBUTING.md), [security reporting](SECURITY.md), and [publication setup](docs/GITHUB-PUBLICATION.md).

## Plugin is good for / not so good for

**Good for:**

- **New features and larger tasks:** turn work across multiple files or components into a clear goal with separate test, implementation, and evaluation roles.
- **Making projects agent-ready:** establish evidence-backed architecture documentation, decisions, agent traces, and verified local tooling.
- **Refactorings and regression-sensitive fixes:** use existing context and call paths, preserve behavior, and verify the result independently.
- **Work that needs reviewable evidence:** keep acceptance criteria, tests, applicable live checks, and configured quality gates tied to the actual change.

**Not so good for:**

- **Tiny tasks needing the full stack:** ordinary clear low-risk minimal changes now use a delegated direct worker, with focused checks and no setup/goal/three-role overhead; uncertainty or risk escalates to stack.
- **Quick questions and one-off lookups:** the full workflow adds little value when no implementation or independent verification is needed.
- **Environments without the required tooling or permissions:** missing runtimes, unavailable MCP tools, or an unreachable configured quality service must be resolved before work can complete.
- **Replacing product or domain decisions:** the stack organizes implementation and verification; unclear requirements still need human input.

## Roadmap

These are future directions, not implemented capabilities or delivery commitments:

- **Routing evidence:** exercise the four configured routes in real host/model sessions and measure their overhead; the routing instructions and contract checks do not guarantee future model compliance.
- **Broader model selection:** context collection is already fixed to fresh GPT-6 Luna low agents; measure choices for other substantive roles without changing that requirement.
- **Simpler onboarding and recovery:** reduce manual steps around prerequisites, MCP visibility, and host reloads while preserving normal hook trust and explicit permissions.
- **Measured overhead:** compare token use, elapsed time, and verification outcomes across task sizes to guide routing and model choices with evidence.
- **Broader compatibility evidence:** verify fresh-machine installation and trusted hook execution across supported hosts and platforms, and document remaining gaps.

## Install through the repository marketplace

Add the GitHub repository marketplace directly; no manual clone or checkout is required:

```powershell
codex plugin marketplace add https://github.com/Chris-1337/KISS-Chris-Stack.git
codex plugin add kiss-chris-stack@kiss-chris-stack
```

The repository provides the marketplace and plugin files used by these commands.

Alternatively install from the repository marketplace in the Codex desktop Plugins Directory. No separate installer is required. This is a repository marketplace plugin with lifecycle hooks, not a public-directory submission.

After adding the plugin, [onboarding](skills/onboarding/SKILL.md) asks whether to set up a project. If yes, supply its existing absolute path before setup starts. First initialization and every explicit `/setup` then ask where maps/tickets belong (local/GitHub/GitLab), showing the current provider/location and waiting for a keep/change choice and target before dependent writes. Defaults are not an answer; ordinary per-task readiness does not repeat this prompt. If no, setup does not run: use the slash command `/setup` later, or let a trusted hook initialize the project on a later ordinary task. Installation never assumes its working directory is the project.

Prerequisites: a supported Codex host, Node.js for lifecycle hooks, Python 3.10+ for bundled searches/setup checks. Missing runtimes require local installation and possibly host reload. Enable the plugin and review/trust the hook definition through the normal host UI. Never bypass review.

## Optional: encapsulated execution environment

Run the plugin in its own Docker environment and connect the Codex desktop app to it over local SSH. The desktop remains the graphical interface; Codex, plugin policies, MCP tools, project files and authentication live inside the container.

With Docker Compose, Python 3.10+ and OpenSSH available, run from a checkout of this repository:

```sh
python3 containers/remote/prepare.py
```

This builds the plugin from the current checkout, starts the environment, creates a dedicated local SSH identity, and writes a pinned SSH configuration fragment. It does not edit your existing SSH configuration, copy your credentials or approve hooks. Follow the [remote container guide](docs/REMOTE-CONTAINER.md) to add the connection, sign in and open `/work` in the desktop app.

Docker provides the isolation boundary in this optional mode. Read the guide's permissions and persistence notes before starting it; the ordinary marketplace installation above is unchanged.

## What happens on a task

The active session coordinates and delegates substantive work. After installation onboarding, it selects a route **before setup, configuration backfill or goal registration**:

| Request | Route |
| --- | --- |
| Tiny, clear, bounded low-risk bugfix/minimal change | One delegated direct worker and focused checks, without setup, goal, interview or three-role overhead. Escalate before broader edits if uncertainty, scope or risk grows. |
| Normal feature/bugfix with clear requirements and fetched context | Stack with strong goal and separate test, implementation and evaluation agents, without an automatic interview. |
| Normal effort with unclear requirements | [grill-with-docs](skills/grill-with-docs/SKILL.md) before goal: delegated interview plus prompt glossary/ADR documentation, then stack. |
| Large task | [Wayfinder](skills/wayfinder/SKILL.md), then all unblocked tickets in parallel through stack goals, within host slots and isolated write ownership. |

Classification considers risk and uncertainty, not keywords or a line count. Pure context collection always uses fresh `gpt-6-luna`, low reasoning, no inherited context: source-linked factual notes only, no implementation/source/configuration changes, design decisions, recommendations or speculation. This includes facts needed before grill-me/grilling, goals, Wayfinder and setup. Separate bounded directions run as slots allow; missing requested model/effort/agents blocks required collection rather than silently falling back. The root delegates interviewing, planning, documentation, tests, implementation and evaluation, while retaining routing, questions/approval relay, native goals and evidence review. Role-specific source inspection belongs to the substantive role.

For stack routes, trusted SessionStart/UserPromptSubmit hooks provide root configuration status and a resolver argv; the root assigns `evaluation-config.py --update` before readiness. Existing `kiss-chris-stack.config.json` is validated and only missing defaults are added, preserving explicit values and complete file bytes/mtime. Invalid configuration blocks. Missing configuration triggers setup bootstrap, with marker creation only after runtime/MCP and documentation success; existing markers never trigger repeated initialization merely from missing docs/traces. Bare hooks remain read-only. Onboarding consent/path replies retain priority, including declines; tiny direct tasks do not execute stack preparation.

Setup delegates executable repairs/documentation and checks current tools, resources, marker-owned global rules, the CodeGraph index/registration and actual root-session MCP visibility. No marker/cached flag replaces readiness or host trust. The root reviews referenced `docs/`, `agent-traces/`, relevant code/tests/designs and scoped feedback gathered by the Luna researchers before formulating a stack goal.

Independent strict Boolean `grill-with-docs` and `wayfinder` default to `true` and enable only their selected automatic routes. Legacy `grill-me` remains supported, default `true`, for explicit invocation; it adds no extra automatic interview. Explicit skill requests remain possible with automatic switches false. Disabled selected skills are skipped, never permission to implement unresolved requirements. Interview agents prepare prerequisite-aware questions; root relays them, waits for real user answers and pending research, and resumes the same interview across replies. Once settled, continue automatically without a closing confirmation. Clear requests need no invented questions; documentation roles persist settled glossary/ADR decisions promptly.

Project-root `kiss-chris-stack.config.json` also supports top-level `"plan-mode": false` by default. Set it to `true` to review the strong registered goal before implementation: the root presents it and ends its turn awaiting explicit approval before dispatching test, implementation or evaluation agents. Approval resumes the same goal; omitted/false keeps automatic execution. See [configuration](docs/EVALUATION.md).

Sub-agents receive bounded assignments and context under the root goal or ticket goal; direct workers and setup/context roles may work before an implementation goal. They do not start another setup, native goal or recursive agent group. The root schedules every dependency-ready Wayfinder ticket and its separate phases, queues excess work and verifies integrated source. One-active-native-goal hosts retain a native umbrella with explicitly textual/unregistered strong ticket goals; only root owns native goals. External ticket/branch publication still requires authorization; the local Markdown tracker is the omitted-setting default; an explicitly selected hosted target never silently falls back. Upstream Ponytail lifecycle hooks run alongside stack hooks.

`docs/` holds human architecture, business decisions and ADRs. `agent-traces/<component>/` holds brief records of implemented goals. First-time setup and explicit `/setup` fill only evidence-backed gaps and preserve existing documents; empty projects receive only the structure and generic feedback protocol. Automatic readiness checks in configured projects do not reinitialize missing documentation.

After creating or reusing the system overview, [setup](skills/setup/SKILL.md#module-research-and-synthesis) assigns each real module a fresh-context GPT-6 Luna (`gpt-6-luna`, reasoning `low`) researcher. Each reads only that module and retains source-linked notes under `docs/<module>/`. The root waits for all research, delegates linked module architecture and usage documentation to a separate documentation role, then reviews it, reusing existing layouts. Missing model/agent support or incomplete research blocks bootstrap completion; there is no silent fallback.

After documentation, first-time and explicit setup run [native `/init` and root instruction review](skills/setup/SKILL.md#native-initialization-and-project-instructions) before initialization completion and staging. A delegated documentation role makes project `AGENTS.md` concise and evidence-backed for root review, preserves unique valid rules and links canonical documentation instead of copying it. Existing files, managed blocks and instruction scopes remain protected. If the host cannot dispatch `/init`, setup stays pending until the user runs it in the project and the root reviews the result; ordinary readiness does not repeat this phase.

Successful first-time or explicit `/setup` and authorized `/setup-sonarqube` automatically maintain `.gitignore` for their local artifacts and stage the exact nonsecret files they create or change, including configuration and documentation. The [shared Git workflow](skills/setup/SKILL.md#git-hygiene-and-staging) preserves existing staged/unstaged work, reports mixed files it leaves unstaged, and skips staging outside Git. Ordinary readiness checks do not stage files; setup never commits or pushes.

Actionable user feedback is retained in [`agent-traces/user-feedback/`](agent-traces/user-feedback/README.md). Agents record corrections with concrete prevention actions, review relevant lessons before future goals, and include them in the separate roles' acceptance checks. Setup creates the generic feedback protocol even in empty projects, preserving existing entries; this is project memory maintained by the agent, not model training or a background service. See [learning from feedback](docs/LEARNING.md) for the workflow, an example and its limits.

The [shared language policy](assets/global-stack-policy.md#language) requires English documentation and internal reasoning; user-facing communication follows the language of the prompt. See [ADR 0003](docs/adr/0003-documentation-language.md).

The independent [evaluation step](skills/evaluate/SKILL.md) proves affected functionality in the running project, started directly or with Docker Compose. Frontend changes require real browser/Playwright interactions and assertions; the agent automatically installs missing CLI/headless Chromium dependencies when needed. Project-root [kiss-chris-stack.config.json](kiss-chris-stack.config.json) independently enables/disables `evaluation.live.enabled` and `evaluation.sonarqube.enabled`. Both default to `true`; SonarQube applies to configured projects. Set a switch to `false` for an explicit reported skip. See [configuration and evidence](docs/EVALUATION.md).

## Project configuration

Project-root `kiss-chris-stack.config.json` uses these defaults:

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

| Setting | Default | `true` | `false` |
| --- | --- | --- | --- |
| `grill-me` | `true` | Compatibility key; explicit Grilling remains available, with no extra automatic interview. | Explicit invocation remains available. |
| `grill-with-docs` | `true` | Enable the unclear-normal-work interview/documentation route before goal. | Skip automatic skill use; settle unresolved requirements before work. |
| `wayfinder` | `true` | Enable large-task mapping and parallel unblocked stack tickets. | Skip automatic skill use; choose a safe bounded route or resolve the routing decision. |
| `plan-mode` | `false` | Present the registered goal and wait for explicit approval before dispatching the three roles. | Continue automatically after goal registration. |
| `evaluation.live.enabled` | `true` | Require applicable live functional proof; documentation-only tasks use document/contract checks. | Skip the live gate; ordinary tests still apply. |
| `evaluation.sonarqube.enabled` | `true` | Require fresh green quality gates for configured SonarQube projects. | Skip scanner, readback and token operations; preserve service configuration and data. |

Workflow/evaluation switches must be JSON booleans; quoted booleans, numbers and unknown keys are invalid. The independent `wayfinder-tracker` object selects the typed provider/location: local directory, GitHub.com `OWNER/REPO`, or GitLab HTTPS project URL. See [Wayfinder storage/setup](docs/WAYFINDER.md) for exact examples and safe reconciliation. Setup prepares/checks the selected root and managed operations document without creating a fake map/ticket; invalid/unavailable selected hosted targets block without fallback. Disabled gates are reported as skipped, never passed. Setup creates the file only after successful initialization; later ordinary tasks add missing defaults without overriding explicit values. Feedback learning has no configuration switch. See the [complete configuration reference](docs/EVALUATION.md) for containers, examples, validation and update behavior.

## Verify and repair

After onboarding `/setup`, a usable Linux container engine triggers an optional offer to run [`/setup-sonarqube`](skills/setup-sonarqube/SKILL.md). Docker Desktop, Rancher Desktop (Docker CLI) and Podman are supported through their engine CLI. Without a usable engine, setup explains how to run the skill later and continues. Per-task readiness checks do not repeat the offer. Acceptance provisions local SonarQube, protected project `.env` credentials, actual component analysis and a dedicated gate: zero vulnerabilities, bugs and code smells, and at least 80% overall test coverage. Once configured and enabled in evaluation configuration, every goal requires fresh green gates before completion. See [SonarQube setup and limits](docs/SONARQUBE.md).

Use `/setup` to check or repair local prerequisites. The internal read-only checker is also available:

```powershell
python scripts/setup-runtime.py --project .
```

Exit 0 / `runtime_ready=true` proves executable checks only. `ready` remains false until the setup agent successfully calls the real CodeGraph MCP tool in that session. Missing tools after registration mean reload-required. Exit nonzero identifies a runtime failure. Pins live in [assets/versions.json](assets/versions.json).

Repository checks:

```powershell
uv run --offline --with pytest python -m pytest tests/test_managed_configuration.py tests/test_plugin_lifecycle.py -q
```

## Compatibility and limits

Codex CLI 0.159.0 silently drops hooks from portable-schema root manifests. This package uses native `.codex-plugin/plugin.json` and a minimal root identity, matching the working Ponytail layout. See [ADR 0002](docs/adr/0002-codex-marketplace-und-lifecycle.md). Actual hook discovery must show six plugin hooks before execution is claimed.

Automatic execution requires an enabled/loaded plugin, available Node.js, and user-trusted hooks. MCP configuration does not prove session visibility. Setup never self-approves trust, overwrites conflicting MCP entries, changes credentials or grants external publication permissions. Authorized repair may require network access. Complete fresh-machine installation and execution after user trust remain separate checks.
