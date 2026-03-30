"""Idea Evaluation workflow — PG-inspired idea scoring."""

from yoak.workflows.base import Workflow, WorkflowStep


class IdeaEvaluationWorkflow(Workflow):
    name = "idea_evaluation"
    description = "Evaluate a startup idea through PG filters, BMC mapping, and risk identification."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="Understand the Idea",
                prompt_supplement=(
                    "Ask the founder to describe their idea. Get clarity on: "
                    "What problem does it solve? Who has this problem? How do they solve it today? "
                    "Why is now the right time? Listen carefully before analyzing."
                ),
            ),
            WorkflowStep(
                name="Apply PG Filters",
                prompt_supplement=(
                    "Apply Paul Graham's idea filters to what the founder described:\n"
                    "1. The 'well, not field' test: who wants this desperately, enough for a crappy v1?\n"
                    "2. Schlep blindness check: is this avoided because it's scary/tedious? (positive signal)\n"
                    "3. Unsexy filter check: does it sound boring? (positive signal)\n"
                    "4. Organic vs manufactured: does this come from personal experience?\n"
                    "5. Path out: can this expand from niche to large market?\n"
                    "Be honest and specific. Cite evidence from the founder's description."
                ),
            ),
            WorkflowStep(
                name="Map to Business Model Canvas",
                prompt_supplement=(
                    "Map the idea to the 9 Business Model Canvas blocks. For each block, classify "
                    "what the founder knows as Fact (validated), Hypothesis (believed but untested), "
                    "or Unknown (not yet considered). Flag the blocks with the riskiest hypotheses."
                ),
            ),
            WorkflowStep(
                name="Identify Riskiest Assumption",
                prompt_supplement=(
                    "Identify the single assumption that, if wrong, kills the entire idea. "
                    "Then suggest the cheapest, fastest experiment to test it. "
                    "What evidence would validate it? What evidence would invalidate it?"
                ),
            ),
            WorkflowStep(
                name="Score and Advise",
                prompt_supplement=(
                    "Score the idea on 5 dimensions (1-10 each):\n"
                    "- Strength of need: How painful is this problem?\n"
                    "- Founder-market fit: How well does this founder understand the domain?\n"
                    "- Timing: Why now? Is there a secular trend?\n"
                    "- Moat potential: Can this build compounding advantages?\n"
                    "- Path out: Plausible expansion from niche to large market?\n\n"
                    "Then give concrete next steps. Be direct about weaknesses."
                ),
            ),
        ]
        super().__init__()
