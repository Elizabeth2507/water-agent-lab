from water_agent_lab.agent_transcript import (
    load_agent_transcript_json,
    save_agent_transcript_json,
)
from water_agent_lab.llm_negotiation import run_mock_llm_multi_round_negotiation


def test_run_mock_llm_multi_round_negotiation() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    assert transcript.scenario_name == "moderate_drought_mvp"
    assert transcript.initial_strategy == "proportional"
    assert transcript.backend_name == "mock"
    assert transcript.model_name == "mock-llm"
    assert 1 <= transcript.rounds_used <= transcript.max_rounds
    assert len(transcript.rounds) == transcript.rounds_used

    first_round = transcript.rounds[0]

    assert first_round.round_number == 1
    assert first_round.strategy == "proportional"
    assert len(first_round.decisions) == 4
    assert len(first_round.messages) == 4


def test_mock_llm_multi_round_negotiation_revises_strategy() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    strategies = [round_transcript.strategy for round_transcript in transcript.rounds]

    assert strategies[0] == "proportional"

    if transcript.rounds_used > 1:
        assert strategies[1] == "minimum-first"


def test_mock_llm_multi_round_negotiation_with_minimum_first() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="minimum-first",
    )

    assert transcript.initial_strategy == "minimum-first"
    assert transcript.rounds[0].strategy == "minimum-first"
    assert transcript.rounds_used >= 1


def test_mock_llm_multi_round_negotiation_transcript_can_be_saved_and_loaded(
    tmp_path,
) -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    output_path = tmp_path / "mock_llm_multi_round.json"

    save_agent_transcript_json(
        transcript=transcript,
        output_path=output_path,
    )

    loaded = load_agent_transcript_json(output_path)

    assert loaded.scenario_name == transcript.scenario_name
    assert loaded.rounds_used == transcript.rounds_used
    assert len(loaded.rounds) == len(transcript.rounds)
