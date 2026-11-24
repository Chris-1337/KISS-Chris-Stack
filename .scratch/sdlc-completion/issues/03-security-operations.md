# Risk-based security and operations

Type: task
Status: completed
Blocked by: 02
Claimed by: root orchestration; separate T3 test/implementation/evaluation roles

## Target and strong child goal

**Textual/unregistered under the active root umbrella goal.** Give existing stack roles proportionate lifecycle security, operational handoff and incident/recovery responsibilities, and document actionable plugin operations using existing tools and approval boundaries.

## Settled design and scope

- Add risk-based applicability to existing goals and evaluation: user data/secrets, trust/permissions, exposed interfaces, dependencies/supply chain, migrations/irreversible effects and availability. Trigger a small threat/abuse and mitigation check only when affected; no unsupported compliance certification, new security role or universal enterprise checklist.
- Carry applicable security checks through discovery/design, implementation, verification, delivery and ongoing maintenance. Reuse Sonar, existing dependency/provenance integrity, normal trust and private reporting; automated scanners cannot certify all secrets/vulnerabilities absent.
- Operational handoff identifies owner/contact where known, target/configuration, health and failure signals, observability/log redaction, backup/restore limitations, recovery and maintenance dependencies. Unknown ownership/SLA stays unknown; do not invent one.
- Incident instructions distinguish detection/triage, evidence preservation/redaction, authorized containment, recovery verification, communication and scoped follow-up. Public issue/email/other outbound messages and production changes require their actual authorization. No on-call tooling or background monitoring service.

## Allowed write ownership

Test role: focused `tests/test_sdlc_lifecycle.py` contracts/negative scenarios. Implementation role: canonical `assets/global-stack-policy.md`, `skills/kiss-chris-stack/SKILL.md`, `skills/evaluate/SKILL.md`, `assets/bundle-manifest.json` hashes for owned changed bundled files, `SECURITY.md`, `docs/OPERATIONS.md`, and one `agent-traces/workflow/` note. Changes to existing Sonar/runtime helper behavior are out of scope; surface defects to root. Root alone changes tracker status.

## Measurable acceptance and verification

1. RED/GREEN contract tests distinguish low-risk direct work from security/permission/data-loss sensitive stack work, and require each applicable lifecycle mitigation/check and operational recovery step.
2. A security-sensitive scenario identifies assets/trust boundaries/abuse, mitigations and verification; a benign documentation scenario records proportionate inapplicability without adding setup/interviews/new roles. Neither skips enabled configured evaluation gates.
3. Incident walkthrough covers stopped local service, failed release/revert and suspected credential exposure with honest restore limits; no secret values/raw logs or unauthorized destructive/external action are performed or prescribed automatically.
4. Runbook commands are checked against owning existing CLI/docs; safe read-only commands are exercised locally where applicable. Documentation/contract checks are the live proof for these instructions, explicitly not an actual production incident/recovery test.
5. Independent evaluator reviews the full owned diff, regression tests, feedback prevention actions, preservation/trust boundaries and current-source integrated Sonar. Existing complete suite remains GREEN.

## Source context

Predecessor [Delivery and rollback readiness](02-delivery-rollback.md); `SECURITY.md`, `docs/SONARQUBE.md`, `docs/REMOTE-CONTAINER.md`, `docs/LEARNING.md`, `docs/THIRD-PARTY.md`, canonical policy and evaluation. Source facts and explicit limits are in `C:/jtmp/kiss-sdlc-delivery-20261123.md` and `C:/jtmp/kiss-sdlc-quality-feedback-20261123.md`.

## Resolution and evidence

Completed after independent root evidence review: 110 current contract/routing/lifecycle checks passed (two Windows symlink privilege skips), five bounded security/operations tabletop walkthroughs passed, safe actual status/interface checks and fresh runtime/tracker readiness passed. Managed global policy synchronized via existing helper, outside bytes independently verified unchanged; no other profile/trust/auth changes.

Fresh Sonar task `36006517-88d4-45c9-a6c9-96c87761cdde`, analysis `ea355e91-3abd-4d4d-997d-7f92b61da5e8`: gate OK all 10 conditions, 87.5% overall/85.7% new coverage, zero open issues. All 39 production files matched T2, coverage provenance retained; exact 254-file source fingerprint `8453bcd6371252c5216016213e4b004ba36402c02e6acef16cfb3a66e09191bc` unchanged during analysis. Evidence `.sonar-evidence/sdlc-t3/final-scan/sonar-evidence.json` and walkthrough/readiness receipts. No actual incident, production restore, service stop, credential rotation or outbound report occurred.

Prerequisite T2 completed with actual source-candidate reversal/preservation and fresh analysis-specific green gate. RED: `uv run --offline --with pytest python -m pytest tests/test_sdlc_lifecycle.py -q` exited 1 with six expected failures (0.14s): missing scoped security/role/runbook/authorization contracts. Separate implementation role dispatched for minimal documentation/workflow changes, no new executable framework or service.

GREEN: six lifecycle contract tests passed; minimal policy/role references, SECURITY authorization corrections, OPERATIONS handoff/diagnosis/three tabletop scenarios and owned hashes/trace frozen. Safe read-only command probes passed. Runtime detected only managed-global-policy drift after the owned canonical change; root assigned existing narrow managed-block repair with unrelated-text preservation, then fresh runtime/tracker proof. Independent documentation/scenario evaluation and fresh Sonar pending; no actual incident/service stop/credential rotation authorized or performed.
