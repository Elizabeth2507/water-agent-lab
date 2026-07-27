import pytest

from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import (
    compute_conflict_score,
    compute_fairness_score,
    compute_minimum_satisfaction_score,
    compute_shortage_score,
    compute_total_allocated,
    compute_total_requested,
    evaluate_proposal,
)
from water_agent_lab.simulator import (
    minimum_first_allocation,
    minimum_priority_allocation,
    proportional_allocation,
)


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
    assert result.minimum_satisfaction_score == pytest.approx(0.954059829)
    assert result.shortage_score == pytest.approx(1.0 - 100.0 / 130.0)


def test_minimum_first_allocation_reaches_agreement_for_moderate_drought() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = minimum_first_allocation(scenario)

    result = evaluate_proposal(scenario, proposal)

    assert result.water_budget_valid is True
    assert result.conflict_score == 0.0
    assert result.agreement_reached is True


def test_compute_minimum_satisfaction_score() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)

    score = compute_minimum_satisfaction_score(scenario, proposal)

    assert score == pytest.approx(0.954059829)


def test_compute_shortage_score() -> None:
    score = compute_shortage_score(
        total_requested=130.0,
        total_allocated=100.0,
    )

    assert score == pytest.approx(1.0 - 100.0 / 130.0)


def test_minimum_first_allocation_has_full_minimum_satisfaction() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = minimum_first_allocation(scenario)

    result = evaluate_proposal(scenario, proposal)

    assert result.minimum_satisfaction_score == 1.0
    assert result.conflict_score == 0.0
    assert result.agreement_reached is True


def test_minimum_priority_allocation_reaches_agreement_for_moderate_drought() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = minimum_priority_allocation(scenario)

    result = evaluate_proposal(scenario, proposal)

    assert result.water_budget_valid is True
    assert result.conflict_score == 0.0
    assert result.minimum_satisfaction_score == 1.0
    assert result.agreement_reached is True