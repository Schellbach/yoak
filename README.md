# Yoak — Lean Startup Cofounder Agent

An AI cofounder harness that thinks like Paul Graham, operates like Steve Blank, and demands quality like Steve Jobs.

Yoak wraps frontier LLMs (cloud and local) with structured startup methodology — prompts, persistent memory, workflows, and skills — so you can run your startup like a lean team from day one.

## Why Yoak?

Every startup begins with untested assumptions. Most founders execute instead of learning — building features nobody wants, scaling before finding fit, ignoring the hard questions.

Yoak encodes three complementary worldviews as the agent's operating system:

| Layer | Thinker | Role in Yoak |
|-------|---------|--------------|
| **Instincts** | Paul Graham | How to evaluate ideas, recognize what matters, use growth as a compass |
| **Methodology** | Steve Blank | Customer Development — the structured search for a repeatable business model |
| **Taste** | Steve Jobs | Product quality, simplicity, starting from the customer experience |

The result is an AI cofounder that asks the questions you're avoiding, challenges your assumptions with frameworks, and keeps you honest about what's validated versus what's hoped for.

## Quick Start

Copy and paste this into your terminal:

```bash
git clone https://github.com/Schellbach/yoak.git && cd yoak && make
```

That's it — one line. It clones the repo, installs everything, and drops you into a conversation with your AI cofounder. No API key needed. First run takes about a minute; every run after is instant.

### Want to use a frontier model?

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # or OPENAI_API_KEY, GEMINI_API_KEY
make init                               # picks up the key, lets you switch
```

### Commands

```bash
make                   # start chatting (installs everything on first run)
make chat              # go straight to chat
make serve             # start the web dashboard at http://127.0.0.1:8420
make canvas            # print your Business Model Canvas
make journal           # show your learning journal
make init              # reconfigure model, project name, etc.
make help              # show all commands
```

### Prerequisites

- Python 3.10+
- That's it. Ollama (free local AI) is offered during first-run setup. No accounts, no API keys.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERFACES                              │
│   Web Dashboard (React)              CLI (Typer)                │
└──────────┬───────────────────────────────┬──────────────────────┘
           │                               │
┌──────────▼───────────────────────────────▼──────────────────────┐
│                        API LAYER                                │
│   FastAPI (31 endpoints)         WebSocket (streaming chat)     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                      CORE ENGINE                                │
│                                                                 │
│   Agent Orchestrator ─── assembles system prompt from:          │
│     ├─ Philosophy Engine (PG + Blank + Jobs)                    │
│     ├─ Memory Context (canvas, hypotheses, journal)             │
│     ├─ Workflow Context (active step + prompt supplement)       │
│     └─ Skill Context (market analysis, user research, etc.)    │
│                                                                 │
│   Workflow Router ─── detects intent, dispatches to:            │
│     ├─ 6 Workflows (idea eval, discovery, validation, ...)     │
│     └─ 5 Skills (market, competition, growth, economics, ...)  │
└──────────┬──────────────────────────────┬───────────────────────┘
           │                              │
┌──────────▼──────────┐    ┌──────────────▼───────────────────────┐
│   MEMORY (SQLite)   │    │         MODEL PROVIDERS              │
│                     │    │                                       │
│ Business Model      │    │  LiteLLM (Anthropic, OpenAI, Google, │
│   Canvas (9 blocks) │    │           Mistral, Cohere, ...)      │
│ Hypothesis Tracker  │    │  Ollama (llama, mistral, codellama,  │
│ Learning Journal    │    │          gemma, phi, ...)             │
│ Pivot History       │    │                                       │
└─────────────────────┘    └──────────────────────────────────────┘
```

## Features

### Encoded Philosophy (~21,000 chars of startup methodology)

