---
name: setup-matt-pocock-skills
description: Configure the stack's local, GitHub or GitLab Wayfinder target and prepare its managed operations document without publishing tickets or changing credentials.
---

# Configure Wayfinder storage

Follow the [shared policy](../../assets/global-stack-policy.md) and [setup lifecycle](../setup/SKILL.md#configured-wayfinder-tracker). The active root delegates substantive setup to an appropriate setup worker. All pure fact collection goes exclusively to fresh GPT-6 Luna low agents with no inherited context, factual notes only and no implementation/design decisions. Do not register another goal or initiate recursive setup.

## Authoritative choice

Project-root `kiss-chris-stack.config.json` is authoritative. The Boolean `wayfinder` controls automatic workflow selection; the separate `wayfinder-tracker` chooses where maps/tickets are initialized and processed:

- Local, default: `{ "provider": "local", "directory": ".scratch" }`. A custom safe project-relative directory is supported.
- GitHub.com: `{ "provider": "github", "repository": "OWNER/REPO" }`. The host is explicitly github.com; inherited GH_HOST/remotes cannot redirect it.
- GitLab: `{ "provider": "gitlab", "project": "https://HOST/GROUP/PROJECT" }`, including nested groups and explicit self-hosted HTTPS targets.

For first-time initialization, every explicit `/setup` and an explicit invocation of this tracker setup skill, the root must ask for the storage choice among local Markdown, GitHub and GitLab. Display the current provider/location when configured and offer keep/change, then collect or confirm its directory or hosted target. Wait for an actual user answer before dependent configuration, tracker or documentation writes; an existing/backfilled setting, recommended default, preselection or silence is not consent. Retain explicit answers in the same setup dialogue without asking again or adding a closing confirmation, including internal tracker setup calls after the main setup answer. Ordinary per-task readiness reuses validated configuration without another prompt. Follow the [required setup choice gate](../setup/SKILL.md#required-storage-choice) before preparation.

Preserve the answered choice and use local only as the resolver's omitted-setting default, never as an automatic setup answer. Do not recommend GitHub merely from a remote. Unknown providers, including freeform other trackers, need separate adapter/config implementation rather than silently accepted prose.

No credentials, tokens, shell commands or per-user identity belong in configuration. Existing configured projects update only the requested tracker fields while preserving workflow/evaluation values, then validate through bundled `scripts/evaluation-config.py`. For a first initialization, retain full validated pending settings in memory without creating the marker yet.

## Prepare and verify

Use bundled `scripts/setup-wayfinder.py --project <project-root> --prepare`, followed by `--check`. Default invocation is also read-only check. The helper renders the selected existing [local](issue-tracker-local.md), [GitHub](issue-tracker-github.md) or [GitLab](issue-tracker-gitlab.md) template into `docs/agents/issue-tracker.md`, binding actual map/ticket paths or every operative command to the configured target. It prepares a local root only, with no fake map/effort/tickets. It preserves old data on provider changes and never treats tracker artifacts as disposable.

Before first marker creation, supply the full selected pending settings through helper `--config-stdin` on stdin for prepare/check. After all setup prerequisites, write exactly those settings as the final exclusive marker and recheck without stdin. An existing/concurrent conflicting marker blocks; never overwrite or prepare a different target silently.

The operations document has a single owned `kiss-chris-stack:wayfinder-tracker` block. Identical preparation changes no bytes/mtime; updates preserve surrounding user bytes/newlines and existing permissions. Unmanaged/malformed/duplicate blocks, unsafe paths, symlink/junction/reparse escapes or concurrent document changes block without overwrite. Report the concrete conflict instead of copying unrelated content over it. Routine tracker reconciliation does not run docs bootstrap, native init or broad staging.

Hosted preflights require existing native `gh` or `glab`, explicit host/target, matching authenticated metadata, Issues enabled and an unarchived target. The bundled claim/label workflow requires GitHub TRIAGE+ or GitLab Developer+ visible access; lower roles may create an individual issue but do not satisfy this setup. Read-only metadata does not prove token scope for every write. Missing CLI/auth/access blocks without automatic install/login, credential edits or local fallback. No setup command publishes issues, labels, claims, comments, branches or repository changes; external writes need separate authorization.

Report the effective provider/location, operations document, changed paths and executable check results, with remote-write proof limits. The [Wayfinder](../wayfinder/SKILL.md) role re-reads this same config and requires the binding before map operations.

## Optional domain and triage documentation

When explicitly relevant, preserve existing glossary/ADR layout using [domain rules](domain.md), [domain-modeling](../domain-modeling/SKILL.md) and its formats. If a separately installed triage skill is actually used, [triage-labels.md](triage-labels.md) is available as a seed; it does not authorize external label creation or add another provider. Do not rewrite AGENTS.md/CLAUDE.md or perform Git initialization/remote changes merely to configure this tracker.

Adapted from Matt Pocock's [setup-matt-pocock-skills](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/setup-matt-pocock-skills/SKILL.md), commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, under [MIT](../../licenses/mattpocock-skills-LICENSE). Stack adaptations: authoritative strict provider/location config, local default, deterministic managed setup/check, first-init config-last selection, universal Luna-low factual collection, delegated setup, explicit host/target and unchanged external-write permissions.
