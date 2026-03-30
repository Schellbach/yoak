"""Pivot Decision workflow — structured pivot-or-persevere analysis."""

from yoak.workflows.base import Workflow, WorkflowStep


class PivotDecisionWorkflow(Workflow):
    name = "pivot_decision"
    description = "Structured pivot-or-persevere decision based on evidence and hypothesis status."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="Evidence Review",
                prompt_supplement=(
                    "Gather the evidence:\n"
                    "- What hypotheses have been tested?\n"
                    "- How many experiments run on the current thesis?\n"
                    "- Summarize validated and invalidated hypotheses.\n"
                    "- What does the learning journal show?\n"
                    "Be thorough — the quality of this decision depends on the evidence base."
                ),
            ),
            WorkflowStep(
                name="Signal Analysis",
                prompt_supplement=(
                    "Check for pivot signals:\n"
                    "PIVOT signals: consistently failing milestones after 3+ iterations, "
                    "customer interviews invalidating core hypotheses, users engage but don't pay, "
                    "high CAC with low retention, team morale declining, market shifted.\n\n"
                    "PERSEVERE signals: haven't rigorously tested yet, only 1-2 negative data points, "
                    "wanting to pivot because work is hard (not because data says to), "
                    "have paying customers with growing revenue even if slow.\n\n"
                    "Which signals are present? Be honest."
                ),
            ),
            WorkflowStep(
                name="Diagnosis",
                prompt_supplement=(
                    "If pivoting seems right, diagnose:\n"
                    "- Which Business Model Canvas block(s) specifically failed?\n"
                    "- Is it the problem (wrong pain), customer (wrong segment), "
                    "solution (wrong approach), or model (wrong economics)?\n"
                    "The diagnosis determines the pivot type."
                ),
            ),
            WorkflowStep(
                name="Pivot Type Selection",
                prompt_supplement=(
                    "Based on the diagnosis, recommend a pivot type:\n"
                    "Zoom-in, Zoom-out, Customer Segment, Customer Need, Platform, "
                    "Business Architecture, Value Capture, Engine of Growth, Channel, Technology.\n"
                    "Explain why this specific pivot type fits the evidence."
                ),
            ),
            WorkflowStep(
                name="New Hypothesis & Plan",
                prompt_supplement=(
                    "Articulate the new direction:\n"
                    "- New hypothesis stated clearly\n"
                    "- Evidence from previous experiments that supports this direction\n"
                    "- First experiment to run on the new thesis\n"
                    "- Runway check: do you have enough to execute this pivot?\n"
                    "- Update the Business Model Canvas with the new hypotheses.\n"
                    "Log the pivot in the learning journal."
                ),
            ),
        ]
        super().__init__()
