"""Yoak CLI — management and chat interface."""

from __future__ import annotations

import asyncio
import sys

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from yoak.core.config import load_settings, update_setting

app = typer.Typer(
    name="yoak",
    help="Yoak — Lean Startup Cofounder Agent",
    no_args_is_help=True,
)
console = Console()


# ── Chat ──────────────────────────────────────────────────────────────

@app.command()
def chat():
    """Start an interactive chat session with your AI cofounder."""
    asyncio.run(_chat_loop())


async def _chat_loop():
    from yoak.core.agent import Agent
    from yoak.models.streaming import StreamAccumulator

    settings = load_settings()
    agent = Agent(settings)

    console.print(
        Panel(
            "[bold]Yoak[/bold] — Your AI Cofounder\n"
            "Type your message. Commands: /workflow, /advance, /canvas, /phase, /reset, /quit",
            border_style="blue",
        )
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
                step = wf['current_step'] + 1
                console.print(
                    f"  [dim]Workflow: {wf['name']} — Step {step}/{wf['total_steps']}: {wf['step_name']}[/dim]"
                )

            console.print("[bold blue]Yoak:[/bold blue] ", end="")
            acc = StreamAccumulator()
            full_text = ""
            try:
                async for chunk in agent.chat_stream(user_input):
                    acc.feed(chunk)
                    sys.stdout.write(chunk.delta)
                    sys.stdout.flush()
                full_text = acc.text
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                console.print("[dim]Falling back to non-streaming...[/dim]")
                try:
                    agent._messages = agent._messages[:-1]
                    full_text = await agent.chat(user_input)
                    console.print(Markdown(full_text))
                except Exception as e2:
                    console.print(f"[red]Error: {e2}[/red]")
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
        summary = canvas_summary(blocks)
        console.print(Markdown(summary))

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

    console.print(
        Panel(
            f"[bold]Yoak Server[/bold]\n"
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
    from yoak.core.config import load_settings
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
