"""Lightweight intent detection for meta commands inside chat."""

from __future__ import annotations

_CANVAS_PHRASES = (
    "show the canvas",
    "show me the canvas",
    "can you show the canvas",
    "display the canvas",
    "see the canvas",
    "view the canvas",
    "what's on the canvas",
    "whats on the canvas",
    "show canvas",
)


def wants_canvas_display(message: str) -> bool:
    msg = message.lower().strip()
    if msg.startswith("/canvas"):
        return True
    return any(phrase in msg for phrase in _CANVAS_PHRASES)


def is_meta_request(message: str) -> bool:
    stripped = message.strip()
    return wants_canvas_display(message) or stripped.startswith("/")
