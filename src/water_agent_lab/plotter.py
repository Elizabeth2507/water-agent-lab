from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_fairness_conflict(input_path: str | Path, output_path: str | Path) -> None:
    """
    Plot fairness and conflict scores from exported simulation results.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(input_file)

    required_columns = {
        "scenario_name",
        "strategy",
        "fairness_score",
        "conflict_score",
    }

    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    data["label"] = data["scenario_name"] + " / " + data["strategy"]

    x_positions = range(len(data))
    bar_width = 0.4

    plt.figure(figsize=(12, 6))

    plt.bar(
        [position - bar_width / 2 for position in x_positions],
        data["fairness_score"],
        width=bar_width,
        label="Fairness score",
    )

    plt.bar(
        [position + bar_width / 2 for position in x_positions],
        data["conflict_score"],
        width=bar_width,
        label="Conflict score",
    )

    plt.xticks(x_positions, data["label"], rotation=45, ha="right")
    plt.ylim(0, 1)
    plt.ylabel("Score")
    plt.title("Fairness and Conflict Across Drought Scenarios")
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_file)
    plt.close()
