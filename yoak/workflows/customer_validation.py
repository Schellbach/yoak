"""Customer Validation workflow — Blank Phase 2."""

from yoak.workflows.base import Workflow, WorkflowStep


class CustomerValidationWorkflow(Workflow):
    name = "customer_validation"
    description = "Guide through Customer Validation: MVP development, sales to earlyvangelists, unit economics."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="MVP Development",
                prompt_supplement=(
                    "Help plan a higher-fidelity MVP for actual transactions:\n"
                    "- What MVP type is appropriate now? (needs to be functional enough for sales)\n"
                    "- Apply Jobs's quality lens: the core experience must be extraordinary even if incomplete.\n"
                    "- What is the minimum set of features to complete a real transaction?\n"
                    "- What can be manual/behind-the-scenes for now?"
                ),
            ),
            WorkflowStep(
                name="Sell to Earlyvangelists",
                prompt_supplement=(
                    "Guide the founder through actual sales attempts:\n"
                    "- Help identify earlyvangelist characteristics (visionary, has budget, has the problem)\n"
                    "- Attempt real transactions — not free trials, not LOIs. Real money.\n"
                    "- Document: who was contacted, the pitch used, objections raised, what worked.\n"
                    "- Collison installation: when someone says yes, set them up immediately."
                ),
            ),
            WorkflowStep(
                name="Sales Roadmap",
                prompt_supplement=(
                    "Help build a repeatable sales playbook:\n"
                    "- Who is the buyer? (title, role, decision authority)\n"
                    "- What triggers the buying decision?\n"
                    "- What pitch works? What are the top 3 objections?\n"
                    "- Average sales cycle, close rate.\n"
                    "- Could someone other than the founders execute this playbook?"
                ),
            ),
            WorkflowStep(
                name="Unit Economics",
                prompt_supplement=(
                    "Validate the unit economics:\n"
                    "- CAC: customer acquisition cost (all-in)\n"
                    "- LTV: lifetime value (ARPU / churn rate)\n"
                    "- LTV/CAC ratio (target > 3:1)\n"
                    "- Conversion funnel: awareness → interest → trial → purchase → retention\n"
                    "- Payback period (target < 12 months)\n"
                    "Flag any red flags honestly."
                ),
            ),
            WorkflowStep(
                name="P/M Fit Check",
                prompt_supplement=(
                    "Assess Product/Market Fit signals:\n"
                    "- Sean Ellis test: would 40%+ users be 'very disappointed' without the product?\n"
                    "- Do retention curves flatten?\n"
                    "- Is usage growing organically?\n"
                    "- Are customers referring others?\n"
                    "Provide an honest assessment: strong fit, partial fit, or no fit."
                ),
            ),
            WorkflowStep(
                name="Phase Gate",
                prompt_supplement=(
                    "Evaluate whether to advance to Customer Creation:\n"
                    "- [ ] Paying customers exist\n"
                    "- [ ] Sales process documented and repeatable\n"
                    "- [ ] Unit economics validated (LTV > 3× CAC)\n"
                    "- [ ] Product/Market Fit signals present\n"
                    "- [ ] Growth measurable and on trajectory\n\n"
                    "If not ready: recommend specific areas to iterate or consider pivot.\n"
                    "If ready: prepare for scaling investment."
                ),
            ),
        ]
        super().__init__()
