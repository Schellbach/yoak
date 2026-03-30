"""Skill registry."""

from yoak.skills.base import Skill
from yoak.skills.competitive_intel import CompetitiveIntelSkill
from yoak.skills.growth_strategy import GrowthStrategySkill
from yoak.skills.market_analysis import MarketAnalysisSkill
from yoak.skills.unit_economics import UnitEconomicsSkill
from yoak.skills.user_research import UserResearchSkill

SKILL_REGISTRY: dict[str, Skill] = {
    "market_analysis": MarketAnalysisSkill(),
    "user_research": UserResearchSkill(),
    "competitive_intel": CompetitiveIntelSkill(),
    "growth_strategy": GrowthStrategySkill(),
    "unit_economics": UnitEconomicsSkill(),
}


def get_skill(name: str) -> Skill | None:
    return SKILL_REGISTRY.get(name)
