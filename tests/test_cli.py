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
