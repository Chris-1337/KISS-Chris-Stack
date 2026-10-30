## KISS-Chris-Stack

Automatically use the installed `kiss-chris-stack` skill for software development. The user request and project rules take precedence.

### Setup and context before the goal

- Plugin installation runs bundled `skills/onboarding/SKILL.md` before lifecycle setup/readiness: ask whether to initialize a project; yes requires an explicit existing project path before setup, no/cancel only gets the manual `/setup` or later trusted-hook hint. Keep pending onboarding replies in that dialogue; do not initialize the installation `cwd` or fall through on decline.
- Before each ordinary new task, the root session uses bundled `/setup` runtime checks for skills, global rules, CodeGraph index/MCP, and a real MCP tool call in this session. Do not implement without readiness or while `reload-required`; no cached ready flag or automatic hook approval. Sub-agents do not run setup.
- Establish context before every implementation: review both `docs/` and `agent-traces/`, read relevant documents and traces, and inspect affected code, call paths, tests, and existing designs.
- Project-root `kiss-chris-stack.config.json` is the sole initialization indicator: validate and preserve existing configuration through the bundled resolver; invalid/unreadable configuration blocks setup. If absent, `/setup` performs local initialization and documentation bootstrap, then creates default configuration only after runtime/MCP and documentation success. Existing configuration requires fresh readiness, not repeated initialization based on missing docs/traces; explicit `/setup` still fills gaps. This bootstrap is exempt from the implementation goal gate and invokes neither itself nor another goal.
- Clarify missing information, conflicting requirements, and necessary unresolved decisions with the user before starting dependent work. Do not invent requirements.
- Before defining the goal, resolve project-root `kiss-chris-stack.config.json` through the installed plugin's bundled `skills/evaluate/SKILL.md` and `scripts/evaluation-config.py`. Then use Ponytail to formulate a strong `/goal`: target state, scope, constraints, measurable acceptance criteria, and suitable verification including enabled evaluation gates.
- Only the root session manages the goal: check `get_goal` and reuse an open goal for the same task. Clarify conflicts with an unrelated open goal instead of replacing it. Otherwise register with `create_goal` and confirm success before implementation. Set `token_budget` only on explicit request. Resolve registration failures; if native tools are unavailable, explicitly label the goal textual and unregistered.
- `plan-mode` is a top-level JSON boolean, default `false`: continue automatically after goal registration when false. When `true`, present the strong registered goal, request explicit user approval, then stop and yield the turn before dispatching test, implementation or evaluation agents; explain that configured `plan-mode=true` requires this approval. Resume the same goal only after approval; silence, elapsed time, a pending reply or rejection is not approval. A changed goal requires renewed approval. This workflow gate does not change the host's collaboration mode.

### Implementation through separate agents

The root session orchestrates and supplies the goal, context, and boundaries to three separate sub-agents:

1. **Test agent:** writes tests from the goal specification and demonstrates the expected failure (RED).
2. **Implementation agent:** makes the smallest complete change until the specified tests pass (GREEN). It does not weaken tests; specification errors go to the orchestrator and test agent for clarification.
3. **Evaluation agent:** independently checks all acceptance criteria, constraints, and regressions through the bundled evaluation skill: prove affected functionality in the actual project started directly or with Docker Compose; test affected frontend behavior with a browser/Playwright and automatically install missing CLI/headless-browser dependencies when live evaluation is enabled.

Sub-agents handle only their assigned role under the same goal; they register no goals and delegate no recursive groups of three. Test specification, implementation, and final verification remain with different agents/sessions. For documentation-only tasks, suitable document and contract checks serve as tests. If sub-agents are unavailable, clarify the blocked workflow instead of silently combining roles.

The orchestrator assigns failures to the responsible agent and autonomously continues repair and reevaluation until the goal is met. Pause for a necessary user decision or approval. Never infer success from agent prose alone. Before marking a native goal `complete` with `update_goal`, re-read evaluation configuration and require current-source evidence for all enabled applicable gates; invalid configuration or failed required checks block completion. Record explicit disabled gates as skipped, never passed; other statuses follow host rules.

### SonarQube quality gates

- `evaluation.live.enabled` and `evaluation.sonarqube.enabled` default to `true`; explicit `false` in `kiss-chris-stack.config.json` independently disables that gate. Follow the bundled evaluation skill for strict configuration validation, live proof, dependency installation and evidence. Never edit switches merely to pass a failing goal.
- Before enabled configured SonarQube scanner/readback/gate operations, run the bundled `/setup-sonarqube` token-renewal preflight: silently renew only confirmed expired managed tokens using protected owner credentials and unchanged scope. Reuse healthy tokens; unresolved expiry or other authentication/permission failures still block completion. No permanent background service is implied.
- When SonarQube is configured for the project and its evaluation gate is enabled, include its quality gates in goal acceptance and evaluation. Before marking a goal `complete`, require fresh successful analysis of the current source (including uncommitted changes) and green quality gates for all configured relevant projects/components; use each scanner task's analysis ID, never a cached dashboard pass. A failed, pending, missing or unreachable analysis/gate, missing required coverage, stale source, or expired credentials prevents completion. Preserve configured thresholds; do not bypass gates, silently disable configuration or weaken exclusions to pass. The optional bundled `/setup-sonarqube` skill establishes project-specific scanners, credentials and gate configuration; its absence does not require installing SonarQube for unrelated projects.

### Tools and boundaries

- **Ponytail:** first consider deletion, reuse, platform/standard library features, and existing dependencies; make the smallest robust change without speculative abstractions. Preserve security, validation, error handling, accessibility, and business requirements.
- **CodeGraph:** use focused context, call paths, and impact for structural questions. Before nontrivial code changes, synchronize an existing index (`codegraph sync <repo>`) or initialize a missing one (`codegraph init -i <repo>`). The host starts MCP; do not start a second server. Use `rg` for literal searches.
- **ui-ux-pro-max:** use for every UI task, including design, interaction, responsiveness, accessibility, and review; skip for purely nonvisual work.
- **Caveman and RTK:** keep communication in the user's language and shell output concise; preserve errors, exit codes, technical facts, and verification evidence in full.
- Preserve unrelated changes. No destructive Git commands without explicit approval. External systems are read-only by default; push, merge, publication, deployment, credential changes, and other external writes require explicit user authorization.

### Language

- Write all existing and future documentation, including `docs/` and `agent-traces/`, in English. Conduct internal reasoning in English; communicate with the user in the language of their prompt.

### Documentation

- `docs/` is for people: system architecture covering all existing components (for example frontend, backend, integrations), business decisions, and technical decisions as ADRs. Maintain existing documentation; identify evidence and open questions.
- `agent-traces/<component>/` is long-term agent memory: for each implemented goal, add a short note with the goal/target, what changed, why, affected locations, checks/results, and remaining limits. Derive components from the actual project; for cross-cutting work, use one main note with references instead of duplicates.
- Update both areas as appropriate to the change. Store no secrets, raw logs, or chat transcripts; project knowledge belongs in the repository, not global rules.
