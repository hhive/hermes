---
name: browser
description: "Use when browser automation or web UI interaction is needed and a narrower browser-specific skill is not available."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [browser, alias, software-development]
    related_skills: [dogfood]
---

# Browser Automation

## Overview

This is a compatibility entry point for skills that reference `browser`. Load `dogfood` for the maintained workflow unless the user specifically asks for this legacy name.

## When to Use

- A skill's `related_skills` metadata points to `browser`.
- The user asks for `browser` directly.
- You need a stable routing target for older skill references.

## Routing

Load `dogfood` for the detailed, maintained instructions.

## Verification Checklist

- [ ] `dogfood` is loaded when detailed workflow steps are needed.
- [ ] Official or live tool documentation is checked for current commands before execution.
