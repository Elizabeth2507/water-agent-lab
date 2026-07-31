from water_agent_lab.agent_models import AgentDecision, AgentState


def update_agent_state_from_decision(
    state: AgentState,
    decision: AgentDecision,
) -> AgentState:
    """
    Return an updated copy of the agent state after one decision.

    This centralizes state-update logic so agents and negotiation loops use the
    same behaviour.
    """
    updated_state = state.model_copy()
    updated_state.last_status = decision.status

    if decision.status == "rejected":
        updated_state.frustration = min(
            1.0,
            updated_state.frustration + 0.2,
        )
        updated_state.trust_in_mediator = max(
            0.0,
            updated_state.trust_in_mediator - 0.1,
        )

    elif decision.status == "concerned":
        updated_state.frustration = min(
            1.0,
            updated_state.frustration + 0.1,
        )
        updated_state.concessions_made += 1

    elif decision.status == "accepted":
        updated_state.frustration = max(
            0.0,
            updated_state.frustration - 0.1,
        )
        updated_state.trust_in_mediator = min(
            1.0,
            updated_state.trust_in_mediator + 0.1,
        )

    return updated_state


def initialize_agent_states(
    stakeholder_names: list[str],
) -> dict[str, AgentState]:
    """
    Create one initial AgentState per stakeholder.
    """
    return {stakeholder_name: AgentState() for stakeholder_name in stakeholder_names}
