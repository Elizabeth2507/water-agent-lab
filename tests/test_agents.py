from water_agent_lab.agents import (
    RuleBasedStakeholderAgent,
    evaluate_stakeholder_responses,
)
from water_agent_lab.config import load_scenario_config
from water_agent_lab.models import AllocationProposal, StakeholderConfig
from water_agent_lab.simulator import minimum_first_allocation, proportional_allocation


def test_agent_rejects_allocation_below_minimum() -> None:
    stakeholder = StakeholderConfig(
        name="ecosystem",
        requested_water=20.0,
        minimum_acceptable_water=18.0,
        priority=1.0,
    )
    proposal = AllocationProposal(allocations={"ecosystem": 15.0})

    agent = RuleBasedStakeholderAgent(stakeholder)
    response = agent.evaluate_allocation(proposal)

    assert response.status == "rejected"
    assert response.stakeholder_name == "ecosystem"
    assert response.allocated_water == 15.0


def test_agent_is_concerned_when_above_minimum_but_below_request() -> None:
    stakeholder = StakeholderConfig(
        name="agriculture",
        requested_water=50.0,
        minimum_acceptable_water=35.0,
        priority=0.8,
    )
    proposal = AllocationProposal(allocations={"agriculture": 40.0})

    agent = RuleBasedStakeholderAgent(stakeholder)
    response = agent.evaluate_allocation(proposal)

    assert response.status == "concerned"


def test_agent_accepts_allocation_close_to_request() -> None:
    stakeholder = StakeholderConfig(
        name="urban",
        requested_water=35.0,
        minimum_acceptable_water=28.0,
        priority=0.9,
    )
    proposal = AllocationProposal(allocations={"urban": 33.0})

    agent = RuleBasedStakeholderAgent(stakeholder)
    response = agent.evaluate_allocation(proposal)

    assert response.status == "accepted"


def test_evaluate_stakeholder_responses_returns_one_response_per_stakeholder() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)

    responses = evaluate_stakeholder_responses(
        stakeholders=scenario.stakeholders,
        proposal=proposal,
    )

    assert len(responses) == len(scenario.stakeholders)


def test_minimum_first_allocation_has_no_rejected_responses_for_moderate_drought() -> (
    None
):
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = minimum_first_allocation(scenario)

    responses = evaluate_stakeholder_responses(
        stakeholders=scenario.stakeholders,
        proposal=proposal,
    )

    assert all(response.status != "rejected" for response in responses)
