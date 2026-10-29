# Optional local SonarQube

The user-requested optional [`/setup-sonarqube`](../skills/setup-sonarqube/SKILL.md) is bundled through the native manifest's existing `./skills/` discovery. Explicit onboarding `/setup` offers it when the read-only [engine probe](../skills/setup-sonarqube/scripts/check-container-runtime.py) finds reachable Linux Docker or Podman. Missing/stopped engines do not block stack readiness. Mandatory per-task checks do not repeat declined offers; an explicit invocation is always available later.

Accepting the offer authorizes local provisioning, login/token setup and project configuration. Discovery does not. Existing instances, data, valid credentials and unrelated `.env` keys are preserved. Credentials live only in protected, untracked and ignored project-root `.env`; documentation records nonsecret keys, resources and commands. Default exposure is loopback only. Durable installations need a supported database; embedded storage is evaluation-only. The skill checks current official image/runtime requirements instead of assuming every Linux engine can run SonarQube.

Actual build components determine Sonar projects and scanners. Java native builds import fresh JaCoCo XML, React/TypeScript imports fresh LCOV from the existing test runner. The default dedicated gate fails overall code for any vulnerability, bug or code smell, or coverage below 80%. Metric support and server mode are verified; ratings and new-code-only checks are not equivalent. Unsupported conditions require a visible decision instead of weaker thresholds.

