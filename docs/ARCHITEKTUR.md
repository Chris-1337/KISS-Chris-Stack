# System architecture

KISS-Chris-Stack is a local Codex plugin, not a web application. It has no frontend or backend of its own. The host loads skills/hooks and starts configured MCP services.

| Component | Responsibility and source |
| --- | --- |
| Package and marketplace | [.agents/plugins/marketplace.json](../.agents/plugins/marketplace.json) references this repository through `./`. The native [.codex-plugin/plugin.json](../.codex-plugin/plugin.json) declares skills, hooks, and setup onboarding. Root `plugin.json` contains only the identity to avoid the demonstrated portable hook-loading limitation. |
| Lifecycle | [hooks/hooks.json](../hooks/hooks.json) contains three stack handlers and three original Ponytail handlers. [stack.js](../hooks/stack.js) reads event JSON and injects setup before the original request. SubagentStart is restricted to the existing assigned role. The adapter installs nothing and changes neither workspace nor profile. |
| Workflow | The [orchestrator](../skills/kiss-chris-stack/SKILL.md) activates the [shared policy](../assets/global-stack-policy.md). The root session reads context, clarifies decisions, and registers the goal. Three separate agents write tests, implement, and evaluate independently. |
| Setup | The [setup skill](../skills/setup/SKILL.md) checks/repairs local prerequisites and fills documentation gaps. [setup-runtime.py](../scripts/setup-runtime.py) checks tools, pins, resource hashes, a real UIUX search, global rules, index, and MCP configuration. `--repair` uses pinned downloads and verifies RTK SHA256 before installation. |
| Readiness | The checker reports `runtime_ready`/exit code for executable checks. `ready=false` and `session_verification_required=true` prevent false session guarantees. Only an actual MCP status/context call in this session closes the gate. Missing tools require reload instead of a cached flag. |
| Bundled skills | All skill entrypoints are directly under `skills/`. The Ponytail suite/hooks, Caveman, UIUX code/data, and CodeGraph/RTK guides are included. Sources/licenses/modifications are recorded in [THIRD-PARTY.md](THIRD-PARTY.md); [bundle-manifest.json](../assets/bundle-manifest.json) records resource hashes. |
| Global rules | Setup updates only the stack marker block in global AGENTS.md and an existing AGENTS.override.md. PowerShell/shell marker helpers remain for existing consumers. There is no standalone installer. |
| Verification | [Contract checks](../tests/test_managed_configuration.py) and [lifecycle checks](../tests/test_plugin_lifecycle.py) verify resources, hook JSON, role separation, and negative readiness. Verifiers are thin invocations of the same checker. Actual plugin/hook discovery is additionally checked through Codex. |

Pins are in [versions.json](../assets/versions.json). The CodeGraph npm package and its observed runtime version are reported separately. Do not start parallel MCP processes, approve trust yourself, or overwrite unrelated MCP entries.

Decisions: [ADR 0001](adr/0001-dokumentation-und-agentenrollen.md), [ADR 0002](adr/0002-codex-marketplace-und-lifecycle.md), and [ADR 0003](adr/0003-documentation-language.md). Historical agent traces are retained. Complete installation from scratch on every platform and hook execution after user approval require separate verification.
