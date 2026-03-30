# Yoak — Lean Startup Cofounder Agent

An AI cofounder harness that thinks like Paul Graham, operates like Steve Blank, and demands quality like Steve Jobs.

Yoak wraps frontier LLMs (cloud and local) with structured startup methodology — prompts, persistent memory, workflows, and skills — so you can run your startup like a lean team from day one.

## Philosophy

| Layer | Thinker | Role |
|-------|---------|------|
| **Instincts** | Paul Graham | How to evaluate ideas, what matters, growth as compass |
| **Methodology** | Steve Blank | Customer Development, Business Model Canvas, hypothesis testing |
| **Taste** | Steve Jobs | Product quality, simplicity, start from the customer experience |

## Quick Start

```bash
# Install
pip install -e .

# Configure a model provider
yoak config set model "anthropic/claude-sonnet-4-20250514"
yoak config set api-key anthropic "sk-..."

# Start the dashboard
yoak serve

# Or chat directly from the terminal
yoak chat
```

## Architecture

```
Interfaces        API Layer       Core Engine        Philosophy
───────────       ─────────       ───────────        ──────────
Web Dashboard ──► FastAPI ──────► Agent ──────────► Paul Graham
CLI ─────────────────────────► Orchestrator ──────► Steve Blank
                                   │                Steve Jobs
                                   │
                              ┌────┴────┐
                          Workflows  Skills
                              │        │
                          Memory    Models
                        (SQLite)  (LiteLLM/Ollama)
```

## Features

- **Business Model Canvas** — persistent, hypothesis-driven canvas that evolves with your startup
- **Customer Development Workflows** — guided Discovery → Validation → Creation → Building phases
- **Idea Evaluation** — PG-inspired scoring with schlep blindness and unsexy filter bypass
- **Pivot Decision Framework** — structured pivot-or-persevere analysis with 10 pivot types
- **Product/Market Fit Assessment** — Sean Ellis test, retention curves, unit economics
- **Product Critique** — Jobs-inspired quality and simplicity review
- **Learning Journal** — append-only log of validated insights, pivots, and key decisions

## Model Support

- **Cloud**: Any provider supported by LiteLLM (Anthropic, OpenAI, Google, Mistral, etc.)
- **Local**: Ollama for running models on your machine

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
