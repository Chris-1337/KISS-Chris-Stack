# Delivery and rollback readiness

Type: task
Status: completed
Blocked by: 01
Claimed by: root orchestration; separate T2 test/implementation/evaluation roles

## Target and strong child goal

**Textual/unregistered under the active root umbrella goal.** Extend existing stack goal/evaluation instructions with proportionate delivery readiness and rollback planning, and make this repository's release-candidate checks executable and locally reviewable without publishing or deploying.

## Settled design and scope

- Reuse existing orchestrator, canonical policy, evaluator and publication guide. Separate implementation completion from user-authorized release and observed post-release verification. Ordinary goals that do not deliver externally record delivery applicability; do not add a universal deployment ceremony.
- Delivery-bearing goals identify target/environment, immutable candidate identity/source, configuration and compatibility prerequisites, owner/authorization, preflight evidence, success/abort signals, rollback or forward recovery, retained data and post-release verification. User-impacting irreversible steps require an explicit decision before execution.
- Add one small standard-library release-readiness command only for mechanically checkable repository facts (manifest identity/version, referenced resources/provenance and bundled hashes, source identity, nonpublication result). Reuse current tests/helpers and native Git/CLI; no new packaging system or release service.
- Document candidate preparation and upgrade/revert using actual repository-marketplace/native host semantics. Perform a local disposable candidate/reversal rehearsal through supported interfaces, preserving the user's profile/data. State precisely what the rehearsal proves; it cannot prove a published marketplace rollback or production data recovery.

## Allowed write ownership

Test role: focused new release/lifecycle contract tests. Implementation role: `assets/global-stack-policy.md`, `skills/kiss-chris-stack/SKILL.md`, `skills/evaluate/SKILL.md`, `assets/bundle-manifest.json` hashes for changed bundled resources only, one `scripts/check-release.py` if necessary, `docs/DELIVERY.md`, `docs/GITHUB-PUBLICATION.md`, and one `agent-traces/workflow/` implementation note. Keep shared edits sequential. No publish/commit/push, version bump for an unshipped candidate, global profile/config or production target mutation.

## Measurable acceptance and verification

1. Separate test role demonstrates RED for missing delivery/authorization/recovery contracts and malformed or stale candidate metadata/hash checks; GREEN uses current real files and negative temp fixtures.
2. Reusable instructions cover preflight, explicit authorization, release target/source, success/abort, recovery preservation and post-release checks, with applicability recorded for nondelivery work. They never infer authorization from a completed development goal.
3. The release-readiness command validates the current candidate and fails on mismatched resource/version/source evidence. It emits nonsecret source-bound results and performs no publication/external mutation.
4. Actual supported local CLI/disposable install or equivalent real candidate-selection workflow is rehearsed and reversed with independent assertions. Unsupported remote/published semantics remain unverified. Data/config preservation is asserted; no invented sample service supplies proof.
5. Existing bundle/license/resource tests and complete suite pass. Independent evaluation uses actual release-check CLI and contract/document checks for downstream workflow instructions, reviews normal trust/external-write boundaries, and links current-source integrated Sonar before resolution.

## Source context

Prerequisite evidence from [CI and actual host/model scenarios](01-ci-host-model.md); `CONTRIBUTING.md`, `docs/GITHUB-PUBLICATION.md`, `docs/REMOTE-CONTAINER.md`, native/marketplace manifests, `assets/versions.json`, `assets/bundle-manifest.json`, `docs/THIRD-PARTY.md`, canonical policy and evaluate skill. Preserve existing historical publication observations rather than relabeling them current.

## Resolution and evidence

Completed after independent root evidence review: full measured suite 555 passed/4 skipped; final checker-specific current-source measurement 29 passed after two behavior-equivalent static repairs, with unchanged-module coverage/source provenance. Linux release-focused 29 passed. Actual current-candidate CLI/16 negative checks and isolated real A/B/A selection/reversal PASS with all 166 installed bytes/files asserted and unrelated config/data preserved. No publication or normal-profile changes.

Fresh gate OK all 10 conditions, task `2d80853e-0941-460d-975c-07d57cce25cc`, analysis `58adf3c9-ae89-4e77-acc8-a1ab7f41beaa`; 87.5% overall/85.7% new coverage, zero open issues, 100% hotspots reviewed. Exact 251-file source fingerprint `6bbcdbf846f73d046ab2a457c57597a253d14fd7140115cfab4f77835105e79f` unchanged during analysis. Evidence `.sonar-evidence/sdlc-t2/final-scan-green/sonar-evidence.json` plus release/reversal receipts. This proves local source-candidate reversal, not published rollback or production data recovery.

Prerequisite T1 completed with current-source native-host assertions and analysis-specific green Sonar; CLI compatibility failures remain explicit. RED: `uv run --with pytest python -m pytest tests/test_release_readiness.py -x -q` failed as expected because `scripts/check-release.py` was missing (1 failure, 3.44s). Separate implementation role dispatched. Release identity must bind runtime/metadata plus exact root LICENSE and provenance bytes; minimal test fixtures cannot waive license preservation.

GREEN: 24 focused tests passed (78.19s); actual current-candidate checker returned passed/published:false and release fingerprint `c10c758f1c947a5034e23ce65bcc694ce98b2e54c0b8dc2269f3b460fb564270`. Implementation frozen for independent metadata negatives, actual A/B/A candidate selection/reversal, preservation assertions and fresh quality gates.

Independent evaluation drove two narrow RED/GREEN repairs before final freeze: actual invalid SemVer false-passes, then omitted/mutable operative delivery guide identity. The checker now enforces native SemVer/64-character bounds and binds seven explicit release resources (LICENSE, provenance, delivery/publication guides, SECURITY and ownership/protection files). Final repair focused checks 8 passed (17.52s); current release fingerprint `f1923341e0c642eac37f3431859acd7edd7fb6a05d713084ceaffd9b6ecac508`, published:false. Final independent rehearsal/full coverage/analysis-specific gate pending.
