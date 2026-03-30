"""Pivot Decision workflow — structured pivot-or-persevere analysis."""

from yoak.workflows.base import Workflow, WorkflowStep


class PivotDecisionWorkflow(Workflow):
    name = "pivot_decision"
    description = "Decide whether to pivot or persevere based on evidence."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="What's not working?",
                prompt_supplement=(
                    "Ask the founder to describe what's not working. Listen for: "
                    "is the problem real but the solution wrong? Or is the customer wrong? "
                    "Or is nothing working at all? One question to understand the pain."
                ),
            ),
            WorkflowStep(
                name="What does the evidence say?",
                prompt_supplement=(
                    "Look at the canvas and hypotheses. Which ones have been invalidated? "
                    "How many experiments have they run? If fewer than 3 serious attempts, "
                    "it's probably too early to pivot. Be honest about the data."
                ),
            ),
            WorkflowStep(
                name="What would you change?",
                prompt_supplement=(
                    "If they should pivot: suggest what to change (customer, problem, solution, "
                    "channel, or revenue model) and why. If they should persevere: say so and "
                    "suggest the next experiment. Record the decision with [LEARNING]."
                ),
            ),
        ]
        super().__init__()
