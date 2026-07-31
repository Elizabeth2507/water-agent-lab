import random
from pathlib import Path
from typing import Any

from water_agent_lab.config import load_scenario_config
from water_agent_lab.llm_negotiation import run_mock_llm_multi_round_negotiation
from water_agent_lab.negotiation import run_multi_round_negotiation
from water_agent_lab.scenario_exporter import save_scenario_yaml
from water_agent_lab.scenario_variation import vary_available_water


def summarize_rule_based_negotiation(
    run_index: int,
    transcript,
) -> dict[str, Any]:
    """
    Convert one rule-based negotiation result into a flat row.
    """
    final_round = transcript.rounds[-1]
    final_result = final_round.result

    return {
        "run_index": run_index,
        "mode": "rule_based",
        "scenario_name": transcript.scenario_name,
        "available_water": final_result.available_water,
        "initial_strategy": transcript.initial_strategy,
        "agreement_reached": transcript.agreement_reached,
        "rounds_used": transcript.rounds_used,
        "final_strategy": final_round.strategy,
        "final_conflict_score": final_result.conflict_score,
        "final_fairness_score": final_result.fairness_score,
        "final_minimum_satisfaction_score": final_result.minimum_satisfaction_score,
        "final_shortage_score": final_result.shortage_score,
        "final_mediator_action": "not_applicable",
    }


def summarize_mock_llm_negotiation(
    run_index: int,
    transcript,
) -> dict[str, Any]:
    """
    Convert one mock LLM negotiation transcript into a flat row.
    """
    final_round = transcript.rounds[-1]
    final_result = final_round.result
    final_recommendation = final_round.mediator_recommendation

    return {
        "run_index": run_index,
        "mode": "mock_llm",
        "scenario_name": transcript.scenario_name,
        "available_water": final_result.available_water,
        "initial_strategy": transcript.initial_strategy,
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


def run_negotiation_mode_comparison(
    config_path: str | Path,
    initial_strategy: str,
    runs: int,
    seed: int,
    work_dir: str | Path,
    variation_fraction: float = 0.15,
) -> list[dict[str, Any]]:
    """
    Compare rule-based and mock LLM-style negotiation over shared scenario variants.
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

        varied_config_path = work_path / f"comparison_variant_{run_index}.yaml"

        save_scenario_yaml(
            scenario=varied_scenario,
            output_path=varied_config_path,
        )

        rule_based_result = run_multi_round_negotiation(
            config_path=str(varied_config_path),
            initial_strategy=initial_strategy,
        )

        mock_llm_result = run_mock_llm_multi_round_negotiation(
            config_path=str(varied_config_path),
            initial_strategy=initial_strategy,
        )

        rows.append(
            summarize_rule_based_negotiation(
                run_index=run_index,
                transcript=rule_based_result,
            )
        )
        rows.append(
            summarize_mock_llm_negotiation(
                run_index=run_index,
                transcript=mock_llm_result,
            )
        )

    return rows
