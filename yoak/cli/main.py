"""Yoak CLI — management and chat interface."""

from __future__ import annotations

import asyncio
import os
from datetime import date
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from yoak.core.config import CONFIG_PATH, load_settings, save_settings, update_setting
from yoak.models.catalog import CLOUD_PROVIDERS, detect_api_key_in_env, provider_env_var

app = typer.Typer(
    name="yoak",
    help="Yoak — Lean Startup Cofounder Agent",
    invoke_without_command=True,
)
console = Console()


def _ollama_available() -> bool:
    """Check if Ollama is running locally."""
    try:
        import httpx

        r = httpx.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _ollama_has_model(model: str) -> bool:
    """Check if a specific model is pulled in Ollama."""
    try:
        import httpx

        r = httpx.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code != 200:
            return False
        tags = r.json().get("models", [])
        return any(model in t.get("name", "") for t in tags)
    except Exception:
        return False


def _detect_api_key() -> tuple[str, str, str] | None:
    """Find the first API key in the environment. Returns (model, label, env_var) or None."""
    return detect_api_key_in_env()


def _check_model_ready(settings) -> bool:
    """Verify the configured model is reachable. Returns True if ok."""
    if settings.ollama.enabled:
        if not _ollama_available():
            console.print(
                Panel(
                    "[yellow bold]Ollama is not running[/yellow bold]\n\n"
                    "Yoak defaults to Ollama for free, local AI. Start it with:\n"
                    "  [green]ollama serve[/green]\n\n"
                    "Then pull a model:\n"
                    "  [green]ollama pull llama3.1[/green]\n\n"
                    "Or switch to a cloud model:\n"
                    "  [green]yoak init[/green]",
                    title="Ollama Not Found",
                    border_style="yellow",
                )
            )
            return False
        return True

    model = settings.model.model
    env_var = provider_env_var(model)
    if env_var and not os.environ.get(env_var):
        console.print(
            Panel(
                f"[red bold]No API key found[/red bold]\n\n"
                f"Model is set to [cyan]{model}[/cyan] but [cyan]{env_var}[/cyan] is not set.\n\n"
                f"Fix it:\n"
                f"  [green]export {env_var}=\"your-key-here\"[/green]\n\n"
                f"Or switch to free local models:\n"
                f"  [green]yoak init[/green]",
                title="Configuration Error",
                border_style="red",
            )
        )
        return False
    return True


def _needs_init() -> bool:
    return not CONFIG_PATH.exists()


# ── Default command (no args) ─────────────────────────────────────────

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    """Run init on first use, then drop into chat."""
    if ctx.invoked_subcommand is not None:
        return
    if _needs_init():
        _run_init()
    asyncio.run(_chat_loop())


# ── Init ──────────────────────────────────────────────────────────────

