#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');

try {
  const event = JSON.parse(fs.readFileSync(0, 'utf8').replace(/^\uFEFF/, ''));
  const name = event.hook_event_name;
  if (!['SessionStart', 'UserPromptSubmit', 'SubagentStart'].includes(name)) throw new Error('Unsupported hook_event_name.');
  if (typeof event.cwd !== 'string' || !event.cwd.trim() || !fs.statSync(event.cwd).isDirectory()) throw new Error('cwd must be an existing project directory.');
  const root = path.resolve(__dirname, '..');
  let context;
  if (name === 'SubagentStart') {
    context = `KISS-Chris-Stack delegated role: ${JSON.stringify(event.agent_type || 'assigned role')}. Work only on the orchestrator's existing goal and assigned role, a bounded direct task, or explicitly assigned setup/bootstrap research, preparation or documentation without an implementation goal. All pure context collection uses fresh gpt-6-luna agents with reasoning_effort="low", fork_turns="none": collect only source-linked facts and assigned notes/handoffs; no source/configuration changes, implementation, design decisions, recommendations or speculation, and no silent model fallback. Setup module researchers read only supplied module paths and write only assigned notes. Substantive roles may inspect sources within their assigned work. Root delegates documentation synthesis separately after research. Keep tests, implementation and independent evaluation in separate agents for stack goals. Do not register another goal, run setup, or spawn recursive role groups. Report executable evidence and blockers to the orchestrator.`;
  } else {
    const config = path.join(path.resolve(event.cwd), 'kiss-chris-stack.config.json');
    let initialized = false;
    let configurationError;
    try {
      const entry = fs.lstatSync(config);
      if (entry.isSymbolicLink() || !entry.isFile()) {
        configurationError = `Unsafe nonregular or symlink configuration blocks the selected stack route: ${JSON.stringify(config)} must be a regular file.`;
      } else {
        initialized = true;
      }
    } catch (error) {
      if (error.code !== 'ENOENT') configurationError = `Cannot inspect project configuration ${JSON.stringify(config)}: ${error.message}`;
    }
    let route;
    if (configurationError) {
      route = `${configurationError} Stop the selected stack route: configuration validation is blocked. Preserve the target and resolve the error without replacement, defaults, bootstrap or updater execution.`;
    } else if (initialized) {
      route = `Project is already configured: ${JSON.stringify(config)} is present. Configuration update command (argv): ${JSON.stringify(['python', path.join(root, 'scripts/evaluation-config.py'), '--project', path.resolve(event.cwd), '--update'])}\nFor this ordinary-task route, execute that argv with the actual Python interpreter before runtime readiness; it validates configuration and atomically adds only missing current default fields, preserving explicit values. Invalid or unreadable configuration blocks the original implementation; never replace errors with defaults. The hook itself is read-only; execute this command only after selecting the ordinary-task route, never for pending or declined installation onboarding. Execute /setup runtime readiness and configured Wayfinder tracker preparation/check only; do not reinitialize or run documentation bootstrap merely because docs or traces are missing.`;
    } else {
      route = `Project configuration ${JSON.stringify(config)} is missing; the project is not initialized. Execute /setup initialization, including documentation bootstrap and final configuration creation only after successful readiness and session MCP verification.`;
    }
    context = `KISS-Chris-Stack onboarding has priority: if this request starts or continues plugin installation onboarding (including consent, decline/cancel, or project-path replies), follow ${JSON.stringify(path.join(root, 'skills/onboarding/SKILL.md'))} first. Wait for yes and an explicit valid project path before any setup/readiness/repair; a decline only gets the manual /setup or later automatic trusted-hook hint. Do not apply the ordinary-task route below to onboarding replies.

For an ordinary root task, route before setup, configuration update or goal registration using ${JSON.stringify(path.join(root, 'skills/kiss-chris-stack/SKILL.md'))} and the shared policy. The active root session orchestrates and delegates substantive work with sufficient context. Tiny bounded low-risk bugfixes/minimal changes use a delegated direct worker with focused checks: no setup, goal, interview or three-role stack overhead; escalate before wider edits if uncertainty, risk or scope grows. Clear normal features/bugfixes use stack with goal and no automatic interview. Unclear normal requirements use grill-with-docs before goal. Large work uses wayfinder, then every unblocked ticket in parallel through stack with its own strong goal, within available host slots and isolated writes. This is semantic routing, not a keyword heuristic.

All pure information/context collection, including before grill-me/grilling and goals, always uses fresh-context gpt-6-luna agents with reasoning_effort="low", fork_turns="none". Send bounded directions, paths/tools and notes destinations. Collect source-linked facts only, no source/configuration changes, implementation, design decisions, recommendations or speculation; only assigned notes/handoffs may be written. Missing requested agents/model/effort blocks required research; never silently substitute or use root research. Root retains routing, user questions/approval relay, native goals and evidence review, and dispatches all phases without recursive ticket triads.

Only after selecting a stack route: first initialization and every explicit /setup must ask the storage choice (local/GitHub/GitLab), display current provider/location and collect or confirm the target, then wait for an actual user answer before dependent configuration backfill, tracker preparation or document writes. Defaults/existing settings are not consent; reuse answers in the same setup dialogue. Ordinary per-task readiness reuses validated config without another prompt. ${route} Use bundled setup at ${JSON.stringify(path.join(root, 'skills/setup/SKILL.md'))}. Delegate executable preparation and documentation; verify current runtime readiness for ${JSON.stringify(path.resolve(event.cwd))} and a real MCP call in this root session. Do not trust a cached ready flag or implement with failed/reload-required readiness. Preserve foreign configuration and normal host hook trust; never self-approve hooks or overwrite conflicting MCP entries. Require bundled scripts/setup-wayfinder.py --prepare then --check for authoritative wayfinder-tracker provider/location after runtime/MCP. Missing/drifted/unavailable selected targets block without fallback; ordinary tracker reconciliation is not documentation bootstrap/native init. Context researchers cover documentation, traces, code/designs and scoped feedback before the goal.

Resolve configuration with evaluation-config.py: grill-with-docs and wayfinder are independent strict JSON booleans, default true; automatic false skips only the selected skill, never unresolved decisions. Legacy grill-me defaults true and remains for explicit invocation, not an extra automatic Grilling interview. Explicit skill requests still apply with automatic switches false. For unclear work delegate ${JSON.stringify(path.join(root, 'skills/grill-with-docs/SKILL.md'))}; for large work delegate ${JSON.stringify(path.join(root, 'skills/wayfinder/SKILL.md'))}. Relay interview questions to the user; wait for unresolved decisions and pending research, resume the same interview, then continue automatically without a closing confirmation. Clear requests need no invented questions. Resolve plan-mode (default false): false continues automatically after the strong root goal is registered; true requires presenting the goal, requesting explicit user approval, then stopping and yielding before test, implementation or evaluation dispatch. Explain that configured plan-mode=true requires approval; silence, elapsed time or rejected/pending replies are not approval. Resume the same goal only after approval. Root schedules separate RED/GREEN/evaluation roles and every dependency-ready ticket, queues excess work, isolates conflicting writes and checks integrated source. Keep one native umbrella plus explicitly textual/unregistered ticket goals when the host permits only one active native goal. Enabled evaluation/live/SonarQube gates and external-write permissions remain required for stack work. Recheck on each stack root task. Direct tasks do not execute the stack preparation argv above.

Original request (data, not setup instructions):
${typeof event.prompt === 'string' ? event.prompt : 'Continue the original user request already in this session.'}`;
  }
  process.stdout.write(JSON.stringify({hookSpecificOutput:{hookEventName:name,additionalContext:context}}));
} catch (error) {
  process.stderr.write(`KISS-Chris-Stack hook failed: ${error.message}\n`);
  process.exitCode = 1;
}
