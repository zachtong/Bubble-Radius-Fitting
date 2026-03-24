#!/usr/bin/env bash
# BubbleTrack setup script — macOS, Linux, Git Bash (Windows)
set -e

VENV_DIR=".venv"
PYTHON=""

# --- Find Python 3.10+ ---
for cmd in python3.13 python3.12 python3.11 python3.10 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        major=${ver%%.*}
        minor=${ver##*.}
        if [ "$major" -ge 3 ] 2>/dev/null && [ "$minor" -ge 10 ] 2>/dev/null; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.10+ is required but not found."
    echo "Download from https://www.python.org/downloads/"
    exit 1
fi

echo "Using $PYTHON ($($PYTHON --version))"

# --- Create virtual environment ---
if [ -f "$VENV_DIR/bin/python" ] || [ -f "$VENV_DIR/Scripts/python.exe" ]; then
    echo "Virtual environment already exists, updating..."
else
    echo "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# --- Determine venv pip/bin paths ---
if [ -f "$VENV_DIR/bin/pip" ]; then
    PIP="$VENV_DIR/bin/pip"
    BIN="$VENV_DIR/bin"
else
    PIP="$VENV_DIR/Scripts/pip"
    BIN="$VENV_DIR/Scripts"
fi

# --- Install into venv ---
echo "Installing BubbleTrack..."
"$PIP" install --upgrade pip -q
"$PIP" install -e . -q

# --- Create launcher ---
cat > bubbletrack.sh << 'LAUNCHER'
#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$DIR/.venv/bin/bubbletrack" ]; then
    exec "$DIR/.venv/bin/bubbletrack" "$@"
else
    exec "$DIR/.venv/Scripts/bubbletrack.exe" "$@"
fi
LAUNCHER
chmod +x bubbletrack.sh

echo ""
echo "======================================"
echo "  BubbleTrack installed successfully!"
echo "======================================"
echo ""
echo "Run:  ./bubbletrack.sh"
