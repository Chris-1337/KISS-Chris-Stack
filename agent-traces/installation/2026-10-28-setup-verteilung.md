# Goal contribution: setup distribution

- What: Both installers distribute `setup` as a separate sibling skill and as a resource in the stack package. Both verifiers check that the setup skill exists.
- Why: `/setup` should be explicitly callable and executable by the stack when the documentation foundation is missing.
- Locations: `scripts/install-stack.ps1`, `scripts/install-stack.sh`, `scripts/verify-stack.ps1`, `scripts/verify-stack.sh`.
- Checks: Isolated installer distribution is part of the regression tests written beforehand by the test agent; GREEN: all 10 regression tests passed, including actual skill copies through isolated PowerShell and shell installer functions. Global policy and locally installed skill copies were updated.
- Limit: No complete tool installation from scratch or external publication within this goal. Main note: [workflow](../workflow/2026-10-28-dokumentation-und-tdd.md).
