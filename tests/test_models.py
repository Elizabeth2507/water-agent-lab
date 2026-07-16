import pytest
from pydantic import ValidationError

from water_agent_lab.models import AllocationProposal, ScenarioConfig, StakeholderConfig


def test_valid_stakeholder_config() -> None:
    stakeholder = StakeholderConfig(
        name="agriculture",
        requested_water=50.0,
        minimum_acceptable_water=35.0,
        priority=0.8,
    )

    assert stakeholder.name == "agriculture"
    assert stakeholder.requested_water == 50.0
    assert stakeholder.minimum_acceptable_water == 35.0
    assert stakeholder.priority == 0.8


def test_stakeholder_minimum_cannot_exceed_requested_water() -> None:
    with pytest.raises(ValidationError):
        StakeholderConfig(
            name="agriculture",
            requested_water=50.0,
            minimum_acceptable_water=60.0,
            priority=0.8,
        )


def test_priority_must_be_between_zero_and_one() -> None:
    with pytest.raises(ValidationError):
        StakeholderConfig(
            name="urban",
            requested_water=35.0,
            minimum_acceptable_water=28.0,
            priority=1.5,
        )


def test_scenario_must_have_stakeholders() -> None:
    with pytest.raises(ValidationError):
        ScenarioConfig(
            scenario_name="empty_scenario",
            country="France",
            region="Occitanie",
            drought_level="moderate",
            available_water=100.0,
            max_rounds=5,
            stakeholders=[],
        )


def test_allocation_values_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        AllocationProposal(
            allocations={
                "agriculture": -10.0,
                "urban": 20.0,
            }
        )
