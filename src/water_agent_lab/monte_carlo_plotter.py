from pathlib import Path

import matplotlib.pyplot as plt

from water_agent_lab.monte_carlo_reporting import load_monte_carlo_results


def plot_final_conflict_distribution(
    input_path: str | Path,
    output_path: str | Path,
) -> None:
    """
    Plot histogram of final conflict scores.
    """
    dataframe = load_monte_carlo_results(input_path)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure()
    plt.hist(dataframe["final_conflict_score"], bins=10)
    plt.xlabel("Final conflict score")
    plt.ylabel("Number of runs")
    plt.title("Monte Carlo final conflict distribution")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def plot_rounds_used_distribution(
    input_path: str | Path,
    output_path: str | Path,
) -> None:
    """
    Plot histogram of rounds used.
    """
    dataframe = load_monte_carlo_results(input_path)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure()
    plt.hist(
        dataframe["rounds_used"], bins=range(1, int(dataframe["rounds_used"].max()) + 3)
    )
    plt.xlabel("Rounds used")
    plt.ylabel("Number of runs")
    plt.title("Monte Carlo negotiation rounds distribution")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
