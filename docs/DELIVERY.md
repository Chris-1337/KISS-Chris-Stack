# Delivery and recovery

Use the [shared contract](../assets/global-stack-policy.md#delivery-and-recovery) through the existing orchestrator and evaluator. Record delivery applicability for each goal. Local implementation-only work needs a brief inapplicable reason. For an actual release, record the target/environment, immutable candidate/source, configuration and compatibility prerequisites, owner/authorization, preflight evidence, success/abort signals, preserved data, rollback or forward recovery and post-release verification. Keep this proportional to the change.

Development completion and local readiness do not authorize publishing, pushing, deploying or changing an external service. Prepare a reviewable candidate and recovery plan before requesting missing authorization. Existing explicit authorization for the same action/target remains valid. Obtain an explicit decision for user-impacting irreversible steps, including any data that recovery cannot restore.

## Check this repository's candidate

Run the existing full suite and enabled evaluation gates against the final source, then:

```powershell
uv run --python 3.13 python scripts/check-release.py --project .
uv run --python 3.13 python scripts/check-release.py --project . --expect-source <previous-fingerprint>
```

The command is read-only and uses only the standard library, local files and Git. JSON reports `status`, `candidate` name/version, `source` revision/fingerprint and `published:false`; failure returns nonzero with nonsecret diagnostics. Native `.codex-plugin/plugin.json` owns the version. Root and marketplace versions may be absent; any present version must match. The marketplace must select this local candidate, native resource references must stay inside it, bundle SHA256 entries must match, and license/provenance resources must remain present. No candidate Python is executed: helper code comes from the trusted checker's own checkout.

The fingerprint combines the existing host runner's complete runtime/metadata inventory with exact bytes of the 26 mandatory public-source resources in the checker's authoritative `RELEASE_EXTRAS` tuple. These include the README/contributor/project instructions, operative SDLC/setup/recovery guides and their four architecture decisions, CI/scanner configuration, licenses/security and publication prerequisites. Missing or empty required resources fail readiness; modifying them changes the receipt. The inventory is finite, not a recursive Markdown-link crawler. It includes untracked deliverable scripts and excludes credentials, interpreter caches, `.git`, scratch and evaluation outputs, project workflow configuration and generated tracker binding. A Git revision alone cannot identify dirty/untracked source. A source-only directory without its own Git repository reports a null revision; retain its originating revision and fingerprint in the release record. This is a mechanical integrity receipt, not a signature, secret scan, compatibility certification, quality-gate result or publication authorization. Do not treat excluded outputs as part of the candidate.

## Prepare a source-only local candidate

Never point native local marketplace installation at the raw working tree: the host may copy ignored files including `.env`. Use Python 3.13 and the trusted owning checkout's `scripts/check-release.py` module, not candidate Python. In a fresh disposable destination, reuse its `host_helpers().copy_candidate(source, destination)`, then loop over that module's `RELEASE_EXTRAS`: obtain each file with `resource(source.resolve(), relative)`, create its destination parent and copy the exact bytes with `shutil.copy2`. This uses one authoritative inventory for checking and staging rather than a second hand-maintained list. It retains operative guides and prerequisites without credentials, auth, normal profile data or caches. Preserve relative paths. Run the owning checkout's `check-release.py --project <stage>` and bind its fingerprint with `--expect-source` before selecting that stage. Preserve upstream license/notice files and review final staged content for secrets.

For a prior candidate, use a known retained source-only artifact or extract the reviewed tracked commit with `git archive` into a fresh disposable location, then curate it through the same helper and authoritative release-resource loop. Audit the selected commit first; archive excludes untracked files but does not remove secrets committed to history. If that commit predates required release resources, retain it as historical source rather than claiming it passes current readiness. Use a complete retained unshipped candidate checkpoint for a rehearsal under the current contract. Keep prior and new candidates separately, without rewriting their versions merely for an unshipped rehearsal. Record both fingerprints and originating revisions.

## Rehearse selection and reversal locally

Use the actual host CLI's `plugin add/remove --help` before running it; this is a local repository marketplace, not a remote release/version registry. Use an empty disposable `CODEX_HOME` and a disposable project directory. Do not copy the normal profile/authentication, change trust or run a model. Set only the local marketplace source in invocation-scoped CLI overrides:

```text
codex -c marketplaces.kiss-chris-stack.source_type="local" -c marketplaces.kiss-chris-stack.source="<source-only-stage>" plugin add kiss-chris-stack@kiss-chris-stack --json
codex -c marketplaces.kiss-chris-stack.source_type="local" -c marketplaces.kiss-chris-stack.source="<source-only-stage>" plugin remove kiss-chris-stack@kiss-chris-stack --json
```

Pass overrides as separate arguments and quote string values for TOML using the host shell or a subprocess argument array. The CLI writes only to the isolated profile/cache. Install retained candidate A, independently assert installed bytes, remove it through the supported interface, select/install candidate B and assert its bytes, then remove B and reinstall A. Explicit removal prevents same-version cache reuse; this procedure tests selection/reversal, not automatic upgrade semantics. Preserve both source stages throughout. Check installed runtime fingerprint plus the exact bytes of every `RELEASE_EXTRAS` resource, including guide/prerequisite preservation, rather than trusting command success alone. Recheck the release fingerprint on each source stage after the exercise.

Place known configuration and project-data sentinels outside the managed plugin cache before starting; assert their exact bytes and unrelated profile settings after every transition. A successful rehearsal requires A/B/A installed-content matches, unchanged retained candidates/configuration/data and no credentials in the stages/cache. Abort on a failed command, identity mismatch, changed sentinel or unexpected path. Stop only owned processes; remove only disposable resources created for this exercise. Retain concise nonsecret command/assertion evidence and source identities.

## Authorized delivery and post-release checks

Use [publication guidance](GITHUB-PUBLICATION.md) for the separately authorized repository publication, final candidate/history secret review, licenses and protection readback. Recheck source identity immediately before executing the authorized action. Preserve the previous usable candidate and the target's required configuration/data backups first; ensure the accountable owner can execute the recovery procedure. Define observable success/abort signals and a bounded verification window before delivery.

After authorized release, verify the actual target identity and user-relevant behavior, compatibility and applicable configuration/data preservation. If abort signals occur, stop and execute the authorized rollback or forward recovery, then verify the resulting behavior and preserved data. Irreversible data/schema changes require their own decision and recovery proof; restoring plugin files cannot restore production data. Report implementation completion, release execution and post-release verification separately.

The local rehearsal does not prove a published marketplace rollback, production installation, automatic host update, remote protection state or production data recovery. Those remain unverified until separately authorized actions and observed target-specific checks provide evidence. Historical publication evidence is dated evidence, not current release verification.
