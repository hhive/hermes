---
name: stable-diffusion-image-generation
description: "Use when generating Stable Diffusion images or routing image generation workflows through ComfyUI."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [stable-diffusion-image-generation, alias, creative]
    related_skills: [comfyui]
---

# Stable Diffusion Image Generation

## Overview

This is a compatibility entry point for skills that reference `stable-diffusion-image-generation`. Load `comfyui` for the maintained workflow unless the user specifically asks for this legacy name.

## When to Use

- A skill's `related_skills` metadata points to `stable-diffusion-image-generation`.
- The user asks for `stable-diffusion-image-generation` directly.
- You need a stable routing target for older skill references.

## Routing

Load `comfyui` for the detailed, maintained instructions.

## Verification Checklist

- [ ] `comfyui` is loaded when detailed workflow steps are needed.
- [ ] Official or live tool documentation is checked for current commands before execution.
