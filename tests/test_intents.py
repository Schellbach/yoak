from yoak.core.intents import is_meta_request, wants_canvas_display


def test_wants_canvas_display():
    assert wants_canvas_display("can you show the canvas?")
    assert wants_canvas_display("/canvas")
    assert not wants_canvas_display("I have mango trees in my yard")


def test_meta_request_skips_workflow_turns():
    assert is_meta_request("/canvas")
    assert is_meta_request("show me the canvas")
    assert not is_meta_request("people will pay for individual analyses")
