# Colima support documentation

- Goal: document Colima as a supported macOS Docker runtime for the existing remote-container workflow.
- Source: the user explicitly confirmed in the current chat that the environment works and was tested successfully on a Mac with Colima.
- Change: `docs/REMOTE-CONTAINER.md` now names Colima with the existing Docker CLI and Compose prerequisites and the unchanged preparation command.
- Checks: the test agent's pre-change inline document assertion failed because Colima was absent. After the change, inline content assertions and `git diff --check` passed. No permanent test source or runtime/configuration changes were needed.
- Independent verification: final content, relative links and whitespace checks passed. Fresh SonarQube analysis `a60c6a03-a816-45a7-8c5d-cb475c2d5506` (task `e77b57db-7d2f-4438-bc50-eff1ddc72870`) passed all ten quality-gate conditions, scanner exit 0. Existing genuine coverage was reused only after confirming that all analyzed source, tests and scanner configuration remained unchanged; no broad regression or runtime rerun was needed for this prose-only addition. Evidence is retained under ignored `.sonar-evidence/pr1-colima-docs/`.
- Limits: this records user-confirmed compatibility, not a fresh local Colima run. No Colima version, Mac architecture or additional onboarding/authentication coverage was provided or inferred.
