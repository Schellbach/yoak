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
pip install -q --upgrade pip
echo "Installing dependencies..."
pip install -q -e .

# Check for Ollama (the free default)
if command -v ollama &>/dev/null; then
    echo "Found Ollama."
    if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo ""
        echo "Ollama is installed but not running. Start it with:"
        echo "  ollama serve"
        echo ""
        echo "Then pull a model:"
        echo "  ollama pull llama3.1"
    fi
elif ! env | grep -qi "API_KEY"; then
    echo ""
    echo "Tip: Install Ollama for free local AI (no API key needed):"
    echo "  brew install ollama && ollama serve && ollama pull llama3.1"
    echo ""
    echo "Or set a cloud API key:"
    echo "  export ANTHROPIC_API_KEY=...  (or OPENAI_API_KEY, GEMINI_API_KEY)"
fi

echo ""
echo "Done! Run:"
echo ""
echo "  source .venv/bin/activate"
echo "  yoak"
echo ""
