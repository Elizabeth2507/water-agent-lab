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


def test_run_all_command_with_csv_output(tmp_path: Path) -> None:
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


def test_plot_results_command(tmp_path: Path) -> None:
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


def test_negotiate_multi_command_with_json_output(tmp_path: Path) -> None:
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


def test_summarize_negotiation_command(tmp_path: Path) -> None:
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


def test_simulate_command_with_log_file(tmp_path: Path) -> None:
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


def test_negotiate_multi_command_with_log_file(tmp_path: Path) -> None:
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


def test_run_all_export_includes_run_metadata(tmp_path: Path) -> None:
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


def test_list_runs_command_with_custom_registry(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.jsonl"

    registry_path.write_text(
        (
            '{"run_id": "test-run-id", '
            '"created_at_utc": "2026-01-01T00:00:00+00:00", '
            '"command": "run-all", '
            '"status": "completed", '
            '"outputs": {"results": "outputs/results.csv"}}\n'
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "list-runs",
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code == 0
    assert "Experiment Registry" in result.stdout
    assert "test-run-id" in result.stdout
    assert "run-all" in result.stdout


def test_run_all_writes_to_custom_registry(tmp_path: Path) -> None:
    output_path = tmp_path / "results.csv"
    registry_path = tmp_path / "registry.jsonl"

    result = runner.invoke(
        app,
        [
            "run-all",
            "--config-dir",
            "configs",
            "--output",
            str(output_path),
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert registry_path.exists()

    registry_lines = registry_path.read_text(encoding="utf-8").splitlines()
    registry_entry = json.loads(registry_lines[0])

    assert registry_entry["command"] == "run-all"
    assert registry_entry["status"] == "completed"
    assert registry_entry["config_dir"] == "configs"
    assert Path(registry_entry["outputs"]["results"]) == output_path


def test_negotiate_multi_writes_to_custom_registry(tmp_path: Path) -> None:
    output_path = tmp_path / "negotiation_history.json"
    registry_path = tmp_path / "registry.jsonl"

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
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert registry_path.exists()

    registry_lines = registry_path.read_text(encoding="utf-8").splitlines()
    registry_entry = json.loads(registry_lines[0])

    assert registry_entry["command"] == "negotiate-multi"
    assert registry_entry["status"] == "completed"
    assert Path(registry_entry["config_path"]) == Path("configs/drought_mvp.yaml")
    assert registry_entry["initial_strategy"] == "proportional"
    assert Path(registry_entry["outputs"]["negotiation_history"]) == output_path


def test_show_run_command_with_custom_registry(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.jsonl"

    registry_path.write_text(
        (
            '{"run_id": "test-run-id", '
            '"created_at_utc": "2026-01-01T00:00:00+00:00", '
            '"command": "run-all", '
            '"status": "completed", '
            '"outputs": {"results": "outputs/results.csv"}}\n'
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "show-run",
            "--run-id",
            "test-run-id",
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code == 0
    assert "Experiment Run" in result.stdout
    assert "Run Outputs" in result.stdout
    assert "test-run-id" in result.stdout
    assert "run-all" in result.stdout


def test_show_run_command_fails_for_missing_run_id(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.jsonl"

    registry_path.write_text("", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "show-run",
            "--run-id",
            "missing-run",
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code != 0


def test_verify_run_command_with_matching_config_hash(tmp_path: Path) -> None:
    import json

    from water_agent_lab.hashing import compute_file_sha256

    config_path = tmp_path / "scenario.yaml"
    registry_path = tmp_path / "registry.jsonl"

    config_path.write_text("available_water: 100\n", encoding="utf-8")

    config_hash = compute_file_sha256(config_path)

    record = {
        "run_id": "test-run-id",
        "created_at_utc": "2026-01-01T00:00:00+00:00",
        "command": "negotiate-multi",
        "status": "completed",
        "config_path": str(config_path),
        "config_hash": config_hash,
        "outputs": {
            "negotiation_history": "outputs/history.json",
        },
    }

    registry_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "verify-run",
            "--run-id",
            "test-run-id",
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code == 0
    assert "Run Reproducibility Check" in result.stdout
    assert "All config files match" in result.stdout


def test_verify_run_command_fails_for_missing_run_id(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.jsonl"
    registry_path.write_text("", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "verify-run",
            "--run-id",
            "missing-run",
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code != 0


def test_reproduce_run_for_run_all(tmp_path: Path) -> None:
    output_path = tmp_path / "results.csv"
    registry_path = tmp_path / "registry.jsonl"

    create_result = runner.invoke(
        app,
        [
            "run-all",
            "--config-dir",
            "configs",
            "--output",
            str(output_path),
            "--registry",
            str(registry_path),
        ],
    )

    assert create_result.exit_code == 0

    import json

    records = [
        json.loads(line)
        for line in registry_path.read_text(encoding="utf-8").splitlines()
    ]

    run_id = records[0]["run_id"]

    reproduce_result = runner.invoke(
        app,
        [
            "reproduce-run",
            "--run-id",
            run_id,
            "--registry",
            str(registry_path),
        ],
    )

    assert reproduce_result.exit_code == 0
    assert "Run is reproducible" in reproduce_result.stdout

    updated_records = [
        json.loads(line)
        for line in registry_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(updated_records) == 2
    assert updated_records[1]["reproduced_from_run_id"] == run_id


def test_reproduce_run_fails_for_missing_run_id(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.jsonl"
    registry_path.write_text("", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "reproduce-run",
            "--run-id",
            "missing-run",
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code != 0


def test_compare_runs_command_for_reproduced_run_all(tmp_path) -> None:
    import json

    output_path = tmp_path / "results.csv"
    registry_path = tmp_path / "registry.jsonl"

    create_result = runner.invoke(
        app,
        [
            "run-all",
            "--config-dir",
            "configs",
            "--output",
            str(output_path),
            "--registry",
            str(registry_path),
        ],
    )

    assert create_result.exit_code == 0

    records = [
        json.loads(line)
        for line in registry_path.read_text(encoding="utf-8").splitlines()
    ]
    original_run_id = records[0]["run_id"]

    reproduce_result = runner.invoke(
        app,
        [
            "reproduce-run",
            "--run-id",
            original_run_id,
            "--registry",
            str(registry_path),
        ],
    )

    assert reproduce_result.exit_code == 0

    updated_records = [
        json.loads(line)
        for line in registry_path.read_text(encoding="utf-8").splitlines()
    ]
    reproduced_run_id = updated_records[1]["run_id"]

    compare_result = runner.invoke(
        app,
        [
            "compare-runs",
            "--run-id",
            original_run_id,
            "--reproduced-run-id",
            reproduced_run_id,
            "--registry",
            str(registry_path),
        ],
    )

    assert compare_result.exit_code == 0
    assert "Run Comparison" in compare_result.stdout
    assert "Reproduced output matches original output" in compare_result.stdout


def test_generate_run_report_command(tmp_path) -> None:
    import json

    results_path = tmp_path / "results.csv"
    registry_path = tmp_path / "registry.jsonl"
    report_path = tmp_path / "report.md"
    # plot_path = tmp_path / "report_plot.png"

    results_path.write_text(
        (
            "scenario_name,drought_level,strategy,fairness_score,conflict_score,"
            "minimum_satisfaction_score,shortage_score,agreement_reached\n"
            "mild_drought,mild,proportional,0.9,0.0,1.0,0.1,True\n"
            "severe_drought,severe,proportional,0.6,0.5,0.7,0.4,False\n"
        ),
        encoding="utf-8",
    )

    record = {
        "run_id": "test-run-id",
        "created_at_utc": "2026-01-01T00:00:00+00:00",
        "command": "run-all",
        "status": "completed",
        "outputs": {
            "results": str(results_path),
        },
    }

    registry_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "generate-run-report",
            "--run-id",
            "test-run-id",
            "--registry",
            str(registry_path),
            "--output",
            str(report_path),
            # "--plot",
            # str(plot_path),
        ],
    )

    assert result.exit_code == 0
    assert report_path.exists()
    # assert plot_path.exists()
    assert "Saved experiment report" in result.stdout
    assert "Recorded report generation run" in result.stdout

    records = [
        json.loads(line)
        for line in registry_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(records) == 2
    assert records[1]["command"] == "generate-run-report"
    assert records[1]["source_run_id"] == "test-run-id"
    assert records[1]["outputs"]["report"] == str(report_path)


def test_generate_run_report_fails_for_missing_run_id(tmp_path) -> None:
    registry_path = tmp_path / "registry.jsonl"
    registry_path.write_text("", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "generate-run-report",
            "--run-id",
            "missing-run",
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code != 0


def test_dashboard_command_with_custom_registry(tmp_path) -> None:
    registry_path = tmp_path / "registry.jsonl"

    registry_path.write_text(
        (
            '{"run_id": "run-1", '
            '"created_at_utc": "2026-01-01T00:00:00+00:00", '
            '"command": "run-all", '
            '"status": "completed", '
            '"outputs": {"results": "outputs/results.csv"}}\n'
            '{"run_id": "run-2", '
            '"created_at_utc": "2026-01-01T01:00:00+00:00", '
            '"command": "negotiate-multi", '
            '"status": "completed", '
            '"outputs": {"negotiation_history": "outputs/history.json"}}\n'
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "dashboard",
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code == 0
    assert "WaterAgentLab Experiment Dashboard" in result.stdout
    assert "Runs by Command" in result.stdout
    assert "Outputs by Type" in result.stdout
    assert "run-all" in result.stdout
    assert "negotiate-multi" in result.stdout


def test_run_experiment_command(tmp_path) -> None:
    import json

    results_path = tmp_path / "results.csv"
    report_path = tmp_path / "report.md"
    # plot_path = tmp_path / "report_plot.png"
    registry_path = tmp_path / "registry.jsonl"

    result = runner.invoke(
        app,
        [
            "run-experiment",
            "--config-dir",
            "configs",
            "--results",
            str(results_path),
            "--report",
            str(report_path),
            # "--plot",
            # str(plot_path),
            "--registry",
            str(registry_path),
        ],
    )

    assert result.exit_code == 0
    assert results_path.exists()
    assert report_path.exists()
    # assert plot_path.exists()
    assert registry_path.exists()

    assert "Experiment pipeline completed" in result.stdout

    records = [
        json.loads(line)
        for line in registry_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(records) == 1
    assert records[0]["command"] == "run-experiment"
    assert records[0]["outputs"]["results"] == str(results_path)
    assert records[0]["outputs"]["report"] == str(report_path)
    # assert records[0]["outputs"]["plot"] == str(plot_path)


def test_generate_report_command_with_plot(tmp_path: Path) -> None:
    results_path = tmp_path / "all_results.csv"
    report_path = tmp_path / "experiment_report.md"
    plot_path = tmp_path / "fairness_conflict.png"

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
            "--plot",
            str(plot_path),
        ],
    )

    assert report_result.exit_code == 0
    assert report_path.exists()
    assert plot_path.exists()
    assert "Saved experiment report" in report_result.stdout
    assert "Saved report plot" in report_result.stdout


def test_generate_report_command_rejects_non_png_plot(
    tmp_path: Path,
) -> None:
    results_path = tmp_path / "all_results.csv"
    report_path = tmp_path / "experiment_report.md"
    plot_path = tmp_path / "fairness_conflict.jpg"

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
            "--plot",
            str(plot_path),
        ],
    )

    assert report_result.exit_code != 0