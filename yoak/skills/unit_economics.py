"""Unit Economics skill — CAC/LTV, burn rate, default alive analysis."""

from yoak.skills.base import Skill


class UnitEconomicsSkill(Skill):
    name = "unit_economics"
    description = "Model unit economics: CAC, LTV, burn rate, runway, default alive/dead."
    prompt_file = "economics.md"
