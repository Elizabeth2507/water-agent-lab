import json

from pathlib import Path
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
            "scenario_name,drought_level,strategy,fairness_score,conflict_score\n"
            "mild_drought,mild,proportional,0.9,0.0\n"
            "severe_drought,severe,priority,0.6,0.5\n"
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


def test_simulate_minimum_first_command() -> None:
    result = runner.invoke(
        app,
        [
            "simulate",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "minimum-first",
        ],
    )

    assert result.exit_code == 0

    output = json.loads(result.stdout)

    assert output["strategy"] == "minimum-first"
    assert output["scenario_name"] == "moderate_drought_mvp"
    assert output["water_budget_valid"] is True
    assert output["conflict_score"] == 0.0
    assert output["agreement_reached"] is True


def test_simulate_minimum_priority_command() -> None:
    result = runner.invoke(
        app,
        [
            "simulate",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "minimum-priority",
        ],
    )

    assert result.exit_code == 0

    output = json.loads(result.stdout)

    assert output["strategy"] == "minimum-priority"
    assert output["scenario_name"] == "moderate_drought_mvp"
    assert output["water_budget_valid"] is True
    assert output["conflict_score"] == 0.0
    assert output["minimum_satisfaction_score"] == 1.0
    assert output["agreement_reached"] is True


def test_generate_report_command(tmp_path: Path) -> None:
    results_path = tmp_path / "all_results.csv"
    report_path = tmp_path / "experiment_report.md"

    run_all_result = runner.invoke(
        app,
        [
            "run-all",
            "--config-dir",
            "configs",
            "--output",
            str(results_path),
        ],
    )

    assert run_all_result.exit_code == 0
    assert results_path.exists()

    report_result = runner.invoke(
        app,
        [
            "generate-report",
            "--input",
            str(results_path),
            "--output",
            str(report_path),
        ],
    )

    assert report_result.exit_code == 0
    assert report_path.exists()
    assert "Saved experiment report" in report_result.stdout


def test_generate_report_command_rejects_non_markdown_output(
    tmp_path: Path,
) -> None:
    results_path = tmp_path / "all_results.csv"
    report_path = tmp_path / "experiment_report.txt"

    run_all_result = runner.invoke(
        app,
        [
            "run-all",
            "--config-dir",
            "configs",
            "--output",
            str(results_path),
        ],
    )

    assert run_all_result.exit_code == 0

    report_result = runner.invoke(
        app,
        [
            "generate-report",
            "--input",
            str(results_path),
            "--output",
            str(report_path),
        ],
    )

    assert report_result.exit_code != 0


def test_agent_responses_command() -> None:
    result = runner.invoke(
        app,
        [
            "agent-responses",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "minimum-first",
        ],
    )

    assert result.exit_code == 0
    assert "Rule-Based Stakeholder Responses" in result.stdout


def test_negotiate_command() -> None:
    result = runner.invoke(
        app,
        [
            "negotiate",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "proportional",
        ],
    )

    assert result.exit_code == 0
    assert "Simple Negotiation Round" in result.stdout


def test_negotiate_multi_command() -> None:
    result = runner.invoke(
        app,
        [
            "negotiate-multi",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "proportional",
        ],
    )

    assert result.exit_code == 0
    assert "Multi-Round Negotiation" in result.stdout
    assert "Final agreement reached" in result.stdout


def test_negotiate_multi_command_with_json_output(tmp_path) -> None:
    output_path = tmp_path / "negotiation_history.json"

    result = runner.invoke(
        app,
        [
            "negotiate-multi",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "proportional",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Saved negotiation history" in result.stdout


def test_summarize_negotiation_command(tmp_path) -> None:
    output_path = tmp_path / "negotiation_history.json"

    create_result = runner.invoke(
        app,
        [
            "negotiate-multi",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "proportional",
            "--output",
            str(output_path),
        ],
    )

    assert create_result.exit_code == 0
    assert output_path.exists()

    summary_result = runner.invoke(
        app,
        [
            "summarize-negotiation",
            "--input",
            str(output_path),
        ],
    )

    assert summary_result.exit_code == 0
    assert "Negotiation Summary" in summary_result.stdout
    assert "Rejected Stakeholders by Round" in summary_result.stdout


def test_simulate_command_with_log_file(tmp_path) -> None:
    log_path = tmp_path / "simulation.log"

    result = runner.invoke(
        app,
        [
            "simulate",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "proportional",
            "--log-file",
            str(log_path),
        ],
    )

    assert result.exit_code == 0
    assert log_path.exists()

    log_content = log_path.read_text(encoding="utf-8")

    assert "simulation_started" in log_content
    assert "simulation_completed" in log_content


def test_negotiate_multi_command_with_log_file(tmp_path) -> None:
    log_path = tmp_path / "negotiation.log"

    result = runner.invoke(
        app,
        [
            "negotiate-multi",
            "--config",
            "configs/drought_mvp.yaml",
            "--strategy",
            "proportional",
            "--log-file",
            str(log_path),
        ],
    )

    assert result.exit_code == 0
    assert log_path.exists()

    log_content = log_path.read_text(encoding="utf-8")

    assert "negotiation_started" in log_content
    assert "negotiation_completed" in log_content
    assert "negotiation_round_completed" in log_content


def test_run_all_export_includes_run_metadata(tmp_path) -> None:
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

    content = output_path.read_text(encoding="utf-8")

    assert "run_id" in content
    assert "created_at_utc" in content
    assert "command" in content
    assert "run-all" in content
