#!/usr/bin/env bash
# ==============================================================================
# 🌱 Bias Flora / Sentient Plant - Runner Script
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Ensure DISPLAY and XAUTHORITY are exported for mouse listener
export DISPLAY="${DISPLAY:-:0}"
if [ -f "$HOME/.Xauthority" ]; then
    export XAUTHORITY="$HOME/.Xauthority"
fi

# Use virtual environment python
PYTHON_BIN="$DIR/vnv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="/home/pi-4b/jamal_ai/vnv/bin/python"
fi
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "========================================================"
echo " Starting Sentient Plant State Machine (Bias Flora)"
echo " Working Dir: $DIR"
echo " Python Bin : $PYTHON_BIN"
echo " Display    : $DISPLAY"
echo "========================================================"

# Run unbuffered so output streams immediately
exec "$PYTHON_BIN" -u "$DIR/main.py"
