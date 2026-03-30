"""Idea Evaluation workflow — PG-inspired idea scoring."""

from yoak.workflows.base import Workflow, WorkflowStep


class IdeaEvaluationWorkflow(Workflow):
    name = "idea_evaluation"
    description = "Evaluate a startup idea through PG filters and BMC mapping."

    def __init__(self) -> None:
        self.steps = [
            WorkflowStep(
                name="Understand the Idea",
                prompt_supplement=(
                    "The founder is describing a startup idea. "
                    "Ask ONE clarifying question to understand the core problem they're solving. "
                    "Don't analyze yet — just listen and ask."
                ),
            ),
            WorkflowStep(
                name="Who wants this?",
                prompt_supplement=(
                    "Now apply the 'well, not field' test: who wants this desperately enough "
                    "to use a crappy v1? Push the founder to name a specific person, not a market segment. "
                    "If the idea came from personal experience, note that as a strength. "
                    "Record what you learn with [CANVAS:customer_segments] and [HYPOTHESIS:*] tags."
                ),
            ),
            WorkflowStep(
                name="Map what we know",
                prompt_supplement=(
                    "Based on the conversation so far, fill in what we know on the canvas. "
                    "Use [CANVAS:*] tags for facts and [HYPOTHESIS:*] tags for guesses. "
                    "Tell the founder which blocks are empty or risky. Keep it brief — "
                    "just state what's known, what's guessed, and what's unknown."
                ),
            ),
            WorkflowStep(
                name="Riskiest assumption",
                prompt_supplement=(
                    "Identify the single riskiest assumption — the one that kills the idea if wrong. "
                    "Suggest the cheapest experiment to test it. Be specific: who to talk to, "
                    "what to build, what evidence would validate or kill it. One experiment, not five."
                ),
            ),
            WorkflowStep(
                name="Honest take",
                prompt_supplement=(
                    "Give your honest assessment in 3-4 sentences. What's strong, what's weak, "
                    "and what should the founder do THIS WEEK. Don't score on numbered scales — "
                    "just be direct. Record any key insight with a [LEARNING] tag."
                ),
            ),
        ]
        super().__init__()
