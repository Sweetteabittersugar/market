#!/usr/bin/env python3
"""Agency SessionStart hook — model reminder + memory injection.

Called by Claude Code at session start via settings.json:
    {
      "hooks": {
        "SessionStart": [{"command": "python -m agency.hooks.session_start"}]
      }
    }

Reads handoff.md for current stage → model mismatch reminder.
Reads ~/.agency/memory/ → injects policy/preference/fact/episodic into context.
Silent on failure — never blocks session start.
"""

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# ── Stage → Model mapping (must match workflow.sh) ──
STAGE_MODEL = {
    "-1": "DeepSeek V4 Pro",
    "0": "DeepSeek V4 Pro",
    "1": "DeepSeek V4 Pro",
    "2": "DeepSeek V4 Pro",
    "3": "DeepSeek V4 Pro",
    "4": "DeepSeek V4 Pro",
    "5": "MiMo V2.5 Pro",
    "6": "DeepSeek V4 Pro",
    "7": "MiMo V2.5 Pro",
    "8": "DeepSeek V4 Pro",
    "9": "DeepSeek V4 Pro",
}

MEMORY_ROOT = Path.home() / ".agency" / "memory"
EPISODIC_EXPIRY_SEC = 90 * 24 * 3600  # 90 days


def strip_frontmatter(content):
    """Strip YAML frontmatter (--- ... ---) from content.
    Returns body only — frontmatter is metadata for the system, not for the LLM."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content


def find_handoff(cwd):
    """Search for handoff.md from cwd upward."""
    p = Path(cwd)
    while p != p.parent:
        candidate = p / ".context" / "handoff.md"
        if candidate.exists():
            return candidate
        p = p.parent
    return None


def extract_stage(handoff_path):
    """Extract current stage number from handoff.md.

    Expected format: ## stage: N  (line starts with exactly this)
    """
    try:
        text = handoff_path.read_text(encoding="utf-8")
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("## stage:") or line.startswith("## Stage:"):
                after = line.split(":", 1)[1].strip()
                import re
                m = re.search(r"(-?\d+)", after)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return None


def read_md_files(directory, seen_hashes):
    """Read all .md files in a directory, return list of (name, body) tuples.
    Strips YAML frontmatter, skips empty files and SHA256 duplicates."""
    results = []
    if not directory.is_dir():
        return results
    for f in sorted(directory.glob("*.md")):
        try:
            raw = f.read_text(encoding="utf-8").strip()
            if not raw:
                continue
            body = strip_frontmatter(raw)
            if not body:
                continue
            h = hashlib.sha256(body.encode()).hexdigest()
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            results.append((f.name, body))
        except Exception:
            pass
    return results


def find_project_slug(cwd):
    """Derive a stable project slug from git remote or path.
    Uses origin URL basename (strips .git) for stability across moves.
    Falls back to path-derived slug."""
    try:
        p = Path(cwd).resolve()
        # Try git remote first — stable across directory moves
        import subprocess
        result = subprocess.run(
            ["git", "-C", str(p), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            url = result.stdout.strip()
            # Extract repo name from URL: git@github.com:user/repo.git → repo
            slug = url.rstrip("/").split("/")[-1].replace(".git", "")
            if slug:
                return slug
    except Exception:
        pass
    # Fallback: use last 2 path components
    try:
        p = Path(cwd).resolve()
        parts = [x for x in p.parts[-2:] if x and not x.startswith(".")]
        return "-".join(parts).lower().replace(" ", "-") or "unknown"
    except Exception:
        return "unknown"


def inject_memory(cwd):
    """Read memory from ~/.agency/memory/ and format for context injection.

    Injection order (matching industry best practices):
      1. policy/     — hard constraints, pinned at top
      2. preference/ — user preferences
      3. fact/       — project context (if in a known project)
      4. episodic/active/ — recent lessons, top 3 by recency

    Dedup: SHA256 exact-match across ALL sections (a lesson duplicated
           in policy and episodic only appears once, in policy).
    Expiry: episodic/active files >90 days old → auto-migrated to archived/.
    """
    if not MEMORY_ROOT.is_dir():
        return "", []

    now = time.time()
    seen_hashes = set()
    sections = []  # [(label, body), ...]
    migrated = []

    # ── 1. Policy (always inject all) ──
    policy_files = read_md_files(MEMORY_ROOT / "policy", seen_hashes)
    if policy_files:
        bodies = [b for _, b in policy_files]
        sections.append(("[Policy]", "\n\n---\n\n".join(bodies)))

    # ── 2. Preference (always inject all) ──
    pref_files = read_md_files(MEMORY_ROOT / "preference", seen_hashes)
    if pref_files:
        bodies = [b for _, b in pref_files]
        sections.append(("[Preference]", "\n\n---\n\n".join(bodies)))

    # ── 3. Fact (project-specific: match by filename slug or frontmatter scope) ──
    if cwd:
        slug = find_project_slug(cwd)
        fact_dir = MEMORY_ROOT / "fact"
        if fact_dir.is_dir():
            for f in sorted(fact_dir.glob("*.md")):
                # Match: filename contains slug OR frontmatter scope matches
                if slug not in f.stem.lower():
                    # Check frontmatter scope as fallback
                    try:
                        raw = f.read_text(encoding="utf-8")
                        m = re.search(r"scope:\s*project:(\S+)", raw)
                        if not m or slug not in m.group(1).lower():
                            continue
                    except Exception:
                        continue
                try:
                    raw = f.read_text(encoding="utf-8").strip()
                    if not raw:
                        continue
                    body = strip_frontmatter(raw)
                    if not body:
                        continue
                    h = hashlib.sha256(body.encode()).hexdigest()
                    if h in seen_hashes:
                        continue
                    seen_hashes.add(h)
                    sections.append(("[Fact]", body))
                except Exception:
                    pass

    # ── 4. Episodic/active (top 3 by recency, with expiry) ──
    active_dir = MEMORY_ROOT / "episodic" / "active"
    archived_dir = MEMORY_ROOT / "episodic" / "archived"
    if active_dir.is_dir():
        episodic = []
        for f in sorted(active_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                raw = f.read_text(encoding="utf-8").strip()
                if not raw:
                    continue
                body = strip_frontmatter(raw)
                if not body:
                    continue
                # Expiry check → auto-migrate to archived
                mtime = f.stat().st_mtime
                if now - mtime > EPISODIC_EXPIRY_SEC:
                    archived_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        f.rename(archived_dir / f.name)
                        migrated.append(f.name)
                    except Exception:
                        pass
                    continue
                # Dedup
                h = hashlib.sha256(body.encode()).hexdigest()
                if h in seen_hashes:
                    continue
                seen_hashes.add(h)
                episodic.append(body)
                if len(episodic) >= 3:
                    break
            except Exception:
                pass
        if episodic:
            sections.append(("[Episodic]", "\n\n---\n\n".join(episodic)))

    if not sections:
        return "", migrated

    # Format output with labelled sections
    out_parts = []
    for label, body in sections:
        out_parts.append(f"## {label}\n{body}")
    output = "\n\n".join(out_parts)

    if migrated:
        output += f"\n\n[Agency] {len(migrated)} 条教训超过90天，已自动归档: {', '.join(migrated)}"

    return output, migrated


def main():
    # Fix Windows GBK encoding so Chinese characters don't get garbled
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return

        hook_data = json.loads(raw)
        cwd = hook_data.get("cwd", "")

        parts = []

        # ── Model reminder ──
        handoff = find_handoff(cwd) if cwd else None
        if handoff:
            stage = extract_stage(handoff)
            if stage and stage in STAGE_MODEL:
                expected = STAGE_MODEL[stage]
                parts.append(
                    f"[Agency] 当前阶段 {stage} → 推荐模型: {expected}。"
                    f"运行 source scripts/workflow.sh {stage} 切换。"
                )

        # ── Memory injection ──
        memory, _migrated = inject_memory(cwd)
        if memory.strip():
            parts.append(memory)

        # ── Dreaming check (only for D:\ai project, 8h cooldown) ──
        dream_script = Path(cwd) / "scripts" / "dream.py"
        if dream_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(dream_script)],
                    capture_output=True, text=True, timeout=60,
                    cwd=cwd
                )
                dream_output = result.stdout.strip()
                if dream_output:
                    parts.append(dream_output)
            except Exception:
                pass  # dreaming failure never blocks session start

        # ── Sync check ──
        src_agents = Path(__file__).resolve().parent.parent.parent.parent / "agents"
        deployed_agents = Path.home() / ".claude" / "agents"
        if src_agents.is_dir() and deployed_agents.is_dir():
            try:
                src_newest = max(f.stat().st_mtime for f in src_agents.glob("*.md"))
                deployed_newest = max(f.stat().st_mtime for f in deployed_agents.glob("*.md"))
                if src_newest > deployed_newest + 60:
                    parts.append(
                        "[Agency] agents/skills 有更新。运行 bash install.sh --sync 同步。"
                    )
            except Exception:
                pass

        if parts:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "\n\n".join(parts),
                }
            }
            print(json.dumps(output, ensure_ascii=False))

    except Exception:
        # Never block session start
        pass


if __name__ == "__main__":
    main()
