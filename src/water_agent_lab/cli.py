import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.simulator import (
    priority_weighted_allocation,
    proportional_allocation,
)

app = typer.Typer(
    help="WaterAgentLab command-line interface.",
    no_args_is_help=True,
)
console = Console()


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
    scenario = load_scenario_config(config)

    if strategy == "proportional":
        proposal = proportional_allocation(scenario)
    elif strategy == "priority":
        proposal = priority_weighted_allocation(scenario)
    else:
        raise typer.BadParameter(
            "Unknown strategy. Choose either 'proportional' or 'priority'."
        )

    result = evaluate_proposal(scenario, proposal)

    output = {
        "strategy": strategy,
        **result.model_dump(),
    }

    console.print_json(json.dumps(output, indent=2))


@app.command("version")
def version() -> None:
    """
    Show the WaterAgentLab version.
    """
    console.print("WaterAgentLab 0.1.0")


if __name__ == "__main__":
    app()
