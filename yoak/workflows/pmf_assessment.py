"""Product/Market Fit Assessment workflow."""

from yoak.workflows.base import Workflow, WorkflowStep


class PMFAssessmentWorkflow(Workflow):
    name = "pmf_assessment"
    description = "Assess Product/Market Fit using qualitative and quantitative signals."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="Qualitative Assessment",
                prompt_supplement=(
                    "Check each qualitative P/M Fit signal with the founder:\n"
                    "- Customers buying as fast as you can produce?\n"
                    "- Usage growing organically / word of mouth?\n"
                    "- Customers upset at idea of product disappearing?\n"
                    "- Press/analysts reaching out to you?\n"
                    "- Hiring because demand exceeds capacity?\n"
                    "- Revenue growing without proportional marketing spend?\n"
                    "- Customer referrals as meaningful acquisition source?\n"
                    "Get specific evidence for each, not just yes/no."
                ),
            ),
            WorkflowStep(
                name="Quantitative Assessment",
                prompt_supplement=(
                    "Gather the numbers:\n"
                    "- Sean Ellis test results (% 'very disappointed' — need 40%+)\n"
                    "- Retention curves: flatten or decline to zero?\n"
                    "- Weekly growth rate (target 5-7%)\n"
                    "- Organic vs. paid ratio\n"
                    "- CAC, LTV, LTV/CAC ratio (target >3:1)\n"
                    "- Monthly churn (target <5% SMB, <2% enterprise)\n"
                    "- NPS score (target 40+)\n"
                    "Help them calculate what they don't have."
                ),
            ),
            WorkflowStep(
                name="Diagnosis & Recommendation",
                prompt_supplement=(
                    "Based on qualitative + quantitative data, diagnose:\n\n"
                    "**Strong P/M Fit**: 40%+ very disappointed, retention flattens, LTV/CAC >3:1, "
                    "organic growth present. → Advance to Customer Creation.\n\n"
                    "**Partial P/M Fit**: Fit exists in a subsegment. Some strong signals but inconsistent. "
                    "→ Narrow focus to strongest segment, deepen the fit there.\n\n"
                    "**No P/M Fit**: Most signals negative, growth proportional to spend, high churn, "
                    "divergent feature requests. → Return to Discovery/Validation, consider pivot.\n\n"
                    "Be direct about the diagnosis. Hope is not a strategy."
                ),
            ),
        ]
        super().__init__()
