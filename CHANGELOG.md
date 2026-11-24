# Changelog

Conceptual development history grouped by development date. Merging into `main` constitutes a release; merge commits are covered with the changes they integrate.

## 2026-11-23 — Full lifecycle and host verification

### Lifecycle, delivery and operations

- Extended the workflow beyond implementation to delivery, maintenance, incidents and retirement, with explicit authorization, preservation and recovery boundaries.
- Added criterion-to-evidence mapping tied to the actual source and candidate. Passed, failed, skipped and unverified checks remain distinct; local rehearsals do not establish production recovery.
- Added proportionate security and operations guidance, including trust boundaries, negative checks, observable health signals and ownership gaps.
- Added a local release-readiness checker and candidate guidance. Development completion does not authorize publication or deployment.

### Host verification and portability

- Added bounded standalone Codex CLI workflow checks with isolated candidate staging, exact fixture assertions, child-process cleanup and redacted evidence. Removed inherited desktop runtime selectors from standalone child environments.
- Added GitHub Actions tests for Ubuntu and Windows on pull requests and branch pushes, with read-only workflow permissions.
- Corrected Windows Bash path conversion and symlink-preservation assertions in tests.

## 2026-11-04 — Proportionate orchestration

- Replaced a uniform workflow with four routes: a delegated direct fix, a clear goal with separate roles, `grill-with-docs` for unresolved requirements, and Wayfinder for larger dependent work.
- Made the root responsible for routing, approvals, native goals and evidence review. Fresh GPT-6 Luna low agents collect facts; separate agents handle documentation, tests, implementation and independent evaluation.
- Made interviews selective: clear work proceeds without automatic grilling, while unresolved decisions wait for the user. Kept explicit grilling available and added independent workflow switches.
- Added domain modeling, research, prototype and handoff skills, retaining upstream licenses and pinned provenance.
- Added local Markdown, GitHub and GitLab tracker bindings with explicit storage choice, preparation and validation. Unavailable hosted targets cannot silently fall back to local storage.
- Clarified configuration as the initialization marker, fresh runtime/MCP readiness, dependency-ready ticket scheduling, write isolation and scoped feedback review. Aligned the README with these routes; the changes were integrated into `main` on 2026-11-06.

## 2026-11-03 — Setup research and configurable interviews

- Added module-scoped factual research and documentation synthesis to setup, plus a native project `/init` workflow. Documented instructions and contract checks separately from actual native-host execution.
- Improved setup Git hygiene by ignoring generated artifacts and limiting staging to setup-owned files.
- Introduced a grilling skill, initially required before every goal, then made it configurable. The later routed workflow above supersedes that universal interview policy.
- Expanded remote-environment checks for native Windows OpenSSH and recorded user-tested macOS Colima support. Windows graphical onboarding and hook approval remained unverified.

## 2026-10-30–2026-10-31 — Consent, retained feedback and isolated execution

### Project setup and learning

- Added consent-first onboarding: obtain an existing project path before setup and leave the installation directory untouched on decline or cancellation.
- Added optional `plan-mode` approval after goal registration, requiring a real user answer before implementation.
- Added strict configuration backfill that fills missing settings while preserving explicit values and rejecting invalid configuration.
- Added project-local user-feedback records so corrections become scoped prevention checks, with documentation explaining project settings and retained lessons.

### Optional Docker and SSH environment

- Added a dedicated remote execution environment with a local-only SSH endpoint, dedicated keys and separate persistent home, project and host-key volumes. Host credentials are not copied into it; authenticated commands run as an unprivileged user.
- Hardened preparation and persistence behavior after contribution review, preserved user tool environments in SSH sessions, and documented the narrowly scoped Sonar exception for the root SSH daemon.
- Clarified checkout and connection guidance, removing premature relocation instructions. Preferred verified device sign-in for headless authentication and retained normal hook approval.
- Recorded ARM64 and emulated Linux/AMD64 validation, followed by human-completed macOS desktop setup and an actual remote CodeGraph MCP call. Platform evidence is scoped in the [container guide](docs/REMOTE-CONTAINER.md).

## 2026-10-29 — Configurable evaluation gates

- Added SonarQube setup, scanner configuration, runtime checks and managed-token renewal, with fresh analysis-specific quality gates where configured.
- Added strict project configuration with independent live and SonarQube evaluation switches, both enabled by default. Live evaluation covers actual project behavior, including browser checks for affected frontend work.
- Distinguished disabled gates from passed checks and documented plugin positioning, practical limits and the roadmap.

## 2026-10-28 — Native plugin and community distribution

- Evolved the standalone stack into a native Codex plugin distributed through a repository marketplace, with bundled skills, lifecycle hooks and managed runtime configuration.
- Replaced the separate installer and Ouroboros execution path with native Codex goals, verified setup and separate test, implementation and evaluation agents.
- Bundled Ponytail, Caveman and UI-UX-Pro-Max capabilities while retaining third-party licensing, provenance and checkout byte preservation.
- Added controlled contribution and security processes, CODEOWNERS and repository protection configuration. Recorded publication and verified protection behavior, including the owner's bypass boundary.

## 2026-10-27 — Initial stack

- Established the original installable stack with setup tooling, shared agent policy, workflow documentation and tests.
- Combined a fast path and deeper Ouroboros workflows with CodeGraph context, UI-UX-Pro-Max design guidance, Ponytail minimality, Caveman communication and RTK output compression.
