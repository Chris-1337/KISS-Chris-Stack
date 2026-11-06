---
name: kiss-chris-stack
description: Route software work by scope and clarity, delegate context to GPT-6 Luna low, and coordinate direct fixes or separate stack roles with goals and dependency-ready Wayfinder tickets.
---

# KISS-Chris-Stack

Follow [the shared policy](../../assets/global-stack-policy.md), the canonical source for routing, delegation, native goals, role separation, approvals and permissions.

## Route before setup

The active session is the root orchestrator. Installation [onboarding](../onboarding/SKILL.md) takes priority, including pending consent/path replies and decline/cancel: never initialize the installation working directory. Explicit setup follows [setup](../setup/SKILL.md).

First-time initialization and every explicit `/setup` must follow setup's [required storage choice](../setup/SKILL.md#required-storage-choice): display any current provider/location, ask keep/change among local/GitHub/GitLab and confirm its target, then wait for a real answer before dependent config backfill/preparation/document writes. Defaults and existing settings are not an answer. Retain answers from the same setup dialogue; ordinary per-task readiness reuses validated config without another prompt.

Classify the request before setup, configuration backfill or goal registration:

| Request | Workflow |
| --- | --- |
| Tiny bugfix/minimal change, clear, bounded and low-risk | Delegate a direct worker with relevant context and focused checks: no setup, goal, interview or three-role overhead. Escalate before wider edits if scope, risk or uncertainty grows. |
| Normal feature/bugfix, requirements and fetched context clear and unambiguous | Stack with goal, without an automatic interview. |
| Normal effort, unclear requirements | Stack with [grill-with-docs](../grill-with-docs/SKILL.md) before goal, settling decisions and retaining domain documentation. |
| Large task with independent tickets or more than one session's context | [Wayfinder](../wayfinder/SKILL.md), then every unblocked ticket in parallel through stack with its own strong goal, within host slots and isolated writes. |

If missing facts prevent classification, collect them first. Do not use a tiny route for uncertain or risky work merely because its edit looks short.

## Delegate context and substantive work

All pure context collection, including before grill-me/grilling and goals, always uses fresh-context `gpt-6-luna` agents with `reasoning_effort="low"`, `fork_turns="none"`. Assign separate bounded directions and source-linked notes/handoffs, allowed paths/tools and exclusions. Researchers collect facts only: no source/configuration changes, implementation, design decisions, recommendations or speculation. They may write only assigned factual notes. Missing model/effort/agents blocks required research; never silently substitute or fall back to root research. Use [research](../research/SKILL.md) and [handoff](../handoff/SKILL.md) for these assignments.

The root delegates interviewing/planning, documentation, tests, implementation and evaluation with enough context; it retains routing, coordination, user-question/approval relay, native goal lifecycle and evidence review. Substantive roles may inspect sources as part of their assigned work. Researchers and ticket workers do not start setup, register goals or recursively fan out role groups.

## Stack routes

1. Coordinate current [setup](../setup/SKILL.md) runtime/MCP readiness. Delegate executable preparation; retain the real MCP call in the root session. Existing project-root `kiss-chris-stack.config.json` is the sole initialization marker: assign `evaluation-config.py --update` before readiness, validating and adding only missing defaults while preserving explicit values. Invalid configuration blocks; never default over errors. Missing configuration triggers bootstrap before final marker creation; existing configuration never triggers reinitialization merely from missing docs/traces. Require the configured `wayfinder-tracker` binding through bundled `scripts/setup-wayfinder.py --prepare` and `--check` after runtime/MCP; ordinary reconciliation is not docs bootstrap/native init. The tracker is a strict provider-specific target object, default local `.scratch`, independent of the Boolean `wayfinder`. First setup uses validated full pending selection via `--config-stdin` before exact config-last marker creation. No cached ready flag or automatic hook trust.
2. Obtain and review researchers' `docs/`, `agent-traces/`, relevant code/call paths/tests/designs and scoped `agent-traces/user-feedback/` facts before defining the goal. Carry prevention actions into goal acceptance and role handoffs.
3. Resolve [workflow/evaluation configuration](../evaluate/SKILL.md): independent strict `grill-with-docs=true`, `wayfinder=true`, legacy `grill-me=true`, `plan-mode=false`, live/SonarQube gates enabled by default. `grill-me` is retained for explicit invocation, not an extra automatic interview. Explicit skill requests remain available even with automatic switches false. A disabled selected route is skipped; unresolved decisions still require a user answer or routing choice before work.
4. Delegate the selected interview/planning skill before the goal. Relay prerequisite-aware questions to the user; wait for unanswered decisions and pending fact research. Resume the same interview across replies. No agent answers for the user; clear requests need no invented questions. Delegate prompt glossary/ADR persistence. Continue automatically once settled, without a closing confirmation.
5. Use [Ponytail](../ponytail/SKILL.md) to formulate/register the strong goal through the root's native goal tools, reusing the same open goal and preserving unrelated-goal conflicts. Honor `plan-mode`: false continues; true presents the strong goal, requests explicit approval and yields the turn before test/implementation/evaluation dispatch. Resume the same goal only after approval; changed goals need renewed approval. Silence/pending replies are not approval.
6. Root dispatches separate test RED, implementation GREEN and independent [evaluation](../evaluate/SKILL.md) roles. Repair failures through their responsible role. Re-read configuration and review executable current-source evidence for every enabled applicable gate before native completion; disabled gates are skipped, not passed.

For Wayfinder, claim and dispatch all dependency-ready tickets, queue excess phases within host concurrency, isolate conflicting writes and verify integrated changes. Root schedules every implementation ticket's three separate roles without recursive triads. On a single-active-native-goal host, retain the root umbrella and explicitly textual/unregistered child goals for each ticket; do not invent concurrent native goals. Blocked tickets wait for actual prerequisite completion and approval. External tracker publication/branch pushes need authorization; local Markdown is only the omitted-setting default. Use the explicitly configured provider/target and checked binding; unavailable/unapproved external work blocks without a silent backend switch.

Use bundled [Caveman](../caveman/SKILL.md), [CodeGraph](../codegraph/SKILL.md), [RTK](../rtk/SKILL.md), and [UI-UX-Pro-Max](../ui-ux-pro-max/SKILL.md) as appropriate. Bundled skills are siblings; read/invoke their `SKILL.md` directly if the host has no native Skill tool. See [README](../../README.md) for marketplace installation and limits.
