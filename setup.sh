#!/usr/bin/env bash
# Yoak — one-command setup
set -e

cd "$(dirname "$0")"

echo "Setting up Yoak..."

# Python venv
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -e .

echo ""
echo "Done! Run:"
echo ""
echo "  source .venv/bin/activate"
echo "  yoak"
echo ""
