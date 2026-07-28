import json
from pathlib import Path
from typing import Any
from water_agent_lab.hashing import compute_file_sha256


DEFAULT_REGISTRY_PATH = Path("outputs/experiment_registry.jsonl")


def append_experiment_record(
    record: dict[str, Any],
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> None:
    """
    Append one experiment record to a JSONL registry file.
    """
    path = Path(registry_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_experiment_registry(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> list[dict[str, Any]]:
    """
    Load all records from the experiment registry.
    """
    path = Path(registry_path)

    if not path.exists():
        return []

    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            records.append(json.loads(line))

    return records


def find_experiment_record(
    run_id: str,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any] | None:
    """
    Find one experiment record by run ID.

    Returns None if the run ID is not found.
    """
    records = load_experiment_registry(registry_path=registry_path)

    for record in records:
        if record.get("run_id") == run_id:
            return record

    return None


def verify_experiment_record_configs(
    record: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Verify whether the current config files still match the hashes
    recorded in an experiment registry record.
    """
    verification_results = []

    if "config_hash" in record and "config_path" in record:
        config_path = Path(record["config_path"])
        expected_hash = record["config_hash"]

        if not config_path.exists():
            verification_results.append(
                {
                    "config_path": str(config_path),
                    "status": "missing",
                    "expected_hash": expected_hash,
                    "current_hash": None,
                    "matches": False,
                }
            )
            return verification_results

        current_hash = compute_file_sha256(config_path)

        verification_results.append(
            {
                "config_path": str(config_path),
                "status": "checked",
                "expected_hash": expected_hash,
                "current_hash": current_hash,
                "matches": current_hash == expected_hash,
            }
        )

        return verification_results

    if "config_hashes" in record:
        for config_path_text, expected_hash in record["config_hashes"].items():
            config_path = Path(config_path_text)

            if not config_path.exists():
                verification_results.append(
                    {
                        "config_path": str(config_path),
                        "status": "missing",
                        "expected_hash": expected_hash,
                        "current_hash": None,
                        "matches": False,
                    }
                )
                continue

            current_hash = compute_file_sha256(config_path)

            verification_results.append(
                {
                    "config_path": str(config_path),
                    "status": "checked",
                    "expected_hash": expected_hash,
                    "current_hash": current_hash,
                    "matches": current_hash == expected_hash,
                }
            )

    return verification_results
