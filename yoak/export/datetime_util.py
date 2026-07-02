"""Parse SQLite datetime strings for export."""

from __future__ import annotations


def parse_date(value: str) -> str:
    return value[:10]


def parse_time(value: str) -> str:
    if len(value) >= 16 and value[10] == " ":
        return value[11:16]
    return "00:00"
