#!/usr/bin/env bash
# Build BubbleTrack into a macOS .app bundle using a clean virtual environment.
set -e

BUILD_ENV=".build_env_mac"
PYTHON=""

echo "======================================"
echo "  Building BubbleTrack for macOS"
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
if [ -f "$BUILD_ENV/bin/python" ]; then
    echo "Reusing build environment at $BUILD_ENV"
else
    echo "Creating clean build environment..."
    "$PYTHON" -m venv "$BUILD_ENV"
fi

PIP="$BUILD_ENV/bin/pip"
PYINST="$BUILD_ENV/bin/pyinstaller"

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
    TMPDIR_ICON=$(mktemp -d)
    ICONSET_DIR="$TMPDIR_ICON/icon.iconset"
    mkdir -p "$ICONSET_DIR"

    # Convert .ico → intermediate PNG via Python (sips cannot read .ico)
    ICON_PNG="$TMPDIR_ICON/icon_source.png"
    "$BUILD_ENV/bin/python" -c "
from PIL import Image
img = Image.open('$ICON_ICO')
img.save('$ICON_PNG')
" 2>/dev/null || true

    if [[ -f "$ICON_PNG" ]]; then
        # Generate all required sizes including @2x Retina variants
        for size in 16 32 128 256 512; do
            sips -z $size $size "$ICON_PNG" --out "$ICONSET_DIR/icon_${size}x${size}.png" &>/dev/null || true
        done
        # @2x variants: 32(16@2x), 64(32@2x), 256(128@2x), 512(256@2x), 1024(512@2x)
        for size in 32 64 256 512 1024; do
            base=$((size / 2))
            sips -z $size $size "$ICON_PNG" --out "$ICONSET_DIR/icon_${base}x${base}@2x.png" &>/dev/null || true
        done
        iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS" 2>/dev/null || true
    fi

    rm -rf "$TMPDIR_ICON"

    if [[ -f "$ICON_ICNS" ]]; then
        echo "Icon converted successfully."
    else
        echo "Warning: Icon conversion failed, building without custom icon."
    fi
fi

# --- Clean previous build ---
if [[ -d "build/build_onefile" ]]; then
    echo "Cleaning previous build..."
    rm -rf build/build_onefile
fi
if [[ -d "dist/BubbleTrack.app" ]]; then
    rm -rf dist/BubbleTrack.app
fi
if [[ -f "dist/BubbleTrack" ]]; then
    rm -f dist/BubbleTrack
fi

# --- Build ---
echo "Running PyInstaller..."
"$PYINST" build_onefile.spec --noconfirm

echo ""
if [[ -d "dist/BubbleTrack.app" ]]; then
    echo "======================================"
    echo "  Build successful!"
    echo "  Output: dist/BubbleTrack.app"
    echo "======================================"
elif [[ -f "dist/BubbleTrack" ]]; then
    echo "======================================"
    echo "  Build successful!"
    echo "  Output: dist/BubbleTrack"
    echo "======================================"
else
    echo "ERROR: Build failed. Check output above."
    exit 1
fi
