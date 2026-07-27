import json
from pathlib import Path
from typing import Any


def load_negotiation_history(input_path: str | Path) -> dict[str, Any]:
    """
    Load a saved negotiation history JSON file.
    """
    path = Path(input_path)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def summarize_negotiation_history(history: dict[str, Any]) -> dict[str, Any]:
    """
    Create a compact summary from a full negotiation history.
    """
    rounds = history["rounds"]
    final_round = rounds[-1]

    strategy_sequence = [round_data["strategy"] for round_data in rounds]

    rejected_by_round = {
        round_data["round_number"]: round_data["rejected_stakeholders"]
        for round_data in rounds
    }

    final_result = final_round["result"]

    return {
        "scenario_name": history["scenario_name"],
        "initial_strategy": history["initial_strategy"],
        "agreement_reached": history["agreement_reached"],
        "rounds_used": history["rounds_used"],
        "max_rounds": history["max_rounds"],
        "strategy_sequence": strategy_sequence,
        "rejected_by_round": rejected_by_round,
        "final_strategy": final_round["strategy"],
        "final_conflict_score": final_result["conflict_score"],
        "final_minimum_satisfaction_score": final_result["minimum_satisfaction_score"],
        "final_fairness_score": final_result["fairness_score"],
    }
