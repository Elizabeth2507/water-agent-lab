from water_agent_lab.agent_message_builder import decision_to_message
from water_agent_lab.agent_models import AgentDecision


def test_decision_to_response_message() -> None:
    decision = AgentDecision(
        stakeholder_name="urban",
        status="accepted",
        argument="The allocation is acceptable.",
        requested_extra_water=0.0,
        willingness_to_compromise=0.9,
    )

    message = decision_to_message(
        decision=decision,
        round_number=1,
    )

    assert message.sender == "urban"
    assert message.recipient == "mediator"
    assert message.message_type == "response"
    assert message.requested_water_change is None


def test_decision_to_counterproposal_message() -> None:
    decision = AgentDecision(
        stakeholder_name="agriculture",
        status="concerned",
        argument="Agriculture needs more water to reduce crop losses.",
        requested_extra_water=4.0,
        willingness_to_compromise=0.6,
    )

    message = decision_to_message(
        decision=decision,
        round_number=2,
    )

    assert message.sender == "agriculture"
    assert message.round_number == 2
    assert message.message_type == "counterproposal"
    assert message.requested_water_change == 4.0
