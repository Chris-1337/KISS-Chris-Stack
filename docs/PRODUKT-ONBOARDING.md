# KISS-Chris-Stack

## What is it?

A Codex plugin with bundled skills, lifecycle hooks, and verified local setup. The active root session delegates context collection and substantive work, coordinating separate agents for tests, implementation, and evaluation.

## Purpose

Classify before setup: tiny bounded low-risk fixes use a delegated direct worker and focused checks without setup/goal/triad overhead; clear normal features/bugs use stack with goal; unclear normal work uses grill-with-docs before goal; large work uses Wayfinder followed by every unblocked ticket in parallel through stack goals.

Independent strict Boolean `grill-with-docs` and `wayfinder` default to true and enable their selected automatic routes. Legacy `grill-me` defaults true but remains explicit-only, with no extra automatic interview. Explicit skill requests remain available when automatic switches are false. Unresolved decisions still wait for actual human answers; once settled interviews continue automatically without a closing confirmation. Independent `plan-mode=true` still requires explicit approval of the strong registered goal before implementation phases.

## Responsibilities

The active session delegates substantive work with sufficient context, retaining native goals, approval/question relay and evidence review. All pure fact gathering always uses fresh GPT-6 Luna (`gpt-6-luna`, low reasoning, no inherited context) agents: referenced facts/notes only, no implementation/source/configuration changes, design decisions or speculation. Missing model/effort support blocks required collection without silent fallback. Interview/planning and documentation are separate roles; root schedules test RED, implementation GREEN and independent evaluation for stack work. Ponytail minimizes code, Caveman communication, RTK output; CodeGraph supplies structure and UI-UX-Pro-Max supports UI tasks.

## Architecture diagram

```mermaid
flowchart TD
    H[Codex: plugin enabled, hooks trusted] --> E[Root event]
    E --> Route{Classify before setup}
    Route -->|Tiny clear low-risk| Direct[Delegated direct worker and focused checks]
    Route -->|Stack routes| P{Root project config exists?}
    P -->|No| S[Setup: runtime and documentation bootstrap]
    P -->|Yes| R[Add missing config defaults, then runtime checks]
    R --> M
    S --> M[Real MCP tool call in this session]
    M --> C[Fresh Luna low agents collect facts and feedback]
    C --> F[Review relevant feedback and derive acceptance checks]
    F --> Kind{Scope and clarity}
    Kind -->|Normal clear| G
    Kind -->|Normal unclear| Q[Delegated grill-with-docs and domain documentation]
    Kind -->|Large| Map[Wayfinder map and dependencies]
    Map --> Tickets[All ready tickets within slots and isolated writes]
    Tickets --> G
    Q -->|Decisions settled: automatic, no closing confirmation| G[Strong native goal]
    G --> PMode{plan-mode?}
    PMode -->|false: default| T[Test agent: RED]
    PMode -->|true| A[Present goal, request approval, end turn]
    A -->|Explicit user approval of this goal| T
    T --> I[Implementation agent: GREEN]
    I --> V[Evaluation agent: check criteria]
    V -->|Failure| O[Orchestrator assigns repair]
    O --> T
    O --> I
    V -->|Fulfilled| D[Documentation, trace, and goal completion]
```

## Quick start

1. Add the GitHub repository marketplace directly, without a manual clone or checkout: `codex plugin marketplace add https://github.com/Chris-1337/KISS-Chris-Stack.git`.
2. Install the plugin: `codex plugin add kiss-chris-stack@kiss-chris-stack`.
3. Reload the host, enable the plugin, and review/approve hooks through the normal host UI.
4. Answer the onboarding question about setting up a project. If yes, provide an explicit absolute path to an existing directory before `/setup` runs. If no, no setup runs; the slash command `/setup` remains available manually, and trusted hooks can initialize the project on a later ordinary task. Onboarding never infers a project from the installation working directory. Node.js, Python 3.10+, and Codex must be available for setup, which checks bundled resources, performs authorized local tool repairs, and requires a real CodeGraph MCP call in this session.
5. Continue the original request through the stack. Optional top-level `"plan-mode": true` in project configuration requires explicit approval of the strong goal before implementation roles start; default false continues automatically. See [configuration](EVALUATION.md). No additional standalone installer is needed.

## Usage

