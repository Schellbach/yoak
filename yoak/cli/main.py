"""Yoak CLI — management and chat interface."""

from __future__ import annotations

import asyncio
import os
import sys

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from yoak.core.config import CONFIG_PATH, load_settings, save_settings, update_setting

app = typer.Typer(
    name="yoak",
    help="Yoak — Lean Startup Cofounder Agent",
    invoke_without_command=True,
)
console = Console()

_KEY_MAP = {
    "ANTHROPIC_API_KEY": ("anthropic/claude-sonnet-4-20250514", "Anthropic (Claude)"),
    "OPENAI_API_KEY": ("gpt-4o", "OpenAI (GPT-4o)"),
    "GEMINI_API_KEY": ("gemini/gemini-2.5-pro", "Google (Gemini)"),
    "MISTRAL_API_KEY": ("mistral/mistral-large-latest", "Mistral"),
}

_PROVIDER_KEY = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GEMINI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "mistral": "MISTRAL_API_KEY",
}


def _detect_available_provider() -> tuple[str, str] | None:
    """Find the first API key already set in the environment."""
    for env_var, (model, label) in _KEY_MAP.items():
        if os.environ.get(env_var):
            return model, label
    return None


def _needs_init() -> bool:
    return not CONFIG_PATH.exists()


def _check_model_ready(settings) -> bool:
    """Check if we can reach the configured model. Returns True if ok."""
    if settings.ollama.enabled:
        return True
    model = settings.model.model
    provider = model.split("/")[0] if "/" in model else model
    env_var = _PROVIDER_KEY.get(provider)
    if env_var and not os.environ.get(env_var):
        console.print(
            Panel(
                f"[red bold]No API key found[/red bold]\n\n"
                f"Model is set to [cyan]{model}[/cyan] but [cyan]{env_var}[/cyan] is not set.\n\n"
                f"Fix it:\n"
                f"  [green]export {env_var}=\"your-key-here\"[/green]\n\n"
                f"Or run [green]yoak init[/green] to reconfigure.",
                title="Configuration Error",
                border_style="red",
            )
        )
        return False
    return True


# ── Default command (no args) ─────────────────────────────────────────

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    """Run init on first use, then drop into chat."""
    if ctx.invoked_subcommand is not None:
        return
    if _needs_init():
        init()
    else:
        chat()


# ── Init ──────────────────────────────────────────────────────────────

@app.command()
def init():
    """Set up Yoak for the first time (or reconfigure)."""
    console.print(
        Panel(
            "[bold]Welcome to Yoak[/bold] — Your AI Cofounder\n\n"
            "Let's get you set up. This takes about 30 seconds.",
            border_style="blue",
        )
    )

    # 1. Project name
    project = console.input(
        "\n[bold]What's your startup called?[/bold] (or press Enter to skip): "
    ).strip()
    if not project:
        project = "My Startup"

    # 2. Detect or ask for model provider
    detected = _detect_available_provider()
    if detected:
        model, label = detected
        console.print(f"\n  Found [green]{label}[/green] API key in your environment.")
        use_detected = console.input(f"  Use [cyan]{model}[/cyan]? [Y/n]: ").strip().lower()
        if use_detected in ("", "y", "yes"):
            pass  # keep detected model
        else:
            model = _ask_model_choice()
    else:
        console.print(
            "\n  No API keys detected in your environment.\n"
            "  You'll need one from Anthropic, OpenAI, or Google — or use Ollama for local models."
        )
        model = _ask_model_choice()

    # 3. Save config
    settings = load_settings()
    settings.project_name = project

    if model == "ollama":
        settings.ollama.enabled = True
        ollama_model = console.input("  Ollama model name [llama3.1]: ").strip() or "llama3.1"
        settings.ollama.model = ollama_model
    else:
        settings.model.model = model
        settings.ollama.enabled = False

    save_settings(settings)

    console.print(
        Panel(
            f"[green bold]Ready![/green bold]\n\n"
            f"Project: [cyan]{project}[/cyan]\n"
            f"Model:   [cyan]{model}[/cyan]\n"
            f"Config:  [dim]{CONFIG_PATH}[/dim]\n\n"
            f"Run [green]yoak[/green] to start chatting with your cofounder.",
            border_style="green",
        )
    )


