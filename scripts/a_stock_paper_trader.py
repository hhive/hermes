#!/usr/bin/env python3
"""Stable A-share paper-trading report for Hermes cron.

No real orders are placed. This script is intentionally simple and cron-safe:
- Python standard library only.
- Reads existing paper portfolio state.
- Fetches quotes with Sina as query source, Tencent as full cross-check,
  and Eastmoney as fallback for missing quotes.
- Prints one UTF-8 report to stdout every run.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

BASE = Path(r"C:/Users/jax/AppData/Local/hermes")
PORTFOLIO_PATH = BASE / "a_stock_paper_portfolio.json"

INDEX_CODES = ["sh000001", "sz399001", "sz399006"]
INDEX_NAMES = {"sh000001": "上证", "sz399001": "深成", "sz399006": "创业板"}
WATCHLIST = [
    ("sh510300", "沪深300ETF", "宽基/大盘"),
    ("sh510500", "中证500ETF", "宽基/中盘"),
    ("sh588000", "科创50ETF", "成长/科技"),
    ("sz159915", "创业板ETF", "成长/科技"),
    ("sh600519", "贵州茅台", "消费/质量"),
    ("sz300750", "宁德时代", "成长/新能源"),
    ("sz000333", "美的集团", "消费/质量"),
    ("sh601318", "中国平安", "金融/价值"),
    ("sh600036", "招商银行", "金融/价值"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://finance.sina.com.cn/",
}


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def stage() -> str:
    hour = datetime.now().hour
    minute = datetime.now().minute
    hm = hour * 60 + minute
    if hm < 11 * 60 + 20:
        return "早盘/盘中"
    if hm < 14 * 60 + 50:
        return "盘中"
    return "收盘前后"


def fetch_text(url: str, encoding: str = "gbk", timeout: int = 12) -> str:
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return raw.decode(encoding, errors="replace")


def fetch_sina(codes: list[str]) -> tuple[dict[str, dict], str]:
    if not codes:
        return {}, "新浪：无代码"
    url = "https://hq.sinajs.cn/list=" + ",".join(codes)
    text = fetch_text(url, "gbk")
    quotes: dict[str, dict] = {}
    for code, payload in re.findall(r'var hq_str_([a-z0-9]+)="(.*?)";', text):
        if not payload:
            continue
        parts = payload.split(",")
        try:
            name = parts[0] or code
            prev = float(parts[1] or 0)
            open_price = float(parts[2] or 0)
            price = float(parts[3] or 0)
            high = float(parts[4] or 0)
            low = float(parts[5] or 0)
            if price <= 0:
                continue
            pct = (price / prev - 1) * 100 if prev else 0.0
            quote_time = " ".join(x for x in [parts[30] if len(parts) > 30 else "", parts[31] if len(parts) > 31 else ""] if x).strip()
            quotes[code] = {
                "code": code,
                "name": name,
                "price": price,
                "prev": prev,
                "open": open_price,
                "high": high,
                "low": low,
                "pct": pct,
                "quote_time": quote_time,
                "source": "新浪",
            }
        except Exception:
            continue
    return quotes, f"新浪{len(quotes)}条"


def fetch_tencent(codes: list[str]) -> tuple[dict[str, dict], str]:
    if not codes:
        return {}, "腾讯：无代码"
    url = "https://qt.gtimg.cn/q=" + ",".join(codes)
    text = fetch_text(url, "gbk")
    quotes: dict[str, dict] = {}
    for code, payload in re.findall(r'v_([a-z0-9]+)="(.*?)";', text):
        parts = payload.split("~")
        try:
            name = parts[1] or code
            price = float(parts[3] or 0)
            prev = float(parts[4] or 0)
            open_price = float(parts[5] or 0)
            if price <= 0:
                continue
            pct = float(parts[32]) if len(parts) > 32 and parts[32] else ((price / prev - 1) * 100 if prev else 0.0)
            quotes[code] = {
                "code": code,
                "name": name,
                "price": price,
                "prev": prev,
                "open": open_price,
                "high": float(parts[33] or 0) if len(parts) > 33 else 0,
                "low": float(parts[34] or 0) if len(parts) > 34 else 0,
                "pct": pct,
                "quote_time": parts[30] if len(parts) > 30 else "",
                "source": "腾讯",
            }
        except Exception:
            continue
    return quotes, f"腾讯校验{len(quotes)}条"


def eastmoney_secid(code: str) -> str:
    if code.startswith("sh"):
        return "1." + code[2:]
    if code.startswith("sz"):
        return "0." + code[2:]
    raise ValueError(f"unsupported code: {code}")


def fetch_eastmoney(codes: list[str]) -> tuple[dict[str, dict], str]:
    if not codes:
        return {}, "东方财富：无缺口"
    secids = ",".join(eastmoney_secid(code) for code in codes)
    fields = "f12,f13,f14,f2,f3,f15,f16,f17,f18,f124"
    url = f"https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields={fields}&secids={secids}"
    text = fetch_text(url, "utf-8")
    data = json.loads(text)
    quotes: dict[str, dict] = {}
    for item in (data.get("data") or {}).get("diff", []) or []:
        try:
            raw = str(item.get("f12") or "")
            market = str(item.get("f13") or "")
            if not raw or market not in {"0", "1"}:
                continue
            code = ("sh" if market == "1" else "sz") + raw
            price = float(item.get("f2") or 0)
            prev = float(item.get("f18") or 0)
            if price <= 0:
                continue
            ts = item.get("f124")
            quote_time = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
            quotes[code] = {
                "code": code,
                "name": item.get("f14") or code,
                "price": price,
                "prev": prev,
                "open": float(item.get("f17") or 0),
                "high": float(item.get("f15") or 0),
                "low": float(item.get("f16") or 0),
                "pct": float(item.get("f3") or ((price / prev - 1) * 100 if prev else 0.0)),
                "quote_time": quote_time,
                "source": "东方财富",
            }
        except Exception:
            continue
    return quotes, f"东方财富备用{len(quotes)}条"


def quote_diff_count(primary: dict[str, dict], check: dict[str, dict]) -> int:
    count = 0
    for code, quote in primary.items():
        other = check.get(code)
        if not other:
            continue
        price = float(quote.get("price", 0) or 0)
        other_price = float(other.get("price", 0) or 0)
        if price and other_price and abs(price - other_price) / price > 0.003:
            count += 1
    return count


def fetch_quotes(codes: list[str]) -> tuple[dict[str, dict], str]:
    notes: list[str] = []
    primary: dict[str, dict] = {}
    check: dict[str, dict] = {}
    try:
        primary, note = fetch_sina(codes)
        notes.append(f"查询:{note}")
    except Exception as exc:
        notes.append(f"查询:新浪失败:{exc.__class__.__name__}")
    try:
        check, note = fetch_tencent(codes)
        diff_count = quote_diff_count(primary, check)
        notes.append(f"校验:{note}" + (f"，差异{diff_count}条" if diff_count else "，一致"))
    except Exception as exc:
        notes.append(f"校验:腾讯失败:{exc.__class__.__name__}")
    quotes = dict(primary)
    missing = [code for code in codes if code not in quotes]
    if missing:
        try:
            fallback, note = fetch_eastmoney(missing)
            notes.append(f"备用:{note}")
            quotes.update(fallback)
        except Exception as exc:
            notes.append(f"备用:东方财富失败:{exc.__class__.__name__}")
    return quotes, "；".join(notes)


def load_portfolio() -> dict:
    if not PORTFOLIO_PATH.exists():
        return {"currency": "CNY", "initial_cash": 100000.0, "cash": 100000.0, "positions": [], "trade_log": []}
    return json.loads(PORTFOLIO_PATH.read_text(encoding="utf-8"))


def save_portfolio(portfolio: dict) -> None:
    portfolio["updated_at"] = now_str()
    PORTFOLIO_PATH.write_text(json.dumps(portfolio, ensure_ascii=False, indent=2), encoding="utf-8")


def fmt_money(value: float) -> str:
    return f"{value:,.2f}元"


def market_view(index_quotes: dict[str, dict], stock_quotes: dict[str, dict]) -> tuple[str, str]:
    index_pcts = [q["pct"] for q in index_quotes.values()]
    avg_index = sum(index_pcts) / len(index_pcts) if index_pcts else 0.0
    if avg_index <= -0.7:
        trend = "指数整体偏弱，优先控仓和等待企稳"
        future = "未来方向以防守为主，保留现金，等指数止跌或热点重新扩散。"
    elif avg_index >= 0.7:
        trend = "指数整体偏强，市场风险偏好回升"
        future = "未来方向可关注放量突破和权重/成长共振，但仍分批，不追高。"
    else:
        trend = "指数整体震荡，结构性轮动为主"
        future = "未来方向以轻仓观察和分批试错为主，等待主线更清晰。"

    buckets: dict[str, list[float]] = {}
    kind_by_code = {code: kind for code, _name, kind in WATCHLIST}
    for code, quote in stock_quotes.items():
        kind = kind_by_code.get(code, "其他")
        buckets.setdefault(kind, []).append(float(quote.get("pct", 0)))
    bucket_avg = [(kind, sum(vals) / len(vals)) for kind, vals in buckets.items() if vals]
    bucket_avg.sort(key=lambda x: x[1], reverse=True)
    leaders = sorted(stock_quotes.values(), key=lambda q: q.get("pct", 0), reverse=True)[:3]
    if bucket_avg:
        hot = f"相对强势：{bucket_avg[0][0]}({bucket_avg[0][1]:+.2f}%)；相对弱势：{bucket_avg[-1][0]}({bucket_avg[-1][1]:+.2f}%)"
    else:
        hot = "热点不明显"
    if leaders:
        hot += "；领涨样本：" + "、".join(f"{q['name']}{q['pct']:+.2f}%" for q in leaders)
    return f"- 趋势：{trend}\n- 热点：{hot}\n- 未来方向：{future}", trend


def choose_operation(portfolio: dict, exposure: float, trend: str) -> tuple[str, str]:
    if exposure > 70:
        return "HOLD/等待：本次未新增模拟买卖", "仓位偏高，优先控制风险，不再加仓"
    if "偏弱" in trend:
        return "HOLD/等待：本次未新增模拟买卖", "指数偏弱，优先控制仓位，等待企稳"
    return "HOLD/等待：本次未新增模拟买卖", "当前持仓结构已建立，先观察现有仓位表现，不追高"


def main() -> int:
    try:
        portfolio = load_portfolio()
        position_codes = [p.get("code", "") for p in portfolio.get("positions", []) if p.get("code")]
        codes = sorted(set(INDEX_CODES + [code for code, _name, _kind in WATCHLIST] + position_codes))
        quotes, data_note = fetch_quotes(codes)

        index_quotes = {c: quotes[c] for c in INDEX_CODES if c in quotes}
        stock_quotes = {c: q for c, q in quotes.items() if c not in INDEX_CODES}

        for pos in portfolio.get("positions", []):
            q = stock_quotes.get(pos.get("code"))
            if q:
                pos["last_price"] = q["price"]
        save_portfolio(portfolio)

        cash = float(portfolio.get("cash", 0.0))
        positions = portfolio.get("positions", [])
        market_value = 0.0
        pos_lines: list[str] = []
        for pos in positions:
            code = pos.get("code", "")
            shares = int(pos.get("shares", 0) or 0)
            avg = float(pos.get("avg_price", 0) or 0)
            quote = stock_quotes.get(code, {})
            price = float(quote.get("price", pos.get("last_price", avg)) or 0)
            value = shares * price
            market_value += value
            pnl = (price / avg - 1) * 100 if avg else 0.0
            name = pos.get("name") or quote.get("name") or code
            pos_lines.append(f"- {name}({code}): {shares}股，成本{avg:.3f}，现价{price:.3f}，浮盈亏{pnl:+.2f}%")

        total_assets = cash + market_value
        exposure = market_value / total_assets * 100 if total_assets else 0.0
        trend_lines, trend = market_view(index_quotes, stock_quotes)
        op, reason = choose_operation(portfolio, exposure, trend)

        index_line = "；".join(
            f"{INDEX_NAMES.get(code, code)}{q['price']:.2f}({q['pct']:+.2f}%)" for code, q in index_quotes.items()
        ) or "行情不可用"
        last_trade = (portfolio.get("trade_log") or [])[-1] if portfolio.get("trade_log") else None
        last_trade_line = "无历史操作" if not last_trade else f"最近一次：{last_trade.get('time','')} {last_trade.get('action','')} {last_trade.get('name', last_trade.get('code',''))} {last_trade.get('shares','')}股"

        report = f"""A股模拟交易汇报（{stage()}）
时间：{now_str()}

股市情况：
- 指数：{index_line}
- 行情状态：{data_note}

热点/趋势与未来方向：
{trend_lines}

操作情况：
- {op}
- {last_trade_line}

操作原因：
- {reason}

资金情况：
- 现金：{fmt_money(cash)}
- 持仓市值估算：{fmt_money(market_value)}
- 总资产估算：{fmt_money(total_assets)}
- 仓位：{exposure:.1f}%

当前持仓：
{chr(10).join(pos_lines) if pos_lines else '- 空仓'}

风险提示：以上仅为10万元纸面模拟交易记录，不构成投资建议。"""
        print(report, flush=True)
        return 0
    except Exception as exc:
        print(f"A股模拟交易汇报生成失败：{exc.__class__.__name__}: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
