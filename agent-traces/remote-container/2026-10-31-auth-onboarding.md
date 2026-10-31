# Container authentication onboarding

- Scope: user-assisted graphical onboarding of a fresh AMD64 test container from PR revision `cb9b0c1`; Docker runs AMD64 under emulation on Apple Silicon.
- Baseline: no login cache, six untrusted KISS hooks, no hook errors; separate localhost SSH target and fresh named volumes.
- Finding: the user reported that the standard browser redirect failed again. The profile does not forward the remote callback on port 1455, so the host browser cannot reach that listener through its own localhost.
- Change: make device authentication the initial documented sign-in step, before connecting the desktop project. Preserve the existing network boundary and normal hook trust.
- Authentication evidence: ran the documented container-only `codex login --device-auth`; the user completed the official browser authorization. The command reported success, `codex login status` confirmed ChatGPT sign-in and a fresh SSH App Server returned an authenticated account. No credentials were copied from the host or recorded here.
- Pending: all six KISS hooks still reported untrusted on readback. Desktop reconnection, graphical hook review, trusted hook execution and model-driven `/setup` are awaiting user action. Computer Use refuses access to the Codex application, so the agent cannot perform or observe those UI actions directly.
- Verification: documentation-only changes; relative links and whitespace checked. Runtime source, network settings, tests and quality-gate settings are unchanged. The test service remains running for the pending desktop checks; preserve its named volumes during cleanup.
