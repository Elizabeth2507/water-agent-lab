from water_agent_lab.models import AllocationProposal, ScenarioConfig


def proportional_allocation(config: ScenarioConfig) -> AllocationProposal:
    """
    Allocate available water proportionally to requested demand.

    This baseline gives every stakeholder the same percentage
    of their requested water.
    """
    total_requested = sum(
        stakeholder.requested_water for stakeholder in config.stakeholders
    )

    ratio = config.available_water / total_requested

    allocations = {
        stakeholder.name: stakeholder.requested_water * ratio
        for stakeholder in config.stakeholders
    }

    return AllocationProposal(allocations=allocations)


def priority_weighted_allocation(config: ScenarioConfig) -> AllocationProposal:
    """
    Allocate available water using requested demand and stakeholder priority.

    Each stakeholder receives water according to:

        requested_water * priority

    Higher-priority stakeholders receive a larger share of the scarce water.
    """
    total_weighted_demand = sum(
        stakeholder.requested_water * stakeholder.priority
        for stakeholder in config.stakeholders
    )

    allocations = {
        stakeholder.name: (
            config.available_water
            * (stakeholder.requested_water * stakeholder.priority)
            / total_weighted_demand
        )
        for stakeholder in config.stakeholders
    }

    return AllocationProposal(allocations=allocations)
