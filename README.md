# KISS-Chris-Stack

A complete Codex plugin for context-first goals and separate test, implementation, and evaluation agents. It bundles the orchestrator, setup, six Ponytail skills, Caveman, UI-UX-Pro-Max with search code/data, and CodeGraph/RTK guides. See [architecture](docs/ARCHITEKTUR.md), [onboarding](docs/PRODUKT-ONBOARDING.md), and [provenance](docs/THIRD-PARTY.md).

Project-original material is [MIT licensed](LICENSE). Bundled third-party components retain their [own licenses and notices](docs/THIRD-PARTY.md). See [contributing](CONTRIBUTING.md), [security reporting](SECURITY.md), and [publication setup](docs/GITHUB-PUBLICATION.md).

## Install through the repository marketplace

Add the GitHub repository marketplace directly; no manual clone or checkout is required:

```powershell
codex plugin marketplace add https://github.com/Chris-1337/KISS-Chris-Stack.git
codex plugin add kiss-chris-stack@kiss-chris-stack
```

The repository provides the marketplace and plugin files used by these commands.

Alternatively install from the repository marketplace in the Codex desktop Plugins Directory. No separate installer is required. This is a repository marketplace plugin with lifecycle hooks, not a public-directory submission.

Prerequisites: a supported Codex host, Node.js for lifecycle hooks, Python 3.10+ for bundled searches/setup checks. Missing runtimes require local installation and possibly host reload. Run the packaged `/setup` during onboarding and review/trust the hook definition through the normal host UI. Never bypass review.

## What happens on a task

Trusted SessionStart and UserPromptSubmit hooks inject setup/readiness before the original request. Setup checks current tools, bundled resources, global marker-owned policy (plus an existing override), the project CodeGraph index, MCP registration and actual session MCP tool visibility. Missing prerequisites are repaired locally; no cached ready flag substitutes for checks. The original request proceeds through the stack after readiness and context collection.

Sub-agents receive only their assigned role under the same goal. They do not start another setup, goal or recursive agent group. Upstream Ponytail lifecycle hooks run alongside stack hooks.

`docs/` holds human architecture, business decisions and ADRs. `agent-traces/<component>/` holds brief records of implemented goals. Setup fills only evidence-backed gaps and preserves existing documents; empty projects receive only the structure.

The [shared language policy](assets/global-stack-policy.md#language) requires English documentation and internal reasoning; user-facing communication follows the language of the prompt. See [ADR 0003](docs/adr/0003-documentation-language.md).

The independent [evaluation step](skills/evaluate/SKILL.md) proves affected functionality in the running project, started directly or with Docker Compose. Frontend changes require real browser/Playwright interactions and assertions; the agent automatically installs missing CLI/headless Chromium dependencies when needed. Project-root [kiss-chris-stack.config.json](kiss-chris-stack.config.json) independently enables/disables `evaluation.live.enabled` and `evaluation.sonarqube.enabled`. Both default to `true`; SonarQube applies to configured projects. Set a switch to `false` for an explicit reported skip. See [configuration and evidence](docs/EVALUATION.md).

## Verify and repair

After onboarding `/setup`, a usable Linux container engine triggers an optional offer to run [`/setup-sonarqube`](skills/setup-sonarqube/SKILL.md). Docker Desktop, Rancher Desktop (Docker CLI) and Podman are supported through their engine CLI. Without a usable engine, setup explains how to run the skill later and continues. Per-task readiness checks do not repeat the offer. Acceptance provisions local SonarQube, protected project `.env` credentials, actual component analysis and a dedicated gate: zero vulnerabilities, bugs and code smells, and at least 80% overall test coverage. Once configured and enabled in evaluation configuration, every goal requires fresh green gates before completion. See [SonarQube setup and limits](docs/SONARQUBE.md).

Use `/setup` to check or repair local prerequisites. The internal read-only checker is also available:

```powershell
python scripts/setup-runtime.py --project .
```

Exit 0 / `runtime_ready=true` proves executable checks only. `ready` remains false until the setup agent successfully calls the real CodeGraph MCP tool in that session. Missing tools after registration mean reload-required. Exit nonzero identifies a runtime failure. Pins live in [assets/versions.json](assets/versions.json).

Repository checks:

```powershell
uv run --offline --with pytest python -m pytest tests/test_managed_configuration.py tests/test_plugin_lifecycle.py -q
```

## Compatibility and limits

Codex CLI 0.159.0 silently drops hooks from portable-schema root manifests. This package uses native `.codex-plugin/plugin.json` and a minimal root identity, matching the working Ponytail layout. See [ADR 0002](docs/adr/0002-codex-marketplace-und-lifecycle.md). Actual hook discovery must show six plugin hooks before execution is claimed.

Automatic execution requires an enabled/loaded plugin, available Node.js, and user-trusted hooks. MCP configuration does not prove session visibility. Setup never self-approves trust, overwrites conflicting MCP entries, changes credentials or grants external publication permissions. Authorized repair may require network access. Complete fresh-machine installation and execution after user trust remain separate checks.
