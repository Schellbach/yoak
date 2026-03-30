"""Product Critique workflow — Jobs-inspired product quality review."""

from yoak.workflows.base import Workflow, WorkflowStep


class ProductCritiqueWorkflow(Workflow):
    name = "product_critique"
    description = "Review a product through Steve Jobs's design philosophy."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="Experience-First Review",
                prompt_supplement=(
                    "Before examining features or technical details:\n"
                    "1. Ask the founder to describe the ideal customer experience in plain language, "
                    "without mentioning technology.\n"
                    "2. Then describe what the actual product delivers.\n"
                    "3. Where does reality fall short of the ideal? Those gaps are the priorities."
                ),
            ),
            WorkflowStep(
                name="Simplicity Audit",
                prompt_supplement=(
                    "Evaluate simplicity:\n"
                    "- Can a new user understand the core value within 30 seconds?\n"
                    "- How many steps from first touch to first value?\n"
                    "- What could be removed without losing the core experience?\n"
                    "- Is any element present from inertia rather than intent?\n"
                    "Remember: 'If you're not embarrassed by v1, you launched too late' — "
                    "but the core experience must still be extraordinary."
                ),
            ),
            WorkflowStep(
                name="Focus & Quality Audit",
                prompt_supplement=(
                    "Evaluate focus and quality:\n"
                    "Focus: What is the ONE thing this does brilliantly? Does every feature serve it?\n"
                    "Quality: Is attention to detail consistent throughout? Check error states, "
                    "empty states, loading states, edge cases.\n"
                    "Does the product feel inevitable — like this is obviously how it should work?"
                ),
            ),
            WorkflowStep(
                name="Verdict & Recommendations",
                prompt_supplement=(
                    "Score each dimension (1-10):\n"
                    "- Simplicity: How effortless is the core experience?\n"
                    "- Focus: How clearly does this serve one purpose brilliantly?\n"
                    "- Craft: How consistent is the quality throughout?\n"
                    "- Empathy: How deeply does this understand the customer?\n"
                    "- Delight: Does anything surprise or delight?\n\n"
                    "Then provide specific, actionable recommendations ordered by impact."
                ),
            ),
        ]
        super().__init__()