**Paul Graham — Instincts** ([source essays](https://www.paulgraham.com/articles.html))
- The "well, not field" test — prefer desperate need from a few over mild interest from many
- Schlep blindness bypass — scary ideas are undervalued signals
- Growth as compass — target 5-7% weekly, measure rate not absolute
- Anti-patterns: sitcom startups, premature scaling, big launch fallacy, playing house
- "Relentlessly resourceful" — the goal is fixed, the path is fluid

**Steve Blank — Methodology** ([source writing](https://steveblank.com/))
- Customer Development 4-phase state machine (Discovery → Validation → Creation → Building)
- Business Model Canvas as a living hypothesis board (9 blocks, each testable)
- MVP type selection (concierge, wizard of oz, landing page, single-feature, pre-order)
- Pivot decision framework with 10 pivot types and structured criteria
- Product/Market Fit measurement (Sean Ellis test, retention curves, LTV/CAC)
- Interview protocols: problem interviews, solution interviews, debrief synthesis
- 2026 concepts: MVP → MPO (Minimum Productive Outcome), P/M Fit → Agent/Customer Outcome Fit

**Steve Jobs — Taste**
- "Start with the customer experience, work backwards to technology"
- Simplicity as highest sophistication — strip until only the essential remains
- Focus means saying no to 100 good ideas
- Craft: quality must be consistent throughout, even in hidden details
- Empathy + Focus + Impute as the product evaluation triad

### Workflows (Multi-Step Guided Processes)

| Workflow | Steps | What It Does |
|----------|-------|-------------|
| **Idea Evaluation** | 5 | PG filters, BMC mapping, riskiest assumption, scoring |
| **Customer Discovery** | 5 | Hypothesis review, interview planning, debrief, solution testing, phase gate |
| **Customer Validation** | 6 | MVP development, earlyvangelist sales, sales roadmap, unit economics, P/M Fit, phase gate |
| **Pivot Decision** | 5 | Evidence review, signal analysis, diagnosis, pivot type selection, new hypothesis |
| **PMF Assessment** | 3 | Qualitative signals, quantitative metrics, diagnosis |
| **Product Critique** | 4 | Experience-first review, simplicity audit, focus/quality audit, verdict |

Workflows are state machines — each step injects specific prompts that guide the conversation. The agent automatically routes to the right workflow based on what you're discussing.

### Skills (Single-Turn Expertise)

| Skill | What It Provides |
|-------|-----------------|
| **Market Analysis** | TAM/SAM/SOM sizing, market type classification, timing analysis |
| **User Research** | Interview script generation, problem/solution templates, insight synthesis |
| **Competitive Intel** | Competitor mapping, moat analysis, the "do nothing" competitor |
| **Growth Strategy** | Growth engine selection (sticky/viral/paid), metric frameworks, PG growth principles |
| **Unit Economics** | CAC/LTV modeling, burn rate, payback period, the "default alive" test |

### Memory (Persistent State)

All state is stored in a local SQLite database (`~/.yoak/yoak.db`):

- **Business Model Canvas** — 9 blocks (Customer Segments, Value Propositions, Channels, etc.), each containing hypothesis objects
- **Hypothesis Tracker** — lifecycle management: `untested → testing → validated/invalidated`, with linked evidence entries
- **Learning Journal** — append-only log with types: learning, pivot, decision, milestone, interview, experiment
- **Phase Tracker** — which Customer Development phase you're in (discovery, validation, creation, building)

Memory context is injected into every conversation turn, so the agent always knows your current canvas state, active hypotheses, and recent learnings.

### Dashboard (Web UI)

A dark-mode "war room" at `http://127.0.0.1:8420` with five views:

- **Overview** — Customer Development phase tracker, hypothesis stats (untested/testing/validated/invalidated), active workflow progress, recent activity
- **Chat** — Streaming conversation with the cofounder agent, workflow phase indicator, suggested starter prompts
- **Canvas** — Visual 9-block Business Model Canvas with clickable hypothesis cards (click status icons to cycle through states)
- **Journal** — Filterable timeline of learnings, pivots, decisions, experiments with inline creation
- **Settings** — Model provider configuration (cloud + Ollama), temperature, project name

### CLI

```
yoak chat      — Interactive terminal chat with the cofounder agent
yoak serve     — Start the API server + dashboard
yoak canvas    — Display the current Business Model Canvas
yoak journal   — Show recent learning journal entries
yoak config    — Manage configuration (show, set)
```

In chat mode, slash commands are available: `/workflow`, `/advance`, `/canvas`, `/phase`, `/reset`, `/quit`.

## Model Support

Yoak defaults to **Ollama** (free, local, private — no API key needed). To upgrade to a frontier model, just set an API key and run `yoak init`.

| Provider | Model String | Setup |
|----------|-------------|-------|
| **Ollama (default)** | `ollama/llama3.1` | `brew install ollama && ollama pull llama3.1` |
| Anthropic | `anthropic/claude-sonnet-4-20250514` | `export ANTHROPIC_API_KEY=...` |
| OpenAI | `gpt-4o` | `export OPENAI_API_KEY=...` |
| Google | `gemini/gemini-2.5-pro` | `export GEMINI_API_KEY=...` |
| Mistral | `mistral/mistral-large-latest` | `export MISTRAL_API_KEY=...` |

Any model supported by [LiteLLM](https://docs.litellm.ai/docs/providers) works. Run `yoak init` to switch models at any time.

## Project Structure

```
yoak/
├── pyproject.toml              # Package definition, dependencies
├── README.md
├── yoak/
│   ├── core/
│   │   ├── agent.py            # Main orchestrator — routes through philosophy + workflows
│   │   ├── router.py           # Intent detection → workflow/skill dispatch
│   │   └── config.py           # YAML-backed settings with env var support
│   ├── models/
│   │   ├── provider.py         # Unified LiteLLM + Ollama interface
│   │   └── streaming.py        # Streaming chunk accumulator
│   ├── philosophy/
│   │   ├── graham.py           # PG heuristics as callable prompt modules
│   │   ├── blank.py            # Customer Dev methodology + phase guidance
│   │   ├── jobs.py             # Product design principles + critique
│   │   └── synthesis.py        # Combined context builder + intent detection
│   ├── memory/
│   │   ├── store.py            # SQLite schema + connection management
│   │   ├── canvas.py           # Business Model Canvas CRUD + summary renderer
│   │   ├── hypotheses.py       # Hypothesis lifecycle + evidence tracking
│   │   └── journal.py          # Learning journal + phase management
│   ├── workflows/
│   │   ├── base.py             # Base workflow state machine
│   │   ├── idea_evaluation.py  # 5-step PG-inspired idea scoring
│   │   ├── customer_discovery.py   # Blank Phase 1
│   │   ├── customer_validation.py  # Blank Phase 2
│   │   ├── pivot_decision.py   # Structured pivot-or-persevere
│   │   ├── pmf_assessment.py   # Product/Market Fit measurement
│   │   └── product_critique.py # Jobs-inspired quality review
│   ├── skills/
│   │   ├── market_analysis.py  # TAM/SAM/SOM, market types
│   │   ├── user_research.py    # Interview scripts, synthesis
│   │   ├── competitive_intel.py # Competitor mapping, moats
│   │   ├── growth_strategy.py  # Growth engine, metrics
│   │   └── unit_economics.py   # CAC/LTV, burn rate
│   ├── prompts/
│   │   ├── system/             # 4 system prompts (cofounder identity, PG, Blank, Jobs)
│   │   ├── workflows/          # 6 workflow prompts (idea eval, discovery, validation, ...)
│   │   └── skills/             # 5 skill prompts (market, interviews, competition, ...)
│   ├── api/
│   │   ├── app.py              # FastAPI app with 31 routes
│   │   └── routes/             # Endpoint modules (chat, canvas, hypotheses, journal, ...)
│   └── cli/
│       └── main.py             # Typer CLI with Rich formatting
└── dashboard/
    ├── package.json
    └── src/
        ├── App.tsx             # Router + icon sidebar
        ├── api/client.ts       # Full API client + WebSocket
        └── pages/              # Overview, Chat, Canvas, Journal, Settings
```

## How It Works

When you send a message, Yoak:

1. **Detects intent** — maps your message to a workflow (multi-step) or skill (single-turn)
2. **Assembles context** — builds a system prompt from:
   - The master cofounder identity prompt
   - Relevant PG/Blank/Jobs principles (based on your topic)
   - Your current Business Model Canvas state
   - Recent learning journal entries
   - Active workflow step (if any) with its specific guidance prompt
   - Or the relevant skill prompt (if routed to a skill)
3. **Calls the model** — sends the assembled messages to your configured LLM
4. **Streams the response** — via WebSocket (dashboard) or terminal (CLI)

The agent's persona is consistent across all interactions: direct, honest, occasionally uncomfortable — like a great cofounder who asks the hard questions.

## API Reference

The API runs on `http://127.0.0.1:8420` with interactive docs at `/docs`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send a message, get a response |
| `WS` | `/api/ws/chat` | Streaming chat via WebSocket |
| `POST` | `/api/chat/reset` | Clear conversation history |
| `GET` | `/api/chat/history` | Get conversation messages |
| `GET` | `/api/canvas` | Get all 9 BMC blocks with hypotheses |
| `PUT` | `/api/canvas/{block_id}` | Update a canvas block |
| `GET` | `/api/hypotheses` | List hypotheses (filter by block, status) |
| `POST` | `/api/hypotheses` | Create a hypothesis |
| `PATCH` | `/api/hypotheses/{id}` | Update status/confidence |
| `POST` | `/api/hypotheses/{id}/evidence` | Add evidence to a hypothesis |
| `DELETE` | `/api/hypotheses/{id}` | Delete a hypothesis |
| `GET` | `/api/journal` | List journal entries (filter by type) |
| `POST` | `/api/journal` | Create a journal entry |
| `GET` | `/api/phase` | Get current Customer Development phase |
| `PUT` | `/api/phase` | Set phase (discovery/validation/creation/building) |
| `GET` | `/api/workflows` | List available workflows |
| `POST` | `/api/workflows/start` | Start a workflow by name |
| `POST` | `/api/workflows/advance` | Advance to next workflow step |
| `POST` | `/api/workflows/cancel` | Cancel active workflow |
| `GET` | `/api/config` | Get current configuration |
| `PUT` | `/api/config` | Update a configuration value |

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run the linter
ruff check yoak/

# Run the dashboard in dev mode (hot reload)
cd dashboard && npm run dev
```

## Configuration

Yoak stores configuration in `~/.yoak/config.yaml` (override with `YOAK_DIR` env var).

```yaml
model:
  provider: ollama
  model: ollama/llama3.1
  temperature: 0.7
  max_tokens: 4096
ollama:
  enabled: true
  base_url: http://localhost:11434
  model: llama3.1
server:
  host: 127.0.0.1
  port: 8420
project_name: My Startup
```

## License

MIT
