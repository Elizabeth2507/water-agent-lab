import pytest

from water_agent_lab.config import load_scenario_config
from water_agent_lab.models import AllocationProposal
from water_agent_lab.simulator import (
    priority_weighted_allocation,
    proportional_allocation,
)


def test_proportional_allocation_returns_allocation_proposal() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    proposal = proportional_allocation(scenario)

    assert isinstance(proposal, AllocationProposal)


def test_proportional_allocation_values() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    proposal = proportional_allocation(scenario)

    assert proposal.allocations["agriculture"] == pytest.approx(38.461538)
    assert proposal.allocations["urban"] == pytest.approx(26.923077)
    assert proposal.allocations["industry"] == pytest.approx(19.230769)
    assert proposal.allocations["ecosystem"] == pytest.approx(15.384615)


def test_proportional_allocation_uses_available_water() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    proposal = proportional_allocation(scenario)

    total_allocated = sum(proposal.allocations.values())

    assert total_allocated == pytest.approx(scenario.available_water)


def test_priority_weighted_allocation_returns_allocation_proposal() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    proposal = priority_weighted_allocation(scenario)

    assert isinstance(proposal, AllocationProposal)


def test_priority_weighted_allocation_uses_available_water() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    proposal = priority_weighted_allocation(scenario)

    total_allocated = sum(proposal.allocations.values())

    assert total_allocated == pytest.approx(scenario.available_water)


def test_priority_weighted_allocation_values() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    proposal = priority_weighted_allocation(scenario)

    assert proposal.allocations["agriculture"] == pytest.approx(38.461538)
    assert proposal.allocations["urban"] == pytest.approx(30.288462)
    assert proposal.allocations["industry"] == pytest.approx(12.019231)
    assert proposal.allocations["ecosystem"] == pytest.approx(19.230769)
