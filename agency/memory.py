"""Agency memory query — on-demand episodic lessons, dreams, and traces.

Usage:
    python -m agency.memory                    # all active lessons (default)
    python -m agency.memory --keyword <word>   # search by tag/keyword
    python -m agency.memory --dreams           # recent dream summaries
    python -m agency.memory --traces           # recent session traces
    python -m agency.memory --all              # everything at once

These files live in ~/.agency/memory/ and are NOT injected into context.
Query them when you need past lessons.
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path.home() / ".agency" / "memory"
EPISODIC_DIR = MEMORY_DIR / "episodic" / "active"
ARCHIVED_DIR = MEMORY_DIR / "episodic" / "archived"
DREAMS_FILE = MEMORY_DIR / "DREAMS.md"
TRACE_DIR = MEMORY_DIR / "trace"


def _parse_frontmatter(text):
    """Extract YAML-like frontmatter from a markdown file."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    meta = {}
    for line in raw.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[end + 3:].strip()


def list_episodic(keyword=None, include_archived=True):
    """List episodic lessons from active + archived dirs, optionally filtered by keyword."""
    # Gather from both active and archived
    files = []
    if EPISODIC_DIR.exists():
        for f in EPISODIC_DIR.glob("*.md"):
            files.append(("active", f))
    if include_archived and ARCHIVED_DIR.exists():
        for f in ARCHIVED_DIR.glob("*.md"):
            files.append(("archived", f))

    if not files:
        return "📋 暂无教训（active 和 archived 均为空）"

    files.sort(key=lambda x: x[1].stat().st_mtime, reverse=True)

    active_count = sum(1 for s, _ in files if s == "active")
    archived_count = sum(1 for s, _ in files if s == "archived")
    label = f"活跃 {active_count} + 归档 {archived_count}"

    lines = [f"🧠 教训 ({label}，共 {len(files)} 条)", "─" * 44]

    shown = 0
    for source, f in files:
        meta, body = _parse_frontmatter(f.read_text(encoding="utf-8"))
        name = meta.get("name", f.stem)
        tags = meta.get("tags", "")

        if keyword:
            kw = keyword.lower()
            if kw not in name.lower() and kw not in tags.lower() and kw not in body.lower():
                continue

        trust = meta.get("trust", "?")
        trust_bar = "█" * min(5, int(float(trust) * 5) if trust != "?" else 0)
        title = body.split("\n")[0].lstrip("#").strip() if body else name
        tag = "" if source == "active" else " [归档]"
        lines.append(f"  {title[:60]}{tag}")
        lines.append(f"  信任:{trust_bar:5s} 标签:{tags or '-'}")
        shown += 1

    if keyword and shown == 0:
        lines.append(f"  (无匹配 '{keyword}')")

    return "\n".join(lines)


def list_dreams(last=5):
    """Show recent dream records from DREAMS.md."""
    if not DREAMS_FILE.exists():
        return "🌙 暂无 Dream 记录"

    text = DREAMS_FILE.read_text(encoding="utf-8")
    # Split by dream entries: entries start with "---\ndreamed:"
    parts = re.split(r"\n---\n(?=dreamed:)", text)
    entries = [p for p in parts if "dreamed:" in p[:50]][-last:]

    if not entries:
        return "🌙 暂无 Dream 记录"

    lines = [f"🌙 最近 Dream ({len(entries)} 条)", "─" * 44]
    for entry in reversed(entries):
        dreamed = re.search(r"dreamed:\s*(.+?)(?:\n|$)", entry)
        ttype = re.search(r"type:\s*(.+?)(?:\n|$)", entry)
        dt = dreamed.group(1).strip() if dreamed else "?"
        tp = ttype.group(1).strip() if ttype else "?"
        # Extract first meaningful heading after frontmatter (## or # title)
        body_match = re.search(r"(?:^|\n)(?:##|#)\s+(.+?)(?:\n|$)", entry)
        first_line = body_match.group(1) if body_match else entry.split("\n")[-1][:70]
        lines.append(f"  {dt} [{tp}]")
        lines.append(f"  {first_line[:65]}")

    return "\n".join(lines)


def list_traces(last=3):
    """Show recent session traces."""
    if not TRACE_DIR.exists():
        return "📊 暂无会话记录"

    files = sorted(TRACE_DIR.glob("*.md"), reverse=True)[:last]
    if not files:
        return "📊 暂无会话记录"

    lines = [f"📊 最近会话 ({len(files)} 条)", "─" * 44]
    for f in files:
        meta, body = _parse_frontmatter(f.read_text(encoding="utf-8"))
        created = meta.get("created", "?")
        topic = meta.get("topic", body.split("\n")[0].lstrip("#").strip() if body else "?")
        corrections = meta.get("corrections", "0")
        models = meta.get("models", "?")
        lines.append(f"  {created} | 纠正:{corrections} | {models}")
        lines.append(f"  {topic[:65]}")

    return "\n".join(lines)


def show_all(keyword=None):
    """Show everything: lessons + recent dreams + recent traces."""
    parts = [list_episodic(keyword=keyword)]
    # Dreams and traces are not keyword-searchable — skip them when filtering
    if not keyword:
        parts.extend(["", list_dreams(last=3), "", list_traces(last=3)])
    parts.extend(["", "💡 用法: @memory | @memory --keyword X | @memory --dreams | @memory --traces"])
    return "\n".join(parts)


def main():
    """CLI entry point."""
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    args = sys.argv[1:]
    keyword = None
    mode = "all"  # all | dreams | traces | episodic

    i = 0
    while i < len(args):
        if args[i] in ("--keyword", "-k") and i + 1 < len(args):
            keyword = args[i + 1]
            i += 2
        elif args[i] == "--dreams":
            mode = "dreams"
            i += 1
        elif args[i] == "--traces":
            mode = "traces"
            i += 1
        elif args[i] == "--episodic":
            mode = "episodic"
            i += 1
        elif args[i] == "--all":
            mode = "all"
            i += 1
        else:
            i += 1

    if mode == "dreams":
        print(list_dreams(last=10))
    elif mode == "traces":
        print(list_traces(last=10))
    elif mode == "episodic":
        print(list_episodic(keyword=keyword))
    else:
        print(show_all(keyword=keyword))


if __name__ == "__main__":
    main()