def _run_init():
    """Interactive configuration (project name, model)."""
    console.print(
        Panel(
            "[bold]Welcome to Yoak[/bold] — your AI cofounder\n\n"
            "Yoak is the tool. On the next prompt, name [italic]your[/italic] startup — not \"Yoak\".\n"
            "This takes about 30 seconds.",
            border_style="blue",
        )
    )

    # 1. Project name
    project = console.input(
        "\n[bold]What's your startup called?[/bold] (press Enter for \"My Startup\"): "
    ).strip() or "My Startup"

    # 2. Detect what's available and pick the best default
    has_ollama = _ollama_available()
    api_key = _detect_api_key()

    if api_key:
        model, label, env_var = api_key
        console.print(f"\n  Found [green]{label}[/green] API key in your environment.")
        if has_ollama:
            console.print("  Also found [green]Ollama[/green] running locally.\n")
            console.print(f"    [cyan]1[/cyan]  {label} (cloud, uses {env_var})")
            console.print("    [cyan]2[/cyan]  Ollama (local, free, private)")
            choice = console.input("\n  Choice [1]: ").strip() or "1"
            if choice == "2":
                model = None  # will configure Ollama below
            # else keep the detected cloud model
        else:
            use_it = console.input(f"  Use [cyan]{model}[/cyan]? [Y/n]: ").strip().lower()
            if use_it not in ("", "y", "yes"):
                model = _ask_model_choice(has_ollama)
    elif has_ollama:
        console.print("\n  Found [green]Ollama[/green] running locally — perfect for getting started.")
        model = None  # will configure Ollama below
    else:
        console.print(
            "\n  No API keys or Ollama detected.\n\n"
            "  [bold]Easiest way to start (free):[/bold]\n"
            "    [green]1.[/green] Install Ollama:  [cyan]brew install ollama[/cyan]  (or https://ollama.ai)\n"
            "    [green]2.[/green] Start it:         [cyan]ollama serve[/cyan]\n"
            "    [green]3.[/green] Pull a model:     [cyan]ollama pull llama3.1[/cyan]\n"
            "    [green]4.[/green] Run this again:   [cyan]yoak init[/cyan]\n\n"
            "  Or set a cloud API key and pick a provider:"
        )
        model = _ask_model_choice(has_ollama=False)

    # 3. Save config
    settings = load_settings()
    settings.project_name = project

    if model is None:
        # Ollama path
        settings.ollama.enabled = True
        pulled = _get_ollama_models()
        if pulled:
            if len(pulled) == 1:
                ollama_model = pulled[0]
                console.print(f"  Using pulled model: [cyan]{ollama_model}[/cyan]")
            else:
                console.print("\n  Available Ollama models:")
                for i, m in enumerate(pulled, 1):
                    console.print(f"    [cyan]{i}[/cyan]  {m}")
                idx = console.input("\n  Choice [1]: ").strip() or "1"
                try:
                    ollama_model = pulled[int(idx) - 1]
                except (ValueError, IndexError):
                    ollama_model = pulled[0]
        else:
            ollama_model = console.input("  Model name [llama3.1]: ").strip() or "llama3.1"
            console.print(f"\n  [dim]Make sure to run: ollama pull {ollama_model}[/dim]")
        settings.ollama.model = ollama_model
        settings.model.model = f"ollama/{ollama_model}"
        display_model = f"ollama/{ollama_model} (local)"
    else:
        settings.model.model = model
        settings.ollama.enabled = False
        display_model = model

    save_settings(settings)

    console.print(
        Panel(
            f"[green bold]Ready![/green bold]\n\n"
            f"Project: [cyan]{project}[/cyan]\n"
            f"Model:   [cyan]{display_model}[/cyan]\n"
            f"Config:  [dim]{CONFIG_PATH}[/dim]\n\n"
            f"Run [green]yoak[/green] to start chatting — the web dashboard starts automatically.\n"
            f"Web UI: [cyan]http://127.0.0.1:8420[/cyan]\n"
            f"Obsidian export: [green]yoak export --vault <path>[/green]",
            border_style="green",
        )
    )


@app.command()
def init():
    """Set up Yoak for the first time (or reconfigure)."""
    _run_init()


def _get_ollama_models() -> list[str]:
    try:
        import httpx

        r = httpx.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code != 200:
            return []
        return [t["name"].split(":")[0] for t in r.json().get("models", [])]
    except Exception:
        return []


def _ask_model_choice(has_ollama: bool = False) -> str | None:
    console.print("\n  Pick a model provider:\n")
    choices: dict[str, str | None] = {}
    for i, provider in enumerate(CLOUD_PROVIDERS, 1):
        console.print(
            f"    [cyan]{i}[/cyan]  {provider.label:<22} — export {provider.env_var}=..."
        )
        choices[str(i)] = provider.default_model
    ollama_idx = len(CLOUD_PROVIDERS) + 1
    if has_ollama:
        console.print(f"    [cyan]{ollama_idx}[/cyan]  Ollama (local, free)")
    else:
        console.print(
            f"    [cyan]{ollama_idx}[/cyan]  Ollama (local, free) — install from https://ollama.ai"
        )
    choices[str(ollama_idx)] = None
    default = str(ollama_idx)
    choice = console.input(f"\n  Choice [{default}]: ").strip() or default
    return choices.get(choice, None)


