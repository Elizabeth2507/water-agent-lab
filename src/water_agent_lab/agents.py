from pydantic import BaseModel

from water_agent_lab.models import AllocationProposal, StakeholderConfig


class StakeholderResponse(BaseModel):
    """
    Rule-based response from one stakeholder to an allocation proposal.
    """

    stakeholder_name: str
    requested_water: float
    minimum_acceptable_water: float
    allocated_water: float
    satisfaction_ratio: float
    status: str
    message: str


class RuleBasedStakeholderAgent:
    """
    Simple rule-based stakeholder agent.

    The agent evaluates whether a proposed allocation is acceptable
    based on its requested water and minimum acceptable water.
    """

    def __init__(self, stakeholder: StakeholderConfig) -> None:
        self.stakeholder = stakeholder

    def evaluate_allocation(
        self,
        proposal: AllocationProposal,
    ) -> StakeholderResponse:
        allocated_water = proposal.allocations.get(self.stakeholder.name, 0.0)
        satisfaction_ratio = allocated_water / self.stakeholder.requested_water

        if allocated_water < self.stakeholder.minimum_acceptable_water:
            status = "rejected"
            message = (
                f"{self.stakeholder.name} rejects the proposal because "
                f"allocated water is below the minimum acceptable level."
            )
        elif satisfaction_ratio < 0.9:
            status = "concerned"
            message = (
                f"{self.stakeholder.name} accepts the proposal with concern because "
                f"allocated water is above the minimum but below requested demand."
            )
        else:
            status = "accepted"
            message = (
                f"{self.stakeholder.name} accepts the proposal because "
                f"allocated water is close to requested demand."
            )

        return StakeholderResponse(
            stakeholder_name=self.stakeholder.name,
            requested_water=self.stakeholder.requested_water,
            minimum_acceptable_water=self.stakeholder.minimum_acceptable_water,
            allocated_water=allocated_water,
            satisfaction_ratio=satisfaction_ratio,
            status=status,
            message=message,
        )


def evaluate_stakeholder_responses(
    stakeholders: list[StakeholderConfig],
    proposal: AllocationProposal,
) -> list[StakeholderResponse]:
    """
    Evaluate one allocation proposal with all stakeholder agents.
    """
    responses = []

    for stakeholder in stakeholders:
        agent = RuleBasedStakeholderAgent(stakeholder)
        response = agent.evaluate_allocation(proposal)
        responses.append(response)

    return responses
