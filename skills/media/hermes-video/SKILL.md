---
name: hermes-video
description: "Use when a skill references Hermes video generation or video processing and no narrower video skill is available."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes-video, alias, media]
    related_skills: [ascii-video]
---

# Hermes Video

## Overview

This is a compatibility entry point for skills that reference `hermes-video`. Load `ascii-video` for the maintained workflow unless the user specifically asks for this legacy name.

## When to Use

- A skill's `related_skills` metadata points to `hermes-video`.
- The user asks for `hermes-video` directly.
- You need a stable routing target for older skill references.

## Routing

Load `ascii-video` for the detailed, maintained instructions.

## Verification Checklist

- [ ] `ascii-video` is loaded when detailed workflow steps are needed.
- [ ] Official or live tool documentation is checked for current commands before execution.