The [canonical policy](../assets/global-stack-policy.md#sonarqube-quality-gates) requires all configured projects to pass fresh analysis before a goal completes. Evidence ties scanner task and analysis IDs to the current source revision and uncommitted content. Pending/failed tasks, stale results, missing coverage and unavailable services prevent completion. Initial red analysis means provisioning may work while quality readiness remains incomplete; this skill does not silently remediate unrelated legacy debt.

## Configured local service

On 2026-10-29, a separately authorized live run provisioned the project-owned `kiss-stack-sonar` and `kiss-stack-sonar-db` containers. The UI is [local SonarQube](http://127.0.0.1:19000). Port 9000 was occupied, so the new service uses loopback port 19000; existing services were preserved. The private network is `kiss-stack-sonar-net`. Named volumes are `kiss-stack-sonar-db`, `kiss-stack-sonar-data`, `kiss-stack-sonar-extensions` and `kiss-stack-sonar-logs`. Both containers use `unless-stopped` restart policy. Start with `docker start kiss-stack-sonar-db kiss-stack-sonar`; stop with `docker stop kiss-stack-sonar kiss-stack-sonar-db`. Never remove volumes to restart the service.

SonarQube Community Build version `26.2.0.119303` uses image digest `sha256:7da13fa170dea4efb77ae98a9fede25627b668f77824da093a69626a1d4a9776`; PostgreSQL 16 uses `sha256:f1c3376c26f2609ab9f29f71f824103fe2fcd8ee0346485cb6122a4f93df6f94`. The user authorized the temporary Docker Desktop WSL setting `vm.max_map_count=524288`; a VM restart can reset it. The database is private, and HTTP binds only to loopback. Generated admin/database/service-user credentials and separate scanner/reader tokens are stored in the ignored project-root `.env` with owner-only Windows ACL. The initially issued tokens expire on 2026-11-28. The skill now automatically renews confirmed expired managed tokens during the next active scan/read/gate preflight; healthy tokens remain unchanged. No credential values belong in commands, docs or evidence.

Private projects `kiss-chris-stack` and `kiss-stack-live-fixture` share the dedicated `kiss-stack-strict` gate. The installed API accepted overall vulnerabilities, bugs, code smells and accepted issues greater than zero as failures, overall coverage below 80%, and security hotspot review below 100%. Newly created gates also include Sonar's new-code defaults (80% coverage, at most 3% duplication, 100% reviewed hotspots and zero new issues); those defaults were retained. They complement the requested overall-code thresholds rather than replacing them. The reader service user has only project Browse, See Source Code and Execute Analysis grants, with no administration or issue-acceptance privilege.

The [repository analysis configuration](../sonar-project.properties) includes first-party production code in `scripts/`, `skills/setup-sonarqube/scripts/` and `hooks/stack.js`, with `tests/` classified as tests. Bundled upstream Ponytail/UIUX/Caveman resources remain upstream-owned and tracked through provenance; they are outside this first-party scope, selected before the baseline scan. No coverage exclusions hide owned code. Fresh Python coverage goes to ignored `.sonar-evidence/coverage.xml`; JavaScript without a measured report must retain its honest uncovered baseline. The fixture's measured coverage and gate status prove integration separately from repository compliance.

Scanner uploads use `SONAR_TOKEN` (repository) or `SONAR_FIXTURE_TOKEN` (isolated fixture). Readback uses the separate `SONAR_READER_TOKEN` user token through [`read-analysis.py`](../skills/setup-sonarqube/scripts/read-analysis.py). It requests actual issue/measure/source data plus task and analysis-specific gate results. A project analysis token's successful upload does not demonstrate Browse/See Source authorization.

Live authorization evidence on this version: the fixture's confirmed `PROJECT_ANALYSIS_TOKEN` could read its three issues through `/api/issues/search` (HTTP 200), but reading the actual file through `/api/sources/lines` returned HTTP 403. The service user's `SONAR_READER_TOKEN` read both issues and those same ten source lines with HTTP 200. This is why setup verifies each required read endpoint instead of assuming either universal denial or universal access from token type.

Effective-permission review found that the default `sonar-users` group initially inherited global provisioning/scan rights, despite the service user's empty direct global grants. It also inherited project Browse/See Source Code, issue administration and hotspot administration rights through the default template. SonarQube rejected removal from its default group. On this newly created dedicated instance only, the broad default-group global/project/template grants were removed, and the administrator received explicit scan permission to preserve the scoped scanner tokens. The reader's `/api/users/current` now reports an empty global permission list; its intended per-project Browse/See Source Code/Execute Analysis grants remain explicit. It must not accept issues or review hotspots through inherited administration rights. Existing/shared instances must not receive those group-policy changes without separate authorization.

The isolated fixture completed a real RED-to-GREEN cycle: initial analysis `366d7c13-d0b4-4646-8a1c-176a16db4680` reported one bug and two code smells at 100% measured coverage. Removing the unused calculation/identical branches exposed a further unused-parameter smell; naming the intentionally unused parameter `_enabled` preserved all six positional test cases without suppression. Final task `bf160b18-229b-4e05-a684-8029a1961b3d` produced analysis `75e89893-1900-449d-8dae-21552b8c59df`, scanner exit 0 and gate `OK`: zero bugs, vulnerabilities, code smells and accepted issues, 100% coverage, zero duplication, with no ignored gate conditions. Original RED and final GREEN evidence remain separate. This validates integration, not the repository's independent quality result.

## Verified repository result

The actual first-party repository scan also passed on 2026-10-29. Task `5472a789-ef8b-4b30-9de3-b96bd5f385e4` produced analysis `f38178b8-b515-48e5-a7e3-874a75c94db7`, scanner exit 0 and quality gate `OK`. All ten conditions passed, with no ignored conditions: overall coverage 96.5%, new-code coverage 96.6%, zero bugs, vulnerabilities, code smells and accepted issues, 100% reviewed security hotspots, and zero duplication. The independently rerun suite passed 107 tests; measured Python line/branch coverage was 96%, and actual Node hook coverage was 100%. This result applies to the documented first-party source scope, not the separately bundled upstream code.

Security hotspot `8c7f46cd-481c-48cc-96e3-f7c52c7c2a3a` was independently reviewed and explicitly marked `SAFE` by the authorized administrator, with the concrete archive safeguards recorded in its review comment. The implementation now bounds compressed downloads, expanded data including TAR metadata, archive member counts and the one regular executable; checksum validation precedes parsing, and failure preserves an existing installation. This was an actual reviewed server status, not an issue suppression or an automation-reader permission bypass.

The actual `read-analysis.py` CLI exited 0 and retrieved findings, measures, task/gate evidence and 100 source lines using the reader token. Ignored `.sonar-evidence/repo-evidence.json` stores the final summary; `.sonar-evidence/source-fingerprint.json` verifies all analyzed source, tests and configuration still match the uploaded snapshot. Original RED baseline evidence is preserved separately as `.sonar-evidence/repo-baseline-evidence.json`. These local generated artifacts are not committed. Changes to analyzed source or configuration require another fresh scan.

After restricting inherited groups, the administrator also needed explicit project Browse and See Source Code grants on both owned projects. Its human login was verified against component, actual source and hotspot-search APIs (HTTP 200). Hotspot review uses a separate explicit administrator project permission; the automation reader has no such grant.

## Repeat verification

Two non-destructive discovery/authentication passes reused the existing containers, projects, administrator/service-user passwords and all three tokens. Container IDs/images, database component row counts and protected `.env` bytes were unchanged. Reruns must validate these existing resources rather than rerunning unconditional create/password/token commands.

Before each upload, readback or goal gate check, the agent runs the [automatic renewal preflight](../skills/setup-sonarqube/SKILL.md#automatic-renewal-of-expired-managed-tokens). It confirms expiry using token-owner metadata, then renews only a known managed token with the same owner/type/project and finite lifetime. Protected `.env` management metadata, the shared exclusive `.sonar-evidence/token-refresh.lock`, atomic ACL-preserving persistence and child-environment reload keep concurrent agents consistent. Only after the replacement is persisted and its single intended operation succeeds is the old token revoked; there is no trial scanner upload. There is one bounded retry; 401/403, revocation and permission errors alone do not trigger rotation. Successful renewal needs no notification or renewed confirmation; actual failures remain visible and block the gate. No idle daemon is installed, and the raw scanner/read helper below does not perform renewal itself.

The current installation's three healthy token slots have been enrolled using verified live owner/type/project/name/expiry metadata. Fifteen nonsecret management keys were appended under that lock with owner-only staging ACL copied before writing, a concurrent-change check and atomic replacement. All original token/password values, unrelated bytes and comments were preserved; no healthy token was regenerated or revoked.

After the renewal instruction update, a separate verification passed 109 tests and fresh analysis `a9430ac6-73f5-4201-b7b7-279deddb6f11` (task `c835ed8b-8817-4f86-914d-c061b93a3806`, scanner exit 0). All ten gate conditions passed without ignored conditions: 96.5% overall and 96.6% new-code coverage, zero bugs/vulnerabilities/code smells/accepted issues and 100% reviewed hotspots. `.sonar-evidence/renewal-source-fingerprint.json` confirms all nine analyzed files match; `.sonar-evidence/renewal-evidence.json` preserves this result separately from the earlier 107-test verification. Independent healthy-token preflight reused all three tokens unchanged. No token was forced to expire, so an actual expired-token replacement/revocation cycle remains untested.

For this repository, regenerate genuine Python and Node coverage from its tests before a fresh scan. These PowerShell commands use a unique ignored V8 directory so old source coverage is not merged accidentally:

```powershell
$sonarV8 = Join-Path (Get-Location) ('.sonar-evidence/v8-' + [guid]::NewGuid().ToString('N'))
$env:NODE_V8_COVERAGE = $sonarV8
uv run --offline --python 3.13 --with pytest --with pytest-cov python -m pytest tests -q --cov=scripts --cov=skills/setup-sonarqube/scripts --cov-branch --cov-report=term --cov-report=xml:.sonar-evidence/coverage.xml
if ($LASTEXITCODE) { throw 'Tests or coverage failed' }
npm exec --yes --package=c8@12.0.0 -- c8 report --all --include=hooks/stack.js --temp-directory=$sonarV8 --reporter=lcov --reporter=text --reports-dir=.sonar-evidence/js
if ($LASTEXITCODE) { throw 'Node coverage reporting failed' }
Remove-Item Env:NODE_V8_COVERAGE
```

After the agent has completed that renewal preflight, select the installed SonarScanner executable (the live verification used official Windows CLI 8.1.0.6389). This low-level command parses only the generated unquoted dotenv entries as data, passes secrets through the child environment, and never prints them or sources shell code. It does not renew expired tokens on its own:

```powershell
$env:SONAR_SCANNER = Read-Host 'Path to installed sonar-scanner executable'
@'
import os
import subprocess
from pathlib import Path

environment = os.environ.copy()
for line in Path('.env').read_text(encoding='utf-8').splitlines():
    key, separator, value = line.partition('=')
    if separator and key in {'SONAR_HOST_URL', 'SONAR_TOKEN', 'SONAR_READER_TOKEN'}:
        environment[key] = value
subprocess.run([environment['SONAR_SCANNER']], env=environment, check=True)
'@ | python
```

The committed scan properties wait for the gate and fail the scanner when it is red. Preserve `.scannerwork/report-task.txt`; resolve its task to the successful analysis ID, discover a real source key, and invoke `read-analysis.py --project kiss-chris-stack --task-id <task> --analysis-id <analysis> --source-key <file-key>` under the same protected environment. The [skill](../skills/setup-sonarqube/SKILL.md#prove-setup-and-enforce-completion) gives the bounded polling and exact API steps. Authentication, upload and findings/source readback are separate checks. A stopped service blocks configured gate completion until restored; do not delete the project instruction to bypass it.

Official operational references: [Docker installation](https://docs.sonarsource.com/sonarqube-community-build/server-installation/from-docker-image/installation-overview), [Web API](https://docs.sonarsource.com/sonarqube-server/extension-guide/web-api), [tokens](https://docs.sonarsource.com/sonarqube-server/user-guide/managing-tokens), [quality gates](https://docs.sonarsource.com/sonarqube-community-build/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates), and [scanner analysis parameters](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/analysis-parameters/parameters-not-settable-in-ui). The running server's API remains authoritative for its installed version.
