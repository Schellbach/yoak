#!/usr/bin/env bash
# Yoak — Lean Startup Cofounder Agent
# Run this script to start Yoak. It handles all setup automatically.
set -e
cd "$(dirname "$0")"

MIN_PY="3.10"

# ── Find a suitable Python ──────────────────────────────────────────
find_python() {
    for cmd in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" &>/dev/null; then
            if "$cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" 2>/dev/null; then
                echo "$cmd"
                return
            fi
        fi
    done
    echo ""
}

PYTHON=$(find_python)
if [ -z "$PYTHON" ]; then
    echo "Python $MIN_PY+ is required but not found."
    echo ""
    echo "Install it:"
    echo "  macOS:  brew install python@3.12"
    echo "  Ubuntu: sudo apt install python3.12"
    echo "  Other:  https://www.python.org/downloads/"
    exit 1
fi

# ── Bootstrap on first run ──────────────────────────────────────────
if [ ! -f ".venv/bin/python" ]; then
    echo "First run — setting up Yoak..."
    echo "Using $($PYTHON --version)"
    $PYTHON -m venv .venv
    .venv/bin/python -m pip install -q --upgrade pip
    .venv/bin/pip install -q -e .

    # Offer to install Ollama if not present (free local AI)
    if ! command -v ollama &>/dev/null; then
        echo ""
        echo "Yoak works best with Ollama (free, local AI — no API key needed)."
        printf "Install Ollama now? [Y/n] "
        read -r yn </dev/tty 2>/dev/null || yn="y"
        case "$yn" in
            [Nn]*)
                echo "Skipped. You can install later: https://ollama.ai"
                echo "Or use a cloud model: export ANTHROPIC_API_KEY=..."
                ;;
            *)
                echo "Installing Ollama..."
                if command -v brew &>/dev/null; then
                    brew install --quiet ollama 2>/dev/null || curl -fsSL https://ollama.com/install.sh | sh
                else
                    curl -fsSL https://ollama.com/install.sh | sh
                fi
                echo "Pulling llama3.1 (this may take a few minutes on first run)..."
                ollama pull llama3.1 2>/dev/null || echo "Could not pull model. Run 'ollama serve' then 'ollama pull llama3.1' manually."
                ;;
        esac
    fi
    echo ""
    echo "Setup complete!"
    echo ""
fi

# ── Run Yoak ────────────────────────────────────────────────────────
exec .venv/bin/python -m yoak.cli.main "$@"
