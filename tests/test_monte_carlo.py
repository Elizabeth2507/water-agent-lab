from pathlib import Path

import pytest

from water_agent_lab.monte_carlo import run_mock_llm_monte_carlo


def test_run_mock_llm_monte_carlo(tmp_path: Path) -> None:
    rows = run_mock_llm_monte_carlo(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=42,
        work_dir=tmp_path,
        variation_fraction=0.10,
    )

    assert len(rows) == 3

    first_row = rows[0]

    assert first_row["run_index"] == 1
    assert first_row["initial_strategy"] == "proportional"
    assert "agreement_reached" in first_row
    assert "final_conflict_score" in first_row
    assert "final_mediator_action" in first_row


def test_run_mock_llm_monte_carlo_is_reproducible(tmp_path: Path) -> None:
    first_rows = run_mock_llm_monte_carlo(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=123,
        work_dir=tmp_path / "first",
    )

    second_rows = run_mock_llm_monte_carlo(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
        runs=3,
        seed=123,
        work_dir=tmp_path / "second",
    )

    assert first_rows == second_rows


def test_run_mock_llm_monte_carlo_rejects_invalid_runs(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="runs must be greater than 0"):
        run_mock_llm_monte_carlo(
            config_path="configs/drought_mvp.yaml",
            initial_strategy="proportional",
            runs=0,
            seed=42,
            work_dir=tmp_path,
        )
