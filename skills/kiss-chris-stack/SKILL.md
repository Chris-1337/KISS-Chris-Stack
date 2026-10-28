---
name: kiss-chris-stack
description: Orchestrate software engineering with verified setup, context before goals, and separate test, implementation, and evaluation agents using the bundled KISS-Chris-Stack tools.
---

# KISS-Chris-Stack

Read and follow [the shared policy](../../assets/global-stack-policy.md), the sole source for native goal lifecycle, separated TDD roles, documentation, tools and permission boundaries.

For each root-session task, run [setup](../setup/SKILL.md) first: check current runtime readiness, repair authorized local prerequisites, and prove actual session MCP visibility before the original implementation. Never infer readiness from a cached flag. If documentation is missing or empty, bootstrap it before goal definition; explicit `/setup` also fills known gaps.

Read `docs/`, `agent-traces/`, relevant code/tests and existing designs. Clarify unresolved decisions before dependent work; then formulate/register the strong goal and orchestrate the three roles until its acceptance criteria are proven. Sub-agents handle only their assigned role under the existing goal, without another setup, goal registration or recursive delegation.

Bundled skills are sibling directories. Use [Ponytail](../ponytail/SKILL.md), [Caveman](../caveman/SKILL.md), [CodeGraph](../codegraph/SKILL.md), [RTK](../rtk/SKILL.md) and [UI-UX-Pro-Max](../ui-ux-pro-max/SKILL.md) when appropriate. Read [README](../../README.md) for installation through the repository marketplace; the plugin has no separate installer.
