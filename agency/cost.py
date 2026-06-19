"""Agency cost tracking — pricing, recording, and querying.

Usage:
    python -m agency.cost              # show today/week/month
    python -m agency.cost --days 7     # last 7 days
    python -m agency.cost --month      # this month detail

Pricing is hardcoded here. When a provider changes prices,
edit PRICING_CNY_PER_M and commit with the date of change.
"""

from datetime import datetime, timedelta
from .db import get_db

# ── Pricing: CNY per million tokens ──
# Last updated: 2026-06-19
# Sources:
#   DeepSeek: https://api-docs.deepseek.com/quick_start/pricing (2026.5.22 permanent cut)
#   MiMo: official pricing page
PRICING_CNY_PER_M = {
    "deepseek-v4-pro": {
        "input": 3.0,
        "output": 6.0,
        "cache_read": 0.025,
        "cache_write": 3.0,
    },
    "mimo-v2.5-pro": {
        "input": 3.0,
        "output": 6.0,
        "cache_read": 0.025,
        "cache_write": 3.0,
    },
}


def compute_cost(model, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens):
    """Calculate cost in CNY from token counts. Unknown models fall back to DS pricing."""
    p = PRICING_CNY_PER_M.get(model, PRICING_CNY_PER_M["deepseek-v4-pro"])
    cost = 0.0
    cost += (input_tokens / 1_000_000) * p["input"]
    cost += (output_tokens / 1_000_000) * p["output"]
    cost += (cache_read_tokens / 1_000_000) * p["cache_read"]
    cost += (cache_write_tokens / 1_000_000) * p["cache_write"]
    return round(cost, 4)


def query(days=None):
    """Return formatted cost summary string for /cost command."""
    conn = get_db()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    today_start = today + " 00:00:00"

    # Today
    cur.execute(
        "SELECT COALESCE(SUM(cost_cny), 0) as total, COUNT(*) as sessions "
        "FROM cost_records WHERE ended_at >= ?",
        (today_start,),
    )
    today_row = cur.fetchone()

    # This week (Monday to today)
    weekday = datetime.now().weekday()
    monday = (datetime.now() - timedelta(days=weekday)).strftime("%Y-%m-%d")
    cur.execute(
        "SELECT COALESCE(SUM(cost_cny), 0) FROM cost_records WHERE ended_at >= ?",
        (monday + " 00:00:00",),
    )
    week_total = cur.fetchone()[0]

    # This month
    month_start = datetime.now().strftime("%Y-%m") + "-01"
    cur.execute(
        "SELECT COALESCE(SUM(cost_cny), 0), COUNT(*) FROM cost_records WHERE ended_at >= ?",
        (month_start,),
    )
    month_row = cur.fetchone()

    # By model (this month)
    cur.execute(
        "SELECT model, COALESCE(SUM(cost_cny), 0) as total "
        "FROM cost_records WHERE ended_at >= ? GROUP BY model",
        (month_start,),
    )
    models = cur.fetchall()

    # Build output
    lines = ["📊 Agency 费用", "─────────────"]
    lines.append(
        f"今日 ({today}):  ¥{today_row['total']:.2f}  "
        f"({today_row['sessions']} 次会话)"
    )
    lines.append(f"本周:         ¥{week_total:.2f}")
    lines.append(f"本月:         ¥{month_row[0]:.2f}  ({month_row[1]} 次)")

    # Last month
    if datetime.now().month == 1:
        last_month_start = f"{datetime.now().year - 1}-12-01"
    else:
        last_month_start = f"{datetime.now().year}-{datetime.now().month - 1:02d}-01"
    cur.execute(
        "SELECT COALESCE(SUM(cost_cny), 0) FROM cost_records "
        "WHERE ended_at >= ? AND ended_at < ?",
        (last_month_start, month_start),
    )
    last_month_total = cur.fetchone()[0]
    if last_month_total > 0:
        lines.append(f"上月:         ¥{last_month_total:.2f}")

    # Model breakdown
    if models:
        lines.append("")
        lines.append("按模型 (本月):")
        total = sum(m["total"] for m in models) or 1
        model_names = {
            "deepseek-v4-pro": "DeepSeek V4 Pro",
            "mimo-v2.5-pro": "MiMo V2.5 Pro",
        }
        for m in models:
            name = model_names.get(m["model"], m["model"])
            pct = m["total"] / total * 100
            lines.append(f"  {name}:  ¥{m['total']:.2f} ({pct:.0f}%)")

    # If requested days
    if days:
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        cur.execute(
            "SELECT COALESCE(SUM(cost_cny), 0), COUNT(*) "
            "FROM cost_records WHERE ended_at >= ?",
            (since,),
        )
        d_row = cur.fetchone()
        lines.append("")
        lines.append(f"近 {days} 天:    ¥{d_row[0]:.2f}  ({d_row[1]} 次)")

    return "\n".join(lines)


def record(session_id, model, input_tokens, output_tokens,
           cache_read_tokens, cache_write_tokens, project="unknown"):
    """Insert a cost record. Session ID is UNIQUE — repeat calls are no-ops."""
    cost = compute_cost(model, input_tokens, output_tokens,
                        cache_read_tokens, cache_write_tokens)
    conn = get_db()
    conn.execute(
        """INSERT OR IGNORE INTO cost_records
           (session_id, ended_at, model, input_tokens, output_tokens,
            cache_read_tokens, cache_write_tokens, cost_cny, project)
           VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)""",
        (session_id, model, input_tokens, output_tokens,
         cache_read_tokens, cache_write_tokens, cost, project),
    )
    conn.commit()
    return cost


def main():
    """CLI entry point for console_scripts and python -m agency.cost."""
    import sys
    # Force UTF-8 on Windows (GBK chokes on emoji)
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    days = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--days" and i + 1 < len(args):
            days = int(args[i + 1])
            i += 2
        elif args[i] == "--month":
            days = 30
            i += 1
        else:
            i += 1
    print(query(days=days))


# ── CLI entry point ──
if __name__ == "__main__":
    main()
