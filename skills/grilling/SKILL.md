---
name: grilling
description: Resolve user decisions through delegated prerequisite-aware interview rounds on explicit request or as part of grill-with-docs and wayfinder, then continue without a closing confirmation.
---

# Grilling before the goal

The root delegates this interview on explicit request or from the selected [grill-with-docs](../grill-with-docs/SKILL.md) or [wayfinder](../wayfinder/SKILL.md) route. Legacy top-level `grill-me` remains a strict JSON boolean defaulting to `true` for configuration compatibility and explicit invocation; it no longer triggers an extra automatic interview before every goal. An explicit invocation still runs with `grill-me=false`. Follow the [shared policy](../../assets/global-stack-policy.md): separate route switches, readiness, context/feedback review, configured `plan-mode` approval, evaluation gates and permission boundaries remain intact. Resume the same interview across answers; onboarding/setup and delegated test, implementation and evaluation roles do not restart it.

All pure fact/context collection before or during the interview is assigned by the root to fresh `gpt-6-luna` agents with `reasoning_effort="low"`, `fork_turns="none"`. They supply source-linked facts/notes only, with no source/configuration changes, implementation, design decisions, recommendations or speculation. Missing requested controls blocks required research; never silently substitute or gather facts in the root. The separate interview agent reasons about requirements using the supplied facts, prepares questions, and returns them to the root for relay; it never answers for the user.

Map the requested outcome as a decision tree: each decision unlocks decisions that depend on it. Use the request, documentation, code and prior answers to mark already settled decisions. Review every branch relevant to the requested scope; do not expand the task or invent questions when the request is already clear.

Work in rounds. The frontier contains unresolved decisions whose prerequisites are settled. Ask the whole available frontier together as numbered questions, each with a short title and your recommended answer. Phrase each question so a "yes" accepts its recommendation. Explain material tradeoffs when they help the user decide. A question depending on an unanswered question belongs to a later round.

Finding facts is assigned context research: reuse supplied context and ask the root for the mandatory Luna-low researchers rather than asking the user for discoverable facts. Do not spawn recursive implementation-role groups. Treat pending research as an unsettled prerequisite and continue with independent frontier questions.

Wait for the user's answers to unresolved decisions before dependent work. Silence, elapsed time and an unanswered recommendation are not answers. Recompute the frontier after each round; an empty frontier does not finish grilling while a relevant decision is still blocked on an unanswered question or pending research.

When all decisions relevant to the requested scope are settled, continue automatically to Ponytail goal formulation and registration through the [orchestrator](../kiss-chris-stack/SKILL.md). No closing confirmation or final shared-understanding approval is required. A clear request can therefore finish grilling without asking any questions. Carry the decisions, constraints and acceptance criteria into the goal and role handoffs.

This automatic continuation preserves the separate configured `plan-mode=true` approval of the registered goal and all permission boundaries in the [shared policy](../../assets/global-stack-policy.md). It does not authorize implementation while a decision, configured goal approval or required permission remains unresolved.

Adapted from Matt Pocock's [Grilling skill](https://github.com/mattpocock/skills/blob/7739eaed7f8f3915437a8def198a6d0d7206dbc7/skills/productivity/grilling/SKILL.md), commit `7739eaed7f8f3915437a8def198a6d0d7206dbc7`, under [MIT](../../licenses/grilling-LICENSE). Stack adaptations: explicit or routed delegated interviews, universal Luna-low facts-only research, bounded task scope, continuation across replies, and automatic completion without the upstream closing confirmation. The 2026-11-04 routing supersedes earlier automatic legacy grill-me use while preserving its configuration key.
