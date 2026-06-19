"""Agency database — SQLite single file at ~/.agency/agency.db.

No ORM, no migrations, no dependencies beyond Python stdlib.
Kept intentionally simple — one person can read and understand it in 2 minutes.
"""

import sqlite3
from pathlib import Path

DB_DIR = Path.home() / ".agency"
DB_PATH = DB_DIR / "agency.db"


def get_db():
    """Return a SQLite connection with tables guaranteed to exist.

    Creates ~/.agency/ directory and agency.db on first call.
    All callers get the same file — no multi-process locking needed
    because only one Claude Code session runs at a time.
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn):
    """Create tables if they don't exist. Idempotent — safe to call every time."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS cost_records (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id          TEXT NOT NULL UNIQUE,
            ended_at            TEXT NOT NULL,
            model               TEXT NOT NULL,
            input_tokens        INTEGER NOT NULL DEFAULT 0,
            output_tokens       INTEGER NOT NULL DEFAULT 0,
            cache_read_tokens   INTEGER NOT NULL DEFAULT 0,
            cache_write_tokens  INTEGER NOT NULL DEFAULT 0,
            cost_cny            REAL NOT NULL DEFAULT 0.0,
            project             TEXT NOT NULL DEFAULT 'unknown'
        );

        CREATE TABLE IF NOT EXISTS task_records (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT NOT NULL,
            created_at      TEXT NOT NULL,
            agent_name      TEXT NOT NULL,
            task_summary    TEXT NOT NULL,
            files_touched   TEXT,
            tool_calls      INTEGER DEFAULT 0,
            tokens_used     INTEGER DEFAULT 0,
            status          TEXT NOT NULL DEFAULT 'completed',
            cost_cny        REAL DEFAULT 0.0
        );

        CREATE INDEX IF NOT EXISTS idx_cost_ended_at ON cost_records(ended_at);
        CREATE INDEX IF NOT EXISTS idx_cost_model ON cost_records(model);
        CREATE INDEX IF NOT EXISTS idx_task_created_at ON task_records(created_at);
        CREATE INDEX IF NOT EXISTS idx_task_agent ON task_records(agent_name);
        CREATE INDEX IF NOT EXISTS idx_task_session ON task_records(session_id);
    """
    )
    conn.commit()
