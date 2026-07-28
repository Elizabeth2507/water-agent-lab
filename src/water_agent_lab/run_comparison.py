import csv
import json
from pathlib import Path
from typing import Any


def load_json_file(path: str | Path) -> Any:
    """
    Load a JSON file.
    """
    file_path = Path(path)

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_csv_file(path: str | Path) -> list[dict[str, str]]:
    """
    Load a CSV file as a list of dictionaries.
    """
    file_path = Path(path)

    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def normalize_run_metadata(data: Any) -> Any:
    """
    Remove run-specific metadata before comparing outputs.

    Reproduced runs will naturally have different run_id and timestamp values.
    """
    if isinstance(data, dict):
        return {
            key: normalize_run_metadata(value)
            for key, value in data.items()
            if key not in {"run_id", "created_at_utc", "run_metadata", "command"}
        }

    if isinstance(data, list):
        return [normalize_run_metadata(item) for item in data]

    return data


def compare_output_files(
    original_path: str | Path,
    reproduced_path: str | Path,
) -> dict[str, Any]:
    """
    Compare two output files after removing run-specific metadata.
    """
    original = Path(original_path)
    reproduced = Path(reproduced_path)

    if original.suffix != reproduced.suffix:
        return {
            "matches": False,
            "reason": "Output file types differ.",
            "original_path": str(original),
            "reproduced_path": str(reproduced),
        }

    if original.suffix == ".json":
        original_data = load_json_file(original)
        reproduced_data = load_json_file(reproduced)
    elif original.suffix == ".csv":
        original_data = load_csv_file(original)
        reproduced_data = load_csv_file(reproduced)
    else:
        return {
            "matches": False,
            "reason": f"Unsupported output file type: {original.suffix}",
            "original_path": str(original),
            "reproduced_path": str(reproduced),
        }

    normalized_original = normalize_run_metadata(original_data)
    normalized_reproduced = normalize_run_metadata(reproduced_data)

    return {
        "matches": normalized_original == normalized_reproduced,
        "reason": (
            "Outputs match after removing run metadata."
            if normalized_original == normalized_reproduced
            else "Outputs differ after removing run metadata."
        ),
        "original_path": str(original),
        "reproduced_path": str(reproduced),
    }
