from pathlib import Path

from water_agent_lab.experiment_registry import (
    append_experiment_record,
    find_experiment_record,
    load_experiment_registry,
    verify_experiment_record_configs,
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


def test_verify_experiment_record_configs_matches_current_file(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "scenario.yaml"
    config_path.write_text("available_water: 100\n", encoding="utf-8")

    from water_agent_lab.hashing import compute_file_sha256

    config_hash = compute_file_sha256(config_path)

    record = {
        "run_id": "test-run-id",
        "command": "negotiate-multi",
        "config_path": str(config_path),
        "config_hash": config_hash,
    }

    results = verify_experiment_record_configs(record)

    assert len(results) == 1
    assert results[0]["config_path"] == str(config_path)
    assert results[0]["status"] == "checked"
    assert results[0]["matches"] is True


def test_verify_experiment_record_configs_detects_changed_file(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "scenario.yaml"
    config_path.write_text("available_water: 100\n", encoding="utf-8")

    from water_agent_lab.hashing import compute_file_sha256

    original_hash = compute_file_sha256(config_path)

    config_path.write_text("available_water: 80\n", encoding="utf-8")

    record = {
        "run_id": "test-run-id",
        "command": "negotiate-multi",
        "config_path": str(config_path),
        "config_hash": original_hash,
    }

    results = verify_experiment_record_configs(record)

    assert len(results) == 1
    assert results[0]["status"] == "checked"
    assert results[0]["matches"] is False
    assert results[0]["expected_hash"] != results[0]["current_hash"]


def test_verify_experiment_record_configs_detects_missing_file(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "missing.yaml"

    record = {
        "run_id": "test-run-id",
        "command": "negotiate-multi",
        "config_path": str(config_path),
        "config_hash": "expected-hash",
    }

    results = verify_experiment_record_configs(record)

    assert len(results) == 1
    assert results[0]["status"] == "missing"
    assert results[0]["matches"] is False
    assert results[0]["current_hash"] is None
