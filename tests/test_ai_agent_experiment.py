import pandas as pd
import pytest

from water_agent_lab.ai_agent_experiment import run_ai_agent_experiment


def test_run_ai_agent_experiment_creates_expected_artifacts(tmp_path) -> None:
    output_dir = tmp_path / "ai_agent_experiment"

    run_ai_agent_experiment(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=42,
        output_dir=output_dir,
    )

    expected_files = [
        "monte_carlo_mock.csv",
        "monte_carlo_report.md",
        "monte_carlo_conflict_histogram.png",
        "monte_carlo_rounds_histogram.png",
        "negotiation_mode_comparison.csv",
        "negotiation_mode_comparison_report.md",
        "mode_comparison_conflict.png",
        "mode_comparison_agreement.png",
        "mode_comparison_rounds.png",
        "ai_agent_experiment_summary.md",
    ]

    for filename in expected_files:
        assert (output_dir / filename).exists()

    monte_carlo_dataframe = pd.read_csv(output_dir / "monte_carlo_mock.csv")
    mode_comparison_dataframe = pd.read_csv(
        output_dir / "negotiation_mode_comparison.csv"
    )

    assert len(monte_carlo_dataframe) == 3
    assert len(mode_comparison_dataframe) == 6

    assert set(mode_comparison_dataframe["mode"]) == {
        "mock_llm",
        "rule_based",
    }


def test_run_ai_agent_experiment_rejects_non_positive_runs(tmp_path) -> None:
    with pytest.raises(ValueError, match="runs must be greater than 0"):
        run_ai_agent_experiment(
            config_path="configs/drought_mvp.yaml",
            initial_strategy="proportional",
            runs=0,
            seed=42,
            output_dir=tmp_path / "experiment",
        )
