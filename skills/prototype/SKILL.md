---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

Follow the [shared policy](../../assets/global-stack-policy.md). The root assigns a separate substantive prototype role and supplies a bounded question, context and allowed paths. All pure fact collection remains fresh GPT-6 Luna low research; prototype design/build is not assigned to a facts-only researcher. Use [UI-UX-Pro-Max](../ui-ux-pro-max/SKILL.md) for UI work and preserve accessibility, trust-boundary validation and safeguards. A prototype never authorizes production changes or external writes. Return the actual artifact and user verdict to the root; do not register another goal, run setup or spawn recursive agents.

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered, using the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file (free-play buttons plus tabbed guided walkthroughs) that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

The two branches produce very different artifacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious, but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner: `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file the user double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE, wipe me" name.
4. **Skip the polish.** Use only focused checks and error handling needed to answer the question safely; preserve validation, accessibility and data-loss safeguards. Avoid speculative abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Capture it when done.** Retain the bounded local prototype as a **primary source** with a context pointer and the actual user verdict. The root routes validated production changes through stack goals and separate roles. Do not automatically commit, push, publish an issue or mutate production; such actions require their own authorization.

Adapted from Matt Pocock's [prototype](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/prototype/SKILL.md), commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, under [MIT](../../licenses/mattpocock-skills-LICENSE). Stack adaptations: portable sibling skill invocation, root delegation and Luna-low factual collection, project permissions and the routed goal lifecycle.
