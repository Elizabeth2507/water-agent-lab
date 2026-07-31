import pytest

from water_agent_lab.config import load_scenario_config
from water_agent_lab.llm_single_agent import (
    evaluate_single_llm_stakeholder,
    find_stakeholder,
)
from water_agent_lab.strategies import proportional_allocation


def test_find_stakeholder() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    stakeholder = find_stakeholder(
        scenario=scenario,
        stakeholder_name="urban",
    )

    assert stakeholder.name == "urban"


def test_find_stakeholder_rejects_unknown_name() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    with pytest.raises(ValueError, match="Unknown stakeholder"):
        find_stakeholder(
            scenario=scenario,
            stakeholder_name="unknown",
        )


def test_evaluate_single_llm_stakeholder_with_mock_backend() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)

    decision = evaluate_single_llm_stakeholder(
        scenario=scenario,
        proposal=proposal,
        stakeholder_name="urban",
        backend_name="mock",
    )

    assert decision.stakeholder_name == "urban"
    assert decision.status == "rejected"
    assert decision.requested_extra_water > 0
    assert decision.argument
