import pytest

from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import (
    compute_conflict_score,
    compute_fairness_score,
    compute_total_allocated,
    compute_total_requested,
    evaluate_proposal,
)
from water_agent_lab.simulator import proportional_allocation


def test_compute_total_requested() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    total_requested = compute_total_requested(scenario)

    assert total_requested == 130.0


def test_compute_total_allocated() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)

    total_allocated = compute_total_allocated(proposal)

    assert total_allocated == pytest.approx(100.0)


def test_compute_fairness_score() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)

    fairness_score = compute_fairness_score(scenario, proposal)

    assert fairness_score == pytest.approx(100.0 / 130.0)


def test_compute_conflict_score() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)

    conflict_score = compute_conflict_score(scenario, proposal)

    assert conflict_score == 0.5


def test_evaluate_proposal_result() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)

    result = evaluate_proposal(scenario, proposal)

    assert result.scenario_name == "moderate_drought_mvp"
    assert result.total_requested == 130.0
    assert result.total_allocated == pytest.approx(100.0)
    assert result.water_budget_valid is True
    assert result.fairness_score == pytest.approx(100.0 / 130.0)
    assert result.conflict_score == 0.5
    assert result.agreement_reached is False
