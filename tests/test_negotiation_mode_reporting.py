import pandas as pd
import pytest

from water_agent_lab.negotiation_mode_reporting import (
    generate_negotiation_mode_comparison_report,
    summarize_negotiation_modes,
)


def test_summarize_negotiation_modes() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "scenario_name": "moderate",
                "mode": "rule_based",
                "initial_strategy": "proportional",
                "final_strategy": "minimum-first",
                "agreement_reached": False,
                "rounds_used": 2,
                "final_conflict_score": 0.5,
            },
            {
                "scenario_name": "severe",
                "mode": "rule_based",
                "initial_strategy": "proportional",
                "final_strategy": "minimum-first",
                "agreement_reached": True,
                "rounds_used": 1,
                "final_conflict_score": 0.0,
            },
            {
                "scenario_name": "moderate",
                "mode": "mock_llm",
                "initial_strategy": "proportional",
                "final_strategy": "minimum-first",
                "agreement_reached": True,
                "rounds_used": 2,
                "final_conflict_score": 0.25,
            },
        ]
    )

    summary = summarize_negotiation_modes(dataframe)

    rule_based_row = summary[summary["mode"] == "rule_based"].iloc[0]
    mock_llm_row = summary[summary["mode"] == "mock_llm"].iloc[0]

    assert rule_based_row["scenarios"] == 2
    assert rule_based_row["agreement_rate"] == pytest.approx(0.5)
    assert rule_based_row["average_final_conflict"] == pytest.approx(0.25)
    assert rule_based_row["average_rounds_used"] == pytest.approx(1.5)

    assert mock_llm_row["scenarios"] == 1
    assert mock_llm_row["agreement_rate"] == pytest.approx(1.0)
    assert mock_llm_row["average_final_conflict"] == pytest.approx(0.25)
    assert mock_llm_row["average_rounds_used"] == pytest.approx(2.0)


def test_generate_negotiation_mode_comparison_report(tmp_path) -> None:
    input_path = tmp_path / "comparison.csv"
    output_path = tmp_path / "report.md"
    conflict_plot_path = tmp_path / "conflict.png"
    agreement_plot_path = tmp_path / "agreement.png"
    rounds_plot_path = tmp_path / "rounds.png"

    dataframe = pd.DataFrame(
        [
            {
                "scenario_name": "moderate",
                "mode": "rule_based",
                "initial_strategy": "proportional",
                "final_strategy": "minimum-first",
                "rounds_used": 2,
                "final_conflict_score": 0.5,
            },
            {
                "scenario_name": "moderate",
                "mode": "mock_llm",
                "initial_strategy": "proportional",
                "final_strategy": "minimum-first",
                "agreement_reached": True,
                "rounds_used": 2,
                "final_conflict_score": 0.25,
            },
        ]
    )
    dataframe.to_csv(input_path, index=False)

    generate_negotiation_mode_comparison_report(
        input_path=input_path,
        output_path=output_path,
        conflict_plot_path=conflict_plot_path,
        agreement_plot_path=agreement_plot_path,
        rounds_plot_path=rounds_plot_path,
    )

    assert output_path.exists()
    assert conflict_plot_path.exists()
    assert agreement_plot_path.exists()
    assert rounds_plot_path.exists()

    report_text = output_path.read_text(encoding="utf-8")

    assert "# Negotiation Mode Comparison Report" in report_text
    assert "Summary by mode" in report_text
    assert "Detailed results" in report_text
    assert "mock_llm" in report_text
    assert "rule_based" in report_text


def test_generate_negotiation_mode_comparison_report_rejects_missing_columns(
    tmp_path,
) -> None:
    input_path = tmp_path / "comparison.csv"
    output_path = tmp_path / "report.md"

    dataframe = pd.DataFrame(
        [
            {
                "scenario_name": "moderate",
                "mode": "rule_based",
            }
        ]
    )
    dataframe.to_csv(input_path, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        generate_negotiation_mode_comparison_report(
            input_path=input_path,
            output_path=output_path,
        )
