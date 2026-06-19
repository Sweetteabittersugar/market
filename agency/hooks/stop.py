#!/usr/bin/env python3
"""Agency Stop Hook — parse Claude Code transcript, record cost and task data.

Called by Claude Code at session end via settings.json:
    {
      "hooks": {
        "Stop": [{"command": "python -m agency.hooks.stop"}]
      }
    }

Receives JSON on stdin: {session_id, transcript_path, cwd, stop_reason}
Reads the session JSONL, extracts usage data, writes to ~/.agency/agency.db.
Silent on success — errors go to ~/.agency/errors.log, never to the user.
"""

import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

# ── Paths ──
AGENCY_DIR = Path.home() / ".agency"
ERROR_LOG = AGENCY_DIR / "errors.log"


def log_error(msg):
    """Append error to log file. Creates directory if needed."""
    AGENCY_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")


def extract_usage_from_transcript(transcript_path):
    """Parse JSONL transcript and return per-model token totals.

    Each line in the JSONL is a JSON object. Lines where
    message.role == "assistant" and message.usage exists
    contain the token counts we need.

    IMPORTANT: Each API response appears MULTIPLE times in the JSONL
    (streaming chunks). We deduplicate by message.id to avoid
    double/triple counting.

    Returns dict: {model: {input_tokens, output_tokens, cache_read, cache_write}}
    """
    models = {}
    seen_ids = set()  # dedup: one API call = many JSONL lines

    if not os.path.exists(transcript_path):
        return models

    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg = data.get("message", {})
            if msg.get("role") != "assistant":
                continue

            usage = msg.get("usage")
            if not usage:
                continue

            # Dedup by message.id — streaming produces duplicate entries
            msg_id = msg.get("id", "")
            if msg_id and msg_id in seen_ids:
                continue
            if msg_id:
                seen_ids.add(msg_id)

            model = msg.get("model", "unknown")

            if model not in models:
                models[model] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_read": 0,
                    "cache_write": 0,
                }

            m = models[model]
            m["input_tokens"] += usage.get("input_tokens", 0)
            m["output_tokens"] += usage.get("output_tokens", 0)
            m["cache_read"] += usage.get("cache_read_input_tokens", 0)

            # cache_creation_input_tokens is the Anthropic field for cache writes
            cc = usage.get("cache_creation", {})
            if isinstance(cc, dict):
                m["cache_write"] += cc.get("ephemeral_1h_input_tokens", 0)
                m["cache_write"] += cc.get("ephemeral_5m_input_tokens", 0)
            # Also check flat field (some API versions)
            m["cache_write"] += usage.get("cache_creation_input_tokens", 0)

    return models


def write_cost_records(session_id, models, project="unknown"):
    """Write one cost_records row per model used in this session.

    Uses the agency.cost module for pricing computation.
    Import here to avoid circular dependency and keep hook runnable standalone.
    """
    # Inline pricing to avoid import issues when run as raw script
    PRICING = {
        "deepseek-v4-pro": {"input": 3.0, "output": 6.0, "cache_read": 0.025, "cache_write": 3.0},
        "mimo-v2.5-pro": {"input": 3.0, "output": 6.0, "cache_read": 0.025, "cache_write": 3.0},
    }

    import sqlite3
    db_path = AGENCY_DIR / "agency.db"
    AGENCY_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))

    # Ensure tables exist
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cost_records (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id          TEXT NOT NULL,
            ended_at            TEXT NOT NULL,
            model               TEXT NOT NULL,
            input_tokens        INTEGER NOT NULL DEFAULT 0,
            output_tokens       INTEGER NOT NULL DEFAULT 0,
            cache_read_tokens   INTEGER NOT NULL DEFAULT 0,
            cache_write_tokens  INTEGER NOT NULL DEFAULT 0,
            cost_cny            REAL NOT NULL DEFAULT 0.0,
            project             TEXT NOT NULL DEFAULT 'unknown',
            UNIQUE(session_id, model)
        );
    """)

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    for model, tokens in models.items():
        # Skip models with no actual usage (e.g. <synthetic>)
        if tokens["input_tokens"] == 0 and tokens["output_tokens"] == 0:
            continue

        p = PRICING.get(model, PRICING["deepseek-v4-pro"])
        cost = 0.0
        cost += (tokens["input_tokens"] / 1_000_000) * p["input"]
        cost += (tokens["output_tokens"] / 1_000_000) * p["output"]
        cost += (tokens["cache_read"] / 1_000_000) * p["cache_read"]
        cost += (tokens["cache_write"] / 1_000_000) * p["cache_write"]
        cost = round(cost, 4)

        conn.execute(
            """INSERT OR IGNORE INTO cost_records
               (session_id, ended_at, model, input_tokens, output_tokens,
                cache_read_tokens, cache_write_tokens, cost_cny, project)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, now, model,
             tokens["input_tokens"], tokens["output_tokens"],
             tokens["cache_read"], tokens["cache_write"],
             cost, project),
        )

    conn.commit()
    conn.close()


