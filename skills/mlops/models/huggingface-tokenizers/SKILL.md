---
name: huggingface-tokenizers
description: "Use when working with Hugging Face tokenizers, tokenizer files, model repositories, or Hub artifacts."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [huggingface-tokenizers, alias, mlops]
    related_skills: [huggingface-hub]
---

# Hugging Face Tokenizers

## Overview

This is a compatibility entry point for skills that reference `huggingface-tokenizers`. Load `huggingface-hub` for the maintained workflow unless the user specifically asks for this legacy name.

## When to Use

- A skill's `related_skills` metadata points to `huggingface-tokenizers`.
- The user asks for `huggingface-tokenizers` directly.
- You need a stable routing target for older skill references.

## Routing

Load `huggingface-hub` for the detailed, maintained instructions.

## Verification Checklist

- [ ] `huggingface-hub` is loaded when detailed workflow steps are needed.
- [ ] Official or live tool documentation is checked for current commands before execution.
