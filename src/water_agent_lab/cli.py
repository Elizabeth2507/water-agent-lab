import json
from pathlib import Path

import typer
from rich.console import Console

from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.simulator import proportional_allocation

app = typer.Typer(
    help="WaterAgentLab command-line interface.",
    no_args_is_help=True,
)
console = Console()


@app.command("simulate")
def simulate(
    config: Path = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to the drought scenario YAML config.",
    ),
) -> None:
    """
    Run the proportional water-allocation baseline on a drought scenario.
    """
    scenario = load_scenario_config(config)
    proposal = proportional_allocation(scenario)
    result = evaluate_proposal(scenario, proposal)

    console.print_json(json.dumps(result.model_dump(), indent=2))


@app.command("version")
def version() -> None:
    """
    Show the WaterAgentLab version.
    """
    console.print("WaterAgentLab 0.1.0")


if __name__ == "__main__":
    app()