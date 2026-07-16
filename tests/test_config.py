from pathlib import Path

import pytest
import yaml

from water_agent_lab.config import load_scenario_config
from water_agent_lab.models import ScenarioConfig


def test_load_scenario_config() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    assert isinstance(scenario, ScenarioConfig)
    assert scenario.scenario_name == "moderate_drought_mvp"
    assert scenario.country == "France"
    assert scenario.available_water == 100.0
    assert len(scenario.stakeholders) == 4


def test_load_missing_config_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_scenario_config("configs/does_not_exist.yaml")


def test_empty_config_file_raises_value_error(tmp_path: Path) -> None:
    config_path = tmp_path / "empty.yaml"
    config_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Config file is empty"):
        load_scenario_config(config_path)


def test_top_level_list_config_raises_value_error(tmp_path: Path) -> None:
    config_path = tmp_path / "list.yaml"

    with config_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(["agriculture", "urban"], file)

    with pytest.raises(ValueError, match="YAML dictionary"):
        load_scenario_config(config_path)


@pytest.mark.parametrize(
    "config_path, expected_scenario_name, expected_available_water",
    [
        ("configs/drought_mvp.yaml", "moderate_drought_mvp", 100.0),
        ("configs/mild_drought.yaml", "mild_drought", 120.0),
        ("configs/severe_drought.yaml", "severe_drought", 80.0),
        ("configs/extreme_drought.yaml", "extreme_drought", 60.0),
    ],
)
def test_all_scenario_configs_load(
    config_path: str,
    expected_scenario_name: str,
    expected_available_water: float,
) -> None:
    scenario = load_scenario_config(config_path)

    assert scenario.scenario_name == expected_scenario_name
    assert scenario.country == "France"
    assert scenario.region == "Occitanie"
    assert scenario.available_water == expected_available_water
    assert len(scenario.stakeholders) == 4
