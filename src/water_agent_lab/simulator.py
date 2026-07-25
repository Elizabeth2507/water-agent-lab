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


def minimum_first_allocation(config: ScenarioConfig) -> AllocationProposal:
    """
    Allocate water by protecting minimum acceptable needs first.

    Algorithm:
    1. If available water is less than total minimum demand,
       allocate proportionally to minimum acceptable water.
    2. Otherwise, give each stakeholder its minimum acceptable water.
    3. Distribute remaining water proportionally to remaining unmet demand.
    """
    total_minimum_required = sum(
        stakeholder.minimum_acceptable_water for stakeholder in config.stakeholders
    )

    if config.available_water <= total_minimum_required:
        allocations = {
            stakeholder.name: (
                config.available_water
                * stakeholder.minimum_acceptable_water
                / total_minimum_required
            )
            for stakeholder in config.stakeholders
        }

        return AllocationProposal(allocations=allocations)

    allocations = {
        stakeholder.name: stakeholder.minimum_acceptable_water
        for stakeholder in config.stakeholders
    }

    remaining_water = config.available_water - total_minimum_required

    total_unmet_demand = sum(
        stakeholder.requested_water - stakeholder.minimum_acceptable_water
        for stakeholder in config.stakeholders
    )

    for stakeholder in config.stakeholders:
        unmet_demand = (
            stakeholder.requested_water - stakeholder.minimum_acceptable_water
        )

        allocations[stakeholder.name] += (
            remaining_water * unmet_demand / total_unmet_demand
        )

    return AllocationProposal(allocations=allocations)
