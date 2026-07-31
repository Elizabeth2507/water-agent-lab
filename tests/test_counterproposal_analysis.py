from water_agent_lab.config import load_scenario_config
from water_agent_lab.counterproposal_analysis import compare_counterproposal_impact
from water_agent_lab.counterproposals import (
    build_counterproposal_adjusted_allocation,
    summarize_counterproposals,
)
from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.models import AllocationProposal


def test_compare_counterproposal_impact() -> None:
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

    adjusted = build_counterproposal_adjusted_allocation(
        scenario=scenario,
        proposal=proposal,
        counterproposal_summary=summary,
    )

    original_result = evaluate_proposal(scenario, proposal)
    adjusted_result = evaluate_proposal(scenario, adjusted)

    impact = compare_counterproposal_impact(
        original_result=original_result,
        adjusted_result=adjusted_result,
    )

    assert isinstance(impact.fairness_delta, float)
    assert isinstance(impact.conflict_delta, float)
    assert isinstance(impact.minimum_satisfaction_delta, float)
    assert isinstance(impact.shortage_delta, float)
