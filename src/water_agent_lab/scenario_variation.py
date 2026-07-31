import random

from water_agent_lab.models import ScenarioConfig


def vary_available_water(
    scenario: ScenarioConfig,
    rng: random.Random,
    variation_fraction: float = 0.15,
) -> ScenarioConfig:
    """
    Create a scenario variation by perturbing available water.

    Example:
    variation_fraction = 0.15 means available water may vary by ±15%.
    """
    multiplier = rng.uniform(
        1.0 - variation_fraction,
        1.0 + variation_fraction,
    )

    varied_available_water = max(
        scenario.available_water * multiplier,
        1.0,
    )

    return scenario.model_copy(
        update={
            "scenario_name": f"{scenario.scenario_name}_variant",
            "available_water": varied_available_water,
        }
    )
