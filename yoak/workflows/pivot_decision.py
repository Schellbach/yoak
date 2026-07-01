"""Pivot Decision workflow — structured pivot-or-persevere analysis."""

from yoak.workflows.base import Workflow, WorkflowStep


class PivotDecisionWorkflow(Workflow):
    name = "pivot_decision"
    description = "Decide whether to pivot or persevere based on evidence."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="What's not working?",
                min_user_chars=30,
                max_turns=1,
                prompt_supplement=(
                    "From what they've already said, name what's failing — wrong customer, weak pain, "
                    "bad solution, or no traction at all. Ask one hard question only if critical context "
                    "is missing."
                ),
            ),
            WorkflowStep(
                name="What does the evidence say?",
                min_user_chars=20,
                max_turns=2,
                prompt_supplement=(
                    "Review canvas and hypotheses: what's invalidated? If fewer than ~3 serious experiments, "
                    "say it's probably too early to pivot. Don't sugarcoat thin evidence."
                ),
            ),
            WorkflowStep(
                name="What would you change?",
                min_user_chars=9999,
                max_turns=1,
                prompt_supplement=(
                    "Recommend pivot or persevere with reasons. If pivoting, name what to change "
                    "(customer, problem, solution, channel, revenue) and the next experiment. "
                    "Record with [LEARNING]."
                ),
            ),
        ]
        super().__init__()
