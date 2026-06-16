---
name: mcporter
description: "Use when porting MCP server definitions, tool schemas, or existing integrations into Hermes Agent native MCP configuration."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mcporter, alias, mcp]
    related_skills: [native-mcp]
---

# MCP Porter

## Overview

This is a compatibility entry point for skills that reference `mcporter`. Load `native-mcp` for the maintained workflow unless the user specifically asks for this legacy name.

## When to Use

- A skill's `related_skills` metadata points to `mcporter`.
- The user asks for `mcporter` directly.
- You need a stable routing target for older skill references.

## Routing

Load `native-mcp` for the detailed, maintained instructions.

## Verification Checklist

- [ ] `native-mcp` is loaded when detailed workflow steps are needed.
- [ ] Official or live tool documentation is checked for current commands before execution.
