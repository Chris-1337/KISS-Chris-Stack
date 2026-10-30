---
name: kiss-chris-stack
description: Orchestrate software engineering with verified setup, context before goals, and separate test, implementation, and evaluation agents using the bundled KISS-Chris-Stack tools.
---

# KISS-Chris-Stack

Read and follow [the shared policy](../../assets/global-stack-policy.md), the sole source for native goal lifecycle, separated TDD roles, documentation, tools and permission boundaries.

For plugin installation, follow [onboarding](../onboarding/SKILL.md) before setup/readiness: wait for yes and an explicit existing project path; a no/cancel reply only receives the manual `/setup` or later trusted-hook hint. Keep pending consent/path replies in onboarding rather than treating them as ordinary tasks.

For each ordinary root-session task, use [setup](../setup/SKILL.md): project-root `kiss-chris-stack.config.json` is the sole initialization marker. Validate and preserve existing configuration through the bundled resolver, then check current runtime readiness, repair authorized local prerequisites, and prove actual session MCP visibility. Invalid configuration blocks setup. Missing configuration requires initialization/documentation bootstrap and final default configuration creation only after success; existing configuration must not trigger repeated initialization from missing docs/traces. Explicit `/setup` still fills known documentation gaps. Never infer current readiness from the marker or a cached flag.

Read `docs/`, `agent-traces/`, relevant code/tests and existing designs. Clarify unresolved decisions before dependent work; resolve project workflow and evaluation switches through [evaluate](../evaluate/SKILL.md), then formulate/register the strong goal. Top-level `plan-mode` defaults to `false`, which continues automatically. With `plan-mode=true`, present the strong goal, request explicit user approval and yield the turn before dispatching the test, implementation or evaluation roles; explain the configured approval requirement and resume the same registered goal only after approval. Silence or a rejected/pending reply is not approval; changes to the goal require renewed approval. This does not switch the host's collaboration mode. After this gate, orchestrate the three roles until acceptance criteria are proven. The independent evaluation agent follows that skill for current-source live functionality and enabled SonarQube gates; re-read configuration before completion. Sub-agents handle only their assigned role under the existing goal, without another setup, goal registration or recursive delegation.

Bundled skills are sibling directories. Use [Ponytail](../ponytail/SKILL.md), [Caveman](../caveman/SKILL.md), [CodeGraph](../codegraph/SKILL.md), [RTK](../rtk/SKILL.md) and [UI-UX-Pro-Max](../ui-ux-pro-max/SKILL.md) when appropriate. Read [README](../../README.md) for installation through the repository marketplace; the plugin has no separate installer.
