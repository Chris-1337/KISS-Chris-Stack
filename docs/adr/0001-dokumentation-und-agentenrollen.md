# ADR 0001: Documentation and separate agent roles

- Status: accepted through the user request dated 2026-10-28.
- Context: General rules and stack rules were duplicated. Human documentation and long-term agent context need different locations.
- Decision: Repository AGENTS and the stack skill reference one shared policy, also distributed as a global managed block. `docs/` contains architecture for each real component, business decisions, and technical ADRs. `agent-traces/<component>/` contains brief notes on implemented goals.
- Workflow: Before defining the goal, review both documentation areas plus relevant code and designs, and clarify missing information with the user. `/setup` fills missing documentation foundations before the goal. The root session orchestrates three separate agents for tests, implementation, and independent evaluation, and continues until evidence proves goal fulfillment.
- Consequences: Multiple agents/sessions are required; no silent fallback to one session for all roles. Setup must not invent decisions or project history. Existing documentation is preserved; repeated execution creates no duplicates.
- Source: explicit user request for this change; implemented in the [policy](../../assets/global-stack-policy.md), [stack skill](../../SKILL.md), and [setup skill](../../skills/setup/SKILL.md). No additional historical or economic decisions are evidenced here.
