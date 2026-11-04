# KISS-Chris-Stack

A Codex plugin that chooses the amount of workflow a software task needs. Tiny, clear, low-risk changes use a delegated direct worker. Larger or less certain work uses goals, separate roles, interviews or dependency-linked Wayfinder tickets.

The plugin bundles the orchestrator, setup, Ponytail, grill-with-docs, Wayfinder and their required skills/templates, Grilling, Caveman, UI-UX-Pro-Max search code/data, and CodeGraph/RTK guides. See [architecture](docs/ARCHITEKTUR.md), [onboarding](docs/PRODUKT-ONBOARDING.md), and [component provenance](docs/THIRD-PARTY.md).

Project-original material is [MIT licensed](LICENSE). Bundled third-party components retain their own licenses and notices. See [contributing](CONTRIBUTING.md), [security reporting](SECURITY.md), and [publication setup](docs/GITHUB-PUBLICATION.md).

## Plugin is good for / not so good for

**Good for:**

- **Small, clear corrections:** use one delegated worker with focused checks, without setup, a goal, an interview or the three-role stack. Escalate if the task turns out uncertain or risky.
- **Features and regression-sensitive fixes:** establish a bounded goal, separate test/implementation/evaluation roles and applicable evidence.
- **Unclear or large work:** settle requirements with grill-with-docs, or use Wayfinder to map dependencies and schedule ready tickets within the host's capacity.
- **Making projects agent-ready:** retain evidence-backed architecture, decisions, module research and agent traces, with verified local tooling.

**Not so good for:**

- **Unattended product or domain decisions:** unresolved choices still need real human answers. The agent cannot treat a recommendation or silence as consent.
- **Work without the required access or tooling:** selected stack routes can be blocked by missing runtimes, MCP visibility, the required research model, provider access or an enabled configured quality service. The direct route does not remove security or permission boundaries.
- **Expecting guaranteed autonomous correctness or lower cost:** instructions and helper tests do not prove that every future host/model session will follow the workflow, or that every task will use fewer tokens.

Quick questions and standalone lookups generally do not need a goal or the full implementation lifecycle.

## Roadmap

The routing and setup foundation is already implemented: four task routes, dedicated Luna-low factual research, separate stack roles, configurable local/GitHub/GitLab ticket storage, and an explicit storage-choice gate during setup. These are current capabilities, not roadmap promises.

Remaining work is validation and improvement, without delivery commitments:

- **Real host/model workflows:** observe route selection, model dispatch, multi-turn interviews, native initialization and parallel ticket iteration in actual sessions. Contract checks cannot guarantee future compliance.
- **Hosted ticket workflows:** verify authenticated GitHub/GitLab map and ticket operations with explicitly authorized writes; read-only metadata and command doubles are not end-to-end proof.
- **Measured overhead and role choices:** compare token use, elapsed time and verification outcomes across routes, and evaluate models for substantive roles. Pure context collection remains fixed to fresh GPT-6 Luna low agents.
- **Onboarding, recovery and compatibility:** simplify prerequisite/MCP/reload recovery and extend fresh-machine, graphical onboarding and post-trust hook evidence across supported hosts. Existing CLI/container checks and platform reports are a starting point, not complete coverage.

## Install through the repository marketplace

Add the repository marketplace directly; no manual clone or checkout is required:

```powershell
codex plugin marketplace add https://github.com/Chris-1337/KISS-Chris-Stack.git
codex plugin add kiss-chris-stack@kiss-chris-stack
```

The repository provides the marketplace and native plugin manifests used by these commands. Supported Codex desktop hosts also expose repository marketplaces in the Plugins Directory. This is a repository marketplace plugin, not a public-directory submission, and has no separate installer.

After installation, [onboarding](skills/onboarding/SKILL.md) asks whether to initialize a project. A yes requires its existing absolute path before setup; a no leaves setup for a later `/setup` or trusted-hook initialization. Installation never assumes its working directory is the project.

