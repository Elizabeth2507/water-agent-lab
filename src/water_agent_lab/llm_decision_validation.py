from pydantic import BaseModel, Field

from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.models import AllocationProposal, StakeholderConfig


ACCEPTANCE_RATIO_THRESHOLD = 0.9
FLOAT_TOLERANCE = 1e-9


class AgentDecisionValidationResult(BaseModel):
    """
    Result of validating an LLM-generated AgentDecision against scenario
    constraints.
    """

    decision: AgentDecision
    was_repaired: bool = False
    repairs: list[str] = Field(default_factory=list)


def validate_or_repair_agent_decision(
    decision: AgentDecision,
    stakeholder: StakeholderConfig,
    proposal: AllocationProposal,
) -> AgentDecisionValidationResult:
    """
    Validate or repair an LLM-generated stakeholder decision.

    This function prevents schema-valid but logically inconsistent LLM outputs
    from being used directly by the mediator.

    Repair rules:
    1. The decision stakeholder name must match the evaluated stakeholder.
    2. If allocated water is below the minimum acceptable water, the decision
       must be rejected.
    3. If allocated water is above the minimum but far below the requested
       amount, an accepted decision is repaired to concerned.
    4. Accepted decisions must not request extra water.
    5. Concerned/rejected decisions should request a positive amount when there
       is a real shortfall.
    """
    allocated_water = proposal.allocations.get(stakeholder.name, 0.0)

    repaired_data = decision.model_dump()
    repairs: list[str] = []

    if decision.stakeholder_name != stakeholder.name:
        repaired_data["stakeholder_name"] = stakeholder.name
        repairs.append(
            "Repaired stakeholder_name to match the evaluated stakeholder."
        )

    if allocated_water + FLOAT_TOLERANCE < stakeholder.minimum_acceptable_water:
        minimum_shortfall = stakeholder.minimum_acceptable_water - allocated_water

        if decision.status != "rejected":
            repaired_data["status"] = "rejected"
            repairs.append(
                "Repaired status to rejected because allocated water is below "
                "the minimum acceptable level."
            )

        if decision.requested_extra_water + FLOAT_TOLERANCE < minimum_shortfall:
            repaired_data["requested_extra_water"] = minimum_shortfall
            repairs.append(
                "Repaired requested_extra_water to cover the minimum shortfall."
            )

    elif (
        decision.status == "accepted"
        and allocated_water + FLOAT_TOLERANCE
        < stakeholder.requested_water * ACCEPTANCE_RATIO_THRESHOLD
    ):
        requested_shortfall = stakeholder.requested_water - allocated_water

        repaired_data["status"] = "concerned"
        repairs.append(
            "Repaired status to concerned because allocated water is above the "
            "minimum but not close to the requested amount."
        )

        if decision.requested_extra_water + FLOAT_TOLERANCE < requested_shortfall:
            repaired_data["requested_extra_water"] = requested_shortfall
            repairs.append(
                "Repaired requested_extra_water to reflect the requested "
                "water shortfall."
            )

    if repaired_data["status"] == "accepted" and repaired_data[
        "requested_extra_water"
    ] != 0.0:
        repaired_data["requested_extra_water"] = 0.0
        repairs.append(
            "Repaired requested_extra_water to 0.0 because accepted decisions "
            "should not request extra water."
        )

    if repaired_data["requested_extra_water"] < 0.0:
        repaired_data["requested_extra_water"] = 0.0
        repairs.append("Repaired negative requested_extra_water to 0.0.")

    repaired_decision = AgentDecision.model_validate(repaired_data)

    return AgentDecisionValidationResult(
        decision=repaired_decision,
        was_repaired=bool(repairs),
        repairs=repairs,
    )