from water_agent_lab.negotiation import run_simple_negotiation


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
