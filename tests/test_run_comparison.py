import json
from pathlib import Path

from water_agent_lab.run_comparison import (
    compare_output_files,
    normalize_run_metadata,
)


def test_normalize_run_metadata_removes_run_specific_fields() -> None:
    data = {
        "run_id": "abc",
        "created_at_utc": "2026-01-01T00:00:00+00:00",
        "scenario_name": "mild_drought",
        "run_metadata": {
            "run_id": "nested",
            "command": "simulate",
        },
    }

    normalized = normalize_run_metadata(data)

    assert "run_id" not in normalized
    assert "created_at_utc" not in normalized
    assert "run_metadata" not in normalized
    assert normalized["scenario_name"] == "mild_drought"


def test_compare_json_outputs_match_after_metadata_removed(tmp_path: Path) -> None:
    original_path = tmp_path / "original.json"
    reproduced_path = tmp_path / "reproduced.json"

    original_path.write_text(
        json.dumps(
            {
                "run_metadata": {
                    "run_id": "old",
                    "created_at_utc": "2026-01-01T00:00:00+00:00",
                    "command": "negotiate-multi",
                },
                "scenario_name": "moderate_drought_mvp",
                "agreement_reached": True,
            }
        ),
        encoding="utf-8",
    )

    reproduced_path.write_text(
        json.dumps(
            {
                "run_metadata": {
                    "run_id": "new",
                    "created_at_utc": "2026-01-02T00:00:00+00:00",
                    "command": "reproduce-negotiate-multi",
                },
                "scenario_name": "moderate_drought_mvp",
                "agreement_reached": True,
            }
        ),
        encoding="utf-8",
    )

    result = compare_output_files(original_path, reproduced_path)

    assert result["matches"] is True


def test_compare_csv_outputs_match_after_metadata_removed(tmp_path: Path) -> None:
    original_path = tmp_path / "original.csv"
    reproduced_path = tmp_path / "reproduced.csv"

    original_path.write_text(
        (
            "run_id,created_at_utc,command,scenario_name,strategy,fairness_score\n"
            "old,2026-01-01T00:00:00+00:00,run-all,mild_drought,proportional,0.9\n"
        ),
        encoding="utf-8",
    )

    reproduced_path.write_text(
        (
            "run_id,created_at_utc,command,scenario_name,strategy,fairness_score\n"
            "new,2026-01-02T00:00:00+00:00,reproduce-run-all,mild_drought,proportional,0.9\n"
        ),
        encoding="utf-8",
    )

    result = compare_output_files(original_path, reproduced_path)

    assert result["matches"] is True


def test_compare_outputs_detects_difference(tmp_path: Path) -> None:
    original_path = tmp_path / "original.json"
    reproduced_path = tmp_path / "reproduced.json"

    original_path.write_text(
        json.dumps({"scenario_name": "mild_drought", "fairness_score": 0.9}),
        encoding="utf-8",
    )

    reproduced_path.write_text(
        json.dumps({"scenario_name": "mild_drought", "fairness_score": 0.8}),
        encoding="utf-8",
    )

    result = compare_output_files(original_path, reproduced_path)

    assert result["matches"] is False
