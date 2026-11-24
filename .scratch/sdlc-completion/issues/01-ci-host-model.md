# CI and actual host/model scenarios

Type: task
Status: completed
Blocked by: none
Claimed by: root orchestration; completed by separate T1 test/implementation/evaluation roles

## Target and strong child goal

**Textual/unregistered under the active root umbrella goal.** Make repository regression checks repeatable on Windows/Linux, add a strict opt-in actual Codex/model CLI harness, and independently prove edit and unanswered-decision behavior in the supported native desktop host. Keep each target's compatibility/results separate; deterministic fixtures or a passing native host cannot turn a failed CLI scenario into E2E proof.

## Settled design and scope

- Add one normal unprivileged CI workflow using the existing full pytest command, Node and supported Python. Bootstrap/cache `uv`/pytest as appropriate; do not use offline-only execution on a clean runner. No protected credentials or authenticated model calls in untrusted PR jobs.
- Reuse subprocess/temporary-directory patterns from existing tests. One standard-library Python live runner plus bounded scenario fixtures is sufficient; no new runner framework or dependency.
- Runner opt-in must really invoke installed Codex with `exec --json` and a model. Observe supported CLI flags/event schema in the implementation role before relying on them. Do not use bypass-trust/approval flags or mutate the user's normal plugin/profile/auth configuration. Resolve candidate plugin discovery through supported host interfaces; copied Markdown in a prompt cannot substitute for discovery.
- Use disposable local projects, bounded subprocess timeouts, asserted final filesystem/output and actual JSONL events. At minimum execute an ordinary local edit scenario and an unanswered-decision/approval scenario that must preserve fixture state. Include direct/stack/interview/Wayfinder scenario expectations as a bounded catalogue where host observability supports them; unsupported orchestration remains explicitly blocked/unverified rather than self-certified.
- Retain sanitized summaries only: candidate source fingerprint, CLI/runtime/model identifiers, scenario/assertion results, elapsed time, usage fields actually supplied by host, missing fields and evidence layer. Never retain credentials or raw model transcripts by default. Distinguish discovery, model execution, behavior assertions and observed delegation; only claim each with its own evidence.
- Additional manual native-host protocol: independent evaluator prepares disposable fixtures and records their exact initial state plus candidate source fingerprint; root dispatches a real native direct worker for the edit and a separate unanswered-decision worker. Evaluator then independently asserts the intended edit, all unrelated bytes unchanged, and complete pending-decision fixture preservation. A sanitized receipt links actual native dispatch/completion identities, requested/inherited model metadata if observable, assertions, elapsed time, unknown usage and source identity. Native dispatch and explicit instruction loading are recorded as such, never as automatic installed-plugin/hook discovery. Keep every existing CLI assertion and failure unchanged.

## Allowed write ownership

Test role: new focused `tests/test_host_workflows.py` and CI contract tests if needed. Implementation role: `.github/workflows/`, one `scripts/test-host-workflows.py` (or equivalently named single runner), bounded `tests/fixtures/host-workflows/`, `docs/HOST-TESTS.md`, `CONTRIBUTING.md`, and `agent-traces/workflow/2026-11-23-sdlc-host-ci.md`. Existing test helpers may be reused with root-approved bounded edits. Do not edit canonical policy/skills or README in this ticket. Root alone edits ticket/map status. No changes to `.env`, trust settings or global profile.

## Measurable acceptance and verification

1. Test agent demonstrates meaningful RED: missing/invalid runner behavior or absent CI matrix, malformed/incomplete JSONL, nonzero child exit, timeout, assertion violation, secret/raw transcript non-retention, and absent usage handled honestly. Doubles test parser/failure mechanics only.
2. CI defines Windows and Linux runs of the existing full suite with runtime/dependency preparation. Local suite is GREEN; YAML/static contract verification is recorded. Hosted workflow activation/execution remains unverified unless separately authorized and actually observed.
3. Actual local Codex/model sessions and real CLI candidate discovery are exercised and separately receipted with observed CLI/requested-model versions. Preserve actual failed CLI edit outcomes and bounded repair evidence as target-specific compatibility failures. Do not claim successful CLI editing, authenticated installed-plugin behavior or automatic hooks from discovery/model generation alone.
4. Actual supported native desktop host edit and unanswered-decision scenarios must pass independent evaluator filesystem assertions, with root's genuine native worker dispatch/completion evidence and candidate source identity recorded. Linux CLI live pending-decision preservation is separately observed; Windows CLI pending-decision behavior remains unverified because its receipt stopped after the failed edit. Failed CLI edit assertions stay failed. No mock, worker self-report, copied prompt or native success can satisfy another target's claim.
5. The runner fails visibly on explicitly requested live-check prerequisites, malformed/incomplete events, timeouts or violated assertions. It does not silently fall back to text contracts or another model.
6. Existing feedback protections survive: proportionate route, pending human answer blocks writes, no automatic invented interview/closing approval, no researcher model substitution, no setup-on-direct. Catalogue unsupported checks honestly.
7. Independent evaluator exercises CLI behavior, performs the actual native-host protocol against current candidate source, reruns appropriate/full existing tests, re-resolves unchanged evaluation flags and links fresh current-source integrated Sonar evidence before root resolution. T1 resolves only when implementation checks, native behavioral assertions and enabled current-source gates pass; preserved CLI compatibility failures remain explicit limitations. No browser is applicable to this plugin-only change.

