"""Competitive Intelligence skill — competitor mapping, moat analysis."""

from yoak.skills.base import Skill


class CompetitiveIntelSkill(Skill):
    name = "competitive_intel"
    description = "Map competitors, analyze moats, and identify positioning opportunities."
    prompt_file = "competition.md"
