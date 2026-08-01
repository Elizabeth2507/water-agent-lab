import pytest

from water_agent_lab.llm_negotiation_runner import (
    run_llm_multi_round_negotiation,
)


def test_run_llm_multi_round_negotiation_with_mock_backend() -> None:
    transcript = run_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        backend_name="mock",
    )

    assert transcript.backend_name == "mock"
    assert transcript.model_name == "mock"
    assert transcript.rounds_used >= 1
    assert transcript.rounds

    first_round = transcript.rounds[0]

    assert first_round.decisions
    assert first_round.messages
    assert first_round.mediator_recommendation is not None
    assert first_round.counterproposal_summary is not None


def test_run_llm_multi_round_negotiation_with_fixed_mock_backend() -> None:
    transcript = run_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        backend_name="fixed-mock",
    )

    assert transcript.backend_name == "fixed-mock"
    assert transcript.model_name == "fixed-mock"
    assert transcript.rounds_used >= 1
    assert transcript.rounds[0].decisions


def test_run_llm_multi_round_negotiation_rejects_unknown_backend() -> None:
    with pytest.raises(ValueError, match="Unknown LLM backend"):
        run_llm_multi_round_negotiation(
            config_path="configs/drought_mvp.yaml",
            initial_strategy="proportional",
            backend_name="unknown",
        )


def test_run_llm_multi_round_negotiation_stores_validation_results() -> None:
    transcript = run_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        backend_name="mock",
    )

    first_round = transcript.rounds[0]

    assert first_round.decision_validation_results
    assert {
        validation_result.stakeholder_name
        for validation_result in first_round.decision_validation_results
    } == {
        "agriculture",
        "urban",
        "industry",
        "ecosystem",
    }

    repaired_results = [
        validation_result
        for validation_result in first_round.decision_validation_results
        if validation_result.was_repaired
    ]

    assert repaired_results == []
