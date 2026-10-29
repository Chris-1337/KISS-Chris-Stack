# Goal: use the full stack name for evaluation configuration

- Target: use project-root `kiss-chris-stack.config.json` consistently, as requested by the user on 2026-10-29.
- Change: renamed the configuration without changing its bytes; updated the resolver, policy, skills, repository instructions, human documentation and current evaluation trace. Refreshed affected bundled resource hashes. No compatibility alias was added.
- Checks: the separate test agent changed filename expectations first and demonstrated RED (25 failed, 14 passed). Implementation GREEN: all 39 focused tests passed, the actual CLI returned both enabled gates and `git diff --check` passed. No previous-filename references remain in repository source/docs. Independent evaluation and a fresh analysis-specific SonarQube gate are pending.
- Limits: the previous filename is no longer read. Existing project configurations must use the new filename; unrelated prior implementation and historical generated evidence are preserved.
