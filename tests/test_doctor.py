from pathlib import Path

from water_agent_lab.doctor import check_project_health, project_health_passed


def test_project_health_passes_for_current_project() -> None:
    checks = check_project_health()

    assert project_health_passed(checks) is True


def test_project_health_detects_missing_configs(tmp_path: Path) -> None:
    config_dir = tmp_path / "missing_configs"
    outputs_dir = tmp_path / "outputs"
    docs_dir = tmp_path / "docs"

    checks = check_project_health(
        config_dir=config_dir,
        outputs_dir=outputs_dir,
        docs_dir=docs_dir,
    )

    assert project_health_passed(checks) is False

    failed_checks = [check for check in checks if not check["passed"]]

    assert any(check["check"] == "configs_directory_exists" for check in failed_checks)
