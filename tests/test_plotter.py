from pathlib import Path

import pandas as pd

from water_agent_lab.plotter import plot_fairness_conflict


def test_plot_fairness_conflict(tmp_path: Path) -> None:
    input_path = tmp_path / "results.csv"
    output_path = tmp_path / "plot.png"

    data = pd.DataFrame(
        [
            {
                "scenario_name": "mild_drought",
                "strategy": "proportional",
                "fairness_score": 0.9,
                "conflict_score": 0.0,
            },
            {
                "scenario_name": "severe_drought",
                "strategy": "priority",
                "fairness_score": 0.6,
                "conflict_score": 0.5,
            },
        ]
    )

    data.to_csv(input_path, index=False)

    plot_fairness_conflict(input_path=input_path, output_path=output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
