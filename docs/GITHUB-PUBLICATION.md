# GitHub publication setup

## Access model

The repository remains owned by the personal account [`Chris-1337`](https://github.com/Chris-1337/KISS-Chris-Stack). The owner confirmed that only this account needs admin access; no team, organization transfer, or additional collaborator is required. The collaborator and invitation APIs showed only the owner and no pending invitations on 2026-10-28.

Anyone with a GitHub account can open Issues, participate in Discussions, and submit pull requests from forks in the public repository. They receive no write access to this repository. Community contributions require owner review. [.github/CODEOWNERS](../.github/CODEOWNERS) assigns every path to `@Chris-1337`.

The active [main ruleset](https://github.com/Chris-1337/KISS-Chris-Stack/rules/26040029), defined by [the repository JSON](../.github/main-ruleset.json), targets `refs/heads/main`: one code-owner approval, stale approval dismissal, resolved review threads, and protection against deletion and force pushes for non-bypassing actors. Repository administrators have an `always` bypass and may push directly or merge without a pull request, as requested. With only the owner holding write access, arbitrary community reviews cannot authorize a merge.

## Verified public settings

| Setting | State verified on 2026-10-28 |
| --- | --- |
| Visibility | Public; owner-authorized publication completed |
| Public forks and participation | Forking allowed; interaction restrictions empty |
| Issues and Discussions | Enabled |
| Repository homepage | Updated to the documentation on `main` |
| Dependabot vulnerability alerts | Enabled; check endpoint returned HTTP 204 |
| Actions default token | Read-only; workflows cannot create/approve pull requests |
| Actions fork contributor approval | `all_external_contributors`; outside contributors require approval before their fork workflows run |
| Main branch rules | Ruleset `26040029` active; one code-owner approval, stale review dismissal, resolved threads, deletion/force-push protection; admin role `5` bypasses always |
| Secret scanning and push protection | Both enabled; secret-scanning alerts API returned HTTP 200 and zero alerts |
| Private vulnerability reporting | Enabled; use the private reporting link in [SECURITY.md](../SECURITY.md) |

The authenticated account has repository admin rights and the ruleset reports that this account can bypass it `always`. No replacement token was required. Initial HTTP 403/422/404 failures while private were visibility/plan restrictions; publication made the requested features available, and they were enabled and read back successfully.

Independent verification used an unauthenticated fresh clone with credential helpers disabled at `258aeaaf31376f7dc8ec8b107cff01e1aaa108e4`: all 108 bundled-resource hashes matched, and all 31 repository tests passed in 7.96 seconds. This verifies public availability and the distributed bytes rather than only the original working tree.

## Before publication

1. Review and commit only the intended plugin distribution and community files. The owner authorized publication of the complete audited plugin candidate; commit `10b2614` published the plugin distribution and community files. Commit `258aeaa` preserves original bundled bytes through `.gitattributes`; all 108 manifest hashes match Git blobs. Preserve unrelated changes during any later release.
2. Run a redacted secret scan over **all Git refs and historical content**, then the complete candidate working tree. Include historical binary/document contents when applicable. `.gitignore` prevents accidental inclusion of common local credential and editor files, but does not remove tracked/history content or replace scanning.
3. Review author/committer metadata for private contact details. The owner explicitly authorized replacing the initial commit's employer email with the GitHub noreply address. The replacement commit `cc444824e741a250055f4ae6fb92dbd6c75d5d02` preserves the original tree and was pushed with a lease. GitHub caches, old object URLs, or existing clones may retain the previous commit; this cleans the reachable branch history rather than guaranteeing erasure. Rotate any real exposed credential before remediation.
4. Preserve upstream licenses/notices in [THIRD-PARTY.md](THIRD-PARTY.md). The owner selected [MIT](../LICENSE) for project-original material; upstream terms remain applicable to bundled components.
5. Obtain the owner's explicit publication decision. The owner subsequently authorized the audited full candidate, publication, and activation of the prepared protection settings; execution and verification are recorded below.

The preparation audit used Gitleaks 8.30.1 with a verified release checksum. One reachable commit, the current candidate tree, and extracted historical PowerPoint content were scanned. No actual credential was found; a bundle-manifest SHA256 matched a scanner pattern and was verified against its source file as a false positive. This result covers the audited snapshot, not future commits or every possible confidential value. Repeat the scan on the final staged files and rewritten history before pushing.

## Publication verification procedure

The owner-authorized visibility transition and settings below were performed and read back through the GitHub API. Use this procedure to verify future configuration changes; the table above records the current result. Do not grant write access beyond the approved administrators.

1. Publish the reviewed, scanned content and change visibility only with owner authorization.
2. Verify the active ruleset against [.github/main-ruleset.json](../.github/main-ruleset.json): `enforcement=active`, the `main` target, required code-owner approval, and the administrator bypass. The deployed ruleset ID is `26040029`; do not POST a duplicate ruleset during verification. A configuration file alone does not enforce any rule.
3. Enable secret scanning and secret-scanning push protection through repository `security_and_analysis` settings, then verify both report `enabled`. Check existing secret-scanning alerts as well.
4. PUT `{"approval_policy":"all_external_contributors"}` to `/repos/Chris-1337/KISS-Chris-Stack/actions/permissions/fork-pr-contributor-approval`; verify the returned policy. Keep default workflow permissions `read` and `can_approve_pull_request_reviews=false`.
5. Verify `/repos/Chris-1337/KISS-Chris-Stack/private-vulnerability-reporting` is enabled, and check the private reporting link in [SECURITY.md](../SECURITY.md).
6. Recheck collaborators, pending invitations, rulesets, Issues, Discussions, vulnerability alerts, and Actions permissions. Test the public contribution path without granting an outside account write access.

GitHub push protection detects supported secret patterns. An administrator may still bypass or change settings; the requested administrator freedom cannot guarantee that no secret can ever be pushed. Do not bypass a secret alert without investigating it.

Generic non-provider secret patterns remain disabled after an enable request did not change their effective state. Validity checks and automatic Dependabot update PRs are also disabled; enabled vulnerability alerts do not imply automatic remediation.

## Token permissions if authentication changes

Prefer a fine-grained personal access token restricted to this repository: **Metadata: read**, **Administration: read/write**, **Contents: read/write** for publishing reviewed files, and **Secret scanning alerts: read** for verification. Add **Workflows: read/write** only if publishing workflow-file changes. Issues/Discussions write permissions are needed only to create or modify their content; enabling their repository settings uses Administration. The authenticated account itself must hold repository admin rights.

The current classic credential was sufficient for the settings successfully changed here. Keep tokens in the credential manager, never repository files or command output.

References: [rulesets and plan availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets), [GitHub Actions permissions](https://docs.github.com/en/rest/actions/permissions), [repository settings API](https://docs.github.com/en/rest/repos/repos), and [fine-grained token permissions](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens).
