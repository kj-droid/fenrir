#!/bin/bash

# ==============================================================================
# Fenrir Desktop Launcher Creator
# ==============================================================================
# This script creates a .desktop file, which acts as a clickable application
# launcher for Fenrir on most Linux desktop environments (GNOME, KDE, XFCE, etc.).
#
# Prerequisites:
# 1. Fenrir must be installed on your system (e.g., via 'sudo python3 setup.py install').
# 2. You must have an icon file located at 'gui/assets/icon.png' within this project.
#
# Usage:
# 1. Run this script from the Fenrir project's root directory: ./create_launcher.sh
# ==============================================================================

echo "--- Creating Fenrir Desktop Launcher ---"

# --- 1. Define Paths ---
# Get the absolute path to the current directory (the Fenrir project root)
CURRENT_DIR=$(pwd)
# Define the path to the icon file
ICON_PATH="$CURRENT_DIR/gui/assets/icon.png"
# Define the path for the output .desktop file
DESKTOP_FILE_PATH="$HOME/Desktop/Fenrir.desktop"

# --- 2. Check for Prerequisites ---
if ! command -v fenrir &> /dev/null; then
    echo "Error: The 'fenrir' command was not found."
    echo "Please ensure Fenrir is installed correctly before creating a launcher."
    exit 1
fi

if [ ! -f "$ICON_PATH" ]; then
    echo "Error: Icon file not found at '$ICON_PATH'."
    echo "Please ensure the icon exists before creating a launcher."
    exit 1
fi

echo "Fenrir installation found."
echo "Icon found at: $ICON_PATH"

# --- 3. Create the .desktop File Content ---
# This is the standard format for a desktop entry file.
# The 'Path' key tells the system what directory to run the command from.
# The 'Exec' line uses the 'fenrir' command, which should be in your system's PATH.
# The 'Icon' line uses the absolute path to your project's icon.
cat > "$DESKTOP_FILE_PATH" << EOL
[Desktop Entry]
Version=1.0
Name=Fenrir Security Scanner
Comment=Run the Fenrir vulnerability scanner
Path=$CURRENT_DIR
Exec=fenrir
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Utility;Security;
EOL

# --- 4. Make the Launcher Executable ---
# This step is crucial for the desktop environment to recognize and trust the launcher.
chmod +x "$DESKTOP_FILE_PATH"

echo ""
echo "--- Success! ---"
echo "A launcher named 'Fenrir.desktop' has been created on your desktop."
echo "You may need to right-click it and select 'Allow Launching' the first time you use it."
