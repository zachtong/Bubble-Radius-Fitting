#!/usr/bin/env bash
# Build BubbleTrack using a clean virtual environment.
# Windows: produces dist/BubbleTrack.exe
# macOS:   produces dist/BubbleTrack.app
set -e

BUILD_ENV=".build_env_mac"
PYTHON=""

echo "======================================"
echo "  Building BubbleTrack"
echo "======================================"
echo ""

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
    exit 1
fi

echo "Using $PYTHON ($($PYTHON --version))"

# --- Create clean build environment ---
if [ -f "$BUILD_ENV/bin/python" ] || [ -f "$BUILD_ENV/Scripts/python.exe" ]; then
    echo "Reusing build environment at $BUILD_ENV"
else
    echo "Creating clean build environment..."
    "$PYTHON" -m venv "$BUILD_ENV"
fi

# --- Determine venv paths ---
if [ -f "$BUILD_ENV/bin/pip" ]; then
    PIP="$BUILD_ENV/bin/pip"
    PYINST="$BUILD_ENV/bin/pyinstaller"
else
    PIP="$BUILD_ENV/Scripts/pip"
    PYINST="$BUILD_ENV/Scripts/pyinstaller"
fi

# --- Install only required dependencies ---
echo "Installing dependencies..."
"$PIP" install --upgrade pip -q
"$PIP" install -e . -q
"$PIP" install pyinstaller -q

# --- Convert icon for macOS ---
ICON_ICO="src/bubbletrack/resources/icon.ico"
ICON_ICNS="src/bubbletrack/resources/icon.icns"

if [[ "$(uname)" == "Darwin" ]] && [[ ! -f "$ICON_ICNS" ]] && [[ -f "$ICON_ICO" ]]; then
    echo "Converting icon to .icns for macOS..."
    ICONSET_DIR=$(mktemp -d)/icon.iconset
    mkdir -p "$ICONSET_DIR"
    for size in 16 32 64 128 256 512; do
        sips -z $size $size "$ICON_ICO" --out "$ICONSET_DIR/icon_${size}x${size}.png" &>/dev/null || true
    done
    iconutil -c icns "$ICONSET_DIR/.." -o "$ICON_ICNS" 2>/dev/null || true
    rm -rf "$(dirname "$ICONSET_DIR")"
fi

# --- Build ---
echo "Running PyInstaller..."
"$PYINST" build_onefile.spec --noconfirm

echo ""
if [[ "$(uname)" == "Darwin" ]]; then
    if [[ -d "dist/BubbleTrack.app" ]]; then
        echo "======================================"
        echo "  Build successful!"
        echo "  Output: dist/BubbleTrack.app"
        echo "======================================"
    else
        echo "ERROR: Build failed."; exit 1
    fi
else
    if [[ -f "dist/BubbleTrack.exe" ]]; then
        echo "======================================"
        echo "  Build successful!"
        echo "  Output: dist/BubbleTrack.exe"
        echo "======================================"
    else
        echo "ERROR: Build failed."; exit 1
    fi
fi
