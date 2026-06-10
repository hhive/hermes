# A-share rebuild from existing portfolio state

Context captured from a Hermes/Weixin scheduled paper-trading report repair.

## Symptom pattern

- Existing A-share cron jobs were enabled and marked `ok`, but output artifacts showed `silent (empty output)`.
- Manual script runs produced reports, while long-running gateway cron runs produced empty output.
- Additional attempts with wrapper scripts added complexity and interacted poorly with Windows/Git Bash availability and gateway process environment.
- Weixin delivery logs also showed `iLink sendmessage rate limited`, which was a separate delivery problem and should not be confused with generation failure.

## User correction

When the user says the current scripts are "修坏了" and asks to delete scripts and restart from existing A-share data, do not keep layering wrappers. Preserve the portfolio/account state and rebuild a minimal script.

## Successful reset approach

1. Preserve `a_stock_paper_portfolio.json` and any durable state/trade log.
2. Delete old report implementations and duplicates under the scripts area:
   - main script
   - wrapper scripts
   - shell wrappers
   - duplicate nested script copies
   - `__pycache__`
3. Recreate one script with these properties:
   - Python standard library only.
   - Reads the existing portfolio JSON.
   - Fetches quotes from one stable public source first, one fallback if needed.
   - Updates last prices in the portfolio state.
   - Always prints exactly one user-facing report or an explicit failure line to stdout.
4. Keep report sections aligned with the user's preference: 股市情况、热点/趋势与未来方向、操作情况、操作原因、资金情况、当前持仓.
5. Update every related cron job with full metadata preserved. Do not send partial updates that clear `deliver`, `workdir`, `enabled_toolsets`, or `name`.
6. Verify by manual cron trigger and inspect the newest `cron/output/<job_id>/*.md` artifact for a non-empty report.

## Key lesson

Treat generation and delivery separately. A non-empty cron output artifact proves the script is fixed. If the user still does not receive the report, inspect gateway delivery logs for messaging rate limits or session issues rather than rewriting the script again.
