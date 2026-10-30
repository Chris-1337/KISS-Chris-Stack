# Portable container checkout

- Scope: review PR #1 for personal host paths and clarify checkout placement and relocation.
- Finding: contributed deployment files derive host paths from the checkout; no personal home or local host-skill path is embedded. Container paths such as `/home/node` and `/work` are intentional image paths.
- Change: document keeping the checkout outside host skill discovery, moving the complete checkout with `.runtime`, preserving Compose project/port settings, regenerating the SSH fragment and replacing the existing SSH alias block. No runtime code, plugin behavior or Ponytail settings changed.
- Verification: all 24 existing remote-environment tests passed with temporary pytest dependencies; whitespace checks passed. These are documentation and existing contract checks, not a fresh live relocation test of this contribution.
- Limits: no fresh SonarQube analysis was performed for these Markdown-only changes outside configured source/test paths. The upstream gate and interactive desktop onboarding limitations recorded in the original contribution remain unresolved.
