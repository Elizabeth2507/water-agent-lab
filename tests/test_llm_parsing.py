import pytest

from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.llm_parsing import parse_json_model


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
    with pytest.raises(ValueError, match="not valid JSON"):
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
