import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from water_agent_lab.scenario_ordering import drought_level_sort_key
from water_agent_lab.exporter import save_results_csv, save_results_json
from water_agent_lab.plotter import plot_fairness_conflict
from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.models import AllocationProposal, ScenarioConfig, SimulationResult
from water_agent_lab.reporting import generate_experiment_report

# from water_agent_lab.simulator import (
#     minimum_first_allocation,
#     minimum_priority_allocation,
#     priority_weighted_allocation,
#     proportional_allocation,
# )
from water_agent_lab.strategies import get_strategy, get_strategy_names
from water_agent_lab.agents import evaluate_stakeholder_responses
from water_agent_lab.negotiation import (
    run_multi_round_negotiation,
    run_simple_negotiation,
    save_negotiation_history_json,
)
from water_agent_lab.negotiation_summary import (
    load_negotiation_history,
    summarize_negotiation_history,
)
from water_agent_lab.logging_utils import configure_logging, log_event


app = typer.Typer(
    help="WaterAgentLab command-line interface.",
    no_args_is_help=True,
)
console = Console(width=120)


def create_proposal(strategy: str, scenario: ScenarioConfig) -> AllocationProposal:
    """
    Create an allocation proposal for one strategy.
    """
    try:
        strategy_function = get_strategy(strategy)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    return strategy_function(scenario)


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
            help="Allocation strategy to use.",
        ),
    ] = "proportional",
    log_file: Annotated[
        Path | None,
        typer.Option(
            "--log-file",
            help="Optional path to save structured JSON logs.",
        ),
    ] = None,
) -> None:
    """
    Run a water-allocation simulation on a drought scenario.
    """
    logger = configure_logging(log_file)
    scenario = load_scenario_config(config)

    log_event(
        logger,
        event="simulation_started",
        message="Simulation started.",
        scenario_name=scenario.scenario_name,
        config_path=str(config),
        strategy=strategy,
    )
    # result = run_strategy(strategy=strategy, config_path=config)
    proposal = create_proposal(strategy=strategy, scenario=scenario)
    result = evaluate_proposal(scenario, proposal)

    log_event(
        logger,
        event="simulation_completed",
        message="Simulation completed.",
        scenario_name=result.scenario_name,
        strategy=strategy,
        agreement_reached=result.agreement_reached,
        fairness_score=result.fairness_score,
        conflict_score=result.conflict_score,
        minimum_satisfaction_score=result.minimum_satisfaction_score,
        shortage_score=result.shortage_score,
    )

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
    strategies = get_strategy_names()
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
    table.add_column("Min satisfaction")
    table.add_column("Shortage")

    for strategy, result in results.items():
        table.add_row(
            strategy,
            f"{result.total_allocated:.2f}",
            str(result.water_budget_valid),
            f"{result.fairness_score:.3f}",
            f"{result.conflict_score:.3f}",
            str(result.agreement_reached),
            f"{result.minimum_satisfaction_score:.3f}",
            f"{result.shortage_score:.3f}",
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

    scenarios = [
        (config_path, load_scenario_config(config_path)) for config_path in config_paths
    ]

    scenarios = sorted(
        scenarios,
        key=lambda item: drought_level_sort_key(item[1].drought_level),
    )

    if not config_paths:
        raise typer.BadParameter(f"No YAML config files found in: {config_dir}")

    strategies = get_strategy_names()
    rows = []

    table = Table(title="All Scenario Strategy Comparison")

    table.add_column("Scenario")
    table.add_column("Drought level")
    table.add_column("Available water")
    table.add_column("Strategy")
    table.add_column("Fairness score")
    table.add_column("Conflict score")
    table.add_column("Agreement reached")
    table.add_column("Min satisfaction")
    table.add_column("Shortage")

    for _config_path, scenario in scenarios:
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
                "minimum_satisfaction_score": result.minimum_satisfaction_score,
                "shortage_score": result.shortage_score,
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
                f"{result.minimum_satisfaction_score:.3f}",
                f"{result.shortage_score:.3f}",
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


@app.command("generate-report")
def generate_report(
    input: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to CSV results produced by run-all.",
        ),
    ] = Path("outputs/all_results.csv"),
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the Markdown experiment report.",
        ),
    ] = Path("docs/experiment_report.md"),
) -> None:
    """
    Generate a Markdown experiment summary report from CSV results.
    """
    if output.suffix != ".md":
        raise typer.BadParameter("Output report file must end with .md.")

    try:
        generate_experiment_report(
            input_path=input,
            output_path=output,
        )
    except FileNotFoundError as error:
        raise typer.BadParameter(str(error)) from error
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    console.print(f"[green]Saved experiment report to {output}[/green]")


