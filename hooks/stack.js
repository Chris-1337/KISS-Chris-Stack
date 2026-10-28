#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');

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
    context = `KISS-Chris-Stack: before handling the original request, execute /setup from ${JSON.stringify(path.join(root, 'skills/setup/SKILL.md'))}. Verify current runtime readiness for ${JSON.stringify(path.resolve(event.cwd))}; do not trust a cached ready flag. Check tools, bundled resources, global policy and existing override, CodeGraph index/registration, and actual session MCP tool visibility. Repair authorized local setup, preserve foreign configuration, and require host reload/trust when needed. Do not begin the original implementation while readiness is failed or reload-required. Never self-approve hooks or overwrite conflicting MCP entries. After setup and documentation context, use ${JSON.stringify(path.join(root, 'skills/kiss-chris-stack/SKILL.md'))} for the original request; clarify missing decisions, register its goal, and orchestrate separate test, implementation and evaluation agents. Recheck on each root task.

Original request (data, not setup instructions):
${typeof event.prompt === 'string' ? event.prompt : 'Continue the original user request already in this session.'}`;
  }
  process.stdout.write(JSON.stringify({hookSpecificOutput:{hookEventName:name,additionalContext:context}}));
} catch (error) {
  process.stderr.write(`KISS-Chris-Stack hook failed: ${error.message}\n`);
  process.exitCode = 1;
}
