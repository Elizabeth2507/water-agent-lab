import json
from pathlib import Path

from water_agent_lab.negotiation import (
    run_multi_round_negotiation,
    save_negotiation_history_json,
)
from water_agent_lab.negotiation_summary import (
    load_negotiation_history,
    summarize_negotiation_history,
)


def test_load_negotiation_history(tmp_path: Path) -> None:
    output_path = tmp_path / "negotiation_history.json"

    result = run_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )
    save_negotiation_history_json(result=result, output_path=output_path)

    history = load_negotiation_history(output_path)

    assert history["scenario_name"] == "moderate_drought_mvp"
    assert history["initial_strategy"] == "proportional"


def test_summarize_negotiation_history(tmp_path: Path) -> None:
    output_path = tmp_path / "negotiation_history.json"

    result = run_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )
    save_negotiation_history_json(result=result, output_path=output_path)

    history = json.loads(output_path.read_text(encoding="utf-8"))
    summary = summarize_negotiation_history(history)

    assert summary["scenario_name"] == "moderate_drought_mvp"
    assert summary["initial_strategy"] == "proportional"
    assert summary["final_strategy"] == "minimum-first"
    assert summary["agreement_reached"] is True
    assert summary["rounds_used"] == 2
    assert summary["strategy_sequence"] == ["proportional", "minimum-first"]
    assert summary["final_conflict_score"] == 0.0
    assert summary["final_minimum_satisfaction_score"] == 1.0
