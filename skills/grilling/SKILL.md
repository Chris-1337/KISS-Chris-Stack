---
name: grilling
description: Resolve the user's decisions through prerequisite-aware interview rounds, always before a new KISS-Chris-Stack goal, then continue automatically without a closing confirmation.
---

# Grilling before the goal

The root always runs grilling after reviewing project context and relevant feedback, before formulating and registering each new goal. Resume the same interview across answers; do not restart it on every reply. Onboarding and setup retain their own routing, and delegated test, implementation and evaluation agents work under the existing goal without another interview.

Map the requested outcome as a decision tree: each decision unlocks decisions that depend on it. Use the request, documentation, code and prior answers to mark already settled decisions. Review every branch relevant to the requested scope; do not expand the task or invent questions when the request is already clear.

Work in rounds. The frontier contains unresolved decisions whose prerequisites are settled. Ask the whole available frontier together as numbered questions, each with a short title and your recommended answer. Phrase each question so a "yes" accepts its recommendation. Explain material tradeoffs when they help the user decide. A question depending on an unanswered question belongs to a later round.

Finding facts is the agent's job: inspect available project sources and tools instead of asking the user for discoverable facts. Reuse existing context and use a focused research agent only when useful and permitted; no recursive implementation-role groups. Treat pending research as an unsettled prerequisite and continue with independent frontier questions.

Wait for the user's answers to unresolved decisions before dependent work. Silence, elapsed time and an unanswered recommendation are not answers. Recompute the frontier after each round; an empty frontier does not finish grilling while a relevant decision is still blocked on an unanswered question or pending research.

When all decisions relevant to the requested scope are settled, continue automatically to Ponytail goal formulation and registration through the [orchestrator](../kiss-chris-stack/SKILL.md). No closing confirmation or final shared-understanding approval is required. A clear request can therefore finish grilling without asking any questions. Carry the decisions, constraints and acceptance criteria into the goal and role handoffs.

This automatic continuation preserves the separate configured `plan-mode=true` approval of the registered goal and all permission boundaries in the [shared policy](../../assets/global-stack-policy.md). It does not authorize implementation while a decision, configured goal approval or required permission remains unresolved.

Adapted from Matt Pocock's [Grilling skill](https://github.com/mattpocock/skills/blob/7739eaed7f8f3915437a8def198a6d0d7206dbc7/skills/productivity/grilling/SKILL.md), commit `7739eaed7f8f3915437a8def198a6d0d7206dbc7`, under [MIT](../../licenses/grilling-LICENSE). Stack adaptations: mandatory pre-goal use, bounded task scope, reusable fact research, continuation across replies, and automatic completion without the upstream closing confirmation.
