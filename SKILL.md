---
name: kiss-chris-stack
description: Install, activate, or use KISS-Chris-Stack, a layered software-engineering stack with Ouroboros, CodeGraph, UI-UX-Pro-Max, Ponytail, Caveman, and RTK. Use for coding, debugging, refactoring, UI work, feature work, architecture changes, stack setup, MCP startup configuration, or deciding between a fast path and a fully evaluated Ouroboros path.
---

# KISS-Chris-Stack

Use the following stack as one system. Do not treat the tools as interchangeable.

## Roles

- **Ouroboros** owns goal clarification, acceptance criteria, bounded execution, evaluation, and repair/evolution.
- **CodeGraph** owns repository/context discovery: existing implementations, symbol relationships, call paths, dependency impact, and architectural context.
- **UI-UX-Pro-Max** owns visual design, interaction, responsiveness, accessibility, and UI/UX review guidance for interface work; skip it for non-visual tasks.
- **Ponytail** owns implementation minimality: reuse what exists and implement the smallest sufficient change; do not remove required validation, security, error handling, or accessibility.
- **Caveman** owns communication minimality: keep agent prose terse without changing code content.
- **RTK** owns tool-output compression: prefer its compact command output whenever available.

Never disable one tool because another tool also reduces tokens or complexity. Their optimization targets are different.

## Routing

Classify the task before changing code.

### Fast path
Use the fast path when the task is explicit, local, low-risk, and does not require architectural choices. Typical examples: a clear bug fix in one area, a small rename, a deterministic config change, a test correction, or a straightforward dependency update.

Flow:

1. Inspect only the relevant repository context. Use CodeGraph when it materially reduces search or impact-analysis work.
2. Apply Ponytail before writing code: reuse existing code, library, or platform capability before inventing anything new.
3. Implement the smallest sufficient change.
4. Use Caveman for terse status/reasoning prose.
5. Use RTK for CLI/tool output where available.
6. Run targeted tests, then the narrowest broader verification justified by the change.

Do **not** invoke the full Ouroboros interview for an obviously small task merely to follow process.

### Deep path
Use Ouroboros when ambiguity, cross-cutting impact, architectural decisions, multiple interacting constraints, risky behavior changes, or weakly specified acceptance criteria make failure likely.

Preferred flow:

`Goal -> Seed/interview only when genuinely ambiguous -> CodeGraph context -> Execute -> Ponytail implementation -> Caveman + RTK -> tests/evidence -> Ouroboros evaluate -> focused repair -> one consolidated final evaluation`

Use `ooo auto "<goal>"` only when the goal is genuinely ambiguous and needs convergence. When the goal already has testable acceptance criteria, create or reuse a Seed and start it directly through `ouroboros_start_execute_seed`; do not add an interview merely for ceremony.

For an ambiguous one-command workflow, `ooo auto "<goal>"` inside the agent must route to the official background `ouroboros_start_auto` MCP tool.

When more control is needed, use the explicit Ouroboros stages:

- `ooo interview` / `ouroboros init start`
- seed generation
- `ooo run` / `ouroboros run`
- `ooo evaluate`
- `ooo evolve` or `ooo ralph` only when the evaluation indicates iteration is warranted

### Bounded deep path

- Before execution, translate every acceptance criterion into an observable statement with source paths, a negative case, and a verification command. Include identity, latest-evidence, readback, and rollback requirements when relevant.
- Run mechanical checks before the first formal evaluation. Pass their exact results and all relevant code, test, evidence, and documentation paths together as the evaluation artifact.
- Keep Stage 3/consensus disabled by default. Enable it only for contradictory Stage-2 evidence, a genuinely high-risk decision, or an explicit user request.
- After a partial rejection, repair only the failed acceptance criteria, verify them narrowly, then run exactly one consolidated evaluation across all criteria.
- Keep `auto_evolve` disabled. Use evolution/Ralph only if the same technical cause remains after one focused repair or evaluation exposes an architectural conflict.
- Treat observer progress as a real phase, cursor, or acceptance-criterion change. After two unchanged observation intervals, inspect exact job state, worker process, and latest error; cancel only the proven-stuck job.
- Default budget: at most 60 minutes per generation, 15 minutes without progress, and three iterations per acceptance criterion. Report any required extension instead of silently continuing.

## Deep-path integration rules