First initialization and every explicit `/setup` ask where maps/tickets belong: local Markdown, GitHub or GitLab, plus the directory/repository/project target. Setup shows an existing choice and waits for an actual keep/change answer before dependent writes. Defaults and preselected options are not answers. Explicit tracker setup follows the same gate; ordinary per-task readiness reuses validated settings without asking again.

Prerequisites are a supported Codex host, Node.js for lifecycle hooks, Python 3.10+ for bundled tooling, and the runtime checks described by [setup](skills/setup/SKILL.md). Enable the plugin and review/trust its hooks through the normal host UI. Missing runtimes, stale process environments or unloaded MCP tools can require installation, repair or reload; the plugin never grants itself hook trust.

## Optional: encapsulated execution environment

Run the plugin in Docker and connect the Codex desktop app over local SSH. The desktop remains the interface; Codex, plugin policies, MCP tools, project files and authentication live inside the container.

With Docker Compose, Python 3.10+ and OpenSSH available, run from a checkout:

```sh
python3 containers/remote/prepare.py
```

This builds from the checkout, starts the environment, creates a dedicated local SSH identity and writes a pinned configuration fragment. It does not edit your existing SSH configuration, copy credentials or approve hooks. Follow the [remote container guide](docs/REMOTE-CONTAINER.md) for connection, sign-in, persistence, permissions and platform evidence. This optional mode does not change ordinary marketplace installation.

## What happens on a task

The active root session coordinates work and delegates substantive roles. After installation-onboarding routing, it chooses a route **before setup, configuration backfill or goal registration**:

| Request | Route |
| --- | --- |
| Tiny, clear, bounded low-risk correction | One delegated direct worker and focused checks. No setup, goal, interview or three-role overhead. Escalate before broader edits if uncertainty, scope or risk grows. |
| Normal feature/bugfix with clear requirements and fetched context | Stack with a strong goal and separate test, implementation and evaluation agents; no automatic interview. |
| Normal effort with unclear requirements | [grill-with-docs](skills/grill-with-docs/SKILL.md) before the goal: a delegated interview and prompt glossary/ADR documentation, then stack work. |
| Large task | [Wayfinder](skills/wayfinder/SKILL.md), then dependency-ready ticket phases in parallel through stack goals, within host slots and isolated write ownership. |

Size alone does not determine the route. Unknown behavior, trust boundaries, migrations, destructive operations and regression-sensitive changes need the stack even when the edit looks short.

### Context, roles and goals

All pure information collection uses fresh `gpt-6-luna` agents with low reasoning and no inherited context. Each receives a bounded direction and returns source-linked facts, notes and explicit unknowns, without implementation/source/configuration changes, design decisions, recommendations or speculation. This also applies before interviews, goals, Wayfinder and setup. Missing requested model/effort/agents blocks required research; there is no silent fallback. Substantive roles may inspect sources as part of their own work.

The root delegates interviewing, planning, documentation, tests, implementation and evaluation. It retains route selection, assignments, user-question/approval relay, native goals and evidence review. Pending research or unanswered decisions block dependent work; independent ready work may continue.

For a stack implementation, the root reviews the collected project context and scoped feedback, registers a strong goal, then assigns separate test RED, implementation GREEN and independent evaluation roles. `plan-mode=true` adds explicit approval of the registered goal before those roles start; the default `false` continues automatically. Settled interviews need no closing confirmation, and clear work needs no invented questions. Direct workers do not acquire this stack overhead.

Wayfinder records a map, ticket claims, prerequisites and resolution evidence. Preparatory tickets need a clear question; implementation tickets need settled requirements. The root queues ready phases within available capacity, isolates conflicting writes and verifies integrated changes. Workers do not start recursive triads or register native goals. On a host with one active native goal, the root retains an umbrella and labels strong child ticket goals textual/unregistered under it.

### Setup and project memory