def _ask_model_choice() -> str:
    console.print("\n  Pick a model provider:\n")
    console.print("    [cyan]1[/cyan]  Anthropic  (Claude)      — export ANTHROPIC_API_KEY=...")
    console.print("    [cyan]2[/cyan]  OpenAI     (GPT-4o)      — export OPENAI_API_KEY=...")
    console.print("    [cyan]3[/cyan]  Google     (Gemini)      — export GEMINI_API_KEY=...")
    console.print("    [cyan]4[/cyan]  Ollama     (local, free) — ollama pull llama3.1")
    choice = console.input("\n  Choice [1]: ").strip() or "1"
    return {
        "1": "anthropic/claude-sonnet-4-20250514",
        "2": "gpt-4o",
        "3": "gemini/gemini-2.5-pro",
        "4": "ollama",
    }.get(choice, "anthropic/claude-sonnet-4-20250514")


# ── Chat ──────────────────────────────────────────────────────────────

@app.command()
def chat():
    """Start an interactive chat session with your AI cofounder."""
    if _needs_init():
        init()
    asyncio.run(_chat_loop())


async def _chat_loop():
    from yoak.core.agent import Agent
    from yoak.memory.canvas import get_canvas
    from yoak.memory.journal import list_entries
    from yoak.models.streaming import StreamAccumulator

    settings = load_settings()
    if not _check_model_ready(settings):
        return

    agent = Agent(settings)
    db = await agent.get_db()

    console.print(
        Panel(
            f"[bold]Yoak[/bold] — Cofounder for [cyan]{settings.project_name}[/cyan]\n"
            "Commands: /canvas  /workflow  /advance  /phase  /reset  /quit",
            border_style="blue",
        )
    )

    # First-run: detect empty project and kick things off
    blocks = await get_canvas(db)
    entries = await list_entries(db, limit=1)
    is_fresh = all(not b.content and not b.hypotheses for b in blocks) and not entries

    if is_fresh:
        console.print(
            "\n[dim]This is a fresh project. Here are some ways to start:[/dim]\n"
            "  [green]\"I have a startup idea about ...\"[/green]        → idea evaluation\n"
            "  [green]\"Help me figure out who my customer is\"[/green]  → customer discovery\n"
            "  [green]\"Review my product\"[/green]                      → product critique\n"
            "  [green]\"Am I default alive?\"[/green]                    → unit economics\n"
        )

    try:
        while True:
            try:
                user_input = console.input("[bold green]You:[/bold green] ")
            except (EOFError, KeyboardInterrupt):
                break

            if not user_input.strip():
                continue

            if user_input.strip().startswith("/"):
                await _handle_command(user_input.strip(), agent)
                continue

            await agent.auto_route(user_input)

            if agent.active_workflow:
                wf = agent.active_workflow
                step = wf["current_step"] + 1
                console.print(
                    f"  [dim]{wf['name'].replace('_', ' ')} — step {step}/{wf['total_steps']}: "
                    f"{wf['step_name']}[/dim]"
                )

            console.print("[bold blue]Yoak:[/bold blue] ", end="")
            acc = StreamAccumulator()
            try:
                async for chunk in agent.chat_stream(user_input):
                    acc.feed(chunk)
                    sys.stdout.write(chunk.delta)
                    sys.stdout.flush()
            except Exception as e:
                err = str(e)
                if "AuthenticationError" in err or "API Key" in err:
                    console.print("\n[red]Authentication failed — check your API key.[/red]")
                    agent._messages = agent._messages[:-1]
                    continue
                console.print(f"\n[red]Error: {e}[/red]")
                try:
                    agent._messages = agent._messages[:-1]
                    result = await agent.chat(user_input)
                    console.print(Markdown(result))
                except Exception as e2:
                    console.print(f"[red]{e2}[/red]")
                continue
            print()
    finally:
        await agent.close()


