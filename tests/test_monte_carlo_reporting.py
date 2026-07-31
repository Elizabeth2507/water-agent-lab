from pathlib import Path

import pytest

from water_agent_lab.exporter import save_results_csv
from water_agent_lab.monte_carlo import run_mock_llm_monte_carlo
from water_agent_lab.monte_carlo_reporting import (
    build_mediator_action_summary,
    generate_monte_carlo_report,
    load_monte_carlo_results,
    summarize_monte_carlo_results,
)


def test_load_monte_carlo_results(tmp_path: Path) -> None:
    rows = run_mock_llm_monte_carlo(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=42,
        work_dir=tmp_path / "variants",
    )

    input_path = tmp_path / "monte_carlo.csv"
    save_results_csv(rows, input_path)

    dataframe = load_monte_carlo_results(input_path)

    assert len(dataframe) == 3
    assert "final_conflict_score" in dataframe.columns


def test_load_monte_carlo_results_rejects_missing_columns(tmp_path: Path) -> None:
    input_path = tmp_path / "bad.csv"
    input_path.write_text("run_index,value\n1,2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required Monte Carlo columns"):
        load_monte_carlo_results(input_path)


def test_summarize_monte_carlo_results(tmp_path: Path) -> None:
    rows = run_mock_llm_monte_carlo(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=42,
        work_dir=tmp_path / "variants",
    )

    input_path = tmp_path / "monte_carlo.csv"
    save_results_csv(rows, input_path)

    dataframe = load_monte_carlo_results(input_path)
    summary = summarize_monte_carlo_results(dataframe)

    assert summary["total_runs"] == 3
    assert 0.0 <= summary["agreement_rate"] <= 1.0
    assert 0.0 <= summary["average_final_conflict"] <= 1.0


def test_build_mediator_action_summary(tmp_path: Path) -> None:
    rows = run_mock_llm_monte_carlo(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=42,
        work_dir=tmp_path / "variants",
    )

    input_path = tmp_path / "monte_carlo.csv"
    save_results_csv(rows, input_path)

    dataframe = load_monte_carlo_results(input_path)
    action_summary = build_mediator_action_summary(dataframe)

    assert "mediator_action" in action_summary.columns
    assert "count" in action_summary.columns
    assert "share" in action_summary.columns


def test_generate_monte_carlo_report(tmp_path: Path) -> None:
    rows = run_mock_llm_monte_carlo(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=42,
        work_dir=tmp_path / "variants",
    )

    input_path = tmp_path / "monte_carlo.csv"
    output_path = tmp_path / "monte_carlo_report.md"

    save_results_csv(rows, input_path)

    generate_monte_carlo_report(
        input_path=input_path,
        output_path=output_path,
    )

    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    assert "Monte Carlo Mock LLM Negotiation Report" in content
    assert "agreement_rate" in content
    assert "Final mediator actions" in content
