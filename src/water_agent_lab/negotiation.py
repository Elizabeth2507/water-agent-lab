from pydantic import BaseModel

from water_agent_lab.agents import StakeholderResponse, evaluate_stakeholder_responses
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.models import SimulationResult
from water_agent_lab.strategies import get_strategy


class NegotiationResult(BaseModel):
    """
    Result of one simple negotiation round.

    If stakeholders reject the initial allocation, the system revises
    the allocation using the minimum-first strategy.
    """

    scenario_name: str
    initial_strategy: str
    revision_triggered: bool
    rejected_stakeholders: list[str]
    initial_result: SimulationResult
    initial_responses: list[StakeholderResponse]
    revised_strategy: str | None
    revised_result: SimulationResult | None
    revised_responses: list[StakeholderResponse] | None


def run_simple_negotiation(
    config_path: str,
    initial_strategy: str = "proportional",
) -> NegotiationResult:
    """
    Run one simple negotiation round.

    The process is:
    1. Run the initial allocation strategy.
    2. Collect stakeholder responses.
    3. If any stakeholder rejects, revise with minimum-first allocation.
    """
    from water_agent_lab.config import load_scenario_config

    scenario = load_scenario_config(config_path)

    initial_strategy_function = get_strategy(initial_strategy)
    initial_proposal = initial_strategy_function(scenario)

    initial_result = evaluate_proposal(scenario, initial_proposal)
    initial_responses = evaluate_stakeholder_responses(
        stakeholders=scenario.stakeholders,
        proposal=initial_proposal,
    )

    rejected_stakeholders = [
        response.stakeholder_name
        for response in initial_responses
        if response.status == "rejected"
    ]

    if not rejected_stakeholders:
        return NegotiationResult(
            scenario_name=scenario.scenario_name,
            initial_strategy=initial_strategy,
            revision_triggered=False,
            rejected_stakeholders=[],
            initial_result=initial_result,
            initial_responses=initial_responses,
            revised_strategy=None,
            revised_result=None,
            revised_responses=None,
        )

    revised_strategy = "minimum-first"
    revised_strategy_function = get_strategy(revised_strategy)
    revised_proposal = revised_strategy_function(scenario)

    revised_result = evaluate_proposal(scenario, revised_proposal)
    revised_responses = evaluate_stakeholder_responses(
        stakeholders=scenario.stakeholders,
        proposal=revised_proposal,
    )

    return NegotiationResult(
        scenario_name=scenario.scenario_name,
        initial_strategy=initial_strategy,
        revision_triggered=True,
        rejected_stakeholders=rejected_stakeholders,
        initial_result=initial_result,
        initial_responses=initial_responses,
        revised_strategy=revised_strategy,
        revised_result=revised_result,
        revised_responses=revised_responses,
    )
