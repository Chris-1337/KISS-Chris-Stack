# Goal: documentation and separate TDD roles

- What: One shared policy replaces duplicated workflow rules. Repository AGENTS and the stack skill reference it; global Codex AGENTS receives the same managed block. Before goals, documentation, traces, relevant code, and designs are read, and open decisions clarified with the user.
- Why: User request dated 2026-10-28: shorter, consistent rules, human documentation separate from agent memory, and independent roles for tests/implementation/evaluation.
- Locations: `assets/global-stack-policy.md`, `AGENTS.md`, `SKILL.md`, `skills/setup/`, `docs/ARCHITEKTUR.md`, `docs/adr/0001-dokumentation-und-agentenrollen.md`.
- Roles: The test agent creates contract checks first; the implementation agent implements; independent evaluation follows through a third agent. Sub-agents start no new goals or groups of three.
- Checks: Before implementation, the test agent reported 6 failed and 4 passed regression tests (RED). Implementation check: 10 regression tests passed; PowerShell configuration test passed; both skills validated through quick_validate.py; installer/verifier syntax and git diff --check without findings. Independent evaluation takes place separately.
- Limit: Implicit skill activation depends on the agent host; newly installed skills/rules load fully after restart.
