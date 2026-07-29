from water_agent_lab.data_sources import SyntheticScenarioDataSource


def test_synthetic_scenario_data_source_loads_config() -> None:
    data_source = SyntheticScenarioDataSource("configs/drought_mvp.yaml")

    scenario = data_source.load_scenario()

    assert scenario.scenario_name == "moderate_drought_mvp"
    assert scenario.country == "France"


def test_synthetic_scenario_data_source_metadata() -> None:
    data_source = SyntheticScenarioDataSource("configs/drought_mvp.yaml")

    metadata = data_source.metadata()

    assert metadata.source_name == "synthetic_yaml"
    assert metadata.source_type == "local_yaml"
    assert metadata.source_path == "configs/drought_mvp.yaml"
