# Container checkout placement

- Scope: review PR #1 for personal host paths and clarify checkout placement.
- Finding: contributed deployment files derive host paths from the checkout; no personal home or local host-skill path is embedded. Container paths such as `/home/node` and `/work` are intentional image paths.
- Change: document keeping the checkout outside host skill discovery. No runtime code, plugin behavior or Ponytail settings changed. Removed the additional relocation procedure at the user’s request; it is premature for this new deployment.
- Verification: whitespace checks passed. The earlier 24 remote-environment tests passed; this follow-up changes Markdown only.
- Limits: no fresh live deployment or SonarQube analysis. Existing upstream gate and desktop onboarding limitations remain unresolved.
