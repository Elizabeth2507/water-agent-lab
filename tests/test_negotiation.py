from water_agent_lab.negotiation import run_simple_negotiation
from water_agent_lab.negotiation import (
    choose_revision_strategy,
    run_multi_round_negotiation,
)


def test_simple_negotiation_triggers_revision_for_proportional_strategy() -> None:
    result = run_simple_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    assert result.scenario_name == "moderate_drought_mvp"
    assert result.initial_strategy == "proportional"
    assert result.revision_triggered is True
    assert "urban" in result.rejected_stakeholders
    assert "ecosystem" in result.rejected_stakeholders
    assert result.revised_strategy == "minimum-first"
    assert result.revised_result is not None
    assert result.revised_result.conflict_score == 0.0
    assert result.revised_result.agreement_reached is True


def test_simple_negotiation_does_not_revise_when_no_rejections() -> None:
    result = run_simple_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="minimum-first",
    )

    assert result.revision_triggered is False
    assert result.rejected_stakeholders == []
    assert result.revised_strategy is None
    assert result.revised_result is None
    assert result.revised_responses is None


def test_choose_revision_strategy() -> None:
    assert choose_revision_strategy("proportional") == "minimum-first"
    assert choose_revision_strategy("priority") == "minimum-priority"
    assert choose_revision_strategy("minimum-first") == "minimum-first"
    assert choose_revision_strategy("minimum-priority") == "minimum-priority"


def test_multi_round_negotiation_reaches_agreement_for_moderate_drought() -> None:
    result = run_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    assert result.scenario_name == "moderate_drought_mvp"
    assert result.initial_strategy == "proportional"
    assert result.rounds_used == 2
    assert result.agreement_reached is True
    assert result.rounds[0].strategy == "proportional"
    assert result.rounds[1].strategy == "minimum-first"


def test_multi_round_negotiation_does_not_reach_agreement_for_extreme_drought() -> None:
    result = run_multi_round_negotiation(
        config_path="configs/extreme_drought.yaml",
        initial_strategy="proportional",
    )

    assert result.scenario_name == "extreme_drought"
    assert result.agreement_reached is False
    assert result.rounds_used >= 1
