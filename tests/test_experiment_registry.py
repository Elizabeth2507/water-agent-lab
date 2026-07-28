from pathlib import Path

from water_agent_lab.experiment_registry import (
    append_experiment_record,
    find_experiment_record,
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


def test_find_experiment_record_returns_matching_record(tmp_path: Path) -> None:
    registry_path = tmp_path / "experiment_registry.jsonl"

    append_experiment_record(
        record={
            "run_id": "first-run",
            "created_at_utc": "2026-01-01T00:00:00+00:00",
            "command": "run-all",
            "status": "completed",
            "outputs": {
                "results": "outputs/results.csv",
            },
        },
        registry_path=registry_path,
    )

    append_experiment_record(
        record={
            "run_id": "second-run",
            "created_at_utc": "2026-01-01T01:00:00+00:00",
            "command": "negotiate-multi",
            "status": "completed",
            "outputs": {
                "negotiation_history": "outputs/negotiation_history.json",
            },
        },
        registry_path=registry_path,
    )

    record = find_experiment_record(
        run_id="second-run",
        registry_path=registry_path,
    )

    assert record is not None
    assert record["run_id"] == "second-run"
    assert record["command"] == "negotiate-multi"


def test_find_experiment_record_returns_none_for_missing_run_id(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "experiment_registry.jsonl"

    append_experiment_record(
        record={
            "run_id": "existing-run",
            "created_at_utc": "2026-01-01T00:00:00+00:00",
            "command": "run-all",
            "status": "completed",
            "outputs": {},
        },
        registry_path=registry_path,
    )

    record = find_experiment_record(
        run_id="missing-run",
        registry_path=registry_path,
    )

    assert record is None
