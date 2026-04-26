#!/bin/bash
# ============================================================
# CFAB Browser – macOS .app bundle builder
# Creates a lightweight .app wrapper that launches the Python
# application as a native macOS GUI app.
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="CFAB Browser"
APP_BUNDLE="${SCRIPT_DIR}/${APP_NAME}.app"
PYTHON="/usr/bin/env python3"
ICON_SRC="${SCRIPT_DIR}/core/resources/img/icon.png"

echo "🔨 Building ${APP_NAME}.app ..."

# ---- Clean previous build ----
if [ -d "$APP_BUNDLE" ]; then
    echo "🧹 Removing old ${APP_NAME}.app ..."
    rm -rf "$APP_BUNDLE"
fi

# ---- Create .app directory structure ----
mkdir -p "${APP_BUNDLE}/Contents/MacOS"
mkdir -p "${APP_BUNDLE}/Contents/Resources"

# ---- Create launch script ----
cat > "${APP_BUNDLE}/Contents/MacOS/launch" << 'LAUNCHER'
#!/bin/bash
# CFAB Browser launcher – runs from inside the .app bundle.

# ---- Resolve project directory ----
APP_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"

# ---- Find python3 ----
for candidate in \
    /usr/bin/python3 \
    /usr/local/bin/python3 \
    /opt/homebrew/bin/python3 \
    /Applications/Xcode.app/Contents/Developer/usr/bin/python3 \
    ; do
    if [ -x "$candidate" ]; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    osascript -e 'display dialog "CFAB Browser: python3 not found!\nPlease install Python 3." buttons {"OK"} default button "OK" with icon stop with title "CFAB Browser"'
    exit 1
fi

# ---- Launch with forced arm64 architecture ----
cd "$APP_DIR"
exec arch -arm64 "$PYTHON" "$APP_DIR/cfab_browser.py" "$@"
LAUNCHER

chmod +x "${APP_BUNDLE}/Contents/MacOS/launch"

# ---- Clear quarantine attributes ----
xattr -cr "${APP_BUNDLE}" 2>/dev/null || true

# ---- Convert icon to .icns if possible ----
ICON_ICNS="${APP_BUNDLE}/Contents/Resources/AppIcon.icns"
if [ -f "$ICON_SRC" ]; then
    ICONSET_DIR="${SCRIPT_DIR}/.tmp_iconset.iconset"
    mkdir -p "$ICONSET_DIR"

    # Generate all required icon sizes
    sips -z 16 16     "$ICON_SRC" --out "${ICONSET_DIR}/icon_16x16.png"      > /dev/null 2>&1
    sips -z 32 32     "$ICON_SRC" --out "${ICONSET_DIR}/icon_16x16@2x.png"   > /dev/null 2>&1
    sips -z 32 32     "$ICON_SRC" --out "${ICONSET_DIR}/icon_32x32.png"      > /dev/null 2>&1
    sips -z 64 64     "$ICON_SRC" --out "${ICONSET_DIR}/icon_32x32@2x.png"   > /dev/null 2>&1
    sips -z 128 128   "$ICON_SRC" --out "${ICONSET_DIR}/icon_128x128.png"    > /dev/null 2>&1
    sips -z 256 256   "$ICON_SRC" --out "${ICONSET_DIR}/icon_128x128@2x.png" > /dev/null 2>&1
    sips -z 256 256   "$ICON_SRC" --out "${ICONSET_DIR}/icon_256x256.png"    > /dev/null 2>&1
    sips -z 512 512   "$ICON_SRC" --out "${ICONSET_DIR}/icon_256x256@2x.png" > /dev/null 2>&1
    sips -z 512 512   "$ICON_SRC" --out "${ICONSET_DIR}/icon_512x512.png"    > /dev/null 2>&1
    sips -z 1024 1024 "$ICON_SRC" --out "${ICONSET_DIR}/icon_512x512@2x.png" > /dev/null 2>&1

    iconutil -c icns -o "$ICON_ICNS" "$ICONSET_DIR" 2>/dev/null && \
        echo "✅ Icon converted to .icns" || \
        echo "⚠️  iconutil failed – app will use default icon"

    rm -rf "$ICONSET_DIR"
else
    echo "⚠️  No icon found at ${ICON_SRC} – using default"
fi

# ---- Determine .icns filename for plist ----
ICNS_NAME="AppIcon"
if [ -f "$ICON_ICNS" ]; then
    ICNS_NAME="AppIcon"
fi

# ---- Create Info.plist ----
cat > "${APP_BUNDLE}/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.cfab.browser</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIconFile</key>
    <string>${ICNS_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>CFAB</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>
PLIST

echo ""
echo "✅ ${APP_NAME}.app created successfully!"
echo "   📁 Location: ${APP_BUNDLE}"
echo ""
echo "   You can now:"
echo "   • Double-click it in Finder to launch"
echo "   • Drag it to your Dock"
echo "   • Open it via Spotlight (Cmd+Space → '${APP_NAME}')"
echo ""