The [shared policy](../assets/global-stack-policy.md) remains authoritative. Installation onboarding takes priority over root readiness instructions until its consent/path dialogue ends. For later selected stack tasks, project-root `kiss-chris-stack.config.json` is the sole initialization indicator: absence invokes setup; presence requires the root to execute the hook-provided `evaluation-config.py --update` argv, validating configuration and adding only missing current defaults before fresh runtime/MCP checks without repeated project initialization. Explicit values remain unchanged. The bare hook remains read-only; pending/declined installation onboarding and delegated roles do not run this updater. Setup creates a missing default config only after successful runtime/session MCP and documentation bootstrap; existing settings remain intact. Invalid configuration blocks setup. Sub-agents do not start recursive goals or setup chains. `docs/` contains human architecture, business decisions, and ADRs; `agent-traces/<component>/` contains brief evidenced goal notes. First-time setup and explicit `/setup` fill documentation gaps and preserve existing files. Documentation and internal reasoning use English; user-facing communication follows the language of the prompt, as recorded in [ADR 0003](adr/0003-documentation-language.md).

## Configured Wayfinder storage

`wayfinder-tracker` is independent of the Boolean `wayfinder` and defaults to local `.scratch`; explicit GitHub.com repositories and GitLab HTTPS project URLs are supported. First initialization and every explicit `/setup` ask local/GitHub/GitLab, show any current provider/location and wait for a keep/change answer and target before dependent writes; defaults are not consent. Ordinary per-task readiness reuses validated config without another prompt. [Setup](../skills/setup/SKILL.md#configured-wayfinder-tracker) prepares/checks the selected root and a managed operations document, not a fake map/tickets. The selected target is authoritative; missing hosted CLI/auth/access blocks without fallback or automatic login/install. First setup retains the chosen full pending config until final marker creation; existing-project reconciliation preserves old tickets and avoids docs bootstrap/native init. See [examples and operational limits](WAYFINDER.md).

## Features

- Module documentation during first-time or explicit setup: one fresh-context GPT-6 Luna (`gpt-6-luna`, reasoning `low`) researcher per real module collects only module-local evidence; the root then assigns a separate documentation role to organize retained notes into linked architecture and usage documents under `docs/<module>/`, preserving existing layouts. Unavailable agents/model settings or incomplete research prevent bootstrap success; see [the module workflow](../skills/setup/SKILL.md#module-research-and-synthesis).
- Final setup instruction review: after documentation, native `/init` prepares project `AGENTS.md` and a delegated documentation role refines concise, evidence-backed guidance for root review while preserving unique valid rules and instruction scopes. An existing file is reused if native initialization refuses it; unavailable native dispatch leaves setup pending for a manual run and review. See [the final instruction phase](../skills/setup/SKILL.md#native-initialization-and-project-instructions).
- All stack skills, including grill-with-docs, Wayfinder and their transitive skill/resource dependencies, the Ponytail suite and UIUX search resources, in the plugin.
- Native Codex marketplace installation with consent-first onboarding and an explicit project path.
- Three stack handlers and three original Ponytail lifecycle handlers.
- Current readiness checks instead of cached success flags.
- Marker-managed global rules preserving unrelated configuration.
- Facts-only Luna-low context before every stack goal, delegated interviews/documentation for unclear normal work, parallel dependency-ready Wayfinder tickets and independent evaluation.
- [Learning from feedback](LEARNING.md): retain scoped lessons, review them before goals and carry prevention checks to all three roles.

## Limits

Automation requires loaded/enabled plugins, available Node.js, and user-trusted hooks. CLI configuration does not prove MCP visibility in the current session. A required reload remains a blocker. Setup neither overwrites MCP conflicts nor approves hooks itself. External writes require user authorization. Complete tool installation from scratch on every platform requires separate verification.

## Release status

As of 2026-10-28: a dedicated repository marketplace plugin with a native Codex manifest. The portable hook-loading limitation in CLI 0.159.0 is documented in the [ADR](adr/0002-codex-marketplace-und-lifecycle.md). Pins are in [versions.json](../assets/versions.json), sources/licenses in [THIRD-PARTY.md](THIRD-PARTY.md).

## Distribution

The repository contains the marketplace and complete plugin. No public directory release is claimed. Usage follows normal marketplace installation and host hook approval.

## Training and onboarding

Guide a tiny clear fix through delegated direct work, then a normal task through readiness, Luna-low context, selected grill-with-docs if unclear, goal, RED, GREEN and independent evaluation. For large work demonstrate a Wayfinder frontier and root-scheduled parallel ticket phases. Continue the same interview across replies; onboarding/setup and delegated roles do not restart it. People read architecture/ADRs; agents add brief traces. Open limits and decisions remain visible.

## Operating model

The host loads the plugin and starts the registered CodeGraph MCP service. After installation onboarding, selected stack root tasks recheck tools, index, and rules even when project configuration marks initialization complete. Documentation contents never substitute for this marker or current readiness. Updates may require reload or renewed hook review. Readiness requires executable checks and a real session tool call; the checker therefore reports `runtime_ready` separately from overall readiness.
