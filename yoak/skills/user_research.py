"""User Research skill — interview scripts and insight synthesis."""

from yoak.skills.base import Skill


class UserResearchSkill(Skill):
    name = "user_research"
    description = "Generate interview scripts and synthesize user research findings."
    prompt_file = "interviews.md"
