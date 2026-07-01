from yoak.core.extractor import parse_response, sanitize_response_text


def test_sanitize_strips_user_header_and_echo():
    text = (
        "Demand for pedigree data is unproven — I'd want proof someone pays.\n\n"
        "### User:\n"
        "It's for selling pedigree analysis and mapping premium trees."
    )
    clean = sanitize_response_text(text)
    assert "### User" not in clean
    assert "pedigree analysis" not in clean
    assert "unproven" in clean


def test_sanitize_strips_role_label_lines():
    text = "Good pushback.\nUser: I already told you the monetization model."
    clean = sanitize_response_text(text)
    assert clean == "Good pushback."


def test_parse_response_applies_sanitizer():
    text = "Real answer.\n### Assistant:\nMore junk"
    extraction = parse_response(text)
    assert extraction.clean_text == "Real answer."


def test_parse_response_still_extracts_tags():
    text = "Noted.\n[CANVAS:customer_segments] Backyard orchard owners"
    extraction = parse_response(text)
    assert extraction.canvas_updates == [("customer_segments", "Backyard orchard owners")]
    assert extraction.clean_text == "Noted."


def test_parse_response_handles_spaced_hypothesis_tag():
    text = (
        "Is the value proposition focused on harvests?\n\n"
        "[HYPOTHESIS: customer_segments] Backyard fruit tree owners are motivated by improving harvests."
    )
    extraction = parse_response(text)
    assert extraction.hypotheses == [
        ("customer_segments", "Backyard fruit tree owners are motivated by improving harvests.")
    ]
    assert "[HYPOTHESIS" not in extraction.clean_text
    assert "value proposition" in extraction.clean_text


def test_parse_response_handles_markdown_wrapped_canvas():
    text = "**[CANVAS:customer_segments] Commercial orchard owners or backyard enthusiasts.**"
    extraction = parse_response(text)
    assert extraction.canvas_updates == [
        ("customer_segments", "Commercial orchard owners or backyard enthusiasts.")
    ]
    assert extraction.clean_text == ""


def test_parse_response_handles_header_prefixed_tag():
    text = "### [CANVAS: channels] Users discover varieties through a shared pedigree map."
    extraction = parse_response(text)
    assert extraction.canvas_updates == [
        ("channels", "Users discover varieties through a shared pedigree map.")
    ]
    assert "[CANVAS" not in extraction.clean_text
