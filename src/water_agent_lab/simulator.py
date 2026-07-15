from water_agent_lab.models import AllocationProposal, ScenarioConfig


def proportional_allocation(config: ScenarioConfig) -> AllocationProposal:
    """
    Allocate available water proportionally to requested demand.

    This is the first deterministic baseline.

    Example:
    - available water = 100
    - total requested = 130
    - ratio = 100 / 130

    Each stakeholder receives:
    requested_water * ratio
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
