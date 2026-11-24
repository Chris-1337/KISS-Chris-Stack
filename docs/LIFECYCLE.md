# Lifecycle evidence, compatibility and retirement

The [shared policy](../assets/global-stack-policy.md) owns this contract; existing test, implementation and evaluation roles carry it through goals and Wayfinder tickets. Reuse the project's documentation, receipts and runbooks. This reference adds no service, role, pricing table or configuration switches. Local implementation is separate from authorized delivery, operation and retirement.

## Criterion evidence mapping

Keep a compact acceptance matrix in the existing goal/ticket or evaluation receipt:

| Criterion | Command and asserted check | Result | Current source | Evidence path | Optional release |
| --- | --- | --- | --- | --- | --- |
| Specific required behavior | Exact invocation, exit code and expected output/state, including a relevant negative assertion | passed / failed / disabled/skipped / inapplicable / unknown or unverified, with reason | Revision plus dirty-source fingerprint and inventory used | Sanitized receipt or assertion artifact | Candidate/version/fingerprint, target and actual delivery status, or inapplicable reason |

A successful command or completed model turn with a missing assertion is not behavioral proof. Stale source, cached gates, worker prose and historical traces cannot establish a current pass. Preserve failed observations and distinguish disabled/skipped checks from inapplicable behavior and unknown/unverified observations. Reexecute affected checks after source changes and refresh enabled applicable gates; the root reviews integrated evidence before completion. A revision alone misses dirty/untracked deliverables. Include the actual document owners when a candidate ships operative instructions.

For this plugin, `scripts/test-host-workflows.py` records the runtime/manifest `candidate_fingerprint`, the scenario bytes and the complete `release_candidate_fingerprint`. It reuses the trusted release checker's finite mandatory `RELEASE_EXTRAS` tuple to copy and bind the full artifact after staging, installation and fixture preparation. `scripts/check-release.py --project .` binds that same runtime-plus-release inventory; `--expect-source <fingerprint>` rejects a different candidate. Neither receipt proves authorization, trusted hooks, compatibility or a quality gate. Follow [delivery](DELIVERY.md) to stage exactly the declared inventory using trusted checkout helpers. Keep receipt fingerprint types explicit rather than comparing unlike inventories.

The final integrated acceptance matrix belongs at `.sonar-evidence/sdlc-t4/acceptance-matrix.json`. The following are required checks and evidence destinations, **not predeclared passing results**:

| Criterion | Required executable/contract assertion | Evidence destination and release boundary |
| --- | --- | --- |
| Routing, evidence, security/operations and retirement contracts | Python 3.13 full `pytest tests -q`; lifecycle/host/release negative cases must reject absent assertions, stale identity and missing operative guides | `evaluation-summary.json` under the final directory above; local development, no release |
| Actual supported native host behavior | Separate real workers edit the exact fixture and preserve unrelated bytes; unanswered decision preserves all fixture bytes; independent evaluator checks source identity and outcomes | `native-desktop-observations.json`; supplied instructions do not prove installed hooks |
| CLI/model compatibility | Actual opt-in host runner, exact filesystem assertions and sanitized failure results; retain failed edit observations | Host observation paths linked from the acceptance matrix; failed CLI compatibility never becomes a native-host pass |
| Candidate integrity and recovery rehearsal | Current checker plus `--expect-source`; actual isolated A/B/A installation/reversal with installed-byte and sentinel assertions | `release-final.json`; `published:false`, local rehearsal only |
| Current configured quality gates | Fresh coverage/current-source analysis, completed scanner task and gate `OK` read by that task's analysis ID, after managed-token preflight | `final-scan/sonar-evidence.json`; unexecuted publication remains unverified |

All destinations above are relative to `.sonar-evidence/sdlc-t4/`. The evaluator records exact commands, results, fingerprints, limitations and supporting paths there after source freeze. The committed trace links these ignored local artifacts before scanning to avoid changing scanned source merely to insert its own analysis ID. Missing artifacts remain missing evidence, never a pass. Ignored evidence is retained locally and does not travel with a source-only distribution.

## Compatibility and overhead observations

Distinguish supported interfaces and prerequisites from observed execution on a particular host/runtime/platform/model and from unverified coverage. [Host protocols](HOST-TESTS.md) own the exact procedures and limitations. Plugin setup's baseline Python 3.10+ does not imply that contributor/host/release verification runs on every Python version; these checks use Python 3.13 and CI specifies Node 24. The Windows/Linux CI definition establishes intended jobs, not a successful hosted CI run. Record an actual run identity/result before claiming hosted execution.

