---
name: handoff
description: Retain a bounded factual handoff with source and goal pointers so a fresh agent can continue a delegated task.
---

# Context handoff

A handoff is pure information collection: the root assigns a fresh `gpt-6-luna` agent with low reasoning and `fork_turns="none"`, supplying only the relevant conversation facts, source/artifact pointers and next role. The agent records facts, established user decisions, current goal/ticket identity, completed checks with evidence, pending questions/blockers, allowed scope and next assignment. It makes no implementation/source/configuration changes, design decisions, recommendations or speculation. No silent model/effort fallback or recursive delegation.

Save the bounded handoff in the OS temporary directory (`tempfile.gettempdir()` or the host equivalent), not the workspace, unless the root explicitly assigns a persistent project notes destination. Include a **Suggested skills** section linking the bundled sibling skills relevant to the next role; read/invoke `SKILL.md` directly when a native Skill tool is unavailable.

Do not duplicate existing specs, plans, ADRs, tickets, diffs or notes: reference their exact paths/URLs, revision/file hashes or source fingerprint. Never include secrets, raw logs, full chat transcripts or unnecessary personal information. If arguments describe the next session, keep the factual summary scoped to that work.

Return the absolute handoff path to the root. The receiving role verifies referenced evidence is still current, resumes the existing root/ticket goal and does not invent prior approval, another setup or native goal. Follow the [shared policy](../../assets/global-stack-policy.md).

Adapted from Matt Pocock's [handoff](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/handoff/SKILL.md), commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, under [MIT](../../licenses/mattpocock-skills-LICENSE). Stack adaptations: portable sibling skill invocation, root delegation and Luna-low factual collection, project permissions and the routed goal lifecycle.
