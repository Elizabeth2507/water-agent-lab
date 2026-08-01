import pytest

from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.llm_decision_validation import (
    validate_or_repair_agent_decision,
)
from water_agent_lab.models import AllocationProposal, StakeholderConfig


def make_urban_stakeholder() -> StakeholderConfig:
    return StakeholderConfig(
        name="urban",
        requested_water=35.0,
        minimum_acceptable_water=28.0,
        priority=0.9,
    )


def test_repairs_accepted_decision_below_minimum_to_rejected() -> None:
    stakeholder = make_urban_stakeholder()
    proposal = AllocationProposal(
        allocations={
            "urban": 26.923076923076923,
        }
    )

    decision = AgentDecision(
        stakeholder_name="urban",
        status="accepted",
        argument=(
            "The current allocation respects our minimum acceptable water needs."
        ),
        requested_extra_water=0.0,
        willingness_to_compromise=0.9,
    )

    result = validate_or_repair_agent_decision(
        decision=decision,
        stakeholder=stakeholder,
        proposal=proposal,
    )

    assert result.was_repaired is True
    assert result.decision.status == "rejected"
    assert result.decision.requested_extra_water == pytest.approx(
        28.0 - 26.923076923076923
    )
    assert result.repairs


def test_repairs_accepted_decision_far_below_request_to_concerned() -> None:
    stakeholder = make_urban_stakeholder()
    proposal = AllocationProposal(
        allocations={
            "urban": 30.0,
        }
    )

    decision = AgentDecision(
        stakeholder_name="urban",
        status="accepted",
        argument="The allocation is acceptable.",
        requested_extra_water=0.0,
        willingness_to_compromise=0.8,
    )

    result = validate_or_repair_agent_decision(
        decision=decision,
        stakeholder=stakeholder,
        proposal=proposal,
    )

    assert result.was_repaired is True
    assert result.decision.status == "concerned"
    assert result.decision.requested_extra_water == pytest.approx(5.0)


def test_keeps_accepted_decision_near_requested_water() -> None:
    stakeholder = make_urban_stakeholder()
    proposal = AllocationProposal(
        allocations={
            "urban": 33.0,
        }
    )

    decision = AgentDecision(
        stakeholder_name="urban",
        status="accepted",
        argument="The allocation is close enough to the requested amount.",
        requested_extra_water=0.0,
        willingness_to_compromise=0.8,
    )

    result = validate_or_repair_agent_decision(
        decision=decision,
        stakeholder=stakeholder,
        proposal=proposal,
    )

    assert result.was_repaired is False
    assert result.decision.status == "accepted"
    assert result.decision.requested_extra_water == 0.0


def test_repairs_stakeholder_name_mismatch() -> None:
    stakeholder = make_urban_stakeholder()
    proposal = AllocationProposal(
        allocations={
            "urban": 33.0,
        }
    )

    decision = AgentDecision(
        stakeholder_name="wrong-name",
        status="accepted",
        argument="The allocation is acceptable.",
        requested_extra_water=0.0,
        willingness_to_compromise=0.8,
    )

    result = validate_or_repair_agent_decision(
        decision=decision,
        stakeholder=stakeholder,
        proposal=proposal,
    )

    assert result.was_repaired is True
    assert result.decision.stakeholder_name == "urban"


def test_repairs_accepted_decision_with_extra_water_request() -> None:
    stakeholder = make_urban_stakeholder()
    proposal = AllocationProposal(
        allocations={
            "urban": 33.0,
        }
    )

    decision = AgentDecision(
        stakeholder_name="urban",
        status="accepted",
        argument="The allocation is acceptable.",
        requested_extra_water=3.0,
        willingness_to_compromise=0.8,
    )

    result = validate_or_repair_agent_decision(
        decision=decision,
        stakeholder=stakeholder,
        proposal=proposal,
    )

    assert result.was_repaired is True
    assert result.decision.status == "accepted"
    assert result.decision.requested_extra_water == 0.0


def test_rejects_negative_requested_extra_water() -> None:
    with pytest.raises(ValueError):
        AgentDecision(
            stakeholder_name="urban",
            status="concerned",
            argument="The allocation is not ideal.",
            requested_extra_water=-1.0,
            willingness_to_compromise=0.6,
        )
