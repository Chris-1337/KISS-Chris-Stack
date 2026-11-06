---
name: grill-with-docs
description: Resolve unclear normal-sized software requirements through a delegated interview while promptly recording settled domain terms and meaningful ADRs before the stack goal.
---

# Grill with docs

Read and follow both sibling [grilling](../grilling/SKILL.md) and [domain-modeling](../domain-modeling/SKILL.md); a native Skill tool is optional. Apply the [shared policy](../../assets/global-stack-policy.md).

The root selects this automatic route only for unclear requirements of normal effort when `grill-with-docs=true` (default); clear requests go directly to a stack goal and large work goes through Wayfinder. Explicit requests remain available when automatic use is false. Legacy `grill-me` adds no extra automatic interview.

The root first delegates all missing information gathering to fresh `gpt-6-luna` agents with low reasoning and no inherited context. Researchers supply referenced facts and notes only, with no implementation changes or design decisions. A separate interview/planning agent uses these facts to prepare prerequisite-aware question rounds; the root relays them and waits for the user's answers. Do not ask discoverable facts, invent questions for clear requests, answer for the user or start dependent work while answers/research are pending. Resume the same interview across replies.

As terminology and consequential tradeoffs settle, the root delegates prompt glossary/ADR updates using the domain-modeling formats and existing document layout. Record only established decisions, preserve existing documents and verify the actual files; do not claim persistence from a proposed edit. Researchers remain facts-only and do not write these decisions.

When requirements are settled and documentation is retained, return constraints and acceptance criteria to the root and continue automatically to the strong goal, without a closing confirmation. Configured `plan-mode=true` remains the separate approval gate before test, implementation and evaluation dispatch. A disabled automatic route never authorizes implementing unresolved requirements.

Adapted from Matt Pocock's [grill-with-docs](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/grill-with-docs/SKILL.md), commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, under [MIT](../../licenses/mattpocock-skills-LICENSE). Stack adaptations: portable sibling skill invocation, root delegation and Luna-low factual collection, project permissions and the routed goal lifecycle.
