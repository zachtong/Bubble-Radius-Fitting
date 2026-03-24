#!/usr/bin/env bash
# Build BubbleTrack into a single executable.
# Windows: produces dist/BubbleTrack.exe
# macOS:   produces dist/BubbleTrack.app
set -e

echo "======================================"
echo "  Building BubbleTrack"
echo "======================================"
echo ""

# --- Ensure PyInstaller ---
if ! python -m PyInstaller --version &>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller -q
fi

# --- Convert icon for macOS (if sips available) ---
ICON_ICO="src/bubbletrack/resources/icon.ico"
ICON_ICNS="src/bubbletrack/resources/icon.icns"

if [[ "$(uname)" == "Darwin" ]] && [[ ! -f "$ICON_ICNS" ]] && [[ -f "$ICON_ICO" ]]; then
    echo "Converting icon to .icns for macOS..."
    ICONSET_DIR=$(mktemp -d)/icon.iconset
    mkdir -p "$ICONSET_DIR"
    # sips is built into macOS — no extra tools needed
    for size in 16 32 64 128 256 512; do
        sips -z $size $size "$ICON_ICO" --out "$ICONSET_DIR/icon_${size}x${size}.png" &>/dev/null || true
    done
    iconutil -c icns "$ICONSET_DIR/.." -o "$ICON_ICNS" 2>/dev/null || true
    rm -rf "$(dirname "$ICONSET_DIR")"
fi

# --- Build ---
echo "Running PyInstaller..."
python -m PyInstaller build_onefile.spec --noconfirm --clean

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
