from pathlib import Path
from typing import Any

from water_agent_lab.config import load_scenario_config
from water_agent_lab.strategies import get_strategy_names


REQUIRED_CONFIG_FILES = [
    "drought_mvp.yaml",
    "mild_drought.yaml",
    "severe_drought.yaml",
    "extreme_drought.yaml",
]


def check_project_health(
    config_dir: str | Path = Path("configs"),
    outputs_dir: str | Path = Path("outputs"),
    docs_dir: str | Path = Path("docs"),
) -> list[dict[str, Any]]:
    """
    Run basic project health checks.
    """
    config_path = Path(config_dir)
    outputs_path = Path(outputs_dir)
    docs_path = Path(docs_dir)

    checks = []

    checks.append(
        {
            "check": "configs_directory_exists",
            "passed": config_path.exists() and config_path.is_dir(),
            "details": str(config_path),
        }
    )

    for config_file in REQUIRED_CONFIG_FILES:
        file_path = config_path / config_file
        checks.append(
            {
                "check": f"config_exists:{config_file}",
                "passed": file_path.exists(),
                "details": str(file_path),
            }
        )

    for config_file in REQUIRED_CONFIG_FILES:
        file_path = config_path / config_file

        if not file_path.exists():
            continue

        try:
            scenario = load_scenario_config(file_path)
            checks.append(
                {
                    "check": f"config_valid:{config_file}",
                    "passed": True,
                    "details": scenario.scenario_name,
                }
            )
        except Exception as error:
            checks.append(
                {
                    "check": f"config_valid:{config_file}",
                    "passed": False,
                    "details": str(error),
                }
            )

    strategy_names = get_strategy_names()

    checks.append(
        {
            "check": "strategies_registered",
            "passed": len(strategy_names) > 0,
            "details": ", ".join(strategy_names),
        }
    )

    try:
        outputs_path.mkdir(parents=True, exist_ok=True)
        checks.append(
            {
                "check": "outputs_directory_writable",
                "passed": True,
                "details": str(outputs_path),
            }
        )
    except Exception as error:
        checks.append(
            {
                "check": "outputs_directory_writable",
                "passed": False,
                "details": str(error),
            }
        )

    try:
        docs_path.mkdir(parents=True, exist_ok=True)
        checks.append(
            {
                "check": "docs_directory_writable",
                "passed": True,
                "details": str(docs_path),
            }
        )
    except Exception as error:
        checks.append(
            {
                "check": "docs_directory_writable",
                "passed": False,
                "details": str(error),
            }
        )

    return checks


def project_health_passed(checks: list[dict[str, Any]]) -> bool:
    """
    Return whether all health checks passed.
    """
    return all(check["passed"] for check in checks)