def extract_project(cwd):
    """Derive project name from working directory.

    Tries git remote origin first, falls back to directory name.
    """
    if not cwd:
        return "unknown"
    try:
        import subprocess
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Extract repo name from URL
            url = result.stdout.strip()
            name = url.rstrip("/").split("/")[-1]
            if name.endswith(".git"):
                name = name[:-4]
            return name
    except Exception:
        pass
    return os.path.basename(cwd.rstrip("/\\")) or "unknown"


# ── Trace: lightweight transcript summary for Dreaming ──

def _build_highlights(tool_counts, files_touched, corrections, user_msg_count):
    """Categorize session activity by tool usage patterns.

    Returns markdown bullet list, one line per category.
    """
    highlights = []

    # Structural changes: Write + Edit count
    writes = tool_counts.get("Write", 0)
    edits = tool_counts.get("Edit", 0)
    if writes + edits > 50:
        highlights.append(f"- **大规模改动**: {writes + edits} 次文件操作（Write {writes} + Edit {edits}）")
    elif writes + edits > 10:
        highlights.append(f"- **文件修改**: {writes + edits} 次（Write {writes} + Edit {edits}）")

    # Agent delegation
    agents = tool_counts.get("Agent", 0)
    if agents > 20:
        highlights.append(f"- **重度 Agent 协作**: {agents} 次 subagent 派发")
    elif agents > 0:
        highlights.append(f"- **Agent 协作**: {agents} 次派发")

    # Research / Web
    web = tool_counts.get("WebSearch", 0) + tool_counts.get("WebFetch", 0)
    if web > 30:
        highlights.append(f"- **重度调研**: {web} 次 WebSearch/Fetch")

    # Debugging / iteration
    if corrections > 20:
        highlights.append(f"- **高纠正率**: {corrections} 次纠正信号，可能方向不明确或多次试错")

    # Config changes
    settings_edits = sum(1 for f in files_touched if "settings" in f.lower())
    if settings_edits > 0:
        highlights.append(f"- **配置修改**: {settings_edits} 个 settings 文件改动")

    # Memory changes
    memory_edits = sum(1 for f in files_touched if "memory" in f.lower() or "lessons" in f.lower())
    if memory_edits > 0:
        highlights.append(f"- **记忆更新**: {memory_edits} 个 memory 文件")

    return "\n".join(highlights) if highlights else ""

