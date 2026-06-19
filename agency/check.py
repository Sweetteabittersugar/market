"""Agency pre-flight check — verify everything is set up correctly.

Usage:
    python -m agency.check
    python -m agency.check --json   # machine-readable output
"""

import os
import sys
import json
import shutil
from pathlib import Path


def check_node():
    """Node.js ≥ 18 (required by Claude Code)."""
    ok = shutil.which("node") is not None
    detail = ""
    if ok:
        import subprocess
        try:
            r = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
            detail = r.stdout.strip()
        except Exception:
            detail = "已安装"
    return {
        "name": "Node.js",
        "ok": ok,
        "detail": detail or "未安装",
        "fix": "Claude Code 需要 Node.js ≥ 18，请安装 https://nodejs.org" if not ok else "",
    }


def check_python():
    """Python version ≥ 3.8."""
    v = sys.version_info
    ok = v.major == 3 and v.minor >= 8
    return {
        "name": "Python",
        "ok": ok,
        "detail": f"{v.major}.{v.minor}.{v.micro}",
        "fix": "需要 Python ≥ 3.8，请升级" if not ok else "",
    }


def check_pip():
    """pip is available."""
    ok = shutil.which("pip") is not None or shutil.which("pip3") is not None
    return {
        "name": "pip",
        "ok": ok,
        "detail": shutil.which("pip") or shutil.which("pip3") or "已安装",
        "fix": "请安装 pip" if not ok else "",
    }


def check_claude_code():
    """Claude Code CLI is installed."""
    ok = shutil.which("claude") is not None or shutil.which("claude-code") is not None
    path = shutil.which("claude") or shutil.which("claude-code") or ""
    return {
        "name": "Claude Code",
        "ok": ok,
        "detail": path,
        "fix": "请安装 Claude Code (https://claude.ai/code)" if not ok else "",
    }


def check_cc_switch():
    """CC Switch profiles exist."""
    profiles = [
        Path.home() / ".cl" / "profiles.yaml",
        Path.home() / ".claude" / "profiles.yaml",
        Path.home() / ".cl" / "settings.json",
    ]
    found = [p for p in profiles if p.exists()]
    # Also check if CC Switch proxy is configured
    proxy_configured = os.environ.get("ANTHROPIC_BASE_URL", "").startswith("http://127.0.0.1")
    ok = len(found) > 0 or proxy_configured
    return {
        "name": "CC Switch",
        "ok": ok,
        "detail": f"{len(found)} 个配置文件" if found else ("检测到本地代理" if proxy_configured else "未检测到"),
        "fix": "请安装 CC Switch 并配置模型" if not ok else "",
    }


def check_deepseek_key():
    """DeepSeek API key is configured somewhere."""
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    # Also check common CC Switch env patterns
    if not key:
        # CC Switch might proxy through Anthropic-compatible endpoint
        key_configured = os.environ.get("ANTHROPIC_BASE_URL", "").find("deepseek") != -1
        return {
            "name": "DeepSeek Key",
            "ok": key_configured,
            "detail": "通过 CC Switch 代理" if key_configured else "未检测到",
            "fix": "请在 CC Switch 中添加 DeepSeek 配置" if not key_configured else "",
        }
    return {
        "name": "DeepSeek Key",
        "ok": True,
        "detail": "已设置 (DEEPSEEK_API_KEY)",
        "fix": "",
    }


def check_settings_hook():
    """Agency Stop hook is registered in settings.json or settings.local.json."""
    settings = Path.home() / ".claude" / "settings.json"
    local_settings = Path.cwd() / ".claude" / "settings.local.json"

    # Collect all Stop hooks from both global and local settings
    all_stop_hooks = []

    for settings_path in [settings, local_settings]:
        if not settings_path.exists():
            continue
        try:
            content = settings_path.read_bytes()
            # Handle BOM in settings.local.json
            if content.startswith(b'\xef\xbb\xbf'):
                content = content[3:]
            s = json.loads(content)
            stop_entries = s.get("hooks", {}).get("Stop", [])
            for entry in stop_entries:
                for h in entry.get("hooks", []):
                    all_stop_hooks.append(h.get("command", ""))
        except Exception:
            pass

    if not all_stop_hooks:
        return {
            "name": "Stop hook",
            "ok": False,
            "detail": "未注册任何 Stop hook",
            "fix": "运行 bash scripts/install.sh",
        }

    found = any("agency.hooks.stop" in cmd for cmd in all_stop_hooks)
    return {
        "name": "Stop hook",
        "ok": found,
        "detail": "已注册" if found else f"未注册 ({len(all_stop_hooks)} 个其他 Stop hook)",
        "fix": "运行 bash scripts/install.sh" if not found else "",
    }


def check_database():
    """Database exists and is writable."""
    db_path = Path.home() / ".agency" / "agency.db"
    if db_path.exists():
        # Check writable
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            conn.execute("SELECT 1")
            conn.close()
            size_kb = db_path.stat().st_size / 1024
            return {
                "name": "数据库",
                "ok": True,
                "detail": f"{db_path} ({size_kb:.0f} KB)",
                "fix": "",
            }
        except Exception:
            return {
                "name": "数据库",
                "ok": False,
                "detail": "数据库文件损坏",
                "fix": f"删掉 {db_path} 重试",
            }
    else:
        return {
            "name": "数据库",
            "ok": True,  # Will be created on first use
            "detail": "尚未创建（首次安装后自动初始化）",
            "fix": "",
        }


def check_all():
    """Run all checks, return list of results."""
    return [
        check_python(),
        check_pip(),
        check_node(),
        check_claude_code(),
        check_cc_switch(),
        check_deepseek_key(),
        check_settings_hook(),
        check_database(),
    ]


def format_text(results):
    """Human-readable output."""
    ok_count = sum(1 for r in results if r["ok"])
    total = len(results)
    lines = ["🔍 Agency v2 环境检查", "─" * 30]

    for r in results:
        if r["ok"]:
            i = "✅"
        elif r["name"] in ("数据库",):
            i = "ℹ️ "  # Not created yet is OK
        elif r["name"] in ("DeepSeek Key", "CC Switch"):
            i = "⚠️ "  # Might work through proxy
        else:
            i = "❌"
        lines.append(f"{i} {r['name']:18s} {r['detail']}")
        if r["fix"]:
            lines.append(f"   → {r['fix']}")

    lines.append("─" * 30)
    if ok_count == total:
        lines.append("✅ 全部通过")
    else:
        lines.append(f"⚠️  {ok_count}/{total} 项通过，{total - ok_count} 项需处理")

    # Feature summary — always show
    lines.append("")
    lines.append("📦 已安装功能：")
    lines.append("  /cost      费用追踪（自动，会话结束后可查）")
    lines.append("  /history   Agent 执行记录")
    lines.append("  /memory    记忆查询（教训/Dream/会话，按需不注入）")
    lines.append("  /help      内置说明书")
    lines.append("  @agent名   20+ Agent 自动路由")
    lines.append("")
    lines.append("💡 在 Claude Code 里输入 /help 开始探索")
    return "\n".join(lines)


def main():
    """CLI entry point."""
    results = check_all()
    if "--json" in sys.argv:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        # Force UTF-8 on Windows
        if sys.platform == "win32":
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        print(format_text(results))


if __name__ == "__main__":
    main()