async def _handle_command(cmd: str, agent):
    from yoak.memory.canvas import canvas_summary, get_canvas
    from yoak.memory.journal import get_phase
    from yoak.workflows import WORKFLOW_REGISTRY

    parts = cmd.split()
    command = parts[0]

    if command == "/quit":
        raise typer.Exit()
    elif command == "/reset":
        agent.reset_conversation()
        console.print("[dim]Conversation reset.[/dim]")
    elif command == "/workflow":
        if len(parts) > 1:
            name = parts[1]
            if agent.start_workflow(name):
                console.print(f"[green]Started workflow: {name}[/green]")
            else:
                console.print(f"[red]Unknown workflow: {name}[/red]")
                console.print(f"Available: {', '.join(WORKFLOW_REGISTRY.keys())}")
        else:
            if agent.active_workflow:
                wf = agent.active_workflow
                console.print(
                    f"Active: [bold]{wf['name']}[/bold] — "
                    f"Step {wf['current_step']+1}/{wf['total_steps']}: {wf['step_name']}"
                )
            else:
                console.print("[dim]No active workflow.[/dim]")
                console.print(f"Available: {', '.join(WORKFLOW_REGISTRY.keys())}")
    elif command == "/advance":
        result = agent.advance_workflow()
        console.print(f"[green]{result or 'No active workflow.'}[/green]")
    elif command == "/canvas":
        db = await agent.get_db()
        blocks = await get_canvas(db)
        console.print(Markdown(canvas_summary(blocks)))
    elif command == "/phase":
        db = await agent.get_db()
        if len(parts) > 1:
            from yoak.memory.journal import set_phase

            await set_phase(db, parts[1])
            console.print(f"[green]Phase set to: {parts[1]}[/green]")
        else:
            phase = await get_phase(db)
            console.print(f"Current phase: [bold]{phase}[/bold]")
    else:
        console.print(f"[dim]Unknown command: {command}[/dim]")


# ── Config ────────────────────────────────────────────────────────────

config_app = typer.Typer(help="Manage Yoak configuration")
app.add_typer(config_app, name="config")


@config_app.command("show")
def config_show():
    """Show current configuration."""
    settings = load_settings()
    data = settings.model_dump()
    table = Table(title="Yoak Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    for section, values in data.items():
        if isinstance(values, dict):
            for k, v in values.items():
                table.add_row(f"{section}.{k}", str(v))
        else:
            table.add_row(section, str(values))
    console.print(table)


@config_app.command("set")
def config_set(key: str, value: str):
    """Set a configuration value (e.g., yoak config set model.model gpt-4o)."""
    try:
        parsed: str | int | float | bool = value
        if value.lower() in ("true", "false"):
            parsed = value.lower() == "true"
        elif "." in value:
            try:
                parsed = float(value)
            except ValueError:
                pass
        elif value.isdigit():
            parsed = int(value)
        update_setting(key, parsed)
        console.print(f"[green]Set {key} = {parsed}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


# ── Serve ─────────────────────────────────────────────────────────────

@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Server host"),
    port: int = typer.Option(8420, help="Server port"),
):
    """Start the Yoak API server and dashboard."""
    import uvicorn

    from yoak.api.app import create_app

    if _needs_init():
        init()

    settings = load_settings()
    if not _check_model_ready(settings):
        raise typer.Exit(1)

    console.print(
        Panel(
            f"[bold]Yoak Server[/bold] — {settings.project_name}\n"
            f"API:       http://{host}:{port}/docs\n"
            f"Dashboard: http://{host}:{port}",
            border_style="blue",
        )
    )
    uvicorn.run(create_app(), host=host, port=port)


# ── Canvas ────────────────────────────────────────────────────────────

@app.command()
def canvas():
    """Display the current Business Model Canvas."""
    asyncio.run(_show_canvas())


async def _show_canvas():
    from yoak.memory.canvas import canvas_summary, get_canvas
    from yoak.memory.store import get_db

    settings = load_settings()
    db = await get_db(settings.db_path)
    blocks = await get_canvas(db)
    console.print(Markdown(canvas_summary(blocks)))
    await db.close()


# ── Journal ───────────────────────────────────────────────────────────

@app.command()
def journal(entry_type: str = typer.Option(None, help="Filter by type"), limit: int = 20):
    """Show recent learning journal entries."""
    asyncio.run(_show_journal(entry_type, limit))


async def _show_journal(entry_type: str | None, limit: int):
    from yoak.memory.journal import list_entries
    from yoak.memory.store import get_db

    settings = load_settings()
    db = await get_db(settings.db_path)
    entries = await list_entries(db, entry_type=entry_type, limit=limit)
    if not entries:
        console.print("[dim]No journal entries yet.[/dim]")
    else:
        table = Table(title="Learning Journal")
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Title", style="bold")
        table.add_column("Date", style="dim")
        for e in entries:
            table.add_row(e.entry_type, e.title, e.created_at)
        console.print(table)
    await db.close()


if __name__ == "__main__":
    app()
