from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.config import load_scenario_config
from water_agent_lab.counterproposals import (
    build_counterproposal_adjusted_allocation,
    summarize_counterproposals,
)
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.models import AllocationProposal
from water_agent_lab.simulator import minimum_first_allocation


def test_summarize_counterproposals() -> None:
    decisions = [
        AgentDecision(
            stakeholder_name="agriculture",
            status="concerned",
            argument="Agriculture requests more water.",
            requested_extra_water=3.0,
            willingness_to_compromise=0.6,
        ),
        AgentDecision(
            stakeholder_name="urban",
            status="accepted",
            argument="Urban accepts.",
            requested_extra_water=0.0,
            willingness_to_compromise=0.9,
        ),
    ]

    summary = summarize_counterproposals(decisions)

    assert summary.requested_changes == {"agriculture": 3.0}
    assert summary.total_requested_extra_water == 3.0
    assert summary.stakeholders_requesting_extra_water == ["agriculture"]


def test_counterproposal_adjusted_allocation_preserves_budget() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = minimum_first_allocation(scenario)

    decisions = [
        AgentDecision(
            stakeholder_name="agriculture",
            status="concerned",
            argument="Agriculture requests more water.",
            requested_extra_water=2.0,
            willingness_to_compromise=0.6,
        )
    ]

    summary = summarize_counterproposals(decisions)

    revised = build_counterproposal_adjusted_allocation(
        scenario=scenario,
        proposal=proposal,
        counterproposal_summary=summary,
    )

    result = evaluate_proposal(scenario, revised)

    assert result.water_budget_valid is True
    assert result.total_allocated <= scenario.available_water + 1e-9


def test_counterproposal_adjusted_allocation_increases_requester_if_possible() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    proposal = AllocationProposal(
        allocations={
            "agriculture": 36.0,
            "urban": 30.0,
            "industry": 16.0,
            "ecosystem": 18.0,
        }
    )

    decisions = [
        AgentDecision(
            stakeholder_name="agriculture",
            status="concerned",
            argument="Agriculture requests more water.",
            requested_extra_water=2.0,
            willingness_to_compromise=0.6,
        )
    ]

    summary = summarize_counterproposals(decisions)

    revised = build_counterproposal_adjusted_allocation(
        scenario=scenario,
        proposal=proposal,
        counterproposal_summary=summary,
    )

    assert revised.allocations["agriculture"] > proposal.allocations["agriculture"]
    assert sum(revised.allocations.values()) <= scenario.available_water + 1e-9


def test_counterproposal_adjusted_allocation_does_not_reduce_below_minimum() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = minimum_first_allocation(scenario)

    decisions = [
        AgentDecision(
            stakeholder_name="urban",
            status="concerned",
            argument="Urban requests more water.",
            requested_extra_water=10.0,
            willingness_to_compromise=0.5,
        )
    ]

    summary = summarize_counterproposals(decisions)

    revised = build_counterproposal_adjusted_allocation(
        scenario=scenario,
        proposal=proposal,
        counterproposal_summary=summary,
    )

    minimum_by_name = {
        stakeholder.name: stakeholder.minimum_acceptable_water
        for stakeholder in scenario.stakeholders
    }

    for stakeholder_name, allocated_water in revised.allocations.items():
        assert allocated_water >= minimum_by_name[stakeholder_name] - 1e-9


def test_counterproposal_adjusted_allocation_returns_same_when_no_requests() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = minimum_first_allocation(scenario)

    summary = summarize_counterproposals([])

    revised = build_counterproposal_adjusted_allocation(
        scenario=scenario,
        proposal=proposal,
        counterproposal_summary=summary,
    )

    assert revised.allocations == proposal.allocations
