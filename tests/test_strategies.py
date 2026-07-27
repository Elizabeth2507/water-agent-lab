import pytest

from water_agent_lab.config import load_scenario_config
from water_agent_lab.models import AllocationProposal
from water_agent_lab.strategies import get_strategy, get_strategy_names


def test_get_strategy_names() -> None:
    strategy_names = get_strategy_names()

    assert "proportional" in strategy_names
    assert "priority" in strategy_names
    assert "minimum-first" in strategy_names
    assert "minimum-priority" in strategy_names


def test_get_strategy_returns_callable_strategy() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    strategy = get_strategy("proportional")
    proposal = strategy(scenario)

    assert isinstance(proposal, AllocationProposal)


def test_get_strategy_raises_for_unknown_strategy() -> None:
    with pytest.raises(ValueError, match="Unknown strategy"):
        get_strategy("unknown")
