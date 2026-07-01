"""Customer Validation workflow — Blank Phase 2."""

from yoak.workflows.base import Workflow, WorkflowStep


class CustomerValidationWorkflow(Workflow):
    name = "customer_validation"
    description = "Prove someone will pay — repeatable sales and unit economics."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="What's the MVP?",
                min_user_chars=25,
                max_turns=1,
                prompt_supplement=(
                    "What's the smallest thing they can put in front of a buyer this week? Push for "
                    "concierge or wizard-of-oz before code. Challenge scope creep — one concrete offer, "
                    "not a roadmap."
                ),
            ),
            WorkflowStep(
                name="Did anyone pay?",
                min_user_chars=20,
                max_turns=2,
                prompt_supplement=(
                    "Ask for a real transaction — money, not intent. If none yet, name what's blocking "
                    "the ask and whether the offer is too vague. Use [CANVAS:revenue_streams] and "
                    "[HYPOTHESIS:*] when something concrete emerges."
                ),
            ),
            WorkflowStep(
                name="Can you repeat it?",
                min_user_chars=25,
                max_turns=2,
                prompt_supplement=(
                    "One sale isn't a business. Could someone else close the same deal? What objections "
                    "came up? Push if the pitch sounds founder-specific or unreplicable."
                ),
            ),
            WorkflowStep(
                name="Unit economics check",
                min_user_chars=20,
                max_turns=2,
                prompt_supplement=(
                    "Ballpark CAC, price, and retention. Flag if LTV looks below ~3x CAC or if they "
                    "don't know the numbers yet — that's a problem. Record with [CANVAS:cost_structure]."
                ),
            ),
            WorkflowStep(
                name="Product/market fit signal",
                min_user_chars=9999,
                max_turns=1,
                prompt_supplement=(
                    "Direct verdict: would customers be upset if this disappeared tomorrow? Say what "
                    "the evidence supports and what it doesn't. Record with [LEARNING]."
                ),
            ),
        ]
        super().__init__()
