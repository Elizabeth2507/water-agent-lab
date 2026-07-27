from collections.abc import Callable

from water_agent_lab.models import AllocationProposal, ScenarioConfig
from water_agent_lab.simulator import (
    minimum_first_allocation,
    minimum_priority_allocation,
    priority_weighted_allocation,
    proportional_allocation,
)

AllocationStrategy = Callable[[ScenarioConfig], AllocationProposal]

ALLOCATION_STRATEGIES: dict[str, AllocationStrategy] = {
    "proportional": proportional_allocation,
    "priority": priority_weighted_allocation,
    "minimum-first": minimum_first_allocation,
    "minimum-priority": minimum_priority_allocation,
}


def get_strategy_names() -> list[str]:
    """
    Return available allocation strategy names.
    """
    return list(ALLOCATION_STRATEGIES.keys())


def get_strategy(strategy_name: str) -> AllocationStrategy:
    """
    Return an allocation strategy by name.
    """
    try:
        return ALLOCATION_STRATEGIES[strategy_name]
    except KeyError as error:
        available = ", ".join(get_strategy_names())
        raise ValueError(
            f"Unknown strategy '{strategy_name}'. Available strategies: {available}."
        ) from error
