#!/bin/bash
# install.sh — Agency v2 one-command install
# Usage: bash install.sh
#
# What it does:
#   1. pip install the agency package
#   2. Register Stop hook in ~/.claude/settings.json
#   3. Initialize database
#   4. Print success message

set -e

AGENCY_DIR="$HOME/.agency"
SETTINGS_FILE="$HOME/.claude/settings.json"

echo "═══ Agency v2 — Install ═══"
echo ""

# ── Step 1: pip install ──
echo "→ Installing agency package..."
pip install -e "$(dirname "$0")/.." 2>/dev/null || pip install "$(dirname "$0")/.."
echo "  ✓ agency package installed"

# ── Step 2: Register Stop hook ──
echo "→ Registering Stop hook..."

if [ -f "$SETTINGS_FILE" ]; then
    # Check if hook already registered (checks both simple and nested formats)
    if python3 -c "
import json
with open('$SETTINGS_FILE') as f:
    s = json.load(f)
stop_hooks = s.get('hooks', {}).get('Stop', [])
found = False
for h in stop_hooks:
    # Simple format: {'command': '...'}
    if 'agency.hooks.stop' in h.get('command', ''):
        found = True
    # Nested format: {'hooks': [{'command': '...'}]}
    for sub in h.get('hooks', []):
        if 'agency.hooks.stop' in sub.get('command', ''):
            found = True
exit(1 if found else 0)
" 2>/dev/null; then
        # Hook not yet registered — add it
        python3 -c "
import json
with open('$SETTINGS_FILE') as f:
    s = json.load(f)
hooks = s.setdefault('hooks', {})
stop_hooks = hooks.setdefault('Stop', [])
stop_hooks.append({'command': 'python -m agency.hooks.stop'})
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(s, f, indent=2)
"
        echo "  ✓ Stop hook registered"
    else
        echo "  • Stop hook already registered (skipping)"
    fi
else
    # Create new settings.json
    mkdir -p "\$(dirname \"$SETTINGS_FILE\")"
    python3 -c "
import json
s = {'hooks': {'Stop': [{'command': 'python -m agency.hooks.stop'}]}}
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(s, f, indent=2)
"
    echo "  ✓ Created $SETTINGS_FILE with Stop hook"
fi

# ── Step 3: Initialize database ──
echo "→ Initializing database..."
python3 -c "
from agency.db import get_db
conn = get_db()
conn.close()
"
echo "  ✓ Database ready at $AGENCY_DIR/agency.db"

# ── Done ──
echo ""
echo "═══ Agency v2 installed ═══"
echo ""
echo "  /cost     → python -m agency.cost"
echo "  /history  → python -m agency.history"
echo ""
echo "  Data: $AGENCY_DIR/"
echo "  Next session auto-records via Stop hook."
