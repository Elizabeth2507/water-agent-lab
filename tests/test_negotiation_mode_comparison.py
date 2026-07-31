from pathlib import Path

import pytest

from water_agent_lab.negotiation_mode_comparison import (
    run_negotiation_mode_comparison,
)


def test_run_negotiation_mode_comparison(tmp_path: Path) -> None:
    rows = run_negotiation_mode_comparison(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=42,
        work_dir=tmp_path,
        variation_fraction=0.10,
    )

    assert len(rows) == 6

    modes = {row["mode"] for row in rows}

    assert modes == {"rule_based", "mock_llm"}

    first_row = rows[0]

    assert "run_index" in first_row
    assert "agreement_reached" in first_row
    assert "final_conflict_score" in first_row
    assert "final_fairness_score" in first_row


def test_negotiation_mode_comparison_has_two_rows_per_run(tmp_path: Path) -> None:
    rows = run_negotiation_mode_comparison(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=4,
        seed=42,
        work_dir=tmp_path,
    )

    run_indices = {row["run_index"] for row in rows}

    assert run_indices == {1, 2, 3, 4}

    for run_index in run_indices:
        run_rows = [row for row in rows if row["run_index"] == run_index]
        assert len(run_rows) == 2
        assert {row["mode"] for row in run_rows} == {"rule_based", "mock_llm"}


def test_negotiation_mode_comparison_is_reproducible(tmp_path: Path) -> None:
    first_rows = run_negotiation_mode_comparison(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=123,
        work_dir=tmp_path / "first",
    )

    second_rows = run_negotiation_mode_comparison(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=123,
        work_dir=tmp_path / "second",
    )

    assert first_rows == second_rows


def test_negotiation_mode_comparison_rejects_invalid_runs(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="runs must be greater than 0"):
        run_negotiation_mode_comparison(
            config_path="configs/drought_mvp.yaml",
            initial_strategy="proportional",
            runs=0,
            seed=42,
            work_dir=tmp_path,
        )
