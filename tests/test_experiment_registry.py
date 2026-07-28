from pathlib import Path

from water_agent_lab.experiment_registry import (
    append_experiment_record,
    load_experiment_registry,
)


def test_append_and_load_experiment_record(tmp_path: Path) -> None:
    registry_path = tmp_path / "experiment_registry.jsonl"

    record = {
        "run_id": "test-run-id",
        "created_at_utc": "2026-01-01T00:00:00+00:00",
        "command": "run-all",
        "status": "completed",
        "outputs": {
            "results": "outputs/results.csv",
        },
    }

    append_experiment_record(
        record=record,
        registry_path=registry_path,
    )

    records = load_experiment_registry(registry_path)

    assert len(records) == 1
    assert records[0]["run_id"] == "test-run-id"
    assert records[0]["command"] == "run-all"
    assert records[0]["status"] == "completed"
    assert records[0]["outputs"]["results"] == "outputs/results.csv"


def test_load_missing_experiment_registry_returns_empty_list(tmp_path: Path) -> None:
    registry_path = tmp_path / "missing_registry.jsonl"

    records = load_experiment_registry(registry_path)

    assert records == []