| Target or observation | Known boundary |
| --- | --- |
| Windows CLI `0.171.0-alpha.13`, Linux CLI `0.166.0` | Historical authenticated runs failed strict delegated-edit behavior; a persistent-session probe also failed. Keep those results. The runner now isolates desktop provider selectors and binds the exact candidate entrypoint; only fresh current-source CLI receipts can establish its edit/pending-state outcomes. Delegation/model separation remains unverified unless independently exposed. |
| Native desktop collaboration | Separate worker edit/pending-decision protocols can prove exact fixture behavior under supplied current instructions. Final current-source receipts decide their status; earlier successes are historical after source changes. This does not prove installed-plugin CLI editing or automatic hooks. |
| Model and runtime identity | Record requested model and observable host/runtime versions. Server model identity and research/role model dispatch remain unknown unless independently exposed. No automatic model substitution is permitted. |
| Wider compatibility | Fresh-machine graphical onboarding, hook approval/execution, hosted ticket writes and full multi-turn/parallel orchestration remain unverified without their own target-specific evidence. User-confirmed platform operation and local/container execution have different evidence strength. |

Reuse runner fields for `elapsed_seconds`, provided numeric `usage` and `missing_usage`, recording invocation, candidate/scenario fingerprints and target. Missing usage is unknown, not zero; event execution can pass while a later filesystem assertion fails. Elapsed time describes the measured boundary, not the whole project or future latency. Tokens and time are not currency cost. No price, savings or model efficiency claim follows without a comparable measured baseline covering the same task, source, route, model/runtime, verification outcome and measurement boundary. There is no cost service or promised savings.

## Retirement and preservation

Retirement planning and tabletop walkthroughs do not authorize destructive action. Existing roles prepare and independently evaluate a target-specific record: accountable owner/contact or unknown; actual action/target authorization; consumers/integrations; deprecation/migration notice and authorized recipient/channel; retention/access/legal obligations and unknowns; credentials, jobs, hooks and runtime dependencies; protected backup owner/location and restore limits; recovery window and observable abort/success checks. An outbound notice requires actual sending authorization. Irrecoverable data must be disclosed before an explicit decision. Reuse [operations](OPERATIONS.md) and [delivery](DELIVERY.md), without inventing an SLA, cleanup daemon or retention period.

### Plugin-only removal walkthrough

**Tabletop, no removal performed by this ticket.** Identify the selected plugin/profile and consumers first. Inspect that host's supported `plugin remove --help`; use its actual interface only with authorization covering that target. Before action, preserve user project data/history, config, ticket roots, docs/traces and a known retained candidate with its recovery prerequisites. Removing the plugin does not retire downstream applications or revoke credentials.

Remove only the identified plugin through the supported interface. Any separately authorized managed global-policy or MCP cleanup must match its exact owned marker/entry and preserve surrounding content. Do not delete user projects, shared Node/Python/CodeGraph/RTK runtimes, shared caches, credentials, container data/volumes, unrelated MCP entries or global policy blocks. Absence of this plugin is not evidence those resources are unused. Configuration/tracker history remains available for recovery and retention.

The independent evaluator checks plugin absence through the host, byte preservation of unrelated settings and project-data sentinels, and unaffected shared-tool/MCP behavior. Record failed checks and unexpected paths as abort signals. A recovery reinstall uses the retained candidate and normal trust with actual target authorization; verify behavior and preserved state independently. Local rehearsal proves neither published rollback nor production restore.

### Downstream system retirement walkthrough

**Tabletop, no system decommissioned.** Inventory the actual application's consumers, integrations, exposed interfaces and dependencies, accountable owner and explicit decommission authorization. Resolve authorized migration/deprecation notice, data export/retention/access/legal requirements and protected backups before stopping anything. Unknown obligations block dependent irreversible actions; never infer authority from plugin removal or a completed development goal.

The target's runbook identifies an ordered, authorized shutdown of its own jobs, hooks, integrations and services, credential-owner revocation where authorized, and recovery or forward migration within the agreed window. Preserve user data/history and shared resources. Destructive deletion needs its own explicit decision after recovery limits are reviewable. An independent evaluator verifies actual service behavior, consumer migration, access/retention and preservation through the target's real interfaces, retaining redacted evidence. A document walkthrough, healthy process or local plugin reversal cannot prove downstream decommissioning, credential revocation or recoverable production data.
