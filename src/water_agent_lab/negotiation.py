import json
from pathlib import Path
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


class NegotiationRound(BaseModel):
    """
    One round of negotiation.
    """

    round_number: int
    strategy: str
    result: SimulationResult
    responses: list[StakeholderResponse]
    rejected_stakeholders: list[str]


class MultiRoundNegotiationResult(BaseModel):
    """
    Result of a multi-round negotiation process.
    """

    scenario_name: str
    initial_strategy: str
    agreement_reached: bool
    rounds_used: int
    max_rounds: int
    rounds: list[NegotiationRound]


def choose_revision_strategy(current_strategy: str) -> str:
    """
    Choose a revised strategy after stakeholder rejection.
    """
    if current_strategy == "proportional":
        return "minimum-first"

    if current_strategy == "priority":
        return "minimum-priority"

    return current_strategy


def run_multi_round_negotiation(
    config_path: str,
    initial_strategy: str = "proportional",
) -> MultiRoundNegotiationResult:
    """
    Run a simple multi-round negotiation process.

    The process stops when agreement is reached or max_rounds is reached.
    """
    from water_agent_lab.config import load_scenario_config

    scenario = load_scenario_config(config_path)
    current_strategy = initial_strategy
    rounds = []

    for round_number in range(1, scenario.max_rounds + 1):
        strategy_function = get_strategy(current_strategy)
        proposal = strategy_function(scenario)

        result = evaluate_proposal(scenario, proposal)
        responses = evaluate_stakeholder_responses(
            stakeholders=scenario.stakeholders,
            proposal=proposal,
        )

        rejected_stakeholders = [
            response.stakeholder_name
            for response in responses
            if response.status == "rejected"
        ]

        negotiation_round = NegotiationRound(
            round_number=round_number,
            strategy=current_strategy,
            result=result,
            responses=responses,
            rejected_stakeholders=rejected_stakeholders,
        )
        rounds.append(negotiation_round)

        if not rejected_stakeholders:
            break

        revised_strategy = choose_revision_strategy(current_strategy)

        if revised_strategy == current_strategy:
            break

        current_strategy = revised_strategy

    final_round = rounds[-1]

    return MultiRoundNegotiationResult(
        scenario_name=scenario.scenario_name,
        initial_strategy=initial_strategy,
        agreement_reached=final_round.result.agreement_reached,
        rounds_used=len(rounds),
        max_rounds=scenario.max_rounds,
        rounds=rounds,
    )


def save_negotiation_history_json(
    result: MultiRoundNegotiationResult,
    output_path: str | Path,
    run_metadata: dict[str, str] | None = None,
) -> None:
    """
    Save multi-round negotiation history to a JSON file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    output_data = result.model_dump()

    if run_metadata is not None:
        output_data["run_metadata"] = run_metadata

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            output_data,
            file,
            indent=2,
        )
