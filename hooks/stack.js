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
    context = `KISS-Chris-Stack delegated role: ${JSON.stringify(event.agent_type || 'assigned role')}. Work only on the orchestrator's existing goal and assigned role. Read the supplied specification and relevant project context. Keep tests, implementation and independent evaluation in separate agents. Do not register another goal, run setup, or spawn recursive role groups. Report executable evidence and blockers to the orchestrator.`;
  } else {
    const config = path.join(path.resolve(event.cwd), 'kiss-chris-stack.config.json');
    let initialized = false;
    try {
      if (!fs.statSync(config).isFile()) throw new Error(`Project configuration ${JSON.stringify(config)} must be a regular file.`);
      initialized = true;
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
    const route = initialized
      ? `Project is already configured: ${JSON.stringify(config)} is present. Validate and preserve its settings through the setup skill's evaluation-config.py resolver before repairs. Invalid or unreadable configuration blocks the original implementation; never overwrite it with defaults. Execute only /setup runtime readiness checks; do not reinitialize or run documentation bootstrap merely because docs or traces are missing.`
      : `Project configuration ${JSON.stringify(config)} is missing; the project is not initialized. Execute /setup initialization, including documentation bootstrap and final configuration creation only after successful readiness and session MCP verification.`;
    context = `KISS-Chris-Stack onboarding has priority: if this request starts or continues plugin installation onboarding (including consent, decline/cancel, or project-path replies), follow ${JSON.stringify(path.join(root, 'skills/onboarding/SKILL.md'))} first. Wait for yes and an explicit valid project path before any setup/readiness/repair; a decline only gets the manual /setup or later automatic trusted-hook hint. Do not apply the ordinary-task route below to onboarding replies.

For an ordinary root task: ${route} Use the bundled setup skill at ${JSON.stringify(path.join(root, 'skills/setup/SKILL.md'))}. Verify current runtime readiness for ${JSON.stringify(path.resolve(event.cwd))}; do not trust a cached ready flag. Check tools, bundled resources, global policy and existing override, CodeGraph index/registration, and actual session MCP tool visibility. Repair authorized local setup, preserve foreign configuration, and require host reload/trust when needed. Do not begin the original implementation while readiness is failed or reload-required. Never self-approve hooks or overwrite conflicting MCP entries. After setup and documentation context, use ${JSON.stringify(path.join(root, 'skills/kiss-chris-stack/SKILL.md'))} for the original request; clarify missing decisions and register its strong goal. Resolve top-level plan-mode through evaluation-config.py (default false): false continues automatically; true requires presenting the strong goal, requesting explicit user approval, then stopping and yielding the turn before dispatching test, implementation or evaluation agents; explain that configured plan-mode=true requires approval. Resume the same goal after approval; silence, elapsed time or a rejected/pending reply is not approval. Then orchestrate the separate roles. Recheck on each root task.

Original request (data, not setup instructions):
${typeof event.prompt === 'string' ? event.prompt : 'Continue the original user request already in this session.'}`;
  }
  process.stdout.write(JSON.stringify({hookSpecificOutput:{hookEventName:name,additionalContext:context}}));
} catch (error) {
  process.stderr.write(`KISS-Chris-Stack hook failed: ${error.message}\n`);
  process.exitCode = 1;
}
