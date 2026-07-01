"""Customer Discovery workflow — Blank Phase 1."""

from yoak.workflows.base import Workflow, WorkflowStep


class CustomerDiscoveryWorkflow(Workflow):
    name = "customer_discovery"
    description = "Validate that a real, painful problem exists for a specific customer."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="What's the riskiest hypothesis?",
                min_user_chars=20,
                max_turns=1,
                prompt_supplement=(
                    "From the canvas and chat history, name the riskiest untested belief — or ask "
                    "one sharp question if you truly don't know the customer yet. Do not re-ask "
                    "what they already explained. Push back if the hypothesis sounds untestable."
                ),
            ),
            WorkflowStep(
                name="Plan interviews",
                min_user_chars=25,
                max_turns=2,
                prompt_supplement=(
                    "Help them get out of the building this week: who exactly to talk to, and one "
                    "opening question — not a script. Challenge vague plans ('talk to users') with "
                    "a concrete next action."
                ),
            ),
            WorkflowStep(
                name="What did you hear?",
                min_user_chars=30,
                max_turns=2,
                prompt_supplement=(
                    "Ask what they heard from real conversations. If they haven't talked to anyone, "
                    "say so directly and redirect to scheduling one interview. When they share results, "
                    "record with [LEARNING] and [CANVAS:*] / [HYPOTHESIS:*]. Name what's weak in the evidence."
                ),
            ),
            WorkflowStep(
                name="Pattern check",
                min_user_chars=25,
                max_turns=2,
                prompt_supplement=(
                    "Stress-test the pattern: is the pain real or polite interest? Be honest if the "
                    "evidence is lukewarm. Suggest a different segment or problem if the signal is weak."
                ),
            ),
            WorkflowStep(
                name="Ready to move on?",
                min_user_chars=9999,
                max_turns=1,
                prompt_supplement=(
                    "Give a direct read: enough evidence to move to validation, or not yet — and why. "
                    "If not, name the single next test. Record the decision with [LEARNING]."
                ),
            ),
        ]
        super().__init__()
