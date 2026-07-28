from pathlib import Path
from typing import Any

from water_agent_lab.experiment_registry import verify_experiment_record_configs


def ensure_record_is_reproducible(record: dict[str, Any]) -> None:
    """
    Raise an error if the recorded config files do not match current files.
    """
    verification_results = verify_experiment_record_configs(record)

    if not verification_results:
        raise ValueError("No config hashes found for this run.")

    mismatches = [result for result in verification_results if not result["matches"]]

    if mismatches:
        raise ValueError(
            "Cannot reproduce run because one or more config files "
            "do not match recorded hashes."
        )


def get_reproduced_output_path(
    original_output_path: str | Path,
    new_run_id: str,
) -> Path:
    """
    Create a reproduced output path based on an original output path.
    """
    path = Path(original_output_path)

    return path.with_name(f"reproduced_{new_run_id}_{path.name}")
