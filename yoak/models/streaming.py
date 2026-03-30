"""Streaming utilities for assembling model output."""

from __future__ import annotations

from dataclasses import dataclass, field

from yoak.models.provider import Chunk


@dataclass
class StreamAccumulator:
    """Collects streaming chunks into a complete response."""

    chunks: list[str] = field(default_factory=list)
    finish_reason: str | None = None

    def feed(self, chunk: Chunk) -> str:
        if chunk.delta:
            self.chunks.append(chunk.delta)
        if chunk.finish_reason:
            self.finish_reason = chunk.finish_reason
        return chunk.delta

    @property
    def text(self) -> str:
        return "".join(self.chunks)

    @property
    def done(self) -> bool:
        return self.finish_reason is not None
