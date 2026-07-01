"""Product Critique workflow — Jobs-inspired product quality review."""

from yoak.workflows.base import Workflow, WorkflowStep


class ProductCritiqueWorkflow(Workflow):
    name = "product_critique"
    description = "Review a product through the lens of simplicity, focus, and craft."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="What's the experience?",
                min_user_chars=30,
                max_turns=1,
                prompt_supplement=(
                    "If they already described the product, skip re-interviewing. State the ideal "
                    "customer experience in one sentence, where reality falls short, and one thing "
                    "that worries you about the UX."
                ),
            ),
            WorkflowStep(
                name="What would you cut?",
                min_user_chars=20,
                max_turns=2,
                prompt_supplement=(
                    "Push hard on focus: what could they remove and still deliver core value? "
                    "Most products have too much. Challenge feature lists that dilute the main job."
                ),
            ),
            WorkflowStep(
                name="Honest critique",
                min_user_chars=9999,
                max_turns=1,
                prompt_supplement=(
                    "Give an honest 3-4 sentence critique: what's strong, what's weak, the one thing "
                    "to fix first. Apply Jobs's test — does it feel inevitable? Include at least one "
                    "uncomfortable truth. Record with [LEARNING] if appropriate."
                ),
            ),
        ]
        super().__init__()
