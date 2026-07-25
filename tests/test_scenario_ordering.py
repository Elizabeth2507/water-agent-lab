from water_agent_lab.scenario_ordering import drought_level_sort_key


def test_drought_level_sort_key() -> None:
    levels = ["extreme", "mild", "severe", "moderate"]

    ordered_levels = sorted(levels, key=drought_level_sort_key)

    assert ordered_levels == ["mild", "moderate", "severe", "extreme"]


def test_unknown_drought_level_goes_last() -> None:
    levels = ["extreme", "unknown", "mild"]

    ordered_levels = sorted(levels, key=drought_level_sort_key)

    assert ordered_levels == ["mild", "extreme", "unknown"]
