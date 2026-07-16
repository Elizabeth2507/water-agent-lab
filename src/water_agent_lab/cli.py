import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from water_agent_lab.exporter import save_results_csv, save_results_json
from water_agent_lab.plotter import plot_fairness_conflict
from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.models import AllocationProposal, ScenarioConfig, SimulationResult
from water_agent_lab.simulator import (
    priority_weighted_allocation,
    proportional_allocation,
)

app = typer.Typer(
    help="WaterAgentLab command-line interface.",
    no_args_is_help=True,
)
console = Console(width=120)


def create_proposal(strategy: str, scenario: ScenarioConfig) -> AllocationProposal:
    """
    Create an allocation proposal for one strategy.
    """
    if strategy == "proportional":
        return proportional_allocation(scenario)

    if strategy == "priority":
        return priority_weighted_allocation(scenario)

    raise typer.BadParameter(
        "Unknown strategy. Choose either 'proportional' or 'priority'."
    )


def run_strategy(strategy: str, config_path: Path) -> SimulationResult:
    """
    Run one allocation strategy and return the evaluated result.
    """
    scenario = load_scenario_config(config_path)
    proposal = create_proposal(strategy=strategy, scenario=scenario)

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


@app.command("run-all")
def run_all(
    config_dir: Annotated[
        Path,
        typer.Option(
            "--config-dir",
            "-d",
            help="Directory containing drought scenario YAML files.",
        ),
    ] = Path("configs"),
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Optional path to save results as .csv or .json.",
        ),
    ] = None,
) -> None:
    """
    Run all scenario configs with all available allocation strategies.
    """
    config_paths = sorted(config_dir.glob("*.yaml"))

    if not config_paths:
        raise typer.BadParameter(f"No YAML config files found in: {config_dir}")

    strategies = ["proportional", "priority"]
    rows = []

    table = Table(title="All Scenario Strategy Comparison")

    table.add_column("Scenario")
    table.add_column("Drought level")
    table.add_column("Available water")
    table.add_column("Strategy")
    table.add_column("Fairness score")
    table.add_column("Conflict score")
    table.add_column("Agreement reached")

    for config_path in config_paths:
        scenario = load_scenario_config(config_path)

        for strategy in strategies:
            proposal = create_proposal(strategy=strategy, scenario=scenario)
            result = evaluate_proposal(scenario, proposal)

            row = {
                "scenario_name": result.scenario_name,
                "drought_level": result.drought_level,
                "available_water": result.available_water,
                "strategy": strategy,
                "total_requested": result.total_requested,
                "total_allocated": result.total_allocated,
                "water_budget_valid": result.water_budget_valid,
                "fairness_score": result.fairness_score,
                "conflict_score": result.conflict_score,
                "agreement_reached": result.agreement_reached,
            }
            rows.append(row)

            table.add_row(
                result.scenario_name,
                result.drought_level,
                f"{result.available_water:.2f}",
                strategy,
                f"{result.fairness_score:.3f}",
                f"{result.conflict_score:.3f}",
                str(result.agreement_reached),
            )

    console.print(table)

    if output is not None:
        if output.suffix == ".csv":
            save_results_csv(rows, output)
        elif output.suffix == ".json":
            save_results_json(rows, output)
        else:
            raise typer.BadParameter("Output file must end with .csv or .json.")

        console.print(f"[green]Saved results to {output}[/green]")


@app.command("validate-config")
def validate_config(
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
    Validate a drought scenario configuration file.
    """
    scenario = load_scenario_config(config)

    console.print("[green]Config is valid.[/green]")
    console.print(f"Scenario: {scenario.scenario_name}")
    console.print(f"Country: {scenario.country}")
    console.print(f"Region: {scenario.region}")
    console.print(f"Stakeholders: {len(scenario.stakeholders)}")


@app.command("plot-results")
def plot_results(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to exported CSV results.",
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the output PNG plot.",
        ),
    ] = Path("outputs/fairness_conflict.png"),
) -> None:
    """
    Plot fairness and conflict scores from exported simulation results.
    """
    plot_fairness_conflict(input_path=input_path, output_path=output)

    console.print(f"[green]Saved plot to {output}[/green]")


@app.command("version")
def version() -> None:
    """
    Show the WaterAgentLab version.
    """
    console.print("WaterAgentLab 0.1.0")


if __name__ == "__main__":
    app()
