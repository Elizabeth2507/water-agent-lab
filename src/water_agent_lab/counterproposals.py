from pydantic import BaseModel, Field

from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.models import AllocationProposal, ScenarioConfig


class CounterproposalSummary(BaseModel):
    """
    Summary of stakeholder counterproposals for one negotiation round.
    """

    requested_changes: dict[str, float] = Field(default_factory=dict)
    total_requested_extra_water: float = 0.0
    stakeholders_requesting_extra_water: list[str] = Field(default_factory=list)


def summarize_counterproposals(
    decisions: list[AgentDecision],
) -> CounterproposalSummary:
    """
    Summarize requested extra water from stakeholder decisions.
    """
    requested_changes = {
        decision.stakeholder_name: decision.requested_extra_water
        for decision in decisions
        if decision.requested_extra_water > 0
    }

    return CounterproposalSummary(
        requested_changes=requested_changes,
        total_requested_extra_water=sum(requested_changes.values()),
        stakeholders_requesting_extra_water=list(requested_changes.keys()),
    )


def build_counterproposal_adjusted_allocation(
    scenario: ScenarioConfig,
    proposal: AllocationProposal,
    counterproposal_summary: CounterproposalSummary,
) -> AllocationProposal:
    """
    Build a revised allocation that tries to satisfy requested extra water.

    Deterministic rule:
    - Add requested extra water to stakeholders who asked for more.
    - Take water proportionally from stakeholders who did not ask for more
      and are above their minimum acceptable level.
    - Never reduce a stakeholder below its minimum acceptable water.
    - Never exceed the available water budget.

    If there is not enough transferable water, only part of the requested
    extra water is granted.
    """
    allocations = dict(proposal.allocations)

    if counterproposal_summary.total_requested_extra_water <= 0:
        return AllocationProposal(allocations=allocations)

    stakeholder_by_name = {
        stakeholder.name: stakeholder for stakeholder in scenario.stakeholders
    }

    requesters = set(counterproposal_summary.requested_changes)

    donors = []
    total_transferable_water = 0.0

    for stakeholder in scenario.stakeholders:
        if stakeholder.name in requesters:
            continue

        current_allocation = allocations.get(stakeholder.name, 0.0)
        transferable = max(
            current_allocation - stakeholder.minimum_acceptable_water,
            0.0,
        )

        if transferable > 0:
            donors.append((stakeholder.name, transferable))
            total_transferable_water += transferable

    granted_extra_water = min(
        counterproposal_summary.total_requested_extra_water,
        total_transferable_water,
    )

    if granted_extra_water <= 0:
        return AllocationProposal(allocations=allocations)

    # Distribute granted extra water among requesters proportionally to their asks.
    for (
        stakeholder_name,
        requested_extra,
    ) in counterproposal_summary.requested_changes.items():
        share = requested_extra / counterproposal_summary.total_requested_extra_water
        extra_granted = granted_extra_water * share

        stakeholder = stakeholder_by_name[stakeholder_name]
        current_allocation = allocations.get(stakeholder_name, 0.0)

        allocations[stakeholder_name] = min(
            current_allocation + extra_granted,
            stakeholder.requested_water,
        )

    # Remove water from donors proportionally to transferable amount.
    for stakeholder_name, transferable in donors:
        donor_share = transferable / total_transferable_water
        reduction = granted_extra_water * donor_share

        donor = stakeholder_by_name[stakeholder_name]
        current_allocation = allocations.get(stakeholder_name, 0.0)

        allocations[stakeholder_name] = max(
            current_allocation - reduction,
            donor.minimum_acceptable_water,
        )

    # Floating-point safety: if total is slightly above budget, scale tiny excess.
    total_allocated = sum(allocations.values())

    if total_allocated > scenario.available_water:
        excess = total_allocated - scenario.available_water

        adjustable_stakeholders = [
            stakeholder
            for stakeholder in scenario.stakeholders
            if allocations[stakeholder.name] > stakeholder.minimum_acceptable_water
        ]

        total_adjustable = sum(
            allocations[stakeholder.name] - stakeholder.minimum_acceptable_water
            for stakeholder in adjustable_stakeholders
        )

        if total_adjustable > 0:
            for stakeholder in adjustable_stakeholders:
                adjustable = (
                    allocations[stakeholder.name] - stakeholder.minimum_acceptable_water
                )
                reduction = excess * (adjustable / total_adjustable)
                allocations[stakeholder.name] = max(
                    allocations[stakeholder.name] - reduction,
                    stakeholder.minimum_acceptable_water,
                )

    return AllocationProposal(allocations=allocations)
