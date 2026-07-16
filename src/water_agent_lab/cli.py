import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.models import SimulationResult
from water_agent_lab.simulator import (
    priority_weighted_allocation,
    proportional_allocation,
)

app = typer.Typer(
    help="WaterAgentLab command-line interface.",
    no_args_is_help=True,
)
console = Console()


def run_strategy(strategy: str, config_path: Path) -> SimulationResult:
    """
    Run one allocation strategy and return the evaluated result.
    """
    scenario = load_scenario_config(config_path)

    if strategy == "proportional":
        proposal = proportional_allocation(scenario)
    elif strategy == "priority":
        proposal = priority_weighted_allocation(scenario)
    else:
        raise typer.BadParameter(
            "Unknown strategy. Choose either 'proportional' or 'priority'."
        )

    return evaluate_proposal(scenario, proposal)


@app.command("simulate")
def simulate(
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help="Path to the drought scenario YAML config.",
        ),
    ],
    strategy: Annotated[
        str,
        typer.Option(
            "--strategy",
            "-s",
            help="Allocation strategy to use: proportional or priority.",
        ),
    ] = "proportional",
) -> None:
    """
    Run a water-allocation simulation on a drought scenario.
    """
    result = run_strategy(strategy=strategy, config_path=config)

    output = {
        "strategy": strategy,
        **result.model_dump(),
    }

    console.print_json(json.dumps(output, indent=2))


@app.command("compare")
def compare(
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help="Path to the drought scenario YAML config.",
        ),
    ],
) -> None:
    """
    Compare available water-allocation strategies on one scenario.
    """
    strategies = ["proportional", "priority"]
    results = {
        strategy: run_strategy(strategy=strategy, config_path=config)
        for strategy in strategies
    }

    table = Table(title="Water Allocation Strategy Comparison")

    table.add_column("Strategy")
    table.add_column("Total allocated")
    table.add_column("Budget valid")
    table.add_column("Fairness score")
    table.add_column("Conflict score")
    table.add_column("Agreement reached")

    for strategy, result in results.items():
        table.add_row(
            strategy,
            f"{result.total_allocated:.2f}",
            str(result.water_budget_valid),
            f"{result.fairness_score:.3f}",
            f"{result.conflict_score:.3f}",
            str(result.agreement_reached),
        )

    console.print(table)


@app.command("version")
def version() -> None:
    """
    Show the WaterAgentLab version.
    """
    console.print("WaterAgentLab 0.1.0")


if __name__ == "__main__":
    app()
