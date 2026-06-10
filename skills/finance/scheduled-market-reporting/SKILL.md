---
name: scheduled-market-reporting
description: Build and maintain deterministic scheduled market/portfolio reporting jobs, especially paper-trading reports delivered through Hermes cron/gateway.
version: 1.0.0
created_by: agent
tags: [finance, cron, reporting, paper-trading, market-data]
---

# Scheduled Market Reporting

Use this skill when setting up, repairing, or simplifying scheduled market/portfolio reports such as A-share paper-trading summaries, gold market summaries, or other recurring finance reports.

## Principles

- Keep recurring finance reports deterministic: prefer `no_agent=true` cron jobs backed by a script that prints the final user-facing report to stdout.
- Preserve durable account state separately from scripts. For paper trading, keep portfolio/cash/position JSON or SQLite state intact unless the user explicitly asks to reset it.
- Prefer simple, dependency-light scripts for cron reliability. Standard-library HTTP is often better than adding runtime dependencies when the job only needs quotes and formatting.
- Clearly label paper-trading output as simulation and not investment advice.
- If the user asks to “start over” after a broken repair, delete/rewrite the script implementation but keep the portfolio/state file if the user wants to use previous A-share data.

## Repair Workflow

1. Inspect current cron jobs and identify the job IDs, schedules, `script`, `deliver`, `enabled_toolsets`, `workdir`, and `no_agent` values.
2. Inspect recent `cron/output/<job_id>/*.md` before changing anything. A job marked `ok` can still be `silent (empty output)`.
3. Preserve durable state files such as `a_stock_paper_portfolio.json`; remove only stale wrappers, duplicate script copies, caches, and broken implementation files.
4. Rebuild one canonical script under the Hermes scripts directory, typically `~/AppData/Local/hermes/scripts/<name>.py` on Windows.
5. Verify in two layers: run the script directly with the same Python used by Hermes, then call `cron.scheduler._run_job_script('<name>.py')` with `HERMES_HOME` set.
6. Update every affected cron job while preserving its original schedule, delivery target, toolsets, workdir, name, and `no_agent=true`.
7. Trigger one job manually and inspect the new cron output file to verify it is non-empty and contains the report body.
8. Separately inspect gateway/send logs for delivery failures such as Weixin rate limits; do not confuse delivery failure with script-output failure.

## Multi-Source Quote Pattern

For A-share reports, use three roles rather than treating all sources equally:

- **Query source**: primary source used for report prices, e.g. Sina `hq.sinajs.cn`.
- **Check source**: full cross-check source queried for all codes, e.g. Tencent `qt.gtimg.cn`; report whether values are consistent or materially different.
- **Fallback source**: used only for missing quotes, e.g. Eastmoney `push2.eastmoney.com`.

The report should expose source health compactly, for example:

```text
行情状态：查询:新浪12条；校验:腾讯校验12条，一致
```

If fallback fills gaps, append:

```text
备用:东方财富备用N条
```

## Windows Cron Pitfalls

- A no-agent `.py` cron job is executed with the scheduler process's `sys.executable`, not necessarily the interactive shell's `python`.
- Manual `python script.py` success is not enough. Always verify through `_run_job_script()` and by reading the actual `cron/output` file after a manual cron trigger.
- Avoid relying on `.sh` wrappers on Windows unless Git Bash availability is proven in the scheduler environment. A background gateway process may not have `bash` on `PATH`.
- When editing cron jobs through tools, pass the original schedule and delivery metadata. Partial updates can accidentally clear or change delivery settings depending on the update path.

## Report Content Checklist

For A-share paper-trading reports, include:

- 股市情况: index levels and source-health line.
- 热点/趋势与未来方向: concise style/sector relative strength and next direction.
- 操作情况: latest simulated operation or `HOLD/等待`.
- 操作原因: short rationale tied to trend, risk, and current exposure.
- 资金情况: cash, estimated position value, estimated total assets, exposure.
- 当前持仓: each position with shares, cost, latest price, and unrealized P/L.
- 风险提示: paper-trading simulation only; not investment advice.

## When Delivery Fails

If the cron output file is valid but the user did not receive a message, investigate gateway delivery separately:

- Search gateway/agent logs for `rate limited`, `send failed`, `delivery error`, and platform-specific session errors.
- For Weixin/iLink rate limits, avoid repeated immediate manual resend attempts; they can prolong the limit window.
- Keep the generated report path available so the content can be summarized manually while delivery recovers.

## References

- `references/a-share-paper-trading-cron-rebuild.md` — concrete rebuild pattern and verification notes from an A-share paper-trading report repair session.
