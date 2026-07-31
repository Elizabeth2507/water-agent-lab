import random

from water_agent_lab.config import load_scenario_config
from water_agent_lab.scenario_variation import vary_available_water


def test_vary_available_water_is_deterministic_with_seed() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    first_rng = random.Random(42)
    second_rng = random.Random(42)

    first = vary_available_water(scenario, first_rng)
    second = vary_available_water(scenario, second_rng)

    assert first.available_water == second.available_water


def test_vary_available_water_changes_available_water_within_bounds() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    rng = random.Random(42)

    varied = vary_available_water(
        scenario=scenario,
        rng=rng,
        variation_fraction=0.10,
    )

    assert 90.0 <= varied.available_water <= 110.0
    assert varied.scenario_name == "moderate_drought_mvp_variant"
