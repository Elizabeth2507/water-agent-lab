import json
from pathlib import Path
from typing import Any


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