async def _confirm_startup(settings, agent) -> None:
    """Confirm the active startup and offer rename."""
    startup = settings.project_name
    console.print(
        Panel(
            f"Current startup: [cyan]{startup}[/cyan]\n\n"
            "• [bold]Enter[/bold] — keep working on this startup\n"
            "• [bold]Type a name[/bold] — switch to a different startup\n\n"
            "[dim]To wipe chat, canvas, and journal, use /reset in chat.[/dim]",
            title="Welcome back",
            border_style="blue",
        )
    )

    try:
        choice = console.input("\nPress Enter to continue, or type a startup name: ").strip()
    except (EOFError, KeyboardInterrupt):
        console.print()
        return

    if not choice or choice == startup:
        return

    try:
        clear = console.input(
            f'Switch to "{choice}" and clear existing work (chat, canvas, journal)? [y/N]: '
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print()
        return

    settings.project_name = choice
    save_settings(settings)
    agent.settings = settings

    if clear in {"y", "yes"}:
        await agent.reset_all()
        console.print(f"[green]Switched to {choice} with a fresh start.[/green]\n")
    else:
        console.print(f"[green]Switched to {choice}.[/green]\n")


# ── Web UI (background server) ────────────────────────────────────────

def _server_responding(host: str, port: int) -> bool:
    try:
        import httpx

        r = httpx.get(f"http://{host}:{port}/api/phase", timeout=1)
        return r.status_code == 200
    except Exception:
        return False


def _ensure_web_ui_running(settings) -> str | None:
    """Start the dashboard in the background if it is not already running."""
    host = settings.server.host
    port = settings.server.port
    url = f"http://{host}:{port}"

    if _server_responding(host, port):
        console.print(f"[dim]Web UI already running at {url}[/dim]")
        return url

    from yoak.api.dashboard_build import ensure_dashboard_built

    try:
        ensure_dashboard_built(log=console.print)
    except SystemExit:
        console.print(
            "[yellow]Web UI skipped — install Node.js (https://nodejs.org/) "
            "then run [green]yoak serve[/green]. CLI chat works normally.[/yellow]"
        )
        return None

    import threading
    import time

    import uvicorn

    from yoak.api.app import create_app

    config = uvicorn.Config(create_app(), host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()

    for _ in range(50):
        if _server_responding(host, port):
            console.print(f"[green]Web UI running at {url}[/green]")
            return url
        time.sleep(0.2)

    console.print(f"[yellow]Web UI is still starting — try {url} in a moment.[/yellow]")
    return url


# ── Chat ──────────────────────────────────────────────────────────────

@app.command()
def chat():
    """Start an interactive chat session with your AI cofounder."""
    if _needs_init():
        _run_init()
    asyncio.run(_chat_loop())


async def _chat_loop():
    from yoak.core.agent import Agent
    from yoak.memory.canvas import get_canvas
    from yoak.memory.journal import list_entries

    settings = load_settings()
    if not _check_model_ready(settings):
        return

    web_url = _ensure_web_ui_running(settings)

    agent = Agent(settings)
    db = await agent.get_db()

    await _confirm_startup(settings, agent)
    settings = agent.settings

    model_label = settings.model.model
    if settings.ollama.enabled:
        model_label = f"{settings.ollama.model} (local)"

    console.print(
        Panel(
            f"[bold]Yoak[/bold] — AI cofounder\n"
            f"Startup: [cyan]{settings.project_name}[/cyan]\n"
            f"Model: [dim]{model_label}[/dim]\n"
            "Commands: /canvas  /workflow  /advance  /phase  /chatreset  /canvasreset  /reset  /quit\n"
            + (
                f"[dim]Web UI: {web_url}[/dim]\n"
                if web_url
                else "[dim]Web UI: run yoak serve (needs Node.js)[/dim]\n"
            )
            + "[dim]Export: yoak export --vault <path>[/dim]",
            border_style="blue",
        )
    )

    # First-run: detect empty project and show starter prompts
    blocks = await get_canvas(db)
    entries = await list_entries(db, limit=1)
    is_fresh = all(not b.content and not b.hypotheses for b in blocks) and not entries

    if is_fresh:
        console.print(
            "\n[dim]Fresh project. Here are some ways to start:[/dim]\n"
            '  [green]"I have a startup idea about ..."[/green]        → idea evaluation\n'
            '  [green]"Help me figure out who my customer is"[/green]  → customer discovery\n'
            '  [green]"Review my product"[/green]                      → product critique\n'
            '  [green]"Am I default alive?"[/green]                    → unit economics\n'
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

            try:
                result = await agent.chat(user_input)
                console.print(f"[bold blue]Yoak:[/bold blue] {result}")
            except Exception as e:
                err = str(e)
                if "AuthenticationError" in err or "API Key" in err:
                    console.print("[red]Authentication failed — check your API key.[/red]")
                    agent._messages = agent._messages[:-1]
                    continue
                if "Connection" in err or "ConnectError" in err:
                    console.print("[red]Cannot reach model. Is Ollama running? (ollama serve)[/red]")
                    agent._messages = agent._messages[:-1]
                    continue
                console.print(f"[red]Error: {e}[/red]")
                agent._messages = agent._messages[:-1]
                continue

            if agent.last_workflow_event:
                console.print(f"  [dim]{agent.last_workflow_event}[/dim]")

            if agent.active_workflow:
                wf = agent.active_workflow
                step = wf["current_step"] + 1
                console.print(
                    f"  [dim]{wf['name'].replace('_', ' ')} — step {step}/{wf['total_steps']}: "
                    f"{wf['step_name']}[/dim]"
                )

            # Show what was saved to memory
            ext = agent.last_extraction
            if ext and (ext.canvas_updates or ext.hypotheses or ext.learnings):
                parts = []
                for block_id, _ in ext.canvas_updates:
                    parts.append(f"canvas:{block_id.replace('_', ' ')}")
                for block_id, _ in ext.hypotheses:
                    parts.append("hypothesis added")
                for title, _ in ext.learnings:
                    parts.append(f"learned: {title}")
                console.print(f"  [dim]saved → {', '.join(parts)}[/dim]")
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
    elif command == "/chatreset":
        await agent.reset_chat()
        console.print("[dim]Conversation reset.[/dim]")
    elif command == "/canvasreset":
        await agent.reset_canvas()
        blocks = await get_canvas(await agent.get_db())
        empty = sum(1 for b in blocks if not b.content and not b.hypotheses)
        console.print(f"[dim]Lean Canvas reset ({empty}/9 blocks empty).[/dim]")
    elif command == "/reset":
        await agent.reset_all()
        blocks = await get_canvas(await agent.get_db())
        empty = sum(1 for b in blocks if not b.content and not b.hypotheses)
        console.print(
            f"[dim]Conversation, canvas, and journal reset ({empty}/9 canvas blocks empty).[/dim]"
        )
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
    elif command == "/model":
        console.print(
            f"Current: [cyan]{agent.settings.model.model}[/cyan]\n"
            f"Run [green]yoak init[/green] to change."
        )
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

def _run_serve(host: str, port: int) -> None:
    import uvicorn

    from yoak.api.app import create_app
    from yoak.api.dashboard_build import ensure_dashboard_built

    if _needs_init():
        _run_init()

    settings = load_settings()
    if not _check_model_ready(settings):
        raise typer.Exit(1)

    if _server_responding(host, port):
        console.print(
            Panel(
                f"[bold]Yoak Server[/bold] — {settings.project_name}\n"
                f"Already running at [cyan]http://{host}:{port}[/cyan]",
                border_style="blue",
            )
        )
        raise typer.Exit(0)

    ensure_dashboard_built(log=console.print)

    console.print(
        Panel(
            f"[bold]Yoak Server[/bold] — {settings.project_name}\n"
            f"API:       http://{host}:{port}/docs\n"
            f"Dashboard: http://{host}:{port}",
            border_style="blue",
        )
    )
    uvicorn.run(create_app(), host=host, port=port)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Server host"),
    port: int = typer.Option(8420, help="Server port"),
):
    """Start the Yoak API server and dashboard."""
    _run_serve(host, port)


# ── Export ────────────────────────────────────────────────────────────

@app.command("export")
def export_cmd(
    vault: Path | None = typer.Option(None, "--vault", help="Obsidian vault root path"),
    project: str | None = typer.Option(
        None,
        "--project",
        help="Project slug for <vault>/yoak/<project>/ (defaults to configured project name)",
    ),
    force: bool = typer.Option(False, "--force", help="Regenerate without confirmation"),
):
    """Export Yoak memory to an Obsidian vault (one-way, DB is source of truth)."""
    asyncio.run(_run_export(vault, project, force))


async def _run_export(vault: Path | None, project: str | None, force: bool):
    from yoak.export.filenames import project_slug
    from yoak.export.runner import export_to_vault
    from yoak.memory.store import get_db

    settings = load_settings()
    vault_path = vault or (Path(settings.export.vault_path) if settings.export.vault_path else None)
    if vault_path is None:
        console.print("[red]No vault path configured. Pass --vault or run a successful export first.[/red]")
        raise typer.Exit(1)

    project_name = settings.project_name
    project_id = project_slug(project) if project else (
        settings.export.project_slug or project_slug(project_name)
    )
    exported = date.today().isoformat()

    db = await get_db(settings.db_path)
    try:
        try:
            result = await export_to_vault(
                db,
                vault_path,
                project_name=project_name,
                project_id=project_id,
                exported=exported,
                force=force,
            )
        except FileExistsError as exc:
            if force or typer.confirm(f"{exc}\nProceed anyway?"):
                result = await export_to_vault(
                    db,
                    vault_path,
                    project_name=project_name,
                    project_id=project_id,
                    exported=exported,
                    force=True,
                )
            else:
                raise typer.Exit() from exc
    finally:
        await db.close()

    settings.export.vault_path = str(vault_path.expanduser().resolve())
    settings.export.project_slug = project_id
    save_settings(settings)

    console.print(
        Panel(
            f"[green bold]Export complete[/green bold]\n\n"
            f"Vault:   [cyan]{result.output_dir.parent.parent}[/cyan]\n"
            f"Project: [cyan]{project_id}[/cyan]\n"
            f"Output:  [cyan]{result.output_dir}[/cyan]\n"
            f"Files:   {len(result.files_written)} written",
            border_style="green",
        )
    )
    for warning in result.warnings:
        console.print(f"[yellow]{warning}[/yellow]")
    for deleted in result.files_deleted:
        console.print(f"[dim]Removed stale: {deleted}[/dim]")


# ── Hypotheses ────────────────────────────────────────────────────────

@app.command()
def hypotheses(
    canvas_block: str = typer.Option(None, "--block", help="Filter by canvas block"),
    status: str = typer.Option(None, help="Filter: untested, testing, validated, invalidated"),
):
    """List hypotheses linked to the Lean Canvas."""
    asyncio.run(_show_hypotheses(canvas_block, status))


async def _show_hypotheses(canvas_block: str | None, status: str | None):
    from yoak.memory.canvas import LEAN_CANVAS_BLOCKS
    from yoak.memory.hypotheses import list_hypotheses
    from yoak.memory.store import get_db

    settings = load_settings()
    db = await get_db(settings.db_path)
    results = await list_hypotheses(db, canvas_block=canvas_block, status=status)
    if not results:
        console.print("[dim]No hypotheses yet.[/dim]")
    else:
        block_names = dict(LEAN_CANVAS_BLOCKS)
        table = Table(title="Hypotheses")
        table.add_column("Block", style="cyan", width=18)
        table.add_column("Status", width=12)
        table.add_column("Statement")
        table.add_column("Conf.", justify="right", width=6)
        for h in results:
            block = block_names.get(h.canvas_block, h.canvas_block.replace("_", " "))
            table.add_row(block, h.status, h.statement, f"{h.confidence:.0%}")
        console.print(table)
    await db.close()


# ── Canvas ────────────────────────────────────────────────────────────

@app.command()
def canvas():
    """Display the current Lean Canvas."""
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
