"""Idea Evaluation workflow — PG-inspired idea scoring."""

from yoak.workflows.base import Workflow, WorkflowStep


class IdeaEvaluationWorkflow(Workflow):
    name = "idea_evaluation"
    description = "Evaluate a startup idea through PG filters and BMC mapping."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="Understand the Idea",
                min_user_chars=25,
                max_turns=1,
                prompt_supplement=(
                    "If the founder already explained the idea in prior messages, do NOT ask them "
                    "to repeat it. State the core problem in one short sentence, name one thing that "
                    "sounds promising and one thing that worries you, then ask the single hardest "
                    "clarifying question you still need."
                ),
            ),
            WorkflowStep(
                name="Who wants this?",
                min_user_chars=30,
                max_turns=2,
                prompt_supplement=(
                    "Apply the 'well, not field' test. Who wants this desperately enough to use a "
                    "crappy v1 — name a specific person, not a segment. Push back if the customer "
                    "sounds vague or the pain sounds mild. Record with [CANVAS:customer_segments] "
                    "and [HYPOTHESIS:*] tags when you learn something concrete."
                ),
            ),
            WorkflowStep(
                name="Map what we know",
                min_user_chars=20,
                max_turns=2,
                prompt_supplement=(
                    "Update the canvas from what was already said — do not re-interview. Use "
                    "[CANVAS:*] and [HYPOTHESIS:*] tags. In plain language, name the biggest gap "
                    "or contradiction you see. Challenge one assumption that still looks untested."
                ),
            ),
            WorkflowStep(
                name="Riskiest assumption",
                min_user_chars=20,
                max_turns=2,
                prompt_supplement=(
                    "Name the single riskiest assumption — the one that kills the idea if wrong. "
                    "If they already mentioned monetization or demand, stress-test it: why would "
                    "someone pay, and for what exactly? Propose one cheap experiment (who to talk "
                    "to, what to build, what result validates or kills it)."
                ),
            ),
            WorkflowStep(
                name="Honest take",
                min_user_chars=9999,
                max_turns=1,
                prompt_supplement=(
                    "Give your honest cofounder take in 3-4 sentences: what's strong, what's weak, "
                    "what to do THIS WEEK. Be direct — include at least one uncomfortable truth. "
                    "No numbered scores. Record a key insight with [LEARNING] if appropriate."
                ),
            ),
        ]
        super().__init__()
