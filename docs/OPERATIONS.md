# Plugin operations and incident response

Use the existing [security and operations contract](../assets/global-stack-policy.md#risk-based-security-and-operations) through the normal orchestrator, test, implementation and evaluation roles. This is the runbook for this repository's plugin and optional local dependencies. Downstream projects use their own targets, owners and operational commands. A benign documentation change can record security/operations as inapplicable with a brief reason; it adds no setup, interview or role and never disables configured evaluation gates.

## Operational handoff

Record only the applicable facts with source/evidence pointers:

| Fact | Required boundary or limitation |
| --- | --- |
| Owner/contact | `.github/CODEOWNERS` identifies repository review ownership; it is not an on-call contact. Record the actual target's accountable owner/contact where known, otherwise unknown. No operational SLA or response-time guarantee is defined. |
| Target/configuration | Retain candidate revision plus dirty-source fingerprint, host/profile identity and relevant nonsecret configuration. A plugin manifest version alone cannot identify installed bytes. |
| Health/failure | Runtime CLI checks and a real session CodeGraph MCP call establish different readiness facts. Sonar process/HTTP health is distinct from a completed analysis-specific gate. Remote Compose health checks SSH configuration, not login or user workflow. Record functional assertions and abort/failure signals separately. |
| Observability | Retain timestamps, command exit codes, nonsecret task/analysis IDs and concise redacted error summaries. Preserve necessary evidence privately; never copy `.env`, auth files, raw logs or transcripts into reports. Unknown impact remains unknown. |
| Backup/restore | Preserve reviewed prior source-only candidates and required project configuration/data before authorized changes. Named volumes, Git history and a retained plugin are not verified database backups. Record backup owner, protected location, age and restore evidence or explicitly unverified restore limits; plugin reversal cannot restore lost production data. |
| Recovery/maintenance | Link [delivery](DELIVERY.md), [SonarQube operations](SONARQUBE.md), [remote container persistence](REMOTE-CONTAINER.md) and [security reporting](../SECURITY.md) as applicable. Record dependencies such as Docker, CLI/runtime versions, host discovery/trust, protected credentials and provenance pins; retain unresolved maintenance/compatibility limits. |

No background monitor, incident service or automatic support promise is installed. Existing [feedback](LEARNING.md) records actionable lessons; it grants no additional permission.

## Read-only diagnosis

Run from the reviewed repository root. Confirm the selected host/profile and Docker engine endpoint first; a local command can otherwise target a remote service. These commands inspect state without repairing setup, rotating tokens, starting/stopping services or publishing anything:

```powershell
python scripts/evaluation-config.py --project .
python scripts/setup-runtime.py --project .
python scripts/check-release.py --project .
docker context show
docker ps --filter name=kiss-stack-sonar --format '{{.Names}} {{.Status}}'
docker inspect --format '{{.Name}} {{.State.Status}}' kiss-stack-sonar kiss-stack-sonar-db
docker compose -f containers/remote/compose.yaml ps
```

The runtime checker does not complete session MCP verification. The candidate checker checks local bytes, not installation, security certification or release authorization. Empty Compose output means no listed service, not a successful workflow. If Docker or a resource is absent, retain the bounded failure and applicability; do not provision a replacement or disable a gate. A stopped configured SonarQube service blocks its enabled gate. Before any scanner/readback/gate operation, follow the existing [managed-token preflight](../skills/setup-sonarqube/SKILL.md#automatic-renewal-of-expired-managed-tokens); diagnosis alone never authorizes credential changes. Keep healthy tokens unchanged.

## Incident response

1. **Detect and triage:** identify the actual target/candidate, symptoms, impact, timing and known scope. Separate observed facts from hypotheses. Check the handoff's health and functional signals with bounded read-only diagnosis.
2. **Preserve evidence:** retain minimal redacted facts, identities and failure results before changing state. Protect sensitive originals under the owner's access policy; do not paste raw logs, secrets or personal data into the repository/chat. Record evidence gaps honestly.
3. **Contain with authorization:** establish the accountable owner and actual permission for the action/target. Reuse an existing authorization covering it; otherwise prepare the concrete action/recovery implications for a decision. Production changes, credential revocation, stopping shared services and destructive actions require their actual authorization. Stop only evaluation resources owned by the current task under its existing scope. Preserve data/configuration; never use volume deletion, pruning or trust bypass as repair.
4. **Communicate:** prepare a redacted impact/status record and identify the intended recipient/channel. Sending private reports, public issues, email or other outbound messages requires actual authorization; a reporting link is not permission to send. Follow [private vulnerability reporting](../SECURITY.md) for exploit details. Unknown ownership or impact is a gap, not an invented promise.
5. **Recover and verify:** use the target's existing authorized rollback/forward recovery procedure, retain the failed candidate and verify identity, affected functionality and preserved data through the actual interface. Check enabled evaluation gates on the repaired source. A healthy process alone does not prove recovery; missing restore evidence stays unverified.
6. **Follow-up:** record cause only to the degree supported, remaining risks, owner and a scoped regression/prevention check. Feed actionable user corrections into the existing [feedback protocol](../agent-traces/user-feedback/README.md); incident notes alone do not prove recurrence prevented.

### Stopped local service walkthrough

**Tabletop, not an executed outage:** confirm target identity and local engine with the read-only commands above. If SonarQube is stopped, retain failure evidence and block enabled gate completion. With actual authorization for these owned containers, the existing [SonarQube procedure](SONARQUBE.md#configured-local-service) starts the database before the server and preserves named volumes. Do not stop a shared service to manufacture evidence. After an authorized restart, bound health polling, then perform actual scanner/readback functional checks with the preflight and fresh analysis-specific gate. For the optional remote container, reuse [preparation/persistence](REMOTE-CONTAINER.md), then verify login, actual project behavior and session MCP; SSH health alone is insufficient. Data restore remains unverified unless a real protected backup was restored and checked.

### Failed release or revert walkthrough

**Tabletop, not an executed release:** trigger the documented abort signal and preserve both failed/current and prior candidate identities, evidence, configuration and data. Establish actual target/action authorization before rollback or forward recovery; a completed local goal authorizes no production change. Reuse [delivery and recovery](DELIVERY.md), bind preflight to the selected candidate and verify actual target functionality and preserved data afterwards. If a revert fails, stop compounding changes, retain evidence and seek the owner's authorized recovery decision. A local A/B/A candidate rehearsal tests selection/reversal only; published rollback, automatic updates and production data recovery remain unverified. Irreversible data loss cannot be fixed by replacing plugin files; disclose that limit before execution.

### Suspected credential exposure walkthrough

**Tabletop using no secret value:** stop copying the suspected value, preserve redacted location/time/scope evidence privately and triage affected systems with the credential owner. Obtain actual authorization for containment and have the authorized owner promptly revoke/rotate the affected credential. The managed expired-token preflight is not a general exposure-response permission. Do not put a secret in command arguments, public issues or raw logs; history/file removal does not revoke it. Verify old access is rejected and replacement access works through the permitted actual interface without printing credentials, and retain nonsecret results. Prepare a private report under [SECURITY.md](../SECURITY.md); send only with actual outbound authorization. Record scoped follow-up/regression checks and unresolved impact/recovery limits. No actual revocation, private submission or exposure recovery is proven by this walkthrough.

Documentation/contract checks and safe status commands validate these instructions only. They do not prove an actual incident, stopped-service recovery, published rollback or production backup restore; record each executed observation separately from these walkthroughs.