def extract_trace(transcript_path, session_id):
    """Extract a lightweight trace summary from a JSONL transcript.

    No API calls — pure text extraction. Extracts:
      - Session topic (first user message, truncated)
      - Correction count (how many times user said "不对"/"错了"/"停")
      - Tool usage summary (counts by tool name)
      - Files touched (deduped list from Write/Edit calls)
      - Model(s) used

    Returns a dict ready for YAML frontmatter + markdown body.
    Returns None if transcript can't be read.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return None

    topic = ""
    corrections = 0
    tool_counts = {}
    files_touched = set()
    models_seen = set()
    user_msg_count = 0
    assistant_msg_count = 0
    total_chars = 0

    correction_keywords = ["不对", "错了", "停", "停下", "换方向", "重新",
                           "wrong", "stop", "fix this", "redo"]

    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg = data.get("message", {})
                role = msg.get("role", "")
                content = msg.get("content", "")

                # Track total size
                if isinstance(content, str):
                    total_chars += len(content)

                # Capture first user message as session topic
                if role == "user" and not topic and content:
                    text = str(content).strip()
                    # Take first line or first 80 chars
                    first_line = text.split("\n")[0][:120]
                    topic = first_line
                    user_msg_count += 1
                elif role == "user":
                    user_msg_count += 1
                    # Check for correction signals
                    if isinstance(content, str):
                        lower = content.lower()
                        if any(kw in lower for kw in correction_keywords):
                            corrections += 1
                elif role == "assistant":
                    assistant_msg_count += 1
                    # Track models
                    model = msg.get("model", "")
                    if model:
                        models_seen.add(model)

                # Track tool usage from top-level tool_use events
                # Claude Code JSONL embeds tool calls differently — check content type
                tool_use = data.get("tool_use") or msg.get("tool_use") or {}
                if not tool_use:
                    # Also check for content blocks with tool_use type
                    cblocks = msg.get("content", [])
                    if isinstance(cblocks, list):
                        for block in cblocks:
                            if isinstance(block, dict) and block.get("type") == "tool_use":
                                tool_name = block.get("name", "unknown")
                                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
                                # Track files from file-editing tools
                                inp = block.get("input", {})
                                fp = inp.get("file_path", inp.get("path", ""))
                                if fp:
                                    files_touched.add(fp)

                # Top-level tool_use
                if isinstance(tool_use, dict) and tool_use.get("name"):
                    tool_name = tool_use.get("name", "unknown")
                    tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
                    fp = tool_use.get("input", {}).get("file_path", "")
                    if fp:
                        files_touched.add(fp)

    except Exception:
        return None

    if not topic and user_msg_count == 0:
        return None  # Empty or unreadable transcript

    # Build markdown body
    body_parts = []
    body_parts.append(f"**Topic**: {topic or '(no user message)'}")
    body_parts.append(f"**Messages**: {user_msg_count} user / {assistant_msg_count} assistant")
    body_parts.append(f"**Corrections**: {corrections}")

    if models_seen:
        body_parts.append(f"**Models**: {', '.join(sorted(models_seen))}")

    if tool_counts:
        tc = ", ".join(f"{k}×{v}" for k, v in sorted(tool_counts.items(), key=lambda x: -x[1])[:10])
        body_parts.append(f"**Tools**: {tc}")

    if files_touched:
        MAX_FILES = 15
        files_list = sorted(files_touched)[:MAX_FILES]
        files_str = "\n".join(f"- `{f}`" for f in files_list)
        if len(files_touched) > MAX_FILES:
            files_str += f"\n- ... and {len(files_touched) - MAX_FILES} more"
        body_parts.append(f"**Files**:\n{files_str}")

    # Highlights: categorize session activity by tool patterns
    highlights = _build_highlights(tool_counts, files_touched, corrections, user_msg_count)
    if highlights:
        body_parts.append(f"**Highlights**:\n{highlights}")

    return {
        "topic": topic[:120],
        "corrections": corrections,
        "tool_counts": tool_counts,
        "files_touched": sorted(files_touched),
        "models": sorted(models_seen),
        "body": "\n\n".join(body_parts),
    }


def write_trace(session_id, trace_data, project="unknown"):
    """Write a trace summary file to ~/.agency/memory/trace/."""
    if not trace_data:
        return

    trace_dir = AGENCY_DIR / "memory" / "trace"
    trace_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    slug = session_id[:8] if session_id else "unknown"

    # YAML frontmatter + markdown body
    content = f"""---
id: trace-{slug}
type: trace
scope: project:{project}
created: {date_str}
updated: {date_str}
expires: {int(now.timestamp() + 90 * 24 * 3600)}
trust: 1.0
tags: [session-trace, project:{project}]
source: stop-hook
corrections: {trace_data['corrections']}
models: [{', '.join(trace_data['models'])}]
tools: [{', '.join(f'{k}:{v}' for k, v in sorted(trace_data['tool_counts'].items()))}]
---

# Session {slug}

{trace_data['body']}
"""
    trace_file = trace_dir / f"{date_str}-{slug}.md"
    try:
        trace_file.write_text(content, encoding="utf-8")
    except Exception:
        pass  # Trace writing is best-effort, never blocks session end


def main():
    """Main entry point. Reads hook data from stdin, processes transcript."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            log_error("Stop hook: no stdin data")
            return

        hook_data = json.loads(raw)
        session_id = hook_data.get("session_id", "")
        transcript_path = hook_data.get("transcript_path", "")
        cwd = hook_data.get("cwd", "")

        if not transcript_path:
            log_error(f"Stop hook: no transcript_path in hook data. Keys: {list(hook_data.keys())}")
            return

        # Extract and record
        models = extract_usage_from_transcript(transcript_path)
        project = extract_project(cwd)
        if models:
            write_cost_records(session_id, models, project)

        # Extract and write trace (best-effort, never block cost recording)
        try:
            trace = extract_trace(transcript_path, session_id)
            if trace:
                write_trace(session_id, trace, project)
        except Exception:
            pass  # Trace writing failure is non-critical

    except Exception:
        log_error(f"Stop hook exception:\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
