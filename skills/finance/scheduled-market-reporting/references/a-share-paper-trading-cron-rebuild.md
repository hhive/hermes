# A-share Paper-Trading Cron Rebuild

This reference captures a concrete pattern for rebuilding a broken A-share paper-trading report job while preserving the user's existing simulated account state.

## What to preserve

Keep the portfolio/account state file intact unless explicitly told to reset it. In this setup the durable state was:

```text
C:/Users/jax/AppData/Local/hermes/a_stock_paper_portfolio.json
```

It contained cash, positions, trade log, rules, and update timestamps. The user wanted to use the previous A-share data, so only script implementations and wrappers were removed.

## What to remove when starting over

Remove stale script implementations, duplicate compatibility copies, wrappers, and bytecode caches, for example:

```text
scripts/a_stock_paper_trader.py
scripts/a_stock_paper_trader_wrapper.py
scripts/a_stock_paper_trader.sh
scripts/scripts/a_stock_paper_trader.py
scripts/__pycache__/
scripts/scripts/__pycache__/
```

Do not delete `cron/output/` history unless the user asks; those files help diagnose whether a run generated an empty report or failed only at delivery.

## Stable rebuild shape

A robust Windows cron script can be a single `.py` file that uses only the Python standard library:

- `urllib.request` for HTTP quote calls.
- `json` for portfolio state.
- `re` for parsing Sina/Tencent JavaScript quote payloads.
- `datetime` and `pathlib` for timestamps and paths.

This avoids dependency mismatches such as `requests` being available in an interactive Python but not the gateway scheduler's Python.

## Three-source quote roles

For A-share quote collection, use explicit source roles:

1. **Query**: Sina `https://hq.sinajs.cn/list=<codes>` — primary report prices.
2. **Check**: Tencent `https://qt.gtimg.cn/q=<codes>` — full cross-check for all codes.
3. **Fallback**: Eastmoney `https://push2.eastmoney.com/api/qt/ulist.np/get?...` — fills only quotes missing from the query source.

Report the source health in one compact line, e.g.:

```text
行情状态：查询:新浪12条；校验:腾讯校验12条，一致
```

When fallback is used, append:

```text
备用:东方财富备用N条
```

## Verification sequence

Run both direct and scheduler-path checks before declaring the repair done:

```bash
"$HOME/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" \
  "$HOME/AppData/Local/hermes/scripts/a_stock_paper_trader.py" | head -60

"$HOME/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" - <<'PY'
import os, sys
os.environ['HERMES_HOME'] = r'C:/Users/jax/AppData/Local/hermes'
sys.path.insert(0, r'C:/Users/jax/AppData/Local/hermes/hermes-agent')
from cron.scheduler import _run_job_script
ok, out = _run_job_script('a_stock_paper_trader.py')
print('OK=', ok, 'LEN=', len(out))
print(out[:1200])
PY
```

Then manually trigger one cron job and inspect the actual output directory:

```text
cron/output/<job_id>/<timestamp>.md
```

A successful repair should produce a report-sized file, not a tiny `silent (empty output)` file.

## Cron metadata to preserve

When updating existing jobs, preserve:

- `schedule`
- `deliver='origin'`
- `enabled_toolsets=['terminal', 'file']`
- `workdir='C:\\Users\\jax\\AppData\\Local\\hermes'`
- `no_agent=true`
- job names and job IDs where possible

For this user's A-share report cadence, the final intended workday times were:

```text
09:00
11:00
13:30
14:50
```

## Delivery-vs-generation distinction

If the output file is valid but the user did not receive the message, treat it as a gateway delivery issue. Weixin/iLink logs may show `rate limited`, `send failed`, or session errors. Repeated manual resend attempts can extend the rate limit; first confirm generation, then investigate delivery.
