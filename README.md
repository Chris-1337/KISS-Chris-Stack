# KISS-Chris-Stack Installer

KISS-Chris-Stack is ready to zip and share. It installs and activates Ouroboros, CodeGraph, UI-UX-Pro-Max, Ponytail, Caveman, RTK, the `kiss-chris-stack` skill, global agent instructions, and MCP startup integration.

Product overview, architecture, operation, onboarding, release status, and limitations are documented in the [product onboarding guide](docs/PRODUKT-ONBOARDING.md).

## Requirements

- Git
- Node.js with `npm` and `npx`
- Python 3 available as `python`, `python3`, or `py` for the UI-UX-Pro-Max search scripts
- At least one supported agent CLI. Codex and Claude Code receive native plugin and global-instruction integration; compatible fallback hosts receive their supported Ouroboros and skill integration.
- Internet access during installation

## Install

Run the installer from the repository that should receive the CodeGraph index.

Windows PowerShell:

```powershell
& 'C:\path\to\KISS-Chris-Stack\scripts\install-stack.ps1' -ProjectPath .
```

macOS, Linux, or WSL:

```bash
bash /path/to/KISS-Chris-Stack/scripts/install-stack.sh "$PWD"
```

The installation is idempotent. It installs the native Ouroboros/Ponytail integrations, applies a bounded dashboard-picker compatibility fix when the installed Ouroboros release still needs it, opens a fresh detected agent whose first prompt is exactly `ooo setup`, then continues only after setup succeeds. It configures the bounded Deep Path (three iterations per acceptance criterion, 15 minutes without progress, 60 minutes per generation, Stage 3 off, and `auto_evolve=false`). It then installs the current `ui-ux-pro-max-cli` and runs `uipro init --ai codex` from the user home for Codex (plus the matching Claude initialization when detected). Existing CodeGraph indexes are synchronized; missing indexes are initialized. Existing `.ouroboros/mechanical.toml` gates are preserved; missing gates are detected. Existing global instruction content is preserved outside the marked `kiss-chris-stack` block; legacy `ouroboros-stack` blocks are migrated in place.

On native Windows, the installer registers a user-logon scheduled task named `Ouroboros MCP`. This is required because current Ouroboros releases intentionally avoid Codex STDIO MCP on native Windows. On macOS, Linux, and WSL, Codex starts the STDIO MCP server when the agent starts. CodeGraph uses host-managed MCP startup on all platforms.

For each Deep Path, the agent starts Ouroboros through MCP, waits until the returned DB-scoped dashboard run picker is actually readable, opens it in the browser, and delegates exactly one read-only host observer before execution workers begin. If Ouroboros has retired an idle dashboard daemon, the launcher replaces the stale port with the current DB-scoped endpoint automatically while preserving `?run=...`.

## Unavoidable manual steps

- Restart/reopen the agent after installation so newly installed plugins, skills, MCP registrations, and global rules are loaded.
- Complete any account login or provider authorization requested by the selected agent runtime. Automatic first-agent setup is currently implemented for Codex and Claude Code; another host must run `ooo setup` once itself before rerunning the installer.
- Review and trust Ponytail lifecycle hooks once when the host asks; installers cannot safely grant hook trust on a recipient's behalf.
- On a headless/SSH machine no browser can be opened. The dashboard URL is printed for manual opening or forwarding.

## Verify

```powershell
& 'C:\path\to\KISS-Chris-Stack\scripts\verify-stack.ps1' -ProjectPath .
```

```bash
bash /path/to/KISS-Chris-Stack/scripts/verify-stack.sh "$PWD"
```

The installer writes only marker-owned global instruction blocks. The sole compatibility patch changes the installed Ouroboros progress-row reader from generic payload identity to the already-projected aggregate identity; it is syntax-checked, idempotent, and refuses unknown upstream source shapes. Upstream installers own their own plugin, skill, MCP, hook, and configuration entries.