The other tools remain active inside the Ouroboros execution path.

Before implementing a non-trivial work item:

1. Use CodeGraph to establish the affected symbols, call/dependency paths, existing patterns, and likely impact surface.
2. Feed that discovered context into the implementation decision without duplicating large raw code dumps.
3. Apply Ponytail to the concrete implementation plan: first reuse existing code, standard library/platform facilities, or existing dependencies; only then add new code.
4. Keep agent narration terse via Caveman.
5. Keep command output compact via RTK.
6. Preserve Ouroboros acceptance criteria as the source of truth for completion.

### Host-owned observability

The Deep Path start receipt is the synchronization boundary:

1. Start the official background Ouroboros MCP flow; do not emulate it with a shell worker.
2. Immediately open the returned `meta.dashboard_url` with `scripts/open-dashboard.ps1` or `scripts/open-dashboard.sh`. The helper verifies `/api/runs` before opening the browser and automatically replaces a retired idle-daemon port with Ouroboros' current DB-scoped endpoint while preserving `?run=...`. A broken run picker therefore fails visibly instead of opening a misleading or unreachable dashboard. Do not guess a port or start a second daemon.
3. Immediately delegate the returned `meta.job_observer` object unchanged to exactly one read-only host child named `run_observer`. It exclusively owns job wait/result and follows chained jobs. The main agent relays its meaningful updates until terminal.
4. Only Ouroboros execution workers implement acceptance criteria. Dashboard and observer remain outside that worker pool and are established during interview/Seed convergence, before execution begins.

If the host cannot create an independent child session, say so explicitly and use Ouroboros' durable catch-up behavior; do not pretend an observer was started. If the host is headless, print the dashboard URL instead of claiming the browser opened.

Do not let Ponytail turn into speculative cleanup. Do not let CodeGraph become an excuse to inspect the whole repository when a bounded graph slice is enough. Do not let Ouroboros turn a tiny change into a heavyweight workflow.

## Verification contract

A task is complete only when the implementation satisfies both:

1. the user's requested outcome, and
2. the relevant executable/test/evidence checks.

On the deep path, use Ouroboros evaluation as the final orchestration gate. If evaluation partially fails, repair only the failed criteria and then perform one consolidated final evaluation rather than repeatedly re-evaluating the full result after every edit.

Never claim verification from a textual success message alone when an executable check is available.

## Human interaction

Ask only questions that materially change the implementation or acceptance criteria. On the deep path, let Ouroboros surface hidden assumptions and convert them into explicit acceptance criteria. On the fast path, avoid unnecessary ceremony.

When a user explicitly asks for a particular implementation approach, keep the requested constraint unless it conflicts with repository correctness or a stronger explicit requirement.

## Installation and availability

Use `scripts/install-stack.ps1` on native Windows and `scripts/install-stack.sh` on macOS, Linux, or WSL. Pass the target repository path. The installers:

- install or update Ouroboros, CodeGraph, RTK, Caveman, and native Ponytail plugins;
- install the current UI-UX-Pro-Max CLI and initialize its skill for each detected Codex/Claude host after the mandatory `ooo setup` gate;
- apply and verify the bounded dashboard progress-link compatibility fix only while the installed Ouroboros source still matches the affected upstream shape;
- install this skill for detected Codex, Claude, or compatible skill hosts;
- register Ouroboros and CodeGraph MCP servers so the agent host starts them automatically;
- add a marker-owned activation block to global `AGENTS.md` and/or `CLAUDE.md` without replacing unrelated instructions; and
- initialize CodeGraph when `.codegraph/` is absent, otherwise synchronize the existing graph; and
- preserve an existing project `.ouroboros/mechanical.toml`, or detect deterministic project gates when it is missing.

After the Ouroboros package and native agent plugins are present, the installer launches a new detected agent process whose first prompt is exactly `ooo setup`. Any later initialization stops unless that action succeeds.

On native Windows, Ouroboros rejects Codex STDIO MCP because it can terminate the app server. The PowerShell installer therefore configures loopback HTTP and a user-logon scheduled task. Other supported systems use host-spawned STDIO. Never create a second server process when the configured host already owns startup.

Read [README.md](README.md) for operator commands. Run the matching `verify-stack` script after installation. If no supported agent CLI is installed, stop after dependency installation and report that host registration still needs an agent.
