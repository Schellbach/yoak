"""Customer Discovery workflow — Blank Phase 1."""

from yoak.workflows.base import Workflow, WorkflowStep


class CustomerDiscoveryWorkflow(Workflow):
    name = "customer_discovery"
    description = "Validate that a real, painful problem exists for a specific customer."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="What's the riskiest hypothesis?",
                prompt_supplement=(
                    "Look at the current canvas. What's the riskiest untested hypothesis? "
                    "If the canvas is empty, ask the founder who their customer is and what "
                    "problem they're solving. One question only."
                ),
            ),
            WorkflowStep(
                name="Plan interviews",
                prompt_supplement=(
                    "Help plan the next customer interview. Ask: who specifically should they "
                    "talk to this week? Help them write ONE opening question — not a full script. "
                    "The goal is to get them out of the building, not to prepare a perfect plan."
                ),
            ),
            WorkflowStep(
                name="What did you hear?",
                prompt_supplement=(
                    "The founder should have talked to someone by now. Ask what they heard. "
                    "Listen for: did the customer recognize the problem? How do they solve it today? "
                    "Record any insight with [LEARNING] and update the canvas with [CANVAS:*] or [HYPOTHESIS:*]."
                ),
            ),
            WorkflowStep(
                name="Pattern check",
                prompt_supplement=(
                    "Ask if they're seeing a pattern across conversations. Does the problem feel "
                    "real and painful, or lukewarm? Be honest about what the evidence says. "
                    "If it's weak, suggest a different customer segment or problem to test."
                ),
            ),
            WorkflowStep(
                name="Ready to move on?",
                prompt_supplement=(
                    "Check: do we have evidence that the problem exists and someone would pay to solve it? "
                    "If yes, suggest moving to validation. If not, suggest what to test next. "
                    "Record the decision with [LEARNING]."
                ),
            ),
        ]
        super().__init__()
