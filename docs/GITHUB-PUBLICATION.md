# GitHub publication setup

## Access model

The repository remains owned by the personal account [`Chris-1337`](https://github.com/Chris-1337/KISS-Chris-Stack). The owner confirmed that only this account needs admin access; no team, organization transfer, or additional collaborator is required. The collaborator and invitation APIs showed only the owner and no pending invitations on 2026-10-28.

Once public, anyone with a GitHub account can open Issues, participate in Discussions, and submit pull requests from forks. They receive no write access to this repository. Community contributions require owner review. [.github/CODEOWNERS](../.github/CODEOWNERS) assigns every path to `@Chris-1337`.

The prepared [main ruleset](../.github/main-ruleset.json) targets `refs/heads/main`: one code-owner approval, stale approval dismissal, resolved review threads, and protection against deletion and force pushes for non-bypassing actors. Repository administrators have an `always` bypass and may push directly or merge without a pull request, as requested. With only the owner holding write access, arbitrary community reviews cannot authorize a merge.

## Verified settings and current limits

| Setting | State verified on 2026-10-28 |
| --- | --- |
| Visibility | Private; publication has not been performed |
| Issues and Discussions | Enabled |
| Repository homepage | Updated to the documentation on `main` |
| Dependabot vulnerability alerts | Enabled; check endpoint returned HTTP 204 |
| Actions default token | Read-only; workflows cannot create/approve pull requests |
| Actions fork contributor approval | HTTP 422: unavailable for this private repository; configure `all_external_contributors` after publication |
| Main branch rules/protection | HTTP 403: upgrade to GitHub Pro or make the repository public; prepared ruleset is not active |
| Secret scanning and push protection | Enable request returned HTTP 422: secret scanning is unavailable for this repository while private |
| Private vulnerability reporting | Enable request returned HTTP 404 while private; the security reporting link is not yet an active channel |

The authenticated account has repository admin rights. The observed failures are repository visibility/plan restrictions, not evidence that a replacement token is required. A token cannot unlock unsupported plan features.

## Before publication

1. Review and commit only the intended plugin distribution and community files. Preserve unrelated changes. The remote initialization commit does not yet provide the local marketplace/plugin package.
2. Run a redacted secret scan over **all Git refs and historical content**, then the complete candidate working tree. Include historical binary/document contents when applicable. `.gitignore` prevents accidental inclusion of common local credential and editor files, but does not remove tracked/history content or replace scanning.
3. Review author/committer metadata for private contact details. The owner explicitly authorized replacing the initial commit's employer email with the GitHub noreply address. The replacement commit `cc444824e741a250055f4ae6fb92dbd6c75d5d02` preserves the original tree and was pushed with a lease. GitHub caches, old object URLs, or existing clones may retain the previous commit; this cleans the reachable branch history rather than guaranteeing erasure. Rotate any real exposed credential before remediation.
4. Preserve upstream licenses/notices in [THIRD-PARTY.md](THIRD-PARTY.md). The owner selected [MIT](../LICENSE) for project-original material; upstream terms remain applicable to bundled components.
5. Obtain the owner's explicit publication decision. The preparation request does not itself change visibility.

The preparation audit used Gitleaks 8.30.1 with a verified release checksum. One reachable commit, the current candidate tree, and extracted historical PowerPoint content were scanned. No actual credential was found; a bundle-manifest SHA256 matched a scanner pattern and was verified against its source file as a false positive. This result covers the audited snapshot, not future commits or every possible confidential value. Repeat the scan on the final staged files and rewritten history before pushing.

## At publication

The visibility transition and the following settings must be performed together, then independently read back through the GitHub API. Until the ruleset is active, do not grant any other account write access.

1. Publish the reviewed, scanned content and change visibility only with owner authorization.
2. POST the exact JSON from [.github/main-ruleset.json](../.github/main-ruleset.json) to `/repos/Chris-1337/KISS-Chris-Stack/rulesets`; verify `enforcement=active`, the `main` target, required code-owner approval, and the administrator bypass. A prepared file alone does not enforce any rule.
3. Enable secret scanning and secret-scanning push protection through repository `security_and_analysis` settings, then verify both report `enabled`. Check existing secret-scanning alerts as well.
4. PUT `{"approval_policy":"all_external_contributors"}` to `/repos/Chris-1337/KISS-Chris-Stack/actions/permissions/fork-pr-contributor-approval`; verify the returned policy. Keep default workflow permissions `read` and `can_approve_pull_request_reviews=false`.
5. Enable `/repos/Chris-1337/KISS-Chris-Stack/private-vulnerability-reporting`, verify it is enabled, and check the private reporting link in [SECURITY.md](../SECURITY.md).
6. Recheck collaborators, pending invitations, rulesets, Issues, Discussions, vulnerability alerts, and Actions permissions. Test the public contribution path without granting an outside account write access.

GitHub push protection detects supported secret patterns. An administrator may still bypass or change settings; the requested administrator freedom cannot guarantee that no secret can ever be pushed. Do not bypass a secret alert without investigating it.

## Token permissions if authentication changes

Prefer a fine-grained personal access token restricted to this repository: **Metadata: read**, **Administration: read/write**, **Contents: read/write** for publishing reviewed files, and **Secret scanning alerts: read** for verification. Add **Workflows: read/write** only if publishing workflow-file changes. Issues/Discussions write permissions are needed only to create or modify their content; enabling their repository settings uses Administration. The authenticated account itself must hold repository admin rights.

The current classic credential was sufficient for the settings successfully changed here. Keep tokens in the credential manager, never repository files or command output.

References: [rulesets and plan availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets), [GitHub Actions permissions](https://docs.github.com/en/rest/actions/permissions), [repository settings API](https://docs.github.com/en/rest/repos/repos), and [fine-grained token permissions](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens).