## Source context and prerequisites

Read `C:/jtmp/kiss-sdlc-execution-facts.md`, `C:/jtmp/kiss-sdlc-implementation-context.md`, `tests/test_plugin_lifecycle.py`, `tests/test_task_routing.py`, `README.md`, `skills/evaluate/SKILL.md`, and applicable `agent-traces/user-feedback/`. CLI observed `0.171.0-alpha.13`; `exec --json`, `--ephemeral`, resume/fork exist, but successful generation/exact schema were not researched live. Preserve historical tests and licenses.

## Resolution and evidence

Completed after independent root evidence review: final Windows full suite 526 passed/4 skipped; Linux full 529 passed/1 skipped plus 39 post-refactor focused checks. Native desktop exact edit and pending-decision preservation PASS, independently verified and source-bound in `.sonar-evidence/sdlc-t1/native-desktop-observations.json`. Strict CLI edit compatibility remains FAILED on observed Windows/Linux hosts, never converted to a pass. CI hosted execution and automatic hooks remain unverified.

Fresh Sonar task `e4b6259e-867d-455f-8ad0-16fb333fa1de`, analysis `2255bcb2-372c-4833-9043-8a5f7f89e7d2`: gate OK all 10 conditions, 87.8% overall/85.7% new coverage; current-source fingerprint unchanged. Evidence `.sonar-evidence/sdlc-t1/final-scan/sonar-evidence.json`. Native cleanup was rejected by automatic approval review (blocked by policy); harmless fixture `C:/jtmp/kiss-sdlc-native-9s_ukgfy` remains, no credentials. Owned containers and persistent sessions removed.

RED: `uv run --with pytest python -m pytest tests/test_host_workflows.py tests/test_ci_workflow.py -q` exited 1 (3 failures, 20 errors, 1.63s): missing runner/workflow as expected. Test role owns both new test files; no live-host proof claimed by doubles. GREEN dispatched to separate implementation role.

Progress: first 23 mechanics/CI tests passed. Independent evaluation then drove RED cases for missing/repeated/reordered lifecycle events and an actual grandchild surviving timeout; implementation reports those corrected with owned process-tree cleanup. Test role is adding high-level discovery/receipt/staging mechanics checks. These doubles are not model proof.

GREEN/source freeze: focused host/CI suite now 36 passed (16.44s), including six clearly synthetic CLI discovery/state/receipt mechanics cases. Independent evaluator dispatched for full Windows/Linux regression, bounded actual Linux Codex/model behavior and fresh analysis-specific Sonar gate. Hosted CI and automatic trusted hooks remain separate unverified layers.

Actual Windows Codex 0.171.0-alpha.13 with gpt-6.1-sol authenticated and emitted usage/events, but tool execution is blocked by the host runtime provisioning service; no successful edit claimed. Isolated candidate discovery succeeded without hook trust. Plugin installation copied ignored source files during initial disposable probes; both owned probe trees were removed, protected original .env unchanged, and source-only staging is now required before install. Independent evaluator is checking staging boundaries and preparing a separate bounded Linux Codex 0.166.0 host test. No hooks are auto-trusted, no credentials copied, no hosted CI execution claimed.

Contract refinement from actual evaluation: Linux 0.166.0 strict pending-decision checks passed; Windows 0.171.0-alpha.13 pending-decision behavior remains unverified because its receipt stopped after the failed edit. Strict delegated-edit checks failed on both versions, including a bounded persistent-session probe. No runner assertion, test or failure result is weakened. Root authorized the additional manual native-host protocol because the user requested real supported-host tests, not universal CLI editing. Native behavior and current-source Sonar remain pending; successful native observations will not close CLI compatibility gaps. Owned test-container cleanup must be recorded separately.
