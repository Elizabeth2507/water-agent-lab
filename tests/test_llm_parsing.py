import pytest

from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.llm_parsing import (
    extract_json_object,
    parse_agent_decision,
    parse_json_model,
)


MARKDOWN_FENCE = "```"

VALID_AGENT_DECISION_JSON = """
{
  "stakeholder_name": "wrong-name",
  "status": "concerned",
  "argument": "Urban receives more than the minimum but less than requested.",
  "requested_extra_water": 5.0,
  "willingness_to_compromise": 0.6
}
"""


def build_fenced_json(json_text: str) -> str:
    """
    Build a Markdown fenced JSON block without making this test file hard
    to read in Markdown-rendered instructions.
    """
    return f"{MARKDOWN_FENCE}json\n{json_text.strip()}\n{MARKDOWN_FENCE}"


def test_parse_json_model_parses_agent_decision() -> None:
    text = """
    {
      "stakeholder_name": "agriculture",
      "status": "concerned",
      "argument": "The allocation is above minimum but still difficult.",
      "requested_extra_water": 2.0,
      "willingness_to_compromise": 0.7
    }
    """

    decision = parse_json_model(text, AgentDecision)

    assert decision.stakeholder_name == "agriculture"
    assert decision.status == "concerned"
    assert decision.requested_extra_water == 2.0


def test_parse_json_model_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="does not contain a JSON object"):
        parse_json_model("not json", AgentDecision)


def test_parse_json_model_rejects_invalid_schema() -> None:
    text = """
    {
      "stakeholder_name": "agriculture",
      "status": "concerned"
    }
    """

    with pytest.raises(ValueError, match="expected schema"):
        parse_json_model(text, AgentDecision)


def test_extract_json_object_from_raw_json() -> None:
    extracted = extract_json_object(VALID_AGENT_DECISION_JSON)

    assert extracted.strip().startswith("{")
    assert extracted.strip().endswith("}")


def test_extract_json_object_from_markdown_fence() -> None:
    text = f"""
Here is the decision:

{build_fenced_json(VALID_AGENT_DECISION_JSON)}
"""

    extracted = extract_json_object(text)

    assert '"stakeholder_name": "wrong-name"' in extracted


def test_extract_json_object_from_extra_text() -> None:
    text = f"""
The stakeholder decision is below.

{VALID_AGENT_DECISION_JSON}

This is the final answer.
"""

    extracted = extract_json_object(text)

    assert '"status": "concerned"' in extracted


def test_extract_json_object_rejects_text_without_json() -> None:
    with pytest.raises(ValueError, match="does not contain a JSON object"):
        extract_json_object("There is no JSON here.")


def test_extract_json_object_rejects_empty_text() -> None:
    with pytest.raises(ValueError, match="LLM response is empty"):
        extract_json_object(" ")


def test_parse_agent_decision_from_raw_json() -> None:
    decision = parse_agent_decision(
        text=VALID_AGENT_DECISION_JSON,
        stakeholder_name="urban",
    )

    assert decision.stakeholder_name == "urban"
    assert decision.status == "concerned"
    assert decision.requested_extra_water == 5.0


def test_parse_agent_decision_from_markdown_fence() -> None:
    text = f"""
Here is the result:

{build_fenced_json(VALID_AGENT_DECISION_JSON)}
"""

    decision = parse_agent_decision(
        text=text,
        stakeholder_name="urban",
    )

    assert decision.stakeholder_name == "urban"
    assert decision.status == "concerned"


def test_parse_agent_decision_from_extra_text() -> None:
    text = f"""
Here is the requested JSON:

{VALID_AGENT_DECISION_JSON}

Thanks.
"""

    decision = parse_agent_decision(
        text=text,
        stakeholder_name="urban",
    )

    assert decision.stakeholder_name == "urban"
    assert decision.status == "concerned"


def test_parse_agent_decision_strict_mode_rejects_extra_text() -> None:
    text = f"""
Here is the requested JSON:

{VALID_AGENT_DECISION_JSON}
"""

    with pytest.raises(ValueError, match="LLM response is not valid JSON"):
        parse_agent_decision(
            text=text,
            stakeholder_name="urban",
            allow_json_extraction=False,
        )


def test_parse_agent_decision_rejects_schema_mismatch() -> None:
    text = """
{
  "stakeholder_name": "urban",
  "status": "unknown",
  "argument": "Invalid status.",
  "requested_extra_water": 0.0,
  "willingness_to_compromise": 0.5
}
"""

    with pytest.raises(ValueError, match="expected schema"):
        parse_agent_decision(
            text=text,
            stakeholder_name="urban",
        )


def test_parse_agent_decision_repairs_simple_trailing_comma() -> None:
    text = """
{
  "stakeholder_name": "urban",
  "status": "concerned",
  "argument": "Urban receives less than requested.",
  "requested_extra_water": 5.0,
  "willingness_to_compromise": 0.6,
}
"""

    decision = parse_agent_decision(
        text=text,
        stakeholder_name="urban",
    )

    assert decision.stakeholder_name == "urban"
    assert decision.status == "concerned"
    assert decision.requested_extra_water == 5.0


def test_parse_json_model_uses_robust_extraction() -> None:
    text = f"""
Here is the model output:

{build_fenced_json(VALID_AGENT_DECISION_JSON)}
"""

    decision = parse_json_model(
        text=text,
        model_class=AgentDecision,
    )

    assert decision.stakeholder_name == "wrong-name"
    assert decision.status == "concerned"
