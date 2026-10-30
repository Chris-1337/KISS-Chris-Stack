---
name: onboarding
description: Ask whether to set up a project after adding the KISS-Chris-Stack plugin, and collect the target path before setup.
---

# KISS-Chris-Stack onboarding

Run this installation dialogue before lifecycle setup/readiness instructions. Adding the plugin does not authorize project setup, runtime repair, global-rule changes, or documentation writes. Keep the dialogue pending across replies; lifecycle hooks must not interpret its yes/no/path answers as ordinary project tasks.

1. Ask in the user's language whether they want to set up a project now. Wait for their answer before running setup or its helpers.
2. If **yes**, ask for the project path and wait for it. Require an explicit absolute path to an existing directory; validate it as a literal filesystem path. Do not infer a project from `cwd`, the plugin installation directory, or a previous task. If a supplied path is invalid, ask for a corrected path without creating a directory or starting setup. If the user already supplied an explicit path with their yes, validate it without asking again.
3. Only after yes and a valid path, invoke the bundled [setup](../setup/SKILL.md) for that exact project. Inspect its root `kiss-chris-stack.config.json` through setup: an existing configuration is preserved and validated; a missing configuration is created only after successful initialization.
4. If **no**, declined, or cancelled at either question, do not run setup or change the project/profile. Explain that they can run the slash command `/setup` manually later, or that the trusted lifecycle hook will automatically set up a project on a later ordinary task when its root `kiss-chris-stack.config.json` is missing. Automatic execution requires the plugin enabled/loaded, Node.js available, and hooks reviewed/trusted through the host; reload can be necessary. End the onboarding dialogue after this explanation. Do not fall through to automatic setup for the decline/cancel reply.

An unanswered question is not consent. Follow [setup](../setup/SKILL.md) only after the target is known; normal runtime/MCP readiness checks and the stack workflow apply to subsequent ordinary project tasks.
