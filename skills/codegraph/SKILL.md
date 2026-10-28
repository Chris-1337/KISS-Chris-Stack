---
name: codegraph
description: Use the bundled stack's pinned local CodeGraph runtime and session MCP tools for repository structure, call paths, dependencies, and impact.
---

# CodeGraph

Run [setup](../setup/SKILL.md) for missing runtime/index/MCP prerequisites. Pins and observed package/runtime version differences live in [versions.json](../../assets/versions.json). The host starts the registered MCP service; never launch a duplicate server or replace a conflicting entry silently.

Prefer session MCP `codegraph_context` for focused task context, `codegraph_explore` for several source symbols, and callers/callees/impact for structural questions. Use `rg` for literal text. Synchronize an existing index before substantive changes; initialize a missing one through setup. An MCP CLI registration alone does not prove tools loaded in this session: call actual MCP status/context against the intended project before accepting readiness. If tools are absent, require a host reload and recheck.
