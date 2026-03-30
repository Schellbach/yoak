"""Ensure the React dashboard is built to dashboard/dist for FastAPI to serve."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DASHBOARD = _REPO_ROOT / "dashboard"
_DIST_INDEX = _DASHBOARD / "dist" / "index.html"


def dashboard_dist_ready() -> bool:
    return _DIST_INDEX.is_file()


def _sources_newer_than_dist() -> bool:
    """True if dashboard source changed after the last production build (heuristic: src vs dist mtime)."""
    if not dashboard_dist_ready():
        return False
    try:
        dist_mtime = _DIST_INDEX.stat().st_mtime
        src_root = _DASHBOARD / "src"
        if not src_root.is_dir():
            return False
        paths = [p for p in src_root.rglob("*") if p.is_file()]
        if not paths:
            return False
        latest = max(p.stat().st_mtime for p in paths)
        return latest > dist_mtime
    except OSError:
        return False


def ensure_dashboard_built(*, log) -> None:
    """Build dashboard with npm if dist/ is missing or stale. ``log`` is a one-arg string printer."""
    if dashboard_dist_ready() and not _sources_newer_than_dist():
        return

    npm = shutil.which("npm")
    if not npm:
        log(
            "[red bold]Web UI needs a one-time build[/red bold]\n\n"
            "Install [cyan]Node.js[/cyan] (includes npm): https://nodejs.org/\n"
            "Then run: [green]make ui[/green]"
        )
        raise SystemExit(1)

    log("[cyan]Building web dashboard[/cyan] (first time only — needs Node.js)...")

    def _npm_run(args: list[str]) -> None:
        subprocess.run([npm, *args], cwd=_DASHBOARD, check=True)

    try:
        if (_DASHBOARD / "package-lock.json").is_file():
            subprocess.run([npm, "ci"], cwd=_DASHBOARD, check=True)
        else:
            _npm_run(["install"])
    except subprocess.CalledProcessError:
        _npm_run(["install"])

    try:
        _npm_run(["run", "build"])
    except subprocess.CalledProcessError as e:
        log(f"[red]Dashboard build failed.[/red] Try manually: cd dashboard && npm install && npm run build\n{e}")
        raise SystemExit(1) from e

    if not dashboard_dist_ready():
        log("[red]Dashboard build finished but dist/index.html is missing.[/red]")
        raise SystemExit(1)

    log("[green]Web dashboard ready.[/green]")
