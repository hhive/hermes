---
name: gguf
description: "Use when working with GGUF models, llama.cpp conversion, quantization, or local GGUF inference."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [gguf, alias, mlops]
    related_skills: [llama-cpp]
---

# GGUF

## Overview

This is a compatibility entry point for skills that reference `gguf`. Load `llama-cpp` for the maintained workflow unless the user specifically asks for this legacy name.

## When to Use

- A skill's `related_skills` metadata points to `gguf`.
- The user asks for `gguf` directly.
- You need a stable routing target for older skill references.

## Routing

Load `llama-cpp` for the detailed, maintained instructions.

## Verification Checklist

- [ ] `llama-cpp` is loaded when detailed workflow steps are needed.
- [ ] Official or live tool documentation is checked for current commands before execution.
