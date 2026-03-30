"""Customer Validation workflow — Blank Phase 2."""

from yoak.workflows.base import Workflow, WorkflowStep


class CustomerValidationWorkflow(Workflow):
    name = "customer_validation"
    description = "Prove someone will pay — repeatable sales and unit economics."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="What's the MVP?",
                prompt_supplement=(
                    "What's the smallest thing the founder can put in front of a customer "
                    "to test willingness to pay? Push for concierge or wizard-of-oz before code. "
                    "One question to clarify what they could ship this week."
                ),
            ),
            WorkflowStep(
                name="Did anyone pay?",
                prompt_supplement=(
                    "Ask if they've gotten a real transaction — money, not a promise. "
                    "If yes, record it. If not, ask what's blocking the ask. "
                    "Use [CANVAS:revenue_streams] and [HYPOTHESIS:*] to capture what's learned."
                ),
            ),
            WorkflowStep(
                name="Can you repeat it?",
                prompt_supplement=(
                    "One sale isn't a business. Ask: could someone else on the team close the same deal? "
                    "What was the pitch? What were the objections? Start building the playbook."
                ),
            ),
            WorkflowStep(
                name="Unit economics check",
                prompt_supplement=(
                    "Ask about the numbers: what does it cost to acquire a customer? "
                    "What do they pay? How long do they stay? Don't need precision — "
                    "ballpark is fine. Flag if LTV < 3x CAC. Record with [CANVAS:cost_structure]."
                ),
            ),
            WorkflowStep(
                name="Product/market fit signal",
                prompt_supplement=(
                    "Ask: if you took this product away tomorrow, would anyone be upset? "
                    "That's the real test. If yes — strong signal, consider scaling. "
                    "If no — keep iterating. Record the assessment with [LEARNING]."
                ),
            ),
        ]
        super().__init__()
