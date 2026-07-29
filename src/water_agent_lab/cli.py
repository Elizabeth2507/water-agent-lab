import json
from pathlib import Path
from typing import Annotated
from typing import Any

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
from water_agent_lab.run_metadata import create_run_metadata
from water_agent_lab.experiment_registry import (
    append_experiment_record,
    find_experiment_record,
    load_experiment_registry,
    verify_experiment_record_configs,
)
from water_agent_lab.hashing import compute_config_hashes, compute_file_sha256
from water_agent_lab.reproduction import (
    ensure_record_is_reproducible,
    get_reproduced_output_path,
)
from water_agent_lab.run_comparison import compare_output_files
from water_agent_lab.dashboard import summarize_registry
from water_agent_lab.cleanup import demo_output_exists, remove_demo_output
from water_agent_lab.doctor import check_project_health, project_health_passed
from water_agent_lab.data_sources import (
    MockDroughtDataSource,
    VigiEauDataSource,
    HubEauHydrometryDataSource,
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


def build_run_all_rows(
    config_dir: Path,
    run_metadata: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Build result rows for all scenario configs and all strategies.
    """
    config_paths = sorted(config_dir.glob("*.yaml"))

    config_paths = sorted(
        config_paths,
        key=lambda path: drought_level_sort_key(
            load_scenario_config(path).drought_level
        ),
    )

    rows: list[dict[str, Any]] = []

    for config_path in config_paths:
        scenario = load_scenario_config(config_path)

        for strategy in get_strategy_names():
            proposal = create_proposal(
                strategy=strategy,
                scenario=scenario,
            )
            result = evaluate_proposal(scenario, proposal)

            rows.append(
                {
                    **run_metadata,
                    "scenario_name": result.scenario_name,
                    "drought_level": result.drought_level,
                    "available_water": result.available_water,
                    "strategy": strategy,
                    "total_requested": result.total_requested,
                    "total_allocated": result.total_allocated,
                    "water_budget_valid": result.water_budget_valid,
                    "fairness_score": result.fairness_score,
                    "conflict_score": result.conflict_score,
                    "minimum_satisfaction_score": result.minimum_satisfaction_score,
                    "shortage_score": result.shortage_score,
                    "agreement_reached": result.agreement_reached,
                }
            )

    return rows


def get_primary_output_path(record: dict[str, object]) -> str:
    """
    Return the main output path for a registry record.
    """
    outputs = record.get("outputs", {})

    if not isinstance(outputs, dict):
        raise ValueError("Run record does not contain valid outputs.")

    if "results" in outputs:
        return str(outputs["results"])

    if "negotiation_history" in outputs:
        return str(outputs["negotiation_history"])

    raise ValueError("Run record does not contain a supported output file.")


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

    run_metadata = create_run_metadata(command="simulate")

    scenario = load_scenario_config(config)

    log_event(
        logger,
        event="simulation_started",
        message="Simulation started.",
        **run_metadata,
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
        **run_metadata,
        scenario_name=result.scenario_name,
        strategy=strategy,
        agreement_reached=result.agreement_reached,
        fairness_score=result.fairness_score,
        conflict_score=result.conflict_score,
        minimum_satisfaction_score=result.minimum_satisfaction_score,
        shortage_score=result.shortage_score,
    )

    output = {
        "run_metadata": run_metadata,
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
            help="Directory containing scenario YAML configs.",
        ),
    ] = Path("configs"),
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Optional path to save results as CSV or JSON.",
        ),
    ] = None,
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
) -> None:
    """
    Run all scenario configs with all available allocation strategies.
    """
    run_metadata = create_run_metadata(command="run-all")

    config_paths = sorted(config_dir.glob("*.yaml"))

    if not config_paths:
        raise typer.BadParameter(f"No YAML config files found in: {config_dir}")

    config_hashes = compute_config_hashes(config_paths)

    rows = build_run_all_rows(
        config_dir=config_dir,
        run_metadata=run_metadata,
    )

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

    for row in rows:
        table.add_row(
            str(row["scenario_name"]),
            str(row["drought_level"]),
            f"{float(row['available_water']):.2f}",
            str(row["strategy"]),
            f"{float(row['fairness_score']):.3f}",
            f"{float(row['conflict_score']):.3f}",
            str(row["agreement_reached"]),
            f"{float(row['minimum_satisfaction_score']):.3f}",
            f"{float(row['shortage_score']):.3f}",
        )

    console.print(table)
    console.print(f"Run ID: {run_metadata['run_id']}")

    if output is None:
        return

    if output.suffix == ".csv":
        save_results_csv(rows, output)
    elif output.suffix == ".json":
        save_results_json(rows, output)
    else:
        raise typer.BadParameter("Output file must end with .csv or .json.")

    append_experiment_record(
        {
            **run_metadata,
            "status": "completed",
            "config_dir": str(config_dir),
            "config_hashes": config_hashes,
            "outputs": {
                "results": str(output),
            },
        },
        registry_path=registry,
    )

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
    plot: Annotated[
        Path | None,
        typer.Option(
            "--plot",
            help="Optional path to save and embed a fairness/conflict plot.",
        ),
    ] = None,
) -> None:
    """
    Generate a Markdown experiment summary report from CSV results.
    """
    if output.suffix != ".md":
        raise typer.BadParameter("Output report file must end with .md.")

    if plot is not None and plot.suffix != ".png":
        raise typer.BadParameter("Plot file must end with .png.")

    try:
        generate_experiment_report(
            input_path=input,
            output_path=output,
            plot_path=plot,
        )
    except FileNotFoundError as error:
        raise typer.BadParameter(str(error)) from error
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    console.print(f"[green]Saved experiment report to {output}[/green]")

    if plot is not None:
        console.print(f"[green]Saved report plot to {plot}[/green]")


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
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
) -> None:
    """
    Run a multi-round rule-based negotiation process.
    """

    logger = configure_logging(log_file)

    run_metadata = create_run_metadata(command="negotiate-multi")

    log_event(
        logger,
        event="negotiation_started",
        message="Multi-round negotiation started.",
        **run_metadata,
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
        **run_metadata,
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
            **run_metadata,
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

    config_hash = compute_file_sha256(config)

    if output is not None:
        if output.suffix != ".json":
            raise typer.BadParameter("Negotiation history output must end with .json.")

        save_negotiation_history_json(
            result=result,
            output_path=output,
            run_metadata=run_metadata,
        )

        append_experiment_record(
            {
                **run_metadata,
                "status": "completed",
                "config_path": str(config),
                "config_hash": config_hash,
                "initial_strategy": strategy,
                "outputs": {
                    "negotiation_history": str(output),
                },
            },
            registry_path=registry,
        )
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


@app.command("list-runs")
def list_runs(
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
) -> None:
    """
    List recorded experiment runs.
    """
    # records = load_experiment_registry()
    records = load_experiment_registry(registry_path=registry)

    table = Table(title="Experiment Registry")

    table.add_column("Run ID")
    table.add_column("Created at UTC")
    table.add_column("Command")
    table.add_column("Status")
    table.add_column("Outputs")

    for record in records:
        outputs = record.get("outputs", {})
        output_text = ", ".join(f"{name}: {path}" for name, path in outputs.items())

        table.add_row(
            str(record.get("run_id", "")),
            str(record.get("created_at_utc", "")),
            str(record.get("command", "")),
            str(record.get("status", "")),
            output_text,
        )

    console.print(table)


@app.command("show-run")
def show_run(
    run_id: Annotated[
        str,
        typer.Option(
            "--run-id",
            help="Run ID to inspect.",
        ),
    ],
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
) -> None:
    """
    Show details for one recorded experiment run.
    """
    record = find_experiment_record(
        run_id=run_id,
        registry_path=registry,
    )

    if record is None:
        raise typer.BadParameter(f"Run ID not found: {run_id}")

    table = Table(title="Experiment Run")

    table.add_column("Field")
    table.add_column("Value")

    for key, value in record.items():
        if key == "outputs":
            continue

        table.add_row(
            str(key),
            str(value),
        )

    console.print(table)

    outputs = record.get("outputs", {})

    output_table = Table(title="Run Outputs")
    output_table.add_column("Name")
    output_table.add_column("Path")

    for name, path in outputs.items():
        output_table.add_row(
            str(name),
            str(path),
        )

    console.print(output_table)


@app.command("verify-run")
def verify_run(
    run_id: Annotated[
        str,
        typer.Option(
            "--run-id",
            help="Run ID to verify.",
        ),
    ],
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
) -> None:
    """
    Verify whether current config files match the hashes recorded for a run.
    """
    record = find_experiment_record(
        run_id=run_id,
        registry_path=registry,
    )

    if record is None:
        raise typer.BadParameter(f"Run ID not found: {run_id}")

    verification_results = verify_experiment_record_configs(record)

    table = Table(title="Run Reproducibility Check")

    table.add_column("Config path")
    table.add_column("Status")
    table.add_column("Matches")
    table.add_column("Expected hash")
    table.add_column("Current hash")

    for result in verification_results:
        expected_hash = str(result["expected_hash"])
        current_hash = result["current_hash"]

        table.add_row(
            str(result["config_path"]),
            str(result["status"]),
            str(result["matches"]),
            expected_hash[:12],
            str(current_hash)[:12] if current_hash is not None else "none",
        )

    console.print(table)

    if verification_results and all(
        result["matches"] for result in verification_results
    ):
        console.print("[green]All config files match recorded hashes.[/green]")
    else:
        console.print("[red]Some config files do not match recorded hashes.[/red]")


@app.command("reproduce-run")
def reproduce_run(
    run_id: Annotated[
        str,
        typer.Option(
            "--run-id",
            help="Run ID to reproduce.",
        ),
    ],
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
) -> None:
    """
    Reproduce a recorded experiment run if config hashes still match.
    """
    record = find_experiment_record(
        run_id=run_id,
        registry_path=registry,
    )

    if record is None:
        raise typer.BadParameter(f"Run ID not found: {run_id}")

    ensure_record_is_reproducible(record)

    command = record.get("command")
    outputs = record.get("outputs", {})

    run_metadata = create_run_metadata(command=f"reproduce-{command}")

    if command == "run-all":
        original_results_path = outputs.get("results")

        if original_results_path is None:
            raise typer.BadParameter("Original run-all record has no results output.")

        output_path = get_reproduced_output_path(
            original_output_path=original_results_path,
            new_run_id=run_metadata["run_id"],
        )

        config_dir = Path(str(record["config_dir"]))
        rows = build_run_all_rows(
            config_dir=config_dir,
            run_metadata=run_metadata,
        )

        if output_path.suffix == ".csv":
            save_results_csv(results=rows, output_path=output_path)
        elif output_path.suffix == ".json":
            save_results_json(results=rows, output_path=output_path)
        else:
            raise typer.BadParameter("Reproduced output must end with .csv or .json.")

        config_paths = sorted(config_dir.glob("*.yaml"))
        config_hashes = compute_config_hashes(config_paths)

        append_experiment_record(
            record={
                **run_metadata,
                "status": "completed",
                "reproduced_from_run_id": run_id,
                "config_dir": str(config_dir),
                "config_hashes": config_hashes,
                "outputs": {
                    "results": str(output_path),
                },
            },
            registry_path=registry,
        )

        console.print("[green]Run is reproducible.[/green]")
        console.print(f"[green]Saved reproduced results to {output_path}[/green]")
        return

    if command == "negotiate-multi":
        original_history_path = outputs.get("negotiation_history")

        if original_history_path is None:
            raise typer.BadParameter(
                "Original negotiate-multi record has no negotiation history output."
            )

        output_path = get_reproduced_output_path(
            original_output_path=original_history_path,
            new_run_id=run_metadata["run_id"],
        )

        config_path = Path(str(record["config_path"]))
        initial_strategy = str(record["initial_strategy"])

        result = run_multi_round_negotiation(
            config_path=str(config_path),
            initial_strategy=initial_strategy,
        )

        save_negotiation_history_json(
            result=result,
            output_path=output_path,
            run_metadata=run_metadata,
        )

        append_experiment_record(
            record={
                **run_metadata,
                "status": "completed",
                "reproduced_from_run_id": run_id,
                "config_path": str(config_path),
                "config_hash": compute_file_sha256(config_path),
                "initial_strategy": initial_strategy,
                "outputs": {
                    "negotiation_history": str(output_path),
                },
            },
            registry_path=registry,
        )

        console.print("[green]Run is reproducible.[/green]")
        console.print(
            f"[green]Saved reproduced negotiation history to {output_path}[/green]"
        )
        return

    raise typer.BadParameter(f"Reproduction is not supported for command: {command}")


@app.command("compare-runs")
def compare_runs(
    run_id: Annotated[
        str,
        typer.Option(
            "--run-id",
            help="Original run ID.",
        ),
    ],
    reproduced_run_id: Annotated[
        str,
        typer.Option(
            "--reproduced-run-id",
            help="Reproduced run ID.",
        ),
    ],
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
) -> None:
    """
    Compare outputs from an original run and a reproduced run.
    """
    original_record = find_experiment_record(
        run_id=run_id,
        registry_path=registry,
    )
    reproduced_record = find_experiment_record(
        run_id=reproduced_run_id,
        registry_path=registry,
    )

    if original_record is None:
        raise typer.BadParameter(f"Original run ID not found: {run_id}")

    if reproduced_record is None:
        raise typer.BadParameter(f"Reproduced run ID not found: {reproduced_run_id}")

    original_output = get_primary_output_path(original_record)
    reproduced_output = get_primary_output_path(reproduced_record)

    comparison = compare_output_files(
        original_path=original_output,
        reproduced_path=reproduced_output,
    )

    table = Table(title="Run Comparison")

    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Original run ID", run_id)
    table.add_row("Reproduced run ID", reproduced_run_id)
    table.add_row("Original output", comparison["original_path"])
    table.add_row("Reproduced output", comparison["reproduced_path"])
    table.add_row("Matches", str(comparison["matches"]))
    table.add_row("Reason", comparison["reason"])

    console.print(table)

    if comparison["matches"]:
        console.print("[green]Reproduced output matches original output.[/green]")
    else:
        console.print("[red]Reproduced output differs from original output.[/red]")


@app.command("generate-run-report")
def generate_run_report(
    run_id: Annotated[
        str,
        typer.Option(
            "--run-id",
            help="Run ID whose results should be used for the report.",
        ),
    ],
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Path to save the Markdown report.",
        ),
    ] = Path("docs/experiment_report.md"),
    plot: Annotated[
        Path | None,
        typer.Option(
            "--plot",
            help="Optional path to generate and embed a fairness/conflict plot.",
        ),
    ] = None,
) -> None:
    """
    Generate a Markdown experiment report from a recorded run-all registry entry.
    """
    record = find_experiment_record(
        run_id=run_id,
        registry_path=registry,
    )

    if record is None:
        raise typer.BadParameter(f"Run ID not found: {run_id}")

    outputs = record.get("outputs", {})

    if not isinstance(outputs, dict):
        raise typer.BadParameter("Run record does not contain valid outputs.")

    results_path = outputs.get("results")

    if results_path is None:
        raise typer.BadParameter(
            "This run does not have a registered results output. "
            "Only run-all result records can be used for report generation."
        )

    results_file = Path(str(results_path))

    if results_file.suffix != ".csv":
        raise typer.BadParameter(
            "Report generation from registry currently expects a CSV results file."
        )

    if output.suffix != ".md":
        raise typer.BadParameter("Report output must end with .md.")

    generate_experiment_report(
        input_path=results_file,
        output_path=output,
        plot_path=plot,
    )

    run_metadata = create_run_metadata(command="generate-run-report")

    report_outputs = {
        "report": str(output),
    }

    # if plot is not None:
    #     report_outputs["plot"] = str(plot)

    append_experiment_record(
        record={
            **run_metadata,
            "status": "completed",
            "source_run_id": run_id,
            "source_results": str(results_file),
            "outputs": report_outputs,
        },
        registry_path=registry,
    )

    console.print(f"[green]Saved experiment report to {output}[/green]")

    # if plot is not None:
    #     console.print(f"[green]Saved report plot to {plot}[/green]")

    console.print(
        f"[green]Recorded report generation run: {run_metadata['run_id']}[/green]"
    )


@app.command("dashboard")
def dashboard(
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
) -> None:
    """
    Show a dashboard summary of recorded experiment runs.
    """
    records = load_experiment_registry(registry_path=registry)
    summary = summarize_registry(records)

    overview_table = Table(title="WaterAgentLab Experiment Dashboard")
    overview_table.add_column("Field")
    overview_table.add_column("Value")

    overview_table.add_row("Registry", str(registry))
    overview_table.add_row("Total runs", str(summary["total_runs"]))
    overview_table.add_row("Reproduced runs", str(summary["reproduced_runs"]))

    latest_run = summary["latest_run"]

    if latest_run is not None:
        overview_table.add_row("Latest run ID", str(latest_run.get("run_id", "")))
        overview_table.add_row("Latest command", str(latest_run.get("command", "")))
        overview_table.add_row(
            "Latest created at UTC",
            str(latest_run.get("created_at_utc", "")),
        )

    console.print(overview_table)

    command_table = Table(title="Runs by Command")
    command_table.add_column("Command")
    command_table.add_column("Count")

    for command, count in sorted(summary["command_counts"].items()):
        command_table.add_row(str(command), str(count))

    console.print(command_table)

    output_table = Table(title="Outputs by Type")
    output_table.add_column("Output type")
    output_table.add_column("Count")

    for output_name, count in sorted(summary["output_counts"].items()):
        output_table.add_row(str(output_name), str(count))

    console.print(output_table)


@app.command("run-experiment")
def run_experiment(
    config_dir: Annotated[
        Path,
        typer.Option(
            "--config-dir",
            help="Directory containing scenario YAML configs.",
        ),
    ] = Path("configs"),
    results: Annotated[
        Path,
        typer.Option(
            "--results",
            help="Path to save batch results as CSV.",
        ),
    ] = Path("outputs/results.csv"),
    report: Annotated[
        Path,
        typer.Option(
            "--report",
            help="Path to save the Markdown experiment report.",
        ),
    ] = Path("docs/experiment_report.md"),
    plot: Annotated[
        Path,
        typer.Option(
            "--plot",
            help="Path to save the fairness/conflict plot.",
        ),
    ] = Path("outputs/report_fairness_conflict.png"),
    registry: Annotated[
        Path,
        typer.Option(
            "--registry",
            help="Path to the experiment registry JSONL file.",
        ),
    ] = Path("outputs/experiment_registry.jsonl"),
) -> None:
    """
    Run the full experiment pipeline.

    This command runs all scenarios, exports results, generates a Markdown
    report, creates a plot, and records the experiment in the registry.
    """
    if results.suffix != ".csv":
        raise typer.BadParameter("Experiment results output must end with .csv.")

    if report.suffix != ".md":
        raise typer.BadParameter("Experiment report output must end with .md.")

    run_metadata = create_run_metadata(command="run-experiment")

    rows = build_run_all_rows(
        config_dir=config_dir,
        run_metadata=run_metadata,
    )

    save_results_csv(
        results=rows,
        output_path=results,
    )

    generate_experiment_report(
        input_path=results,
        output_path=report,
        plot_path=plot,
    )

    config_paths = sorted(config_dir.glob("*.yaml"))
    config_hashes = compute_config_hashes(config_paths)

    append_experiment_record(
        record={
            **run_metadata,
            "status": "completed",
            "config_dir": str(config_dir),
            "config_hashes": config_hashes,
            "outputs": {
                "results": str(results),
                "report": str(report),
                "plot": str(plot),
            },
        },
        registry_path=registry,
    )

    console.print("[green]Experiment pipeline completed.[/green]")
    console.print(f"[green]Saved results to {results}[/green]")
    console.print(f"[green]Saved report to {report}[/green]")
    console.print(f"[green]Saved plot to {plot}[/green]")
    console.print(f"[green]Recorded run: {run_metadata['run_id']}[/green]")


@app.command("demo")
def demo(
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Directory where demo outputs will be saved.",
        ),
    ] = Path("outputs/demo"),
) -> None:
    """
    Run a complete demo experiment with configurable demo output paths.
    """
    config_dir = Path("configs")
    results = output_dir / "results.csv"
    report = output_dir / "experiment_report.md"
    plot = output_dir / "fairness_conflict.png"
    registry = output_dir / "experiment_registry.jsonl"

    run_metadata = create_run_metadata(command="demo")

    rows = build_run_all_rows(
        config_dir=config_dir,
        run_metadata=run_metadata,
    )

    save_results_csv(
        results=rows,
        output_path=results,
    )

    generate_experiment_report(
        input_path=results,
        output_path=report,
        plot_path=plot,
    )

    config_paths = sorted(config_dir.glob("*.yaml"))
    config_hashes = compute_config_hashes(config_paths)

    append_experiment_record(
        record={
            **run_metadata,
            "status": "completed",
            "config_dir": str(config_dir),
            "config_hashes": config_hashes,
            "outputs": {
                "results": str(results),
                "report": str(report),
                "plot": str(plot),
            },
        },
        registry_path=registry,
    )

    table = Table(title="WaterAgentLab Demo Completed")

    table.add_column("Output")
    table.add_column("Path")

    table.add_row("Results CSV", str(results))
    table.add_row("Markdown report", str(report))
    table.add_row("Plot", str(plot))
    table.add_row("Registry", str(registry))
    table.add_row("Run ID", run_metadata["run_id"])

    console.print(table)

    console.print("\nNext commands:")
    console.print(f"uv run water-agent-lab dashboard --registry {registry}")
    console.print(f"uv run water-agent-lab list-runs --registry {registry}")


@app.command("clean-demo")
def clean_demo(
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Demo output directory to remove.",
        ),
    ] = Path("outputs/demo"),
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            help="Actually remove the demo output directory.",
        ),
    ] = False,
) -> None:
    """
    Remove generated demo outputs.

    Without --yes, this command only shows what would be removed.
    """
    if not demo_output_exists(output_dir):
        console.print(
            f"[yellow]Demo output directory does not exist: {output_dir}[/yellow]"
        )
        return

    if not yes:
        console.print("[yellow]Dry run only. No files were deleted.[/yellow]")
        console.print(f"Would remove: {output_dir}")
        console.print("Run again with --yes to delete this directory.")
        return

    remove_demo_output(output_dir)
    console.print(f"[green]Removed demo output directory: {output_dir}[/green]")


@app.command("doctor")
def doctor(
    config_dir: Annotated[
        Path,
        typer.Option(
            "--config-dir",
            help="Directory containing scenario YAML configs.",
        ),
    ] = Path("configs"),
    outputs_dir: Annotated[
        Path,
        typer.Option(
            "--outputs-dir",
            help="Directory for generated outputs.",
        ),
    ] = Path("outputs"),
    docs_dir: Annotated[
        Path,
        typer.Option(
            "--docs-dir",
            help="Directory for generated documentation reports.",
        ),
    ] = Path("docs"),
) -> None:
    """
    Run project health checks.
    """
    checks = check_project_health(
        config_dir=config_dir,
        outputs_dir=outputs_dir,
        docs_dir=docs_dir,
    )

    table = Table(title="WaterAgentLab Project Health Check")

    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Details")

    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"

        table.add_row(
            str(check["check"]),
            status,
            str(check["details"]),
        )

    console.print(table)

    if project_health_passed(checks):
        console.print("[green]Project health check passed.[/green]")
    else:
        console.print("[red]Project health check failed.[/red]")
        raise typer.Exit(code=1)


@app.command("load-mock-data")
def load_mock_data(
    snapshot: Annotated[
        Path,
        typer.Option(
            "--snapshot",
            help="Path to a mock drought JSON snapshot.",
        ),
    ] = Path("data/mock/occitanie_drought_snapshot.json"),
) -> None:
    """
    Load a mock drought data snapshot and show the generated scenario.
    """
    data_source = MockDroughtDataSource(snapshot)

    metadata = data_source.metadata()
    scenario = data_source.load_scenario()

    table = Table(title="Mock Drought Data Source")

    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Source name", metadata.source_name)
    table.add_row("Source type", metadata.source_type)
    table.add_row("Source path", str(metadata.source_path))
    table.add_row("Scenario name", scenario.scenario_name)
    table.add_row("Country", scenario.country)
    table.add_row("Region", scenario.region)
    table.add_row("Drought level", scenario.drought_level)
    table.add_row("Available water", f"{scenario.available_water:.2f}")
    table.add_row("Stakeholders", str(len(scenario.stakeholders)))

    console.print(table)


@app.command("load-vigieau-sample")
def load_vigieau_sample(
    sample: Annotated[
        Path,
        typer.Option(
            "--sample",
            help="Path to a simplified VigiEau-style sample JSON response.",
        ),
    ] = Path("data/sample_vigieau/occitanie_restrictions_sample.json"),
) -> None:
    """
    Load a simplified VigiEau-style sample response and show the generated scenario.
    """
    data_source = VigiEauDataSource(sample_response_path=sample)

    metadata = data_source.metadata()
    scenario = data_source.load_scenario()

    table = Table(title="VigiEau Sample Data Source")

    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Source name", metadata.source_name)
    table.add_row("Source type", metadata.source_type)
    table.add_row("Source URL", str(metadata.source_url))
    table.add_row("Sample path", str(metadata.source_path))
    table.add_row("Scenario name", scenario.scenario_name)
    table.add_row("Country", scenario.country)
    table.add_row("Region", scenario.region)
    table.add_row("Drought level", scenario.drought_level)
    table.add_row("Available water", f"{scenario.available_water:.2f}")
    table.add_row("Stakeholders", str(len(scenario.stakeholders)))

    console.print(table)


@app.command("load-hubeau-sample")
def load_hubeau_sample(
    sample: Annotated[
        Path,
        typer.Option(
            "--sample",
            help="Path to a simplified Hub'Eau hydrometry sample JSON response.",
        ),
    ] = Path("data/sample_hubeau/occitanie_hydrometry_sample.json"),
) -> None:
    """
    Load a simplified Hub'Eau hydrometry sample response and show the generated scenario.
    """
    data_source = HubEauHydrometryDataSource(sample_response_path=sample)

    metadata = data_source.metadata()
    scenario = data_source.load_scenario()
    raw_response = data_source.load_sample_response()

    table = Table(title="Hub'Eau Hydrometry Sample Data Source")

    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Source name", metadata.source_name)
    table.add_row("Source type", metadata.source_type)
    table.add_row("Source URL", str(metadata.source_url))
    table.add_row("Sample path", str(metadata.source_path))
    table.add_row("Station code", str(raw_response.get("station_code", "")))
    table.add_row("Station label", str(raw_response.get("station_label", "")))
    table.add_row("Observed flow", str(raw_response.get("observed_flow_m3s", "")))
    table.add_row("Normal flow", str(raw_response.get("normal_flow_m3s", "")))
    table.add_row("Scenario name", scenario.scenario_name)
    table.add_row("Country", scenario.country)
    table.add_row("Region", scenario.region)
    table.add_row("Drought level", scenario.drought_level)
    table.add_row("Available water", f"{scenario.available_water:.2f}")
    table.add_row("Stakeholders", str(len(scenario.stakeholders)))

    console.print(table)


@app.command("version")
def version() -> None:
    """
    Show the WaterAgentLab version.
    """
    console.print("WaterAgentLab 0.1.0")


if __name__ == "__main__":
    app()
