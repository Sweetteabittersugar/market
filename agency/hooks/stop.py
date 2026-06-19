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
        if models:
            project = extract_project(cwd)
            write_cost_records(session_id, models, project)

    except Exception:
        log_error(f"Stop hook exception:\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
