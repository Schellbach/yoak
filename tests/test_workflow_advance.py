from yoak.workflows.idea_evaluation import IdeaEvaluationWorkflow


def test_auto_advance_after_substantive_reply():
    wf = IdeaEvaluationWorkflow()
    message = "A platform for backyard fruit tree owners to map premium genetics."
    wf.record_user_turn(message)
    assert wf.should_auto_advance(message)
    wf.advance()
    assert wf.current_step.name == "Who wants this?"


def test_no_auto_advance_on_final_step():
    wf = IdeaEvaluationWorkflow()
    wf._current_step_index = len(wf.steps) - 1
    wf.record_user_turn("Anything here.")
    assert not wf.should_auto_advance("Anything here.")


def test_complete_after_response_on_final_step():
    wf = IdeaEvaluationWorkflow()
    wf._current_step_index = len(wf.steps) - 1
    assert wf.complete_after_response()
    assert wf.is_complete
