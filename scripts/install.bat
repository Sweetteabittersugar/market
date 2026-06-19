@echo off
REM install.bat — Agency v2 Windows CMD 安装
REM 如果装了 Git Bash 优先用 scripts/install.sh

echo ═══ Agency v2 — Install ═══
echo.

REM ── Step 1: pip install ──
echo → Installing agency package...
pip install -e "%~dp0.."
if %ERRORLEVEL% NEQ 0 (
    echo   ✗ pip install failed. Is Python installed? https://python.org
    exit /b 1
)
echo   ✓ agency package installed

REM ── Step 2: Register Stop hook ──
echo → Registering Stop hook...
python -c "import json; from pathlib import Path; p=Path.home()/'.claude'/'settings.json'; s=json.load(open(p)) if p.exists() else {}; hooks=s.setdefault('hooks',{}); stops=hooks.setdefault('Stop',[]); stops.append({'command':'python -m agency.hooks.stop'}); json.dump(s,open(p,'w'),indent=2); print('  ✓ Stop hook registered')"
if %ERRORLEVEL% NEQ 0 (
    echo   ✗ Hook registration failed
    exit /b 1
)

REM ── Step 3: Initialize database ──
echo → Initializing database...
python -c "from agency.db import get_db; get_db().close()"
echo   ✓ Database ready

REM ── Done ──
echo.
echo ═══ Agency v2 installed ═══
echo.
echo   /cost     → python -m agency.cost
echo   /history  → python -m agency.history
echo.
echo   Run: python -m agency.check  to verify
