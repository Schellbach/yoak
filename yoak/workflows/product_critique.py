"""Product Critique workflow — Jobs-inspired product quality review."""

from yoak.workflows.base import Workflow, WorkflowStep


class ProductCritiqueWorkflow(Workflow):
    name = "product_critique"
    description = "Review a product through the lens of simplicity, focus, and craft."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="What's the experience?",
                prompt_supplement=(
                    "Ask the founder to describe the ideal customer experience in plain language — "
                    "no technology, no features. Just: what happens for the customer? "
                    "Then ask where reality falls short."
                ),
            ),
            WorkflowStep(
                name="What would you cut?",
                prompt_supplement=(
                    "Ask: what could you remove and still deliver the core value? "
                    "Push hard here. Most products have too much, not too little. "
                    "The goal is to find the one thing it does brilliantly."
                ),
            ),
            WorkflowStep(
                name="Honest critique",
                prompt_supplement=(
                    "Give your honest take on the product in 3-4 sentences. "
                    "What's the one thing that should improve first? "
                    "Apply Jobs's test: does it feel inevitable, like obviously how it should work? "
                    "Record any key insight with [LEARNING]."
                ),
            ),
        ]
        super().__init__()
