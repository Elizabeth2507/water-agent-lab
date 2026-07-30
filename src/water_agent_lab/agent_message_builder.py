from water_agent_lab.agent_models import AgentDecision, AgentMessage


def decision_to_message(
    decision: AgentDecision,
    round_number: int,
    recipient: str = "mediator",
) -> AgentMessage:
    """
    Convert an AgentDecision into a structured AgentMessage.
    """
    message_type = (
        "counterproposal" if decision.requested_extra_water > 0 else "response"
    )

    return AgentMessage(
        sender=decision.stakeholder_name,
        recipient=recipient,
        round_number=round_number,
        message_type=message_type,
        content=decision.argument,
        requested_water_change=(
            decision.requested_extra_water
            if decision.requested_extra_water > 0
            else None
        ),
    )
