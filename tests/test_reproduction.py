from pathlib import Path

import pytest

from water_agent_lab.hashing import compute_file_sha256
from water_agent_lab.reproduction import (
    ensure_record_is_reproducible,
    get_reproduced_output_path,
)


def test_ensure_record_is_reproducible_passes_for_matching_hash(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "scenario.yaml"
    config_path.write_text("available_water: 100\n", encoding="utf-8")

    record = {
        "config_path": str(config_path),
        "config_hash": compute_file_sha256(config_path),
    }

    ensure_record_is_reproducible(record)


def test_ensure_record_is_reproducible_fails_for_changed_hash(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "scenario.yaml"
    config_path.write_text("available_water: 100\n", encoding="utf-8")

    old_hash = compute_file_sha256(config_path)

    config_path.write_text("available_water: 80\n", encoding="utf-8")

    record = {
        "config_path": str(config_path),
        "config_hash": old_hash,
    }

    with pytest.raises(ValueError):
        ensure_record_is_reproducible(record)


def test_get_reproduced_output_path() -> None:
    output_path = get_reproduced_output_path(
        original_output_path="outputs/results.csv",
        new_run_id="abc123",
    )

    assert output_path == Path("outputs/reproduced_abc123_results.csv")
