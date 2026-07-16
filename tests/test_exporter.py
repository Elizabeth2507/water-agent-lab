import json
from pathlib import Path

from water_agent_lab.exporter import save_results_csv, save_results_json


def test_save_results_csv(tmp_path: Path) -> None:
    output_path = tmp_path / "results.csv"

    results = [
        {
            "scenario_name": "mild_drought",
            "strategy": "proportional",
            "fairness_score": 0.9,
            "conflict_score": 0.0,
        }
    ]

    save_results_csv(results, output_path)

    content = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert "scenario_name" in content
    assert "mild_drought" in content
    assert "proportional" in content


def test_save_results_json(tmp_path: Path) -> None:
    output_path = tmp_path / "results.json"

    results = [
        {
            "scenario_name": "mild_drought",
            "strategy": "proportional",
            "fairness_score": 0.9,
            "conflict_score": 0.0,
        }
    ]

    save_results_json(results, output_path)

    content = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path.exists()
    assert content[0]["scenario_name"] == "mild_drought"
    assert content[0]["strategy"] == "proportional"