@app.command("agent-responses")
def agent_responses(
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
            help="Allocation strategy to use.",
        ),
    ] = "proportional",
) -> None:
    """
    Show rule-based stakeholder responses to an allocation proposal.
    """
    scenario = load_scenario_config(config)
    proposal = create_proposal(strategy=strategy, scenario=scenario)

    responses = evaluate_stakeholder_responses(
        stakeholders=scenario.stakeholders,
        proposal=proposal,
    )

    table = Table(title="Rule-Based Stakeholder Responses")

    table.add_column("Stakeholder")
    table.add_column("Allocated")
    table.add_column("Requested")
    table.add_column("Minimum")
    table.add_column("Satisfaction")
    table.add_column("Status")
    table.add_column("Message")

    for response in responses:
        table.add_row(
            response.stakeholder_name,
            f"{response.allocated_water:.2f}",
            f"{response.requested_water:.2f}",
            f"{response.minimum_acceptable_water:.2f}",
            f"{response.satisfaction_ratio:.3f}",
            response.status,
            response.message,
        )

    console.print(table)


@app.command("negotiate")
def negotiate(
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
            help="Initial allocation strategy to use.",
        ),
    ] = "proportional",
) -> None:
    """
    Run a simple negotiation round.

    Rejected stakeholder responses trigger a revised minimum-first allocation.
    """
    result = run_simple_negotiation(
        config_path=str(config),
        initial_strategy=strategy,
    )

    table = Table(title="Simple Negotiation Round")

    table.add_column("Stage")
    table.add_column("Strategy")
    table.add_column("Conflict score")
    table.add_column("Min satisfaction")
    table.add_column("Agreement reached")
    table.add_column("Rejected stakeholders")

    table.add_row(
        "initial",
        result.initial_strategy,
        f"{result.initial_result.conflict_score:.3f}",
        f"{result.initial_result.minimum_satisfaction_score:.3f}",
        str(result.initial_result.agreement_reached),
        ", ".join(result.rejected_stakeholders) or "none",
    )

    if result.revised_result is not None and result.revised_strategy is not None:
        revised_rejections = [
            response.stakeholder_name
            for response in result.revised_responses or []
            if response.status == "rejected"
        ]

        table.add_row(
            "revised",
            result.revised_strategy,
            f"{result.revised_result.conflict_score:.3f}",
            f"{result.revised_result.minimum_satisfaction_score:.3f}",
            str(result.revised_result.agreement_reached),
            ", ".join(revised_rejections) or "none",
        )

    console.print(table)


