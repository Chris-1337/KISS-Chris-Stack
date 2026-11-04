---
name: wayfinder
description: Map large work into dependency-linked decision and execution tickets, then coordinate every unblocked ticket in parallel through stack goals and separate roles.
---

# Wayfinder

Follow the [shared policy](../../assets/global-stack-policy.md). The root selects this route for large tasks when `wayfinder=true` (default); explicit requests remain available when automatic use is false. The active session coordinates and delegates planning, interviewing, documentation and ticket work. This adaptation carries execution into the map: after planning, automatically run every unblocked ticket through stack with a strong goal, within actual host capacity. It replaces upstream's plan-only stop and one-ticket-per-session limit; retain one bounded assignment per worker.

## Destination and tracker

Delegate [grilling](../grilling/SKILL.md) and [domain-modeling](../domain-modeling/SKILL.md) to settle the destination and scope first, then map the frontier breadth-first. Root relays questions and waits; no agent may stand in for the human. All pure fact collection, including outside-repo questions, uses fresh-context `gpt-6-luna`, `reasoning_effort="low"`, `fork_turns="none"` via [research](../research/SKILL.md). Researchers collect referenced facts only, no implementation or design decisions. Planning/design is a separate substantive role.

Read authoritative project-root `wayfinder-tracker` through bundled `scripts/evaluation-config.py` and require `scripts/setup-wayfinder.py --project <project-root> --check` before map/ticket operations. The Boolean `wayfinder` remains the automatic route switch. Local default is `{ "provider": "local", "directory": ".scratch" }`; a configured custom directory replaces `.scratch` in every effort/map/ticket path below. GitHub selects `{ "provider": "github", "repository": "OWNER/REPO" }` on github.com; GitLab selects `{ "provider": "gitlab", "project": "https://HOST/GROUP/PROJECT" }`. Use only that provider/target and its prepared managed `docs/agents/issue-tracker.md` operations, never remote/cwd/environment inference or an independent doc setting. A missing/stale/unsafe binding must be reconciled by the root-assigned [tracker setup](../setup-matt-pocock-skills/SKILL.md) worker, then rechecked; invalid/unavailable selected hosted providers block, with no local fallback.

The helper prepares only a root and operations binding, not an actual map. When work begins, local maps live at `<configured-directory>/<effort>/map.md` and child tickets at `<configured-directory>/<effort>/issues/NN-slug.md`. Hosted commands and API paths must target the configured explicit host/repository/project; preflight requires matching canonical target identity (GitLab project path case is exact; only scheme/host case is normalized). The bundled [local](../setup-matt-pocock-skills/issue-tracker-local.md), [GitHub](../setup-matt-pocock-skills/issue-tracker-github.md) and [GitLab](../setup-matt-pocock-skills/issue-tracker-gitlab.md) templates are rendered by setup. Missing CLI/auth/target/access blocks without automatic install/login. Successful read-only metadata checks prove neither all token write capabilities nor authorization: publication, claims/assignments, comments, labels, branch pushes and closure still need user authorization. Do not silently switch backend to evade a missing permission or migrate/delete old data on a config change.

Refer to every map/ticket by its linked title, not a bare number. The map is an index; detail belongs in its ticket exactly once. Preserve the destination, notes, decisions, fog and out-of-scope boundaries:

```markdown
## Destination
<what completion means for this effort>
## Notes
<scope, relevant skills, constraints; execution continues through stack ticket goals>
## Decisions so far
- [Closed ticket title](ticket.md): one-line gist and evidence pointer
## Not yet specified
<in-scope questions still too vague to ticket>
## Out of scope
<excluded work and why>
```

## Tickets and frontier

Create child tickets only for questions/work that can already be stated precisely. Create identities first, then wire blocking edges and real cross-references in a second pass. Keep in-scope unknown shape in **Not yet specified** rather than speculative tickets; graduate it as prerequisites clarify. Work beyond the destination is **Out of scope**, never fog. Preserve ticket history and explain superseded/out-of-scope closures; do not delete evidence.

Each ticket records title, type, question/target, strong goal (scope, constraints, measurable acceptance and verification), blocking tickets, status, claim/owner, source context and resolution/evidence pointers. Use native tracker blocking where authorized and available; local files use `Type`, `Status`, `Blocked by` and `Claimed by` fields. Ready/frontier means **open, unblocked and unclaimed**, with every blocker completed with evidence, its own question/target and prerequisite facts clear and required approval obtained. Decision/research/prototype tickets start with a clear question to resolve their stated unknowns; implementation tickets require settled design and requirement decisions. Pending human answers, failed checks, unfinished integration and unresolved prerequisite research block dependent work, not unrelated ready tickets.

Ticket types:

- **Research (AFK):** [research](../research/SKILL.md), always the prescribed facts-only Luna-low agent. Retain a local source-linked notes artifact and pointer; never automatically push a research branch. Research preparation can happen before an implementation goal; it produces facts, not a completed implementation ticket.
- **Grilling (HITL):** delegated [grilling](../grilling/SKILL.md) plus [domain-modeling](../domain-modeling/SKILL.md), with real human answers relayed by root.
- **Prototype (HITL):** a separate substantive agent uses [prototype](../prototype/SKILL.md) for a bounded disposable artifact; actual human feedback settles the design question. Preparatory facts still come from Luna low.
- **Task (AFK or HITL):** bounded work or implementation. The root assigns a precise checklist to the human where needed. All implementation uses stack goal and separated roles; provisioning/migration/external writes require their actual authorization.

## Schedule and resolve

1. Root delegates destination/frontier planning and local map/ticket documentation. If the whole effort turns out clear and normal-sized, reclassify to stack with goal without inventing fog or requesting an unnecessary closing confirmation.
2. Claim every ready ticket before dispatch. Root gives each ticket its strong goal, relevant context, feedback, dependencies, allowed paths, permitted effects and evidence requirements. On a host with one active native goal, preserve a root umbrella and explicitly label each child goal textual/unregistered under it; only root manages native goals. Honor configured `plan-mode` before implementation phases, including new or changed ticket goals not yet approved.
3. Root schedules all unblocked tickets in parallel as slots permit: separate test RED, implementation GREEN and independent evaluation agents per stack ticket. Queue excess phases and use available slots across ready tickets; do not reserve three workers simultaneously per ticket. Ticket workers do not recursively spawn triads or register goals. Research/interview preparation retains its pre-goal role rather than fabricating RED tests for collecting facts.
4. Keep disjoint write ownership or isolated worktrees/checkouts, serialize conflicting edits/integration, preserve unrelated changes, and evaluate integrated source. A worker finishing is not proof its ticket passed. Failed or pending checks keep the ticket incomplete and dependent tickets blocked.
5. Record the actual resolution and executable evidence, close only after acceptance and enabled applicable evaluation gates pass, and update the map's decision index. Keep fresh analysis-specific SonarQube proof where configured. Recompute the frontier after every completion, automatically start newly unblocked work, and ticket newly clarified fog within scope. Root reviews all integrated evidence before completing the umbrella goal.

Use [handoff](../handoff/SKILL.md) for bounded context continuity. Upstream neighboring workflows such as to-spec, to-tickets, implement and ask-matt are optional onward skills, not required dependencies or automatic invocations of this stack route. No additional tracker CLI is required for local Markdown.

Adapted from Matt Pocock's [wayfinder](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/wayfinder/SKILL.md), commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, under [MIT](../../licenses/mattpocock-skills-LICENSE). Stack adaptations: portable sibling skill invocation, root delegation and Luna-low factual collection, project permissions and the routed goal lifecycle.
