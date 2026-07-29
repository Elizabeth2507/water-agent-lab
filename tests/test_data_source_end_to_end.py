from pathlib import Path

import pytest

from water_agent_lab.agents import evaluate_stakeholder_responses
from water_agent_lab.config import load_scenario_config
from water_agent_lab.data_source_registry import get_data_source
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.negotiation import run_multi_round_negotiation
from water_agent_lab.scenario_exporter import save_scenario_yaml
from water_agent_lab.simulator import minimum_first_allocation

from water_agent_lab.combined_scenario_builder import (
    build_combined_vigieau_hubeau_scenario,
)
from water_agent_lab.data_sources import HubEauHydrometryDataSource, VigiEauDataSource


DATA_SOURCE_CASES = [
    (
        "mock",
        "data/mock/occitanie_drought_snapshot.json",
        "occitanie_severe_mock_snapshot",
    ),
    (
        "vigieau-sample",
        "data/sample_vigieau/occitanie_restrictions_sample.json",
        "occitanie_extreme_vigieau_sample",
    ),
    (
        "hubeau-sample",
        "data/sample_hubeau/occitanie_hydrometry_sample.json",
        "occitanie_severe_hubeau_hydrometry_sample",
    ),
]


@pytest.mark.parametrize(
    ("source_name", "source_path", "expected_scenario_name"),
    DATA_SOURCE_CASES,
)
def test_data_source_generated_scenario_can_be_exported_and_reloaded(
    tmp_path: Path,
    source_name: str,
    source_path: str,
    expected_scenario_name: str,
) -> None:
    data_source = get_data_source(
        source_name=source_name,
        path=source_path,
    )

    generated_scenario = data_source.load_scenario()

    output_path = tmp_path / f"{source_name}_generated.yaml"

    save_scenario_yaml(
        scenario=generated_scenario,
        output_path=output_path,
    )

    reloaded_scenario = load_scenario_config(output_path)

    assert reloaded_scenario.scenario_name == expected_scenario_name
    assert reloaded_scenario.country == "France"
    assert reloaded_scenario.region == "Occitanie"
    assert len(reloaded_scenario.stakeholders) == 4


@pytest.mark.parametrize(
    ("source_name", "source_path", "expected_scenario_name"),
    DATA_SOURCE_CASES,
)
def test_data_source_generated_scenario_can_run_simulation(
    tmp_path: Path,
    source_name: str,
    source_path: str,
    expected_scenario_name: str,
) -> None:
    data_source = get_data_source(
        source_name=source_name,
        path=source_path,
    )
    generated_scenario = data_source.load_scenario()

    output_path = tmp_path / f"{source_name}_generated.yaml"

    save_scenario_yaml(
        scenario=generated_scenario,
        output_path=output_path,
    )

    scenario = load_scenario_config(output_path)
    proposal = minimum_first_allocation(scenario)
    result = evaluate_proposal(scenario, proposal)

    assert result.scenario_name == expected_scenario_name
    assert result.water_budget_valid is True
    assert result.total_allocated <= result.available_water + 1e-9
    assert 0.0 <= result.fairness_score <= 1.0
    assert 0.0 <= result.conflict_score <= 1.0
    assert 0.0 <= result.minimum_satisfaction_score <= 1.0
    assert 0.0 <= result.shortage_score <= 1.0


@pytest.mark.parametrize(
    ("source_name", "source_path", "expected_scenario_name"),
    DATA_SOURCE_CASES,
)
def test_data_source_generated_scenario_can_run_agent_responses(
    tmp_path: Path,
    source_name: str,
    source_path: str,
    expected_scenario_name: str,
) -> None:
    data_source = get_data_source(
        source_name=source_name,
        path=source_path,
    )
    generated_scenario = data_source.load_scenario()

    output_path = tmp_path / f"{source_name}_generated.yaml"

    save_scenario_yaml(
        scenario=generated_scenario,
        output_path=output_path,
    )

    scenario = load_scenario_config(output_path)
    proposal = minimum_first_allocation(scenario)

    responses = evaluate_stakeholder_responses(
        stakeholders=scenario.stakeholders,
        proposal=proposal,
    )

    assert scenario.scenario_name == expected_scenario_name
    assert len(responses) == len(scenario.stakeholders)
    assert all(
        response.status in {"accepted", "concerned", "rejected"}
        for response in responses
    )


@pytest.mark.parametrize(
    ("source_name", "source_path", "expected_scenario_name"),
    DATA_SOURCE_CASES,
)
def test_data_source_generated_scenario_can_run_multi_round_negotiation(
    tmp_path: Path,
    source_name: str,
    source_path: str,
    expected_scenario_name: str,
) -> None:
    data_source = get_data_source(
        source_name=source_name,
        path=source_path,
    )
    generated_scenario = data_source.load_scenario()

    output_path = tmp_path / f"{source_name}_generated.yaml"

    save_scenario_yaml(
        scenario=generated_scenario,
        output_path=output_path,
    )

    result = run_multi_round_negotiation(
        config_path=str(output_path),
        initial_strategy="proportional",
    )

    assert result.scenario_name == expected_scenario_name
    assert 1 <= result.rounds_used <= result.max_rounds
    assert len(result.rounds) == result.rounds_used


def test_combined_data_source_scenario_can_run_end_to_end(tmp_path: Path) -> None:
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

    output_path = tmp_path / "combined_occitanie.yaml"

    save_scenario_yaml(
        scenario=scenario,
        output_path=output_path,
    )

    reloaded_scenario = load_scenario_config(output_path)
    proposal = minimum_first_allocation(reloaded_scenario)
    result = evaluate_proposal(reloaded_scenario, proposal)

    assert reloaded_scenario.scenario_name == "occitanie_extreme_combined_sample"
    assert result.water_budget_valid is True
    assert result.total_allocated <= result.available_water + 1e-9
