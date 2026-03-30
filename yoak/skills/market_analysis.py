"""Market Analysis skill — TAM/SAM/SOM, market type, timing."""

from yoak.skills.base import Skill


class MarketAnalysisSkill(Skill):
    name = "market_analysis"
    description = "Analyze market size, type, competitive landscape, and timing."
    prompt_file = "market.md"