Stack readiness combines current runtime checks, an actual root-session CodeGraph MCP call and a matching configured tracker binding. Bare hooks provide read-only status and preparation argv; they do not initialize projects themselves. A marker or cached flag never proves readiness.

Project-root `kiss-chris-stack.config.json` is the sole initialization marker. In configured projects, ordinary stack readiness validates/backfills only missing defaults and reconciles tracker wiring; it does not repeat the storage question, full documentation bootstrap, native `/init` or staging. Invalid configuration blocks rather than being replaced with defaults. First/explicit setup asks its storage question before dependent backfill or preparation.

First initialization creates the marker **last**, with the answered provider/target and validated workflow settings, after runtime/MCP, tracker, documentation and native-init prerequisites succeed. Tracker preparation creates the selected local root and managed operations document, not a fake effort/map/tickets. Actual work creates them at the selected location. An explicitly selected hosted target never silently falls back to local when access is unavailable.

`docs/` holds human architecture, business decisions and ADRs. `agent-traces/<component>/` retains concise implementation evidence; [scoped feedback](agent-traces/user-feedback/README.md) records corrections and prevention actions for later acceptance checks. This is project memory maintained by agents, not model training or a background service; see [learning from feedback](docs/LEARNING.md).

First-time and explicit setup fill evidence-backed documentation gaps while preserving existing content. Real modules receive [module-local Luna research and separate documentation synthesis](skills/setup/SKILL.md#module-research-and-synthesis). Empty projects receive truthful structure and the generic feedback protocol, not invented architecture. After documentation, [native `/init` and project-instruction review](skills/setup/SKILL.md#native-initialization-and-project-instructions) preserve unique rules and managed blocks. If native dispatch is unavailable, setup remains pending rather than claiming `/init` ran.

Successful first-time/explicit `/setup` and authorized `/setup-sonarqube` maintain required local-artifact ignore rules and stage only exact nonsecret setup files. The [shared Git workflow](skills/setup/SKILL.md#git-hygiene-and-staging) preserves existing staged/unstaged work and reports mixed files left unstaged. Setup never commits or pushes; external publication remains separately authorized. Upstream Ponytail lifecycle hooks run alongside the stack hooks.

The [shared language policy](assets/global-stack-policy.md#language) requires English documentation and internal reasoning; user-facing communication follows the language of the prompt. See [ADR 0003](docs/adr/0003-documentation-language.md).

## Project configuration

The resolver supplies these defaults; they do not replace the required setup storage-choice answer:

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

| Setting | Default | Effect |
| --- | --- | --- |
| `grill-me` | `true` | Compatibility key for explicit Grilling; no additional automatic interview. |
| `grill-with-docs` | `true` | Enable the unclear-normal-work route before the goal. `false` skips automatic use, not unresolved decisions. |
| `wayfinder` | `true` | Enable large-task mapping and ready-ticket scheduling. `false` skips automatic use; choose a safe bounded route or resolve the routing decision. |
| `plan-mode` | `false` | `true` presents the registered stack goal and waits for explicit approval before the three roles start. |
| `evaluation.live.enabled` | `true` | Require applicable live proof for stack work; `false` reports an explicit skip. |
| `evaluation.sonarqube.enabled` | `true` | Enforce fresh analysis-specific green gates for configured SonarQube projects; `false` skips scanner/readback/token operations without deleting service data. |

Workflow/evaluation switches must be JSON booleans. Explicit skill requests remain available when automatic switches are false. Quoted booleans, numbers, duplicate/unknown keys and invalid types block validation; errors are not opt-outs. Disabled checks are reported as skipped, never passed.

`wayfinder-tracker` independently selects one typed provider/location:

- Local: `{ "provider": "local", "directory": ".scratch" }`, or another safe project-relative directory.
- GitHub.com: `{ "provider": "github", "repository": "OWNER/REPO" }`.
- GitLab: `{ "provider": "gitlab", "project": "https://HOST/GROUP/PROJECT" }`, including nested groups and explicit self-hosted HTTPS targets.

Setup prepares and checks the selected root/binding without moving or deleting old tickets. Missing CLI/auth/access, mismatched targets and unsafe paths block without fallback. Hosted setup uses existing native `gh`/`glab` for read-only preflight; it does not install a CLI, log in or authorize ticket writes. See [Wayfinder storage/setup](docs/WAYFINDER.md) and the [complete configuration reference](docs/EVALUATION.md) for exact variants, safe reconciliation and update behavior. Feedback learning has no configuration switch.

## Verify and repair

On stack routes, the independent [evaluation role](skills/evaluate/SKILL.md) checks the affected behavior and enabled applicable gates:

- Live proof exercises the actual running CLI/plugin/backend/application. Affected frontend behavior needs browser/Playwright interactions and assertions; missing browser dependencies are installed when needed. Documentation-only work uses document/contract checks rather than an invented live application.
- Enabled SonarQube enforcement applies to configured projects and requires fresh current-source, analysis-specific green gates. Failed or unavailable required checks prevent completion; switches are not changed to evade failures.
- Direct workers use focused verification without the stack lifecycle. Instructions prescribing a workflow are not proof that every host/model has executed it correctly.

Use `/setup` for explicit preparation/repair, including its storage-choice dialogue. From a repository checkout, the read-only helpers can be run directly:

```powershell
python scripts/setup-runtime.py --project .
python scripts/setup-wayfinder.py --project . --check
```

Runtime exit 0 / `runtime_ready=true` proves executable checks only. The script's `ready` stays false because it cannot inspect this session's MCP visibility. Overall stack readiness also needs the real root-session MCP call and successful configured tracker check. Missing loaded tools after registration require reload; runtime failures need the reported repair. Pins live in [assets/versions.json](assets/versions.json).

After first-time or explicit setup, projects without configured SonarQube receive an optional [`/setup-sonarqube`](skills/setup-sonarqube/SKILL.md) offer when a usable Linux container engine is available. Already-configured projects follow their existing enabled/disabled evaluation setting instead of receiving another installation offer. Docker Desktop, Rancher Desktop (Docker CLI) and Podman are supported through their engine CLI; ordinary readiness does not repeat the offer. Only acceptance provisions the local service, protected credentials, component analysis and a dedicated gate. Without a usable engine, setup explains how to run it later and continues. See [SonarQube operations and limits](docs/SONARQUBE.md).

For contributors with `uv` installed, run the repository test suite:

```powershell
uv run --with pytest python -m pytest tests -q
```

Use `--offline` when the dependencies are already cached. Coverage and scanner commands for this repository are documented in [SonarQube verification](docs/SONARQUBE.md); the test command alone is not a quality-gate receipt.

## Compatibility and evidence limits

The native `.codex-plugin/plugin.json` and minimal root identity follow the compatibility decision in [ADR 0002](docs/adr/0002-codex-marketplace-und-lifecycle.md). That record observed portable-schema root hooks being dropped by Codex CLI 0.159.0; it is version-specific evidence, not a claim about every current/future host. Verify actual discovery of the expected six plugin hooks and their execution in the intended host.

Automatic execution still requires an enabled/loaded plugin, Node.js and user-trusted hooks. MCP registration is not session visibility. Normal setup does not self-approve hooks, overwrite conflicting MCP entries or grant external-write permissions. Authorized prerequisite repair can require network access; separately authorized SonarQube operations follow their protected credential rules.

Recorded checks include actual local tracker/map/ticket workflows and CLI/container validation. The [remote guide](docs/REMOTE-CONTAINER.md) distinguishes Windows evidence from user-confirmed macOS/Colima operation and the still-unverified Windows graphical onboarding/hook approval. Real GitHub/GitLab authentication and ticket writes, complete fresh-machine/post-trust host setup, and model-driven multi-turn/parallel ticket workflows remain separate validation gaps. Treat the roadmap and these limits as evidence boundaries, not as missing implementations of the existing routing and tracker configuration.
