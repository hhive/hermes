---
name: concept-diagrams
description: "Use when creating conceptual diagrams, explanatory visuals, or architecture sketches; choose the closest diagram skill for output format."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [concept-diagrams, alias, creative]
    related_skills: [architecture-diagram]
---

# Concept Diagrams

## Overview

This is a compatibility entry point for skills that reference `concept-diagrams`. Load `architecture-diagram` for the maintained workflow unless the user specifically asks for this legacy name.

## When to Use

- A skill's `related_skills` metadata points to `concept-diagrams`.
- The user asks for `concept-diagrams` directly.
- You need a stable routing target for older skill references.

## Routing

Load `architecture-diagram` for the detailed, maintained instructions.

## Verification Checklist

- [ ] `architecture-diagram` is loaded when detailed workflow steps are needed.
- [ ] Official or live tool documentation is checked for current commands before execution.
