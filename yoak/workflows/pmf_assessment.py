"""Product/Market Fit Assessment workflow."""

from yoak.workflows.base import Workflow, WorkflowStep


class PMFAssessmentWorkflow(Workflow):
    name = "pmf_assessment"
    description = "Assess whether you have product/market fit."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="The disappointment test",
                prompt_supplement=(
                    "Ask: 'If you shut down tomorrow, would anyone be genuinely upset?' "
                    "Not politely disappointed — actually upset. Push for honesty. "
                    "This is the Sean Ellis test in plain language."
                ),
            ),
            WorkflowStep(
                name="Where's the pull?",
                prompt_supplement=(
                    "Ask about organic growth signals: are customers coming without marketing? "
                    "Are they referring others? Is usage growing week over week? "
                    "Get specific numbers if possible. Record what you learn."
                ),
            ),
            WorkflowStep(
                name="Verdict",
                prompt_supplement=(
                    "Based on what you've heard, give a direct verdict: strong fit, partial fit, "
                    "or no fit yet. If partial — where's the subsegment with the strongest signal? "
                    "If no fit — what should they go back and test? Record with [LEARNING]."
                ),
            ),
        ]
        super().__init__()
