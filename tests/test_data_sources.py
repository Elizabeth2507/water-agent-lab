from pathlib import Path

import pytest

from water_agent_lab.data_sources import (
    MockDroughtDataSource,
    SyntheticScenarioDataSource,
    VigiEauDataSource,
)


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


def test_mock_drought_data_source_loads_snapshot() -> None:
    data_source = MockDroughtDataSource("data/mock/occitanie_drought_snapshot.json")

    raw_snapshot = data_source.load_raw_snapshot()

    assert raw_snapshot["country"] == "France"
    assert raw_snapshot["region"] == "Occitanie"
    assert raw_snapshot["drought_level"] == "severe"


def test_mock_drought_data_source_loads_scenario() -> None:
    data_source = MockDroughtDataSource("data/mock/occitanie_drought_snapshot.json")

    scenario = data_source.load_scenario()

    assert scenario.scenario_name == "occitanie_severe_mock_snapshot"
    assert scenario.country == "France"
    assert scenario.region == "Occitanie"
    assert scenario.drought_level == "severe"
    assert scenario.available_water == 80.0
    assert len(scenario.stakeholders) == 4


def test_mock_drought_data_source_metadata() -> None:
    data_source = MockDroughtDataSource("data/mock/occitanie_drought_snapshot.json")

    metadata = data_source.metadata()

    assert metadata.source_name == "mock_drought_snapshot"
    assert metadata.source_type == "local_json_snapshot"
    assert metadata.source_path == "data/mock/occitanie_drought_snapshot.json"


def test_mock_drought_data_source_rejects_non_object_json(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "bad_snapshot.json"
    snapshot_path.write_text("[1, 2, 3]", encoding="utf-8")

    data_source = MockDroughtDataSource(snapshot_path)

    with pytest.raises(ValueError):
        data_source.load_raw_snapshot()


def test_vigieau_data_source_metadata() -> None:
    data_source = VigiEauDataSource(
        sample_response_path="data/sample_vigieau/occitanie_restrictions_sample.json"
    )

    metadata = data_source.metadata()

    assert metadata.source_name == "vigieau"
    assert metadata.source_type == "public_api_skeleton"
    assert metadata.source_url == "https://api.vigieau.beta.gouv.fr"


def test_vigieau_data_source_loads_sample_response() -> None:
    data_source = VigiEauDataSource(
        sample_response_path="data/sample_vigieau/occitanie_restrictions_sample.json"
    )

    response = data_source.load_sample_response()

    assert response["country"] == "France"
    assert response["region"] == "Occitanie"
    assert response["restriction_level"] == "crise"


def test_vigieau_restriction_level_mapping() -> None:
    data_source = VigiEauDataSource()

    assert data_source.restriction_level_to_drought_level("vigilance") == "mild"
    assert data_source.restriction_level_to_drought_level("alerte") == "moderate"
    assert (
        data_source.restriction_level_to_drought_level("alerte_renforcee") == "severe"
    )
    assert data_source.restriction_level_to_drought_level("crise") == "extreme"
    assert data_source.restriction_level_to_drought_level("unknown_level") == "unknown"


def test_vigieau_data_source_converts_sample_to_scenario() -> None:
    data_source = VigiEauDataSource(
        sample_response_path="data/sample_vigieau/occitanie_restrictions_sample.json"
    )

    scenario = data_source.load_scenario()

    assert scenario.scenario_name == "occitanie_extreme_vigieau_sample"
    assert scenario.country == "France"
    assert scenario.region == "Occitanie"
    assert scenario.drought_level == "extreme"
    assert scenario.available_water == 60.0
    assert len(scenario.stakeholders) == 4

    stakeholder_names = {stakeholder.name for stakeholder in scenario.stakeholders}
    assert stakeholder_names == {"agriculture", "urban", "industry", "ecosystem"}
