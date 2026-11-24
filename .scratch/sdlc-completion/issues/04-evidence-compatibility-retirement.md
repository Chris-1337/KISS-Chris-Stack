# Traceability, compatibility, cost and retirement

Type: task
Status: completed
Blocked by: 03
Claimed by: root orchestration; separate T4 test/implementation/evaluation roles

## Target and strong child goal

**Textual/unregistered under the active root umbrella goal.** Connect criteria to asserted checks, current source and optional released candidate; record measured compatibility/cost without promises; finish the existing lifecycle with a preservation-aware retirement procedure and a consistent README.

## Settled design and scope

- Extend existing goal/ticket/evaluation evidence with a compact criterion-to-check-to-source-to-release mapping. Each row identifies criterion, command/assertion/result, source fingerprint, evidence path and release identity/status or inapplicability. Failures, unavailable checks and disabled gates stay distinct; historical prose is never current proof.
- Reuse the T1 runner's runtime/model/usage/time receipts and T2 candidate identity. Document supported vs observed vs unverified host/runtime/platform compatibility, including Windows/Linux CI definitions versus actual local/hosted execution. No new cost service, pricing table, routing heuristic or promised savings. Missing usage is unknown; tokens/time are not currency cost.
- Retirement planning identifies owner/authorization, affected consumers/integrations, deprecation/migration notice if authorized, retention/access/legal obligations where known, credentials/jobs/hooks/runtime cleanup, backups/recovery window and verification. Preserve user data/history; destructive decommissioning is a separately authorized action. Retiring this plugin must not delete user projects, shared runtimes, caches, credentials or unrelated MCP/global policy blocks.
- Update the whole README against final owning policy/docs and evidence; keep roadmap gaps truthful. Reuse existing docs/skill structure. Do not create an ADR/glossary unless an actual consequential unresolved terminology/design decision emerges.

## Allowed write ownership

Test role: extend focused lifecycle/evidence contract tests and bounded receipt validation tests. Implementation role: canonical policy, `skills/kiss-chris-stack/SKILL.md`, `skills/evaluate/SKILL.md`, `skills/wayfinder/SKILL.md`, owned resource hashes in `assets/bundle-manifest.json`, `docs/EVALUATION.md`, `docs/WAYFINDER.md`, `docs/ARCHITEKTUR.md`, `docs/LIFECYCLE.md`, `README.md`, and one `agent-traces/workflow/` note. Prefer sections in existing new docs over additional overlapping files. Only root-approved corrections may touch earlier tickets' runner/release checker; reevaluate any changed executable source. Root alone updates map/tickets.

## Measurable acceptance and verification

1. Separate RED/GREEN checks require a criterion/evidence/source/release mapping, reject current-pass claims from stale source or missing assertions, and distinguish failed/disabled/inapplicable/unknown states. Use existing receipt shape; no new general schema framework.
2. The effort has a concrete acceptance matrix linking final executable and contract checks to current integrated source, including actual host/model observations, CI validity versus run evidence, release/rollback rehearsal and final analysis-specific Sonar gate.
3. A compatibility/overhead receipt records actual host/model/runtime, elapsed time and provided usage with explicit missing data. No unsupported model dispatch or OS coverage claim and no claimed savings without a comparable baseline.
4. Retirement walkthrough covers plugin-only removal versus downstream system retirement, data/history preservation, shared-tool protection, authorization and independent post-action verification. This ticket performs no destructive retirement or external communication.
5. Full README consistency review addresses all sections against owning final instructions and evidence, preserving roadmap limits and upstream provenance.
6. Independent integrated evaluation re-resolves unchanged configuration, runs the complete suite plus current executable CLI/host checks, records all applicable live results, refreshes coverage/current-source Sonar analysis and verifies a green gate by that analysis ID before root completion. Any earlier evidence made stale by source changes is rerun; documents alone never supply host execution proof.

## Source context

Predecessor [Risk-based security and operations](03-security-operations.md), all earlier ticket evidence, `docs/EVALUATION.md`, `docs/WAYFINDER.md`, `docs/ARCHITEKTUR.md`, README, canonical policy, evaluate/Wayfinder skills and applicable feedback requiring complete README review. No global memory updates.

## Resolution and evidence

