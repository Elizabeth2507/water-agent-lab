from pathlib import Path
from typing import Any

import yaml

from water_agent_lab.models import ScenarioConfig


def load_scenario_config(config_path: str | Path) -> ScenarioConfig:
    """
    Load a drought scenario YAML file and validate it as ScenarioConfig.

    Parameters
    ----------
    config_path:
        Path to a YAML scenario file.

    Returns
    -------
    ScenarioConfig
        Validated scenario configuration.

    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        raw_config: Any = yaml.safe_load(file)

    if raw_config is None:
        raise ValueError(f"Config file is empty: {path}")

    if not isinstance(raw_config, dict):
        raise ValueError(
            f"Config file must contain a YAML dictionary at the top level: {path}"
        )

    return ScenarioConfig.model_validate(raw_config)
