"""Agency task history — recording and querying agent execution records.

Usage:
    python -m agency.history               # last 10 records
    python -m agency.history --last 20     # last 20
    python -m agency.history --agent coder # filter by agent
    python -m agency.history --today       # today only
"""

from datetime import datetime
from .db import get_db


def query(last=10, agent=None, today=False):
    """Return formatted task history string for /history command."""
    conn = get_db()
    cur = conn.cursor()

    where = []
    params = []

    if agent:
        where.append("agent_name = ?")
        params.append(agent)
    if today:
        where.append("created_at >= ?")
        params.append(datetime.now().strftime("%Y-%m-%d") + " 00:00:00")

    sql = "SELECT * FROM task_records"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(last)

    cur.execute(sql, params)
    rows = cur.fetchall()

    if not rows:
        return "📋 暂无执行记录"

    lines = [f"📋 Agent 执行记录 (最近 {len(rows)} 条)", "─" * 44]
    status_icon = {"completed": "✅", "failed": "❌", "aborted": "⚠️"}

    for r in rows:
        dt = r["created_at"][:16].replace("T", " ") if "T" in r["created_at"] else r["created_at"][:16]
        icon = status_icon.get(r["status"], "❓")
        agent_name = r["agent_name"].ljust(12)
        summary = r["task_summary"][:30]
        files = f"{r['tool_calls']} calls" if r["tool_calls"] else ""
        cost = f"¥{r['cost_cny']:.2f}" if r["cost_cny"] else ""
        lines.append(f"{dt}  {agent_name} {summary:30s} {files:10s} {cost:>8s} {icon}")

    return "\n".join(lines)


def record(session_id, agent_name, task_summary, files_touched=None,
           tool_calls=0, tokens_used=0, status="completed", cost_cny=0.0):
    """Insert a task record."""
    import json
    conn = get_db()
    files_json = json.dumps(files_touched) if files_touched else None
    conn.execute(
        """INSERT INTO task_records
           (session_id, created_at, agent_name, task_summary, files_touched,
            tool_calls, tokens_used, status, cost_cny)
           VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)""",
        (session_id, agent_name, task_summary, files_json,
         tool_calls, tokens_used, status, cost_cny),
    )
    conn.commit()


def main():
    """CLI entry point for console_scripts and python -m agency.history."""
    import sys
    # Force UTF-8 on Windows (GBK chokes on emoji)
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    last = 10
    agent = None
    today = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--last" and i + 1 < len(args):
            last = int(args[i + 1])
            i += 2
        elif args[i] == "--agent" and i + 1 < len(args):
            agent = args[i + 1]
            i += 2
        elif args[i] == "--today":
            today = True
            i += 1
        else:
            i += 1
    print(query(last=last, agent=agent, today=today))


# ── CLI entry point ──
if __name__ == "__main__":
    main()
