from water_agent_lab.llm_parsing import parse_agent_decision


MARKDOWN_FENCE = "```"


def build_fenced_json(json_text: str) -> str:
    """
    Build a Markdown fenced JSON block for parser tests.
    """
    return f"{MARKDOWN_FENCE}json\n{json_text.strip()}\n{MARKDOWN_FENCE}"


def test_qwen_smoke_test_parser_accepts_markdown_json() -> None:
    json_text = """
{
  "stakeholder_name": "urban",
  "status": "concerned",
  "argument": "Urban receives more than the minimum but less than requested.",
  "requested_extra_water": 5.0,
  "willingness_to_compromise": 0.6
}
"""

    text = f"""
Here is the result:

{build_fenced_json(json_text)}
"""

    decision = parse_agent_decision(
        text=text,
        stakeholder_name="urban",
    )

    assert decision.stakeholder_name == "urban"
    assert decision.status == "concerned"
