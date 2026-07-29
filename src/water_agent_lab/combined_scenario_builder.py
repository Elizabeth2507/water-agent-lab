from water_agent_lab.data_sources import HubEauHydrometryDataSource, VigiEauDataSource
from water_agent_lab.models import ScenarioConfig


DROUGHT_SEVERITY_ORDER = {
    "mild": 0,
    "moderate": 1,
    "severe": 2,
    "extreme": 3,
    "unknown": -1,
}


def choose_most_severe_drought_level(
    first_drought_level: str,
    second_drought_level: str,
) -> str:
    """
    Return the most severe drought level.
    """
    first_score = DROUGHT_SEVERITY_ORDER.get(first_drought_level, -1)
    second_score = DROUGHT_SEVERITY_ORDER.get(second_drought_level, -1)

    if first_score >= second_score:
        return first_drought_level

    return second_drought_level


def build_combined_vigieau_hubeau_scenario(
    vigieau_data_source: VigiEauDataSource,
    hubeau_data_source: HubEauHydrometryDataSource,
) -> ScenarioConfig:
    """
    Build a combined drought scenario from VigiEau and Hub'Eau sample sources.

    Current rule:
    - drought level: most severe of the two source-derived levels
    - available water: minimum available-water proxy
    - stakeholders: copied from the VigiEau-derived scenario
    """
    vigieau_scenario = vigieau_data_source.load_scenario()
    hubeau_scenario = hubeau_data_source.load_scenario()

    combined_drought_level = choose_most_severe_drought_level(
        vigieau_scenario.drought_level,
        hubeau_scenario.drought_level,
    )

    combined_available_water = min(
        vigieau_scenario.available_water,
        hubeau_scenario.available_water,
    )

    scenario_data = {
        "scenario_name": (
            f"{vigieau_scenario.region.lower()}_"
            f"{combined_drought_level}_combined_sample"
        ),
        "country": vigieau_scenario.country,
        "region": vigieau_scenario.region,
        "drought_level": combined_drought_level,
        "available_water": combined_available_water,
        "max_rounds": min(vigieau_scenario.max_rounds, hubeau_scenario.max_rounds),
        "stakeholders": [
            stakeholder.model_dump() for stakeholder in vigieau_scenario.stakeholders
        ],
    }

    return ScenarioConfig.model_validate(scenario_data)
