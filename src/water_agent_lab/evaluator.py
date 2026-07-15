from water_agent_lab.models import (
    AllocationProposal,
    ScenarioConfig,
    SimulationResult,
)


def compute_total_requested(config: ScenarioConfig) -> float:
    """
    Compute the total amount of water requested by all stakeholders.
    """
    return sum(stakeholder.requested_water for stakeholder in config.stakeholders)


def compute_total_allocated(proposal: AllocationProposal) -> float:
    """
    Compute the total amount of water allocated in a proposal.
    """
    return sum(proposal.allocations.values())


def compute_fairness_score(
    config: ScenarioConfig,
    proposal: AllocationProposal,
) -> float:
    """
    Compute a simple satisfaction-based fairness score.

    For each stakeholder:
        satisfaction = allocated_water / requested_water

    The final score is the average satisfaction across stakeholders.

    A score close to 1.0 means stakeholders received most of what they requested.
    A score close to 0.0 means stakeholders received very little.
    """
    satisfaction_ratios = []

    for stakeholder in config.stakeholders:
        allocated = proposal.allocations.get(stakeholder.name, 0.0)
        satisfaction = allocated / stakeholder.requested_water
        satisfaction_ratios.append(min(satisfaction, 1.0))

    return sum(satisfaction_ratios) / len(satisfaction_ratios)


def compute_conflict_score(
    config: ScenarioConfig,
    proposal: AllocationProposal,
) -> float:
    """
    Compute the fraction of stakeholders below their minimum acceptable water.

    conflict_score = number_of_stakeholders_in_conflict / total_stakeholders

    A score of 0.0 means no stakeholder is below minimum.
    A score of 1.0 means every stakeholder is below minimum.
    """
    conflicts = 0

    for stakeholder in config.stakeholders:
        allocated = proposal.allocations.get(stakeholder.name, 0.0)

        if allocated < stakeholder.minimum_acceptable_water:
            conflicts += 1

    return conflicts / len(config.stakeholders)


def evaluate_proposal(
    config: ScenarioConfig,
    proposal: AllocationProposal,
) -> SimulationResult:
    """
    Evaluate a water-allocation proposal for a given drought scenario.
    """
    total_requested = compute_total_requested(config)
    total_allocated = compute_total_allocated(proposal)

    water_budget_valid = total_allocated <= config.available_water + 1e-9

    fairness_score = compute_fairness_score(config, proposal)
    conflict_score = compute_conflict_score(config, proposal)

    agreement_reached = water_budget_valid and conflict_score == 0.0

    return SimulationResult(
        scenario_name=config.scenario_name,
        country=config.country,
        region=config.region,
        drought_level=config.drought_level,
        available_water=config.available_water,
        total_requested=total_requested,
        total_allocated=total_allocated,
        water_budget_valid=water_budget_valid,
        agreement_reached=agreement_reached,
        fairness_score=fairness_score,
        conflict_score=conflict_score,
        allocations=proposal.allocations,
    )
