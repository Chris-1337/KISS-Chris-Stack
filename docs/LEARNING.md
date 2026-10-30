# Learning from project feedback

KISS-Chris-Stack retains actionable user feedback as project memory in [`agent-traces/user-feedback/`](../agent-traces/user-feedback/README.md). The active agent records lessons and applies them to later work. This includes corrections and negative feedback, plus positive feedback that explicitly identifies behavior to preserve. Routine acknowledgements need no record.

## From feedback to a check

1. Record actionable feedback promptly, before returning to dependent work. Follow the [feedback protocol](../agent-traces/user-feedback/README.md): date/context, scope, observed/requested behavior, concrete prevention action, verification and history. Use one `YYYY-MM-DD-topic.md` record per distinct lesson and write it in English. Distinguish a new requirement from a reported failure; do not invent failure history.
2. Before defining a future goal, the root reads relevant records alongside documentation, traces and affected code. Apply only lessons within their stated scope and turn prevention actions into acceptance checks. Current user instructions and project rules take precedence; clarify actual conflicts before dependent work.
3. Give the applicable feedback and checks to the separate test, implementation and evaluation roles. The test agent specifies the expected behavior, the implementation agent preserves it, and the evaluation agent independently checks the result under the same goal.
4. Update verification with the actual check, result and remaining limits. Keep unproven behavior marked pending/unverified. Recording a lesson or passing an instruction contract does not prove that future mistakes have been prevented.

For repeated feedback, update the existing record instead of creating duplicates. Preserve dated history when a correction supersedes an earlier instruction, and identify which instruction is current.

## Example

The following is an illustrative record, not actual user feedback or a claim that these checks ran:

```markdown
# Preserve explicitly disabled evaluation gates

- Date and context: YYYY-MM-DD, feedback during a configuration update.
- Scope: default backfill in this project's configuration resolver.
- Observed and requested behavior: the user requires an explicit false value
  to remain false when missing settings are added; no prior failure is asserted.
- Prevention action: include preservation of explicit false values in the
  next configuration goal's acceptance checks and all three role handoffs.
- Verification: pending/unverified; run the resolver on a disposable project
  with one disabled gate and check both the preserved value and added defaults.
- History: initial requirement; append dated repeats and later corrections here.
```

A later goal touching the resolver would carry that preservation check to all three roles. After execution, the record should cite the actual command/result and any limits rather than infer success from this example. The [existing configuration tests](../tests/test_evaluation_configuration.py) show how explicit-value preservation can be checked.

## Setup and boundaries

First-time setup and explicit `/setup` create only the missing generic feedback protocol and structure, including in empty projects. They preserve existing records and their README, invent no feedback and copy no other project's lessons. Ordinary tasks in an initialized project run current readiness checks without reinitializing documentation; missing feedback structure can still be created when recording actual feedback. See [setup](../skills/setup/SKILL.md).

There is no learning switch in [`kiss-chris-stack.config.json`](EVALUATION.md). This workflow does not train the model, install a background recorder or guarantee that future agents will avoid every repeated mistake. Its effect depends on active agents reading, applying and verifying relevant lessons. Store no secrets, unnecessary personal information, raw logs or chat transcripts. Project feedback grants no additional permissions or external-write authorization and does not establish global preferences or authorize changes to unrelated projects.

The [shared policy](../assets/global-stack-policy.md) is authoritative; the [orchestrator](../skills/kiss-chris-stack/SKILL.md) carries the recording, pre-goal review and role handoff requirements. [Architecture](ARCHITEKTUR.md) places this memory alongside documentation and goal traces.
