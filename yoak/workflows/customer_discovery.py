"""Customer Discovery workflow — Blank Phase 1."""

from yoak.workflows.base import Workflow, WorkflowStep


class CustomerDiscoveryWorkflow(Workflow):
    name = "customer_discovery"
    description = "Guide through Customer Discovery: hypothesis review, interview design, synthesis, solution testing."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="Hypothesis Review",
                prompt_supplement=(
                    "Review the Business Model Canvas with the founder. For each block:\n"
                    "- What's been validated by evidence?\n"
                    "- What's still a hypothesis?\n"
                    "- What's completely unknown?\n"
                    "Identify the riskiest untested assumption — this is what we test next."
                ),
                exit_criteria=["Riskiest hypothesis identified"],
            ),
            WorkflowStep(
                name="Interview Planning",
                prompt_supplement=(
                    "Help design customer interviews to test the riskiest hypothesis:\n"
                    "- Who should they interview? (specific segment, job title, context)\n"
                    "- What questions should they ask? (use Blank problem interview protocol)\n"
                    "- What would constitute validation vs. invalidation? (define BEFORE interviewing)\n"
                    "- Target: minimum 15-20 problem interviews before conclusions.\n"
                    "Generate a concrete interview script."
                ),
                exit_criteria=["Interview script created", "Target interviewees defined"],
            ),
            WorkflowStep(
                name="Interview Debrief",
                prompt_supplement=(
                    "Help synthesize interview findings:\n"
                    "- What patterns emerged across 3+ interviews?\n"
                    "- What surprised the founder? What contradicted assumptions?\n"
                    "- Capture the most compelling verbatim customer quotes.\n"
                    "- Update the Business Model Canvas based on evidence.\n"
                    "- Did a different, more painful problem emerge?"
                ),
                exit_criteria=["Canvas updated with interview evidence"],
            ),
            WorkflowStep(
                name="Solution Testing",
                prompt_supplement=(
                    "The problem has been validated. Now help design a low-fidelity MVP:\n"
                    "- Which MVP type fits? (concierge, landing page, wizard of oz, etc.)\n"
                    "- Define success criteria BEFORE showing it to anyone.\n"
                    "- Plan the solution test: who will see it, how, when.\n"
                    "Apply Jobs's quality lens: even a low-fi MVP should nail the core experience."
                ),
                exit_criteria=["MVP type selected", "Success criteria defined"],
            ),
            WorkflowStep(
                name="Phase Gate",
                prompt_supplement=(
                    "Evaluate whether to advance to Customer Validation. Check:\n"
                    "- [ ] Customer segment identified and confirmed\n"
                    "- [ ] Problem validated as genuinely painful\n"
                    "- [ ] Evidence of willingness to pay\n"
                    "- [ ] Value proposition in customer's own language\n"
                    "- [ ] At least one MVP tested with real customers\n\n"
                    "If not all boxes checked: recommend iteration or pivot.\n"
                    "If yes: congratulate and prepare to advance to Validation."
                ),
                exit_criteria=["Phase gate decision made"],
            ),
        ]
        super().__init__()
