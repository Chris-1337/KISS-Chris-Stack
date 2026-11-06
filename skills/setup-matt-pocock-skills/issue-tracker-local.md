# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `open`/`blocked`/`claimed`/`running`/`failed`/`resolved`; `Claimed by:` records the assigned owner.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved` with acceptance/evaluation evidence. Missing, failed, pending or merely claimed prerequisites remain blockers.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked, and unclaimed; sort by number and let the root claim every ready ticket as slots and isolated writes permit, queueing excess phases. Decision tickets need a clear own question; implementation tickets require settled decisions.
- **Claim**: set `Status: claimed` and `Claimed by: <owner>` and save before any work. The root owns claims/frontier updates; workers report state changes to it.
- **Resolve**: append the answer under an `## Answer` heading, include actual evidence and acceptance/gate results, set `Status: resolved` only after root review, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.

Stack adaptation of the pinned upstream local-tracker template: root-owned claims, complete state/evidence tracking, all-ready parallel scheduling and clear preparatory/implementation readiness boundaries. See [Wayfinder](../wayfinder/SKILL.md) and the [MIT notice](../../licenses/mattpocock-skills-LICENSE).
