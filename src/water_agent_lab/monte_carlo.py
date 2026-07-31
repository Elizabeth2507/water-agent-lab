import random
from pathlib import Path
from typing import Any

from water_agent_lab.config import load_scenario_config
from water_agent_lab.llm_negotiation import run_mock_llm_multi_round_negotiation
from water_agent_lab.scenario_exporter import save_scenario_yaml
from water_agent_lab.scenario_variation import vary_available_water


def summarize_mock_negotiation_run(
    run_index: int,
    initial_strategy: str,
    transcript,
) -> dict[str, Any]:
    """
    Convert one mock LLM negotiation transcript into a flat result row.
    """
    final_round = transcript.rounds[-1]
    final_result = final_round.result
    final_recommendation = final_round.mediator_recommendation

    return {
        "run_index": run_index,
        "scenario_name": transcript.scenario_name,
        "country": transcript.country,
        "region": transcript.region,
        "drought_level": transcript.drought_level,
        "available_water": final_result.available_water,
        "initial_strategy": initial_strategy,
        "agreement_reached": transcript.agreement_reached,
        "rounds_used": transcript.rounds_used,
        "final_strategy": final_round.strategy,
        "final_conflict_score": final_result.conflict_score,
        "final_fairness_score": final_result.fairness_score,
        "final_minimum_satisfaction_score": final_result.minimum_satisfaction_score,
        "final_shortage_score": final_result.shortage_score,
        "final_mediator_action": (
            final_recommendation.action if final_recommendation is not None else "none"
        ),
    }


def run_mock_llm_monte_carlo(
    config_path: str | Path,
    initial_strategy: str,
    runs: int,
    seed: int,
    work_dir: str | Path,
    variation_fraction: float = 0.15,
) -> list[dict[str, Any]]:
    """
    Run repeated mock LLM negotiations over scenario variations.
    """
    if runs <= 0:
        raise ValueError("runs must be greater than 0")

    if variation_fraction < 0:
        raise ValueError("variation_fraction must be non-negative")

    base_scenario = load_scenario_config(config_path)
    rng = random.Random(seed)

    work_path = Path(work_dir)
    work_path.mkdir(parents=True, exist_ok=True)

    rows = []

    for run_index in range(1, runs + 1):
        varied_scenario = vary_available_water(
            scenario=base_scenario,
            rng=rng,
            variation_fraction=variation_fraction,
        )

        varied_config_path = work_path / f"scenario_variant_{run_index}.yaml"

        save_scenario_yaml(
            scenario=varied_scenario,
            output_path=varied_config_path,
        )

        transcript = run_mock_llm_multi_round_negotiation(
            config_path=varied_config_path,
            initial_strategy=initial_strategy,
        )

        rows.append(
            summarize_mock_negotiation_run(
                run_index=run_index,
                initial_strategy=initial_strategy,
                transcript=transcript,
            )
        )

    return rows
