from water_agent_lab.combined_scenario_builder import (
    build_combined_vigieau_hubeau_scenario,
    choose_most_severe_drought_level,
)
from water_agent_lab.data_sources import HubEauHydrometryDataSource, VigiEauDataSource


def test_choose_most_severe_drought_level() -> None:
    assert choose_most_severe_drought_level("mild", "severe") == "severe"
    assert choose_most_severe_drought_level("extreme", "severe") == "extreme"
    assert choose_most_severe_drought_level("moderate", "moderate") == "moderate"


def test_build_combined_vigieau_hubeau_scenario() -> None:
    vigieau_data_source = VigiEauDataSource(
        sample_response_path="data/sample_vigieau/occitanie_restrictions_sample.json"
    )
    hubeau_data_source = HubEauHydrometryDataSource(
        sample_response_path="data/sample_hubeau/occitanie_hydrometry_sample.json"
    )

    scenario = build_combined_vigieau_hubeau_scenario(
        vigieau_data_source=vigieau_data_source,
        hubeau_data_source=hubeau_data_source,
    )

    assert scenario.scenario_name == "occitanie_extreme_combined_sample"
    assert scenario.country == "France"
    assert scenario.region == "Occitanie"
    assert scenario.drought_level == "extreme"
    assert scenario.available_water == 60.0
    assert len(scenario.stakeholders) == 4
