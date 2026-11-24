# Changelog release convention

- Date and context: 2026-11-24, review of the conceptual changelog covering the complete Git history and current branch.
- Scope: this repository's changelog and release terminology.
- Observed and requested behavior: the draft placed current branch changes under an `Unreleased` heading with a branch-specific pending paragraph. The user requested regular dated entries instead and clarified that merging into `main` constitutes a release.
- Prevention action: group entries by development date, include current branch changes in the regular log, and state the release-on-merge convention without implying that an unmerged branch has already merged. Do not introduce an `Unreleased` section for this convention.
- Verification: focused assertions passed for the dated heading, stated release convention and absence of the old heading and branch paragraph. The edit preserved all 34 conceptual bullets; UTF-8/LF, local-link and whitespace checks passed, including `git diff --check` and checks of both new files. Runtime tests do not apply to this documentation correction; no merge or release was performed.
- History: 2026-11-24, this correction supersedes the draft's separate pending-release treatment; it grants no merge, publication or other external-write authorization.
