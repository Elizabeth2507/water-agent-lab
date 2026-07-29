import pytest

from water_agent_lab.data_source_registry import (
    get_data_source,
    get_data_source_names,
)


def test_get_data_source_names_contains_registered_sources() -> None:
    names = get_data_source_names()

    assert "synthetic" in names
    assert "mock" in names
    assert "vigieau-sample" in names
    assert "hubeau-sample" in names


def test_get_synthetic_data_source() -> None:
    data_source = get_data_source(
        source_name="synthetic",
        path="configs/drought_mvp.yaml",
    )

    scenario = data_source.load_scenario()

    assert scenario.scenario_name == "moderate_drought_mvp"
    assert scenario.country == "France"


def test_get_mock_data_source() -> None:
    data_source = get_data_source(
        source_name="mock",
        path="data/mock/occitanie_drought_snapshot.json",
    )

    scenario = data_source.load_scenario()

    assert scenario.scenario_name == "occitanie_severe_mock_snapshot"
    assert scenario.region == "Occitanie"


def test_get_vigieau_sample_data_source() -> None:
    data_source = get_data_source(
        source_name="vigieau-sample",
        path="data/sample_vigieau/occitanie_restrictions_sample.json",
    )

    scenario = data_source.load_scenario()

    assert scenario.scenario_name == "occitanie_extreme_vigieau_sample"
    assert scenario.drought_level == "extreme"


def test_get_hubeau_sample_data_source() -> None:
    data_source = get_data_source(
        source_name="hubeau-sample",
        path="data/sample_hubeau/occitanie_hydrometry_sample.json",
    )

    scenario = data_source.load_scenario()

    assert scenario.scenario_name == "occitanie_severe_hubeau_hydrometry_sample"
    assert scenario.drought_level == "severe"


def test_get_data_source_rejects_unknown_source() -> None:
    with pytest.raises(ValueError, match="Unknown data source"):
        get_data_source(
            source_name="unknown-source",
            path="configs/drought_mvp.yaml",
        )
