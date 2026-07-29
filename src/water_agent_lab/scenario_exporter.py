from pathlib import Path
from typing import Any

import yaml

from water_agent_lab.models import ScenarioConfig


def scenario_to_dict(scenario: ScenarioConfig) -> dict[str, Any]:
    """
    Convert a ScenarioConfig into a plain dictionary suitable for YAML export.
    """
    return scenario.model_dump()


def save_scenario_yaml(
    scenario: ScenarioConfig,
    output_path: str | Path,
) -> None:
    """
    Save a ScenarioConfig as a YAML file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    scenario_data = scenario_to_dict(scenario)

    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(
            scenario_data,
            file,
            sort_keys=False,
            allow_unicode=True,
        )
