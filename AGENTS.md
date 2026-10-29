# KISS-Chris-Stack

Use [the bundled orchestrator](skills/kiss-chris-stack/SKILL.md) and the canonical [global policy](assets/global-stack-policy.md). Keep rules in that shared source.

Project context: [docs/](docs/) for humans and [agent-traces/](agent-traces/) for long-term agent memory. Distribution uses the repository marketplace and native Codex manifest; local runtime setup belongs to the setup skill. Preserve unrelated changes, upstream licenses/provenance, and normal hook trust. No external writes without explicit authorization.

## Configured SonarQube

SonarQube quality-gate enforcement is active for this project. Use [the project scan configuration](sonar-project.properties) and [operations/evidence](docs/SONARQUBE.md). Read credentials only from protected project `.env`; missing credentials or a stopped service do not disable enforcement. Analyze current owned source and require fresh analysis-specific green gates before marking a development goal complete, following the canonical shared policy. The isolated live fixture demonstrates integration only; its result cannot satisfy this repository's gate.
