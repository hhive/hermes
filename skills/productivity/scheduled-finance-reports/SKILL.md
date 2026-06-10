---
name: scheduled-finance-reports
description: Build and troubleshoot deterministic scheduled finance/market reports, especially paper-trading reports delivered through Hermes cron and messaging gateways.
version: 1.0.0
created_by: agent
tags: [finance, scheduled-reports, cron, paper-trading, market-data, automation]
---

# Scheduled Finance Reports

Use this when creating, repairing, or simplifying scheduled market reports, portfolio summaries, paper-trading reports, watchdog-style finance automations, or recurring market-data digests.

## Core Principles

1. **Separate generation from delivery.** First prove the report script writes non-empty stdout and a cron output artifact. Only then debug messaging delivery, rate limits, or gateway state.
2. **Prefer deterministic no-agent scripts.** For recurring finance reports, use `no_agent=true` with a script that prints the exact user-facing report. Avoid depending on LLM reasoning for every tick unless the user explicitly wants narrative analysis over deterministic behavior.
3. **Preserve account state.** When rebuilding a broken report pipeline, keep durable portfolio/account files unless the user explicitly asks to reset them. Delete brittle wrappers/cache scripts, not the simulation ledger.
4. **Minimize dependencies.** If cron execution is unstable, simplify the script before adding wrappers: Python standard library, one or two public quote sources, clear fallback behavior, and one stdout report.
5. **Verify the real scheduler path.** Manual `python script.py` is not enough. Use the cron runner or a manual cron trigger and inspect `cron/output/<job_id>/*.md` for non-empty content.
6. **Stop stacking patches when the user signals frustration.** If the user says the implementation is now broken or asks to start over, cleanly replace the implementation with a simpler known-good version instead of layering more wrappers.

## Repair Workflow

1. List relevant jobs and note `job_id`, `script`, `schedule`, `deliver`, `enabled_toolsets`, and `workdir`.
2. Inspect latest `cron/output/<job_id>/*.md`:
   - `silent (empty output)` means generation failed or stdout was empty.
   - A normal report saved there means generation works; look at gateway logs for delivery failures.
3. Run the script with the same interpreter family the scheduler uses if possible, then call the cron runner directly when available.
4. If the script is complex and failures are unclear, replace it with a minimal deterministic implementation using existing state files.
5. Update all related cron jobs with the full original metadata preserved: `schedule`, `deliver`, `enabled_toolsets`, `workdir`, `name`, `no_agent=true`, and `script`.
6. Manually trigger one job, wait for the scheduler tick, then read the newest output artifact and check delivery logs.

## Rebuild Pattern

When rebuilding from existing paper-trading data:

- Keep the portfolio JSON/SQLite state and trade log.
- Delete stale script wrappers, duplicate script copies, and `__pycache__` under the script area.
- Write a single script under the scheduler's scripts directory.
- Use stable public quote sources and conservative fallbacks.
- Print a report even when market data is partial; never silently exit on data-source failure.
- Include: market condition, hotspots/trend, future direction, operation status, operation rationale, cash/assets/exposure, current positions, and simulation risk disclaimer.

## Verification Checklist

- Direct script run prints a complete report.
- Cron runner returns `(ok=True, len(output)>0)` or equivalent.
- Manual cron trigger creates a new non-empty `cron/output/<job_id>/*.md` artifact.
- Job config still has `deliver=origin` or the intended delivery target.
- Gateway logs distinguish delivery rate limits from script failures.

## References

- `references/a-share-rebuild-from-existing-state.md` — session-specific notes for rebuilding an A-share paper-trading report from an existing portfolio after wrapper/cron issues.