Completed after root review of concrete final artifacts: full measured suite 572 passed/4 skipped (225.37s), focused Linux changed paths passed, 63 actual CLI integrity assertions passed. Independent native workers passed exact edit and full 204-file pending preservation against current complete 185-file artifact. Actual isolated A/B/A rehearsal passed all installed bytes/discovery and foreign config/data preservation; prior A cryptographically matched a real earlier full checkpoint, B matches final candidate. Whole README review: 12 sections/38 links passed.

Final current source: 256 files, fingerprint `399b1901a64da951943f5718b205478ec51fb8f0e936fa1c472bdff6bf05dcaa`; release fingerprint `ca384108354bfaa7ab332272a3bdd432f94a6d3e424f860d749124ecd4ad65bc`, version 0.2.0, published:false. Native proof provenance explicitly records only two later nonshipped test edits with complete candidate/scenario bytes unchanged. Final managed policy matches canonical with unrelated global content preserved; fresh runtime/tracker/MCP proof retained. Final root configuration re-read live/Sonar enabled, plan-mode false, local tracker unchanged.

Fresh Sonar task `17d21150-7c4a-400e-9ac3-092409f99553`, analysis `722ef485-02b2-4a95-a40b-876d2c1b5999`: all 10 conditions OK, no ignored conditions, 87.5% overall/85.8% new coverage, zero open issues, 100% hotspots reviewed, source unchanged. Root inspected actual gate/native/reversal receipts and 11 passing required acceptance rows. Exact executed command/argv restored in ignored matrix, not condensed pseudocommands. Evidence `.sonar-evidence/sdlc-t4/{acceptance-matrix,evaluation-summary}.json` and `final-scan/sonar-evidence.json`.

Known limitations retained: historical CLI delegated-edit failures, automatic hooks/hosted CI/wider model workflows unverified; no publication, production restore, actual incident or destructive retirement. Harmless old native fixture cleanup was automatically rejected (blocked by policy); current native fixtures intentionally retained as evidence. Owned processes/containers and auth mounts removed, reused services preserved. No source changes after final evaluation.

Prerequisite T3 completed with independent contracts/walkthroughs/readiness and fresh green analysis `ea355e91-3abd-4d4d-997d-7f92b61da5e8`. RED: selected lifecycle/release/host tests produced 11 expected failures and one existing valid-candidate pass (16.37s). Actual false-passes proved: empty filesystem assertion list, and omitted/mutated OPERATIONS accepted under old release identity.

Root approved minimal host assertion guard, finite release-authority inventory completion using the existing extras loop, compact evidence/retirement contracts and full README consistency. Inventory includes existing seven resources plus actual root/operations/quality/onboarding/decision/CI authorities, with exact existing filenames supplied by independent evaluator; excludes generated project state, local configuration, evidence and traces. No Markdown crawler/new framework. Final ignored evidence prefix `.sonar-evidence/sdlc-t4/`; tracked notes reference it before final source freeze to avoid a self-referential fingerprint loop.

GREEN/source freeze: 83 focused lifecycle/host/release tests passed, one Windows symlink privilege skip (132.93s), eight additional scoped document checks passed. Actual release checker passed/published:false, fingerprint `ff1dc601bf66f3e06fa703b23707ba936bf9e8ab4dc0ccaadc0a06828df806b6`. Exact 26-resource inventory and constant-driven callers finalized, three owned skill hashes updated. Tracked final trace contains complete README owner review and 38 valid local links. Root assigned final managed-global-policy-only reconciliation and independent full integrated tests/native-host/fresh Sonar; no final gate pass claimed yet.

Final review corrected only two canonical copied-global reference ambiguities; 13 affected contracts passed, managed block re-synced with outside-byte preservation. Final release fingerprint `ca384108354bfaa7ab332272a3bdd432f94a6d3e424f860d749124ecd4ad65bc`; actual current native worker edit/pending cases independently passed across complete 204-file fixtures.

Full suite then found one obsolete structural test (571 passed/4 skipped): the pre-SDLC 85-line heuristic, introduced when policy had 44 lines, conflicted with the explicitly approved 103-line policy. Test/spec role established no ADR/user numeric budget, only deduplicated concise rules. Root approved replacing that heuristic with a canonical duplicate-paragraph guard, keeping all semantic assertions; actual current policy passes and appending a real duplicate paragraph fails. Also updated explicit release expected-set guard to all 26 agreed paths. Only tests changed; 14 affected tests passed (21.54s), no production/docs/config/gate thresholds changed. Final full clean rerun and fresh gate pending.
