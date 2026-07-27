from pathlib import Path

import pytest

from water_agent_lab.exporter import save_results_csv
from water_agent_lab.reporting import (
    find_best_strategy_by_conflict,
    generate_experiment_report,
    load_experiment_results,
    summarize_by_drought_level,
    summarize_by_strategy,
)


def make_sample_rows() -> list[dict[str, object]]:
    return [
        {
            "scenario_name": "mild_drought",
            "country": "France",
            "region": "Occitanie",
            "drought_level": "mild",
            "available_water": 120.0,
            "strategy": "proportional",
            "fairness_score": 0.9,
            "conflict_score": 0.0,
            "minimum_satisfaction_score": 1.0,
            "shortage_score": 0.1,
            "agreement_reached": True,
        },
        {
            "scenario_name": "mild_drought",
            "country": "France",
            "region": "Occitanie",
            "drought_level": "mild",
            "available_water": 120.0,
            "strategy": "priority",
            "fairness_score": 0.8,
            "conflict_score": 0.25,
            "minimum_satisfaction_score": 0.9,
            "shortage_score": 0.1,
            "agreement_reached": False,
        },
        {
            "scenario_name": "severe_drought",
            "country": "France",
            "region": "Occitanie",
            "drought_level": "severe",
            "available_water": 80.0,
            "strategy": "proportional",
            "fairness_score": 0.6,
            "conflict_score": 0.5,
            "minimum_satisfaction_score": 0.7,
            "shortage_score": 0.4,
            "agreement_reached": False,
        },
    ]


def test_load_experiment_results(tmp_path: Path) -> None:
    input_path = tmp_path / "results.csv"
    save_results_csv(make_sample_rows(), input_path)

    dataframe = load_experiment_results(input_path)

    assert len(dataframe) == 3
    assert "strategy" in dataframe.columns
    assert "fairness_score" in dataframe.columns


def test_load_experiment_results_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Experiment results file not found"):
        load_experiment_results(tmp_path / "missing.csv")


def test_load_experiment_results_rejects_missing_columns(tmp_path: Path) -> None:
    input_path = tmp_path / "bad_results.csv"

    save_results_csv(
        [
            {
                "scenario_name": "mild_drought",
                "strategy": "proportional",
            }
        ],
        input_path,
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        load_experiment_results(input_path)


def test_summarize_by_strategy(tmp_path: Path) -> None:
    input_path = tmp_path / "results.csv"
    save_results_csv(make_sample_rows(), input_path)

    dataframe = load_experiment_results(input_path)
    summary = summarize_by_strategy(dataframe)

    assert set(summary["strategy"]) == {"proportional", "priority"}
    assert "agreement_rate" in summary.columns
    assert "average_conflict" in summary.columns


def test_summarize_by_drought_level(tmp_path: Path) -> None:
    input_path = tmp_path / "results.csv"
    save_results_csv(make_sample_rows(), input_path)

    dataframe = load_experiment_results(input_path)
    summary = summarize_by_drought_level(dataframe)

    assert set(summary["drought_level"]) == {"mild", "severe"}
    assert "agreement_rate" in summary.columns


def test_find_best_strategy_by_conflict(tmp_path: Path) -> None:
    input_path = tmp_path / "results.csv"
    save_results_csv(make_sample_rows(), input_path)

    dataframe = load_experiment_results(input_path)
    best = find_best_strategy_by_conflict(dataframe)

    mild_best = best[best["scenario_name"] == "mild_drought"].iloc[0]

    assert mild_best["strategy"] == "proportional"


def test_generate_experiment_report(tmp_path: Path) -> None:
    input_path = tmp_path / "results.csv"
    output_path = tmp_path / "experiment_report.md"

    save_results_csv(make_sample_rows(), input_path)

    generate_experiment_report(
        input_path=input_path,
        output_path=output_path,
    )

    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    assert "WaterAgentLab Experiment Report" in content
    assert "Summary by strategy" in content
    assert "Summary by drought level" in content
    assert "Best strategy per scenario" in content
