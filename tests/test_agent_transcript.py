from pathlib import Path

from water_agent_lab.agent_models import AgentDecision, AgentMessage
from water_agent_lab.agent_transcript import (
    AgentNegotiationTranscript,
    AgentRoundTranscript,
    load_agent_transcript_json,
    save_agent_transcript_json,
)
from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.simulator import proportional_allocation


def test_agent_round_transcript() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)
    result = evaluate_proposal(scenario, proposal)

    decision = AgentDecision(
        stakeholder_name="agriculture",
        status="concerned",
        argument="The allocation is above minimum but still difficult.",
        requested_extra_water=2.0,
        willingness_to_compromise=0.7,
    )

    message = AgentMessage(
        sender="agriculture",
        recipient="mediator",
        round_number=1,
        message_type="response",
        content="The allocation is difficult but not impossible.",
    )

    transcript = AgentRoundTranscript(
        round_number=1,
        strategy="proportional",
        proposal=proposal,
        decisions=[decision],
        messages=[message],
        result=result,
    )

    assert transcript.round_number == 1
    assert transcript.strategy == "proportional"
    assert len(transcript.decisions) == 1
    assert len(transcript.messages) == 1


def test_save_and_load_agent_negotiation_transcript(tmp_path: Path) -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)
    result = evaluate_proposal(scenario, proposal)

    decision = AgentDecision(
        stakeholder_name="ecosystem",
        status="rejected",
        argument="The allocation is below the ecological minimum.",
        requested_extra_water=3.0,
        willingness_to_compromise=0.2,
    )

    round_transcript = AgentRoundTranscript(
        round_number=1,
        strategy="proportional",
        proposal=proposal,
        decisions=[decision],
        messages=[],
        result=result,
    )

    transcript = AgentNegotiationTranscript(
        scenario_name=scenario.scenario_name,
        country=scenario.country,
        region=scenario.region,
        drought_level=scenario.drought_level,
        initial_strategy="proportional",
        agreement_reached=False,
        rounds_used=1,
        max_rounds=scenario.max_rounds,
        backend_name="mock",
        model_name="mock-llm",
        rounds=[round_transcript],
    )

    output_path = tmp_path / "agent_transcript.json"

    save_agent_transcript_json(
        transcript=transcript,
        output_path=output_path,
    )

    assert output_path.exists()

    loaded_transcript = load_agent_transcript_json(output_path)

    assert loaded_transcript.scenario_name == scenario.scenario_name
    assert loaded_transcript.backend_name == "mock"
    assert loaded_transcript.model_name == "mock-llm"
    assert len(loaded_transcript.rounds) == 1
    assert loaded_transcript.rounds[0].decisions[0].stakeholder_name == "ecosystem"
