#!/bin/bash

# ZADE IGNITE - Build Script (Linux)
# Packages the application into a standalone executable using PyInstaller.

echo "Initiating Build Process..."

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Running setup..."
    ./setup_env.sh
fi

source venv/bin/activate

# Install PyInstaller
pip install pyinstaller

# Run PyInstaller
echo "Bundling ZADE IGNITE into a single folder..."
pyinstaller --noconfirm --onedir --windowed \
    --add-data "src/config.json:src" \
    --add-data "src/requirements.txt:src" \
    --name "ZadeIgnite" \
    src/config_gui.py

echo "Build complete. Executable can be found in dist/ZadeIgnite/ZadeIgnite"
echo "Note: Ensure all .py files in src/ are accessible if not bundled correctly by imports."
