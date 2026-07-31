from water_agent_lab.agent_transcript import (
    load_agent_transcript_json,
    save_agent_transcript_json,
)
from water_agent_lab.llm_negotiation import run_mock_llm_multi_round_negotiation
from water_agent_lab.agent_state_manager import initialize_agent_states
from water_agent_lab.config import load_scenario_config
from water_agent_lab.llm_agent_runner import run_mock_llm_stakeholder_responses
from water_agent_lab.strategies import proportional_allocation


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


def test_mock_llm_responses_persist_agent_state_between_rounds() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)

    agent_states = initialize_agent_states(
        stakeholder_names=[stakeholder.name for stakeholder in scenario.stakeholders]
    )

    first_round_decisions = run_mock_llm_stakeholder_responses(
        scenario=scenario,
        proposal=proposal,
        round_number=1,
        agent_states=agent_states,
    )

    agriculture_first_state = agent_states["agriculture"].model_copy()

    second_round_decisions = run_mock_llm_stakeholder_responses(
        scenario=scenario,
        proposal=proposal,
        round_number=2,
        agent_states=agent_states,
    )

    agriculture_second_state = agent_states["agriculture"]

    assert len(first_round_decisions) == len(scenario.stakeholders)
    assert len(second_round_decisions) == len(scenario.stakeholders)
    assert agriculture_second_state.frustration >= agriculture_first_state.frustration
    assert agriculture_second_state.last_status is not None


def test_mock_llm_multi_round_negotiation_records_mediator_recommendation() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    first_round = transcript.rounds[0]

    assert first_round.mediator_recommendation is not None
    assert first_round.mediator_recommendation.current_strategy == "proportional"
    assert first_round.mediator_recommendation.action in {
        "accept_proposal",
        "revise_strategy",
        "stop_no_improvement",
    }


def test_mock_llm_multi_round_negotiation_uses_mediator_revision() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    first_recommendation = transcript.rounds[0].mediator_recommendation

    assert first_recommendation is not None

    if first_recommendation.action == "revise_strategy":
        assert transcript.rounds_used > 1
        assert (
            transcript.rounds[1].strategy == first_recommendation.recommended_strategy
        )


def test_mock_llm_multi_round_negotiation_records_counterproposal_summary() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    first_round = transcript.rounds[0]

    assert first_round.counterproposal_summary is not None
    assert first_round.counterproposal_summary.total_requested_extra_water >= 0.0


def test_mediator_recommendation_records_requested_extra_water() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    first_round = transcript.rounds[0]

    assert first_round.mediator_recommendation is not None
    assert (
        first_round.mediator_recommendation.total_requested_extra_water
        == first_round.counterproposal_summary.total_requested_extra_water
    )


def test_mock_llm_negotiation_records_counterproposal_adjusted_candidate() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    first_round = transcript.rounds[0]

    assert first_round.counterproposal_summary is not None

    if first_round.counterproposal_summary.total_requested_extra_water > 0:
        assert first_round.counterproposal_adjusted_proposal is not None
        assert first_round.counterproposal_adjusted_result is not None
        assert first_round.counterproposal_adjusted_result.water_budget_valid is True


def test_counterproposal_adjusted_candidate_preserves_water_budget() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    for round_transcript in transcript.rounds:
        adjusted_result = round_transcript.counterproposal_adjusted_result

        if adjusted_result is not None:
            assert (
                adjusted_result.total_allocated
                <= adjusted_result.available_water + 1e-9
            )
            assert adjusted_result.water_budget_valid is True
