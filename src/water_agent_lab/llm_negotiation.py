from pathlib import Path

from water_agent_lab.agent_message_builder import decision_to_message
from water_agent_lab.agent_transcript import (
    AgentNegotiationTranscript,
    AgentRoundTranscript,
)
from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.llm_agent_runner import run_mock_llm_stakeholder_responses
from water_agent_lab.negotiation import choose_revision_strategy
from water_agent_lab.strategies import get_strategy
from water_agent_lab.agent_memory import AgentMemory


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

    for round_number in range(1, scenario.max_rounds + 1):
        strategy_function = get_strategy(current_strategy)
        proposal = strategy_function(scenario)

        result = evaluate_proposal(scenario, proposal)

        decisions = run_mock_llm_stakeholder_responses(
            scenario=scenario,
            proposal=proposal,
            memory=memory,
        )

        messages = [
            decision_to_message(
                decision=decision,
                round_number=round_number,
            )
            for decision in decisions
        ]

        for decision in decisions:
            memory.add(
                round_number=round_number,
                stakeholder_name=decision.stakeholder_name,
                event_type="rejection" if decision.status == "rejected" else "decision",
                content=decision.argument,
                importance=0.9 if decision.status == "rejected" else 0.6,
            )

        for message in messages:
            memory.add(
                round_number=round_number,
                stakeholder_name=message.sender,
                event_type="message",
                content=message.content,
                importance=0.5,
            )

        rejected_decisions = [
            decision for decision in decisions if decision.status == "rejected"
        ]

        round_memory_summary = memory.summarize(limit=10)

        round_transcript = AgentRoundTranscript(
            round_number=round_number,
            strategy=current_strategy,
            proposal=proposal,
            decisions=decisions,
            messages=messages,
            result=result,
            memory_summary=round_memory_summary,
        )
        rounds.append(round_transcript)

        if not rejected_decisions:
            agreement_reached = True
            break

        revised_strategy = choose_revision_strategy(current_strategy)

        if revised_strategy == current_strategy:
            break

        current_strategy = revised_strategy

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
