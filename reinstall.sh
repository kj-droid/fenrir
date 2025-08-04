#!/bin/bash

# ==============================================================================
# Fenrir Reinstallation Script
# ==============================================================================
# This script automates the process of uninstalling any old version of Fenrir
# and reinstalling the current version from this directory.
# It is designed for Debian-based systems like Kali Linux and handles files
# created by 'setup.py install'.
#
# Usage:
# 1. Make the script executable: chmod +x reinstall.sh
# 2. Run with sudo: ./reinstall.sh
# ==============================================================================

# --- Check for Root Privileges ---
if [ "$EUID" -ne 0 ]; then
  echo "Error: This script requires root privileges to manage system files."
  echo "Please run with sudo: sudo ./reinstall.sh"
  exit 1
fi

echo "--- Starting Fenrir Reinstallation ---"

# --- 1. Clean Up Local Build Artifacts ---
# This removes temporary directories created by previous installations.
echo "[1/4] Cleaning up local build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf fenrir.egg-info/
echo "Cleanup complete."

# --- 2. Manually Remove Old Installation Files ---
# This is more reliable than 'pip uninstall' on systems with externally
# managed environments.
echo "[2/4] Removing old installation files from system directories..."

# Find the site-packages or dist-packages directory dynamically
SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")

if [ -d "$SITE_PACKAGES" ]; then
    echo "Found system package directory at: $SITE_PACKAGES"
    # Remove the installed package folder
    rm -rf "$SITE_PACKAGES/fenrir"
    # Remove any old distribution info
    rm -rf "$SITE_PACKAGES/fenrir-"*".dist-info"
    # Remove the standalone modules that were installed
    rm -f "$SITE_PACKAGES/fenrir_launcher.py"
    rm -f "$SITE_PACKAGES/fenrir_cli.py"
    rm -f "$SITE_PACKAGES/update_db.py"
    rm -f "$SITE_PACKAGES/verify_db.py"
    echo "Removed old package files."
else
    echo "Warning: Could not determine site-packages directory. Manual cleanup may be required."
fi

# --- 3. Remove Old Command-Line Entry Point ---
echo "[3/4] Removing old 'fenrir' command..."
if [ -f "/usr/local/bin/fenrir" ]; then
    rm -f /usr/local/bin/fenrir
    echo "Removed /usr/local/bin/fenrir"
else
    echo "'fenrir' command not found, skipping."
fi

# --- 4. Install the New Version ---
echo "[4/4] Installing the latest version from the current directory..."
# The setup.py script will handle installing system and Python dependencies
python3 setup.py install

if [ $? -eq 0 ]; then
    echo ""
    echo "--- Fenrir reinstallation complete! ---"
    echo "You can now run the application by typing 'fenrir' in your terminal."
else
    echo ""
    echo "--- Reinstallation failed. ---"
    echo "Please check the output above for errors."
fi
