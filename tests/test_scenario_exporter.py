from pathlib import Path

from water_agent_lab.config import load_scenario_config
from water_agent_lab.data_source_registry import get_data_source
from water_agent_lab.scenario_exporter import save_scenario_yaml, scenario_to_dict


def test_scenario_to_dict() -> None:
    data_source = get_data_source(
        source_name="hubeau-sample",
        path="data/sample_hubeau/occitanie_hydrometry_sample.json",
    )
    scenario = data_source.load_scenario()

    scenario_data = scenario_to_dict(scenario)

    assert scenario_data["scenario_name"] == (
        "occitanie_severe_hubeau_hydrometry_sample"
    )
    assert scenario_data["country"] == "France"
    assert scenario_data["region"] == "Occitanie"
    assert scenario_data["drought_level"] == "severe"
    assert len(scenario_data["stakeholders"]) == 4


def test_save_scenario_yaml(tmp_path: Path) -> None:
    output_path = tmp_path / "generated_scenario.yaml"

    data_source = get_data_source(
        source_name="vigieau-sample",
        path="data/sample_vigieau/occitanie_restrictions_sample.json",
    )
    scenario = data_source.load_scenario()

    save_scenario_yaml(
        scenario=scenario,
        output_path=output_path,
    )

    assert output_path.exists()

    loaded_scenario = load_scenario_config(output_path)

    assert loaded_scenario.scenario_name == "occitanie_extreme_vigieau_sample"
    assert loaded_scenario.country == "France"
    assert loaded_scenario.drought_level == "extreme"
    assert len(loaded_scenario.stakeholders) == 4
