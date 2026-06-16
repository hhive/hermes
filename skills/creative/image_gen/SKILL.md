---
name: image_gen
description: "Use when image generation is requested through Hermes image tools or when routing image workflows to available creative generation skills."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [image-gen, alias, creative]
    related_skills: [comfyui]
---

# Image Generation

## Overview

This is a compatibility entry point for skills that reference `image_gen`. Load `comfyui` for the maintained workflow unless the user specifically asks for this legacy name.

## When to Use

- A skill's `related_skills` metadata points to `image_gen`.
- The user asks for `image_gen` directly.
- You need a stable routing target for older skill references.

## Routing

Load `comfyui` for the detailed, maintained instructions.

## Verification Checklist

- [ ] `comfyui` is loaded when detailed workflow steps are needed.
- [ ] Official or live tool documentation is checked for current commands before execution.
