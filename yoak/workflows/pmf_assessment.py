"""Product/Market Fit Assessment workflow."""

from yoak.workflows.base import Workflow, WorkflowStep


class PMFAssessmentWorkflow(Workflow):
    name = "pmf_assessment"
    description = "Assess whether you have product/market fit."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="The disappointment test",
                min_user_chars=20,
                max_turns=1,
                prompt_supplement=(
                    "Apply the Sean Ellis test in plain language: if they shut down tomorrow, would "
                    "anyone be genuinely upset? Push for honesty — polite interest doesn't count."
                ),
            ),
            WorkflowStep(
                name="Where's the pull?",
                min_user_chars=25,
                max_turns=2,
                prompt_supplement=(
                    "Ask for organic pull: referrals, usage growth, customers arriving without marketing. "
                    "Challenge hand-wavy answers — get numbers or admit you don't have them yet."
                ),
            ),
            WorkflowStep(
                name="Verdict",
                min_user_chars=9999,
                max_turns=1,
                prompt_supplement=(
                    "Give a direct verdict: strong fit, partial fit, or not yet — with reasons. "
                    "Name the strongest subsegment if partial. Record with [LEARNING]."
                ),
            ),
        ]
        super().__init__()
