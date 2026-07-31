from pathlib import Path

from water_agent_lab.exporter import save_results_csv
from water_agent_lab.monte_carlo import run_mock_llm_monte_carlo
from water_agent_lab.monte_carlo_plotter import (
    plot_final_conflict_distribution,
    plot_rounds_used_distribution,
)


def test_plot_final_conflict_distribution(tmp_path: Path) -> None:
    rows = run_mock_llm_monte_carlo(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=42,
        work_dir=tmp_path / "variants",
    )

    input_path = tmp_path / "monte_carlo.csv"
    output_path = tmp_path / "conflict.png"

    save_results_csv(rows, input_path)

    plot_final_conflict_distribution(
        input_path=input_path,
        output_path=output_path,
    )

    assert output_path.exists()


def test_plot_rounds_used_distribution(tmp_path: Path) -> None:
    rows = run_mock_llm_monte_carlo(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=42,
        work_dir=tmp_path / "variants",
    )

    input_path = tmp_path / "monte_carlo.csv"
    output_path = tmp_path / "rounds.png"

    save_results_csv(rows, input_path)

    plot_rounds_used_distribution(
        input_path=input_path,
        output_path=output_path,
    )

    assert output_path.exists()
