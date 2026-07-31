import pytest
from water_agent_lab.agent_models import AgentDecision, AgentState
from water_agent_lab.agent_state_manager import (
    initialize_agent_states,
    update_agent_state_from_decision,
)


def test_update_agent_state_from_rejected_decision() -> None:
    state = AgentState()

    decision = AgentDecision(
        stakeholder_name="ecosystem",
        status="rejected",
        argument="Allocation is below minimum.",
        requested_extra_water=5.0,
        willingness_to_compromise=0.2,
    )

    updated_state = update_agent_state_from_decision(
        state=state,
        decision=decision,
    )

    assert updated_state.last_status == "rejected"
    assert updated_state.frustration == 0.2
    assert updated_state.trust_in_mediator == 0.4
    assert updated_state.concessions_made == 0


def test_update_agent_state_from_concerned_decision() -> None:
    state = AgentState()

    decision = AgentDecision(
        stakeholder_name="agriculture",
        status="concerned",
        argument="Allocation is acceptable but lower than requested.",
        requested_extra_water=3.0,
        willingness_to_compromise=0.6,
    )

    updated_state = update_agent_state_from_decision(
        state=state,
        decision=decision,
    )

    assert updated_state.last_status == "concerned"
    assert updated_state.frustration == 0.1
    assert updated_state.trust_in_mediator == 0.5
    assert updated_state.concessions_made == 1


def test_update_agent_state_from_accepted_decision() -> None:
    state = AgentState(
        frustration=0.4,
        trust_in_mediator=0.5,
        concessions_made=1,
    )

    decision = AgentDecision(
        stakeholder_name="urban",
        status="accepted",
        argument="Allocation is acceptable.",
        requested_extra_water=0.0,
        willingness_to_compromise=0.8,
    )

    updated_state = update_agent_state_from_decision(
        state=state,
        decision=decision,
    )

    assert updated_state.last_status == "accepted"
    assert updated_state.frustration == pytest.approx(0.3)
    assert updated_state.trust_in_mediator == pytest.approx(0.6)
    assert updated_state.concessions_made == 1


def test_initialize_agent_states() -> None:
    states = initialize_agent_states(
        stakeholder_names=[
            "agriculture",
            "urban",
            "ecosystem",
        ]
    )

    assert set(states) == {
        "agriculture",
        "urban",
        "ecosystem",
    }

    for state in states.values():
        assert state.frustration == 0.0
        assert state.trust_in_mediator == 0.5
        assert state.concessions_made == 0
        assert state.last_status is None
