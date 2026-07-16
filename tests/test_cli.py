import json

from typer.testing import CliRunner

from water_agent_lab.cli import app

runner = CliRunner()


def test_simulate_proportional_command() -> None:
    result = runner.invoke(
        app,
        [
            "simulate",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "proportional",
        ],
    )

    assert result.exit_code == 0

    output = json.loads(result.stdout)

    assert output["strategy"] == "proportional"
    assert output["scenario_name"] == "moderate_drought_mvp"
    assert output["total_requested"] == 130.0
    assert output["water_budget_valid"] is True
    assert output["conflict_score"] == 0.5
    assert output["agreement_reached"] is False


def test_simulate_priority_command() -> None:
    result = runner.invoke(
        app,
        [
            "simulate",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "priority",
        ],
    )

    assert result.exit_code == 0

    output = json.loads(result.stdout)

    assert output["strategy"] == "priority"
    assert output["scenario_name"] == "moderate_drought_mvp"
    assert output["total_requested"] == 130.0
    assert output["water_budget_valid"] is True


def test_simulate_invalid_strategy_fails() -> None:
    result = runner.invoke(
        app,
        [
            "simulate",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "unknown",
        ],
    )

    assert result.exit_code != 0


def test_compare_command() -> None:
    result = runner.invoke(
        app,
        [
            "compare",
            "--config",
            "configs/drought_mvp.yaml",
        ],
    )

    assert result.exit_code == 0
    assert "Water Allocation Strategy Comparison" in result.stdout
    assert "0.500" in result.stdout
    assert "0.250" in result.stdout


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "WaterAgentLab 0.1.0" in result.stdout


def test_validate_config_command() -> None:
    result = runner.invoke(
        app,
        [
            "validate-config",
            "--config",
            "configs/drought_mvp.yaml",
        ],
    )

    assert result.exit_code == 0
    assert "Config is valid." in result.stdout
    assert "moderate_drought_mvp" in result.stdout
    assert "Stakeholders: 4" in result.stdout


def test_run_all_command() -> None:
    result = runner.invoke(
        app,
        [
            "run-all",
            "--config-dir",
            "configs",
        ],
    )

    assert result.exit_code == 0
    assert "All Scenario Strategy Comparison" in result.stdout
    assert "mild_drought" in result.stdout
    assert "severe_drought" in result.stdout
    assert "extreme_drought" in result.stdout


def test_run_all_command_with_csv_output(tmp_path) -> None:
    output_path = tmp_path / "results.csv"

    result = runner.invoke(
        app,
        [
            "run-all",
            "--config-dir",
            "configs",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Saved results" in result.stdout


def test_plot_results_command(tmp_path) -> None:
    input_path = tmp_path / "results.csv"
    output_path = tmp_path / "plot.png"

    input_path.write_text(
        (
            "scenario_name,strategy,fairness_score,conflict_score\n"
            "mild_drought,proportional,0.9,0.0\n"
            "severe_drought,priority,0.6,0.5\n"
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "plot-results",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Saved plot" in result.stdout
