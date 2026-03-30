"""Growth Strategy skill — engine selection, metrics, PG growth principles."""

from yoak.skills.base import Skill


class GrowthStrategySkill(Skill):
    name = "growth_strategy"
    description = "Design growth engine, set metric targets, evaluate growth trajectory."
    prompt_file = "growth.md"
