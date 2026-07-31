from pathlib import Path

from water_agent_lab.agent_transcript import (
    AgentNegotiationTranscript,
    AgentRoundTranscript,
)
from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.llm_agent_runner import run_mock_llm_stakeholder_responses
from water_agent_lab.strategies import get_strategy
from water_agent_lab.agent_memory import AgentMemory
from water_agent_lab.agent_state_manager import initialize_agent_states
from water_agent_lab.mediator import RuleBasedMediatorAgent
from water_agent_lab.counterproposals import (
    build_counterproposal_adjusted_allocation,
    summarize_counterproposals,
)
from water_agent_lab.agent_message_builder import build_agent_messages_from_decisions


def run_mock_llm_multi_round_negotiation(
    config_path: str | Path,
    initial_strategy: str = "proportional",
) -> AgentNegotiationTranscript:
    """
    Run a deterministic mock LLM multi-round negotiation.

    This uses the same structure as a future LLM-based negotiation loop,
    but relies on MockLLMBackend-generated decisions to keep tests reproducible.
    """
    scenario = load_scenario_config(config_path)

    rounds: list[AgentRoundTranscript] = []
    current_strategy = initial_strategy
    agreement_reached = False

    memory = AgentMemory()
    mediator = RuleBasedMediatorAgent()

    agent_states = initialize_agent_states(
        stakeholder_names=[stakeholder.name for stakeholder in scenario.stakeholders]
    )

    for round_number in range(1, scenario.max_rounds + 1):
        strategy_function = get_strategy(current_strategy)
        proposal = strategy_function(scenario)

        result = evaluate_proposal(scenario, proposal)

        decisions = run_mock_llm_stakeholder_responses(
            scenario=scenario,
            proposal=proposal,
            round_number=round_number,
            memory=memory,
            agent_states=agent_states,
        )

        messages = build_agent_messages_from_decisions(
            decisions=decisions,
            round_number=round_number,
        )

        memory_summary = memory.summarize(
            stakeholder_name=None,
            limit=5,
        )

        counterproposal_summary = summarize_counterproposals(decisions)

        counterproposal_adjusted_proposal = None
        counterproposal_adjusted_result = None

        if counterproposal_summary.total_requested_extra_water > 0:
            counterproposal_adjusted_proposal = (
                build_counterproposal_adjusted_allocation(
                    scenario=scenario,
                    proposal=proposal,
                    counterproposal_summary=counterproposal_summary,
                )
            )

            counterproposal_adjusted_result = evaluate_proposal(
                scenario,
                counterproposal_adjusted_proposal,
            )

        mediator_recommendation = mediator.recommend(
            current_strategy=current_strategy,
            decisions=decisions,
            result=result,
            counterproposal_summary=counterproposal_summary,
        )

        rounds.append(
            AgentRoundTranscript(
                round_number=round_number,
                strategy=current_strategy,
                proposal=proposal,
                decisions=decisions,
                messages=messages,
                result=result,
                memory_summary=memory_summary,
                agent_states={
                    stakeholder_name: state.model_copy()
                    for stakeholder_name, state in agent_states.items()
                },
                mediator_recommendation=mediator_recommendation,
                counterproposal_summary=counterproposal_summary,
                counterproposal_adjusted_proposal=counterproposal_adjusted_proposal,
                counterproposal_adjusted_result=counterproposal_adjusted_result,
            )
        )

        if mediator_recommendation.action == "accept_proposal":
            agreement_reached = True
            break

        if mediator_recommendation.action == "stop_no_improvement":
            break

        current_strategy = mediator_recommendation.recommended_strategy

    return AgentNegotiationTranscript(
        scenario_name=scenario.scenario_name,
        country=scenario.country,
        region=scenario.region,
        drought_level=scenario.drought_level,
        initial_strategy=initial_strategy,
        agreement_reached=agreement_reached,
        rounds_used=len(rounds),
        max_rounds=scenario.max_rounds,
        backend_name="mock",
        model_name="mock-llm",
        rounds=rounds,
    )
