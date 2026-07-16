import csv
import json
from pathlib import Path
from typing import Any


def save_results_csv(results: list[dict[str, Any]], output_path: str | Path) -> None:
    """
    Save simulation results to a CSV file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not results:
        raise ValueError("Cannot save empty results.")

    fieldnames = list(results[0].keys())

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def save_results_json(results: list[dict[str, Any]], output_path: str | Path) -> None:
    """
    Save simulation results to a JSON file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)
