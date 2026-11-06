---
name: research
description: Collect source-linked facts in fresh GPT-6 Luna low agents and retain bounded factual context notes, including before interviews and stack goals.
---

# Factual context research

The root dispatches every pure information-gathering assignment to a fresh agent with `model="gpt-6-luna"`, `reasoning_effort="low"`, `fork_turns="none"`. Supply the bounded question/direction, allowed sources/paths/tools, exclusions and factual notes destination directly, not inherited unrelated conversation. Run independent directions in parallel within available slots; missing agents/model/effort blocks required research, never silently substitute.

Collect only observed facts from primary owning sources: code, official documentation/specifications, first-party APIs and existing project documents/decisions. Cite each claim with file/line or source URL and source revision/file hashes or dirty fingerprint; distinguish missing/uncertain facts explicitly. Cover relevant docs, traces, user feedback, callers/tests/configuration as assigned. Do not scan secrets, dependencies/build outputs or unrelated modules.

Researchers make no implementation/source/configuration changes, design decisions, recommendations or speculative reasoning. Their only writes are assigned factual notes or [handoff](../handoff/SKILL.md) artifacts; they do not synthesize final designs/ADRs, run setup, register goals or delegate. Preserve existing artifacts, reference rather than duplicate them, redact secrets and omit raw logs/transcripts. Use established project notes conventions; if none exists the root supplies a bounded notes path.

Return the artifact path, referenced facts, unknowns and completion limits to the root. Pending or stale research blocks dependent decisions until refreshed. The root assigns subsequent planning, documentation or implementation to substantive roles under the [shared policy](../../assets/global-stack-policy.md); those roles may inspect relevant sources as part of their work.

Adapted from Matt Pocock's [research](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/research/SKILL.md), commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, under [MIT](../../licenses/mattpocock-skills-LICENSE). Stack adaptations: portable sibling skill invocation, root delegation and Luna-low factual collection, project permissions and the routed goal lifecycle.
