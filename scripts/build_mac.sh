#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

# Install tools
python -m pip install --upgrade pip
python -m pip install pyinstaller PyQt5

# Clean previous builds
rm -rf build dist Neuro.app 2>/dev/null || true

# Build the macOS .app
pyinstaller \
  --noconfirm \
  --windowed \
  --name "Neuro" \
  --icon "logo.icns" \
  --add-data "Backend:Backend" \
  --add-data "Data:Data" \
  desktop_app.py

echo "✅ Build Finished! App at: dist/Neuro.app"
echo "👉 First launch: Right-click > Open (macOS security approval)."
