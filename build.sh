#!/bin/bash
# Build script to force pip usage and prevent Poetry detection

echo "=== FORCING PIP BUILD ==="
echo "Disabling Poetry detection..."

# Remove any Poetry cache or config
rm -rf ~/.cache/pypoetry
rm -rf ~/.config/pypoetry
rm -rf /opt/render/project/src/.venv

# Set environment to disable Poetry
export DISABLE_POETRY=1
export POETRY_ACTIVE=0

# Upgrade pip and install dependencies
echo "Installing dependencies with pip..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "=== BUILD COMPLETE ==="
