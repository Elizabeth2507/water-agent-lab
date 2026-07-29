import pytest
from pydantic import ValidationError

from water_agent_lab.agent_models import (
    AgentDecision,
    AgentMessage,
    AgentProfile,
    AgentState,
)


def test_agent_profile_defaults() -> None:
    profile = AgentProfile(
        name="agriculture",
        role="Agricultural water user",
    )

    assert profile.name == "agriculture"
    assert profile.role == "Agricultural water user"
    assert profile.goals == []
    assert profile.constraints == []
    assert profile.negotiation_style == "balanced"


def test_agent_state_defaults() -> None:
    state = AgentState()

    assert state.frustration == 0.0
    assert state.trust_in_mediator == 0.5
    assert state.concessions_made == 0
    assert state.last_status is None


def test_agent_state_validates_ranges() -> None:
    with pytest.raises(ValidationError):
        AgentState(frustration=1.5)

    with pytest.raises(ValidationError):
        AgentState(trust_in_mediator=-0.1)


def test_agent_message_accepts_response_message() -> None:
    message = AgentMessage(
        sender="agriculture",
        recipient="mediator",
        round_number=1,
        message_type="response",
        content="The allocation is difficult but acceptable.",
    )

    assert message.sender == "agriculture"
    assert message.recipient == "mediator"
    assert message.round_number == 1
    assert message.message_type == "response"


def test_agent_message_counterproposal_requires_requested_change() -> None:
    with pytest.raises(ValidationError):
        AgentMessage(
            sender="agriculture",
            recipient="mediator",
            round_number=1,
            message_type="counterproposal",
            content="We need more water.",
        )


def test_agent_message_accepts_counterproposal_with_requested_change() -> None:
    message = AgentMessage(
        sender="agriculture",
        recipient="mediator",
        round_number=1,
        message_type="counterproposal",
        content="We need three more units to avoid severe losses.",
        requested_water_change=3.0,
    )

    assert message.requested_water_change == 3.0


def test_agent_decision_accepts_concerned_status() -> None:
    decision = AgentDecision(
        stakeholder_name="urban",
        status="concerned",
        argument="The allocation is above minimum but below preferred demand.",
        requested_extra_water=2.0,
        willingness_to_compromise=0.7,
    )

    assert decision.stakeholder_name == "urban"
    assert decision.status == "concerned"
    assert decision.requested_extra_water == 2.0


def test_agent_decision_rejected_requires_argument() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            stakeholder_name="ecosystem",
            status="rejected",
            argument="",
        )


def test_agent_decision_validates_requested_extra_water() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(
            stakeholder_name="industry",
            status="concerned",
            argument="Industry requests more water.",
            requested_extra_water=-1.0,
        )
