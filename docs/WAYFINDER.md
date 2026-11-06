# Wayfinder storage and setup

The Boolean `wayfinder` selects the large-task workflow automatically. The independent `wayfinder-tracker` object says where its maps and tickets are initialized and processed. Project-root `kiss-chris-stack.config.json` is authoritative; generated operations documentation mirrors it and cannot silently select another backend.

Use one supported variant:

```json
{ "wayfinder-tracker": { "provider": "local", "directory": ".scratch" } }
```

```json
{ "wayfinder-tracker": { "provider": "github", "repository": "OWNER/REPO" } }
```

```json
{ "wayfinder-tracker": { "provider": "gitlab", "project": "https://gitlab.example/group/subgroup/project" } }
```

The omitted setting defaults to local `.scratch`; a present object must select a provider. Only local can omit `directory` to use that default. Hosted variants require their explicit target and accept no local directory field, credentials or executable commands. Unknown providers are unsupported rather than freeform tracker adapters. GitHub targets github.com explicitly, overriding inherited host/remotes; GitLab uses the HTTPS URL's explicit host and canonical nested project identity: namespace/path case must match exactly; only URL scheme/host case is normalized, with an explicit port preserved.

Local directories use portable forward-slash project-relative paths, for example `planning/wayfinder`. Absolute/drive/UNC paths, `..`, metadata directories, Windows reserved/aliased names and unsafe components are rejected. Existing path components, document parents and target files cannot be symlinks, junctions or reparse points. GitLab authorities accept safe DNS/localhost/IP host syntax and optional valid numeric ports; credentials, shell metacharacters, whitespace, query and fragment are invalid.

## Prepare and check

First initialization and every explicit `/setup` ask where maps and tickets will be stored: local Markdown, GitHub or GitLab. Setup displays the current provider/location and offers keep/change, then collects or confirms the directory/repository/project. It waits for a real answer before dependent config/tracker/document writes; neither a default nor an existing/backfilled value is an answer. Answers already given in the same setup dialogue are reused. Ordinary per-task readiness checks the validated selection without prompting again; direct helper invocation remains noninteractive.

After config validation/default backfill and runtime/MCP proof, the root assigns the bundled setup worker:

```text
python <plugin-root>/scripts/setup-wayfinder.py --project <project-root> --prepare
python <plugin-root>/scripts/setup-wayfinder.py --project <project-root> --check
```

Default helper invocation is read-only check. Both commands return safe JSON with effective configuration/provider/location, operations-document path and changed paths. The helper prepares the selected local root and managed `docs/agents/issue-tracker.md` from the existing provider template. It creates no effort, map or tickets; these exist only when actual work starts.

For local storage, Wayfinder creates `<directory>/<effort>/map.md` and one child per ticket at `<directory>/<effort>/issues/NN-slug.md`. Tickets retain Type, Status, Blocked by, Claimed by and resolution/evidence. The root claims all ready tickets within capacity, keeps unmet dependencies blocked, and updates the map's named resolution pointers. The helper is setup/check wiring, not an issue CRUD engine.

Identical preparation preserves bytes/mtime. Managed updates preserve surrounding user bytes/newlines and document permissions; unmanaged, malformed or duplicate markers block without overwrite. Selected-target changes reconcile only the owned binding; old ticket roots and history remain intact without migration or deletion. Ordinary reconciliation does not rerun documentation bootstrap, native `/init` or staging. A missing/stale binding blocks Wayfinder until the assigned worker reconciles and checks it.

Before first initialization, `--config-stdin` accepts full pending settings from stdin, validated by the same resolver. Prepare/check the actual chosen target without creating a marker. Only after all runtime/MCP, tracker, documentation and native-init prerequisites succeed does setup exclusively create the marker with those exact settings, then re-read configuration and check without stdin. A present or concurrently appearing conflicting marker blocks; pending defaults cannot replace a chosen backend.

## Hosted prerequisites and limits

Existing native `gh`/`glab` and authenticated target access are required; setup never installs a CLI, logs in, changes credentials or publishes external tickets. Preflights have no stdin, a bounded timeout, explicit host/target and read-only calls. They verify matching target identity, Issues enabled, unarchived state and visible protocol-level access: GitHub TRIAGE+ or GitLab Developer+ from documented project/group permission fields. Lower roles can sometimes create individual issues but do not satisfy the bundled label/claim protocol.

Read-only metadata does not prove every token scope or write operation. External creation, labels, assignments, comments and closure remain separately authorized. Missing CLI/auth/access, disabled Issues, archived or mismatched targets block without local fallback. Unavailable provider access must be reported honestly; command doubles cannot prove live hosted usability.

The [setup skill](../skills/setup/SKILL.md#configured-wayfinder-tracker), [tracker setup](../skills/setup-matt-pocock-skills/SKILL.md), [Wayfinder](../skills/wayfinder/SKILL.md) and [configuration reference](EVALUATION.md) share this contract. Local operational proof should use a disposable project with a custom root and exercise actual map/ticket create/read/claim/block/unblock/resolve operations; do not create fake maps in a user's real project merely to initialize setup.