@app.command("negotiate-multi")
def negotiate_multi(
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
            help="Initial allocation strategy to use.",
        ),
    ] = "proportional",
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Optional path to save negotiation history as JSON.",
        ),
    ] = None,
    log_file: Annotated[
        Path | None,
        typer.Option(
            "--log-file",
            help="Optional path to save structured JSON logs.",
        ),
    ] = None,
) -> None:
    """
    Run a multi-round rule-based negotiation process.
    """

    logger = configure_logging(log_file)

    log_event(
        logger,
        event="negotiation_started",
        message="Multi-round negotiation started.",
        config_path=str(config),
        initial_strategy=strategy,
    )

    result = run_multi_round_negotiation(
        config_path=str(config),
        initial_strategy=strategy,
    )
    log_event(
        logger,
        event="negotiation_completed",
        message="Multi-round negotiation completed.",
        scenario_name=result.scenario_name,
        initial_strategy=result.initial_strategy,
        agreement_reached=result.agreement_reached,
        rounds_used=result.rounds_used,
        max_rounds=result.max_rounds,
    )

    table = Table(title="Multi-Round Negotiation")

    table.add_column("Round")
    table.add_column("Strategy")
    table.add_column("Conflict score")
    table.add_column("Min satisfaction")
    table.add_column("Agreement reached")
    table.add_column("Rejected stakeholders")

    for negotiation_round in result.rounds:
        log_event(
            logger,
            event="negotiation_round_completed",
            message="Negotiation round completed.",
            round_number=negotiation_round.round_number,
            strategy=negotiation_round.strategy,
            conflict_score=negotiation_round.result.conflict_score,
            minimum_satisfaction_score=(
                negotiation_round.result.minimum_satisfaction_score
            ),
            agreement_reached=negotiation_round.result.agreement_reached,
            rejected_stakeholders=negotiation_round.rejected_stakeholders,
        )
        table.add_row(
            str(negotiation_round.round_number),
            negotiation_round.strategy,
            f"{negotiation_round.result.conflict_score:.3f}",
            f"{negotiation_round.result.minimum_satisfaction_score:.3f}",
            str(negotiation_round.result.agreement_reached),
            ", ".join(negotiation_round.rejected_stakeholders) or "none",
        )

    console.print(table)
    console.print(f"Rounds used: {result.rounds_used}/{result.max_rounds}")
    console.print(f"Final agreement reached: {result.agreement_reached}")

    if output is not None:
        if output.suffix != ".json":
            raise typer.BadParameter("Negotiation history output must end with .json.")

        save_negotiation_history_json(result=result, output_path=output)
        console.print(f"[green]Saved negotiation history to {output}[/green]")


@app.command("summarize-negotiation")
def summarize_negotiation(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to a saved negotiation history JSON file.",
        ),
    ],
) -> None:
    """
    Summarize a saved negotiation history JSON file.
    """
    history = load_negotiation_history(input_path)
    summary = summarize_negotiation_history(history)

    table = Table(title="Negotiation Summary")

    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Scenario", summary["scenario_name"])
    table.add_row("Initial strategy", summary["initial_strategy"])
    table.add_row("Final strategy", summary["final_strategy"])
    table.add_row("Rounds used", f"{summary['rounds_used']}/{summary['max_rounds']}")
    table.add_row("Agreement reached", str(summary["agreement_reached"]))
    table.add_row(
        "Strategy sequence",
        " → ".join(summary["strategy_sequence"]),
    )
    table.add_row(
        "Final conflict score",
        f"{summary['final_conflict_score']:.3f}",
    )
    table.add_row(
        "Final minimum satisfaction",
        f"{summary['final_minimum_satisfaction_score']:.3f}",
    )
    table.add_row(
        "Final fairness score",
        f"{summary['final_fairness_score']:.3f}",
    )

    console.print(table)

    rejected_table = Table(title="Rejected Stakeholders by Round")
    rejected_table.add_column("Round")
    rejected_table.add_column("Rejected stakeholders")

    for round_number, rejected_stakeholders in summary["rejected_by_round"].items():
        rejected_table.add_row(
            str(round_number),
            ", ".join(rejected_stakeholders) or "none",
        )

    console.print(rejected_table)


@app.command("version")
def version() -> None:
    """
    Show the WaterAgentLab version.
    """
    console.print("WaterAgentLab 0.1.0")


if __name__ == "__main__":
    app()
