from pathlib import Path
import random

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.llm_negotiation import run_mock_llm_multi_round_negotiation
from water_agent_lab.models import ScenarioConfig, SimulationResult
from water_agent_lab.negotiation import choose_revision_strategy
from water_agent_lab.negotiation_mode_reporting import (
    generate_negotiation_mode_comparison_report,
)
from water_agent_lab.strategies import get_strategy


def run_ai_agent_experiment(
    config_path: str | Path,
    initial_strategy: str,
    runs: int,
    seed: int,
    output_dir: str | Path,
) -> None:
    """
    Run the full AI-agent experiment workflow.

    The workflow creates:
    1. Monte Carlo mock LLM negotiation results.
    2. Monte Carlo report and plots.
    3. Rule-based vs mock LLM negotiation mode comparison.
    4. Negotiation mode comparison report and plots.
    5. Final experiment summary Markdown file.
    """
    if runs <= 0:
        raise ValueError("runs must be greater than 0.")

    output_directory = Path(output_dir)
    output_directory.mkdir(parents=True, exist_ok=True)

    base_scenario = load_scenario_config(config_path)

    scenario_directory = output_directory / "_generated_scenarios"
    scenario_directory.mkdir(parents=True, exist_ok=True)

    generated_scenarios = _generate_scenario_variations(
        base_scenario=base_scenario,
        runs=runs,
        seed=seed,
        output_dir=scenario_directory,
    )

    monte_carlo_rows: list[dict[str, object]] = []
    mode_comparison_rows: list[dict[str, object]] = []

    for run_index, scenario_path in generated_scenarios:
        scenario = load_scenario_config(scenario_path)

        mock_transcript = run_mock_llm_multi_round_negotiation(
            config_path=scenario_path,
            initial_strategy=initial_strategy,
        )
        mock_row = _mock_transcript_to_row(
            run_index=run_index,
            initial_strategy=initial_strategy,
            available_water=scenario.available_water,
            transcript=mock_transcript,
        )

        monte_carlo_rows.append(mock_row)
        mode_comparison_rows.append(mock_row)

        rule_based_row = _run_rule_based_mode_row(
            run_index=run_index,
            scenario=scenario,
            initial_strategy=initial_strategy,
        )
        mode_comparison_rows.append(rule_based_row)

    monte_carlo_path = output_directory / "monte_carlo_mock.csv"
    monte_carlo_dataframe = pd.DataFrame(monte_carlo_rows)
    monte_carlo_dataframe.to_csv(monte_carlo_path, index=False)

    monte_carlo_report_path = output_directory / "monte_carlo_report.md"
    monte_carlo_conflict_plot_path = (
        output_directory / "monte_carlo_conflict_histogram.png"
    )
    monte_carlo_rounds_plot_path = output_directory / "monte_carlo_rounds_histogram.png"

    _generate_monte_carlo_report(
        dataframe=monte_carlo_dataframe,
        output_path=monte_carlo_report_path,
        conflict_plot_path=monte_carlo_conflict_plot_path,
        rounds_plot_path=monte_carlo_rounds_plot_path,
    )

    mode_comparison_path = output_directory / "negotiation_mode_comparison.csv"
    mode_comparison_dataframe = pd.DataFrame(mode_comparison_rows)
    mode_comparison_dataframe.to_csv(mode_comparison_path, index=False)

    mode_report_path = output_directory / "negotiation_mode_comparison_report.md"
    mode_conflict_plot_path = output_directory / "mode_comparison_conflict.png"
    mode_agreement_plot_path = output_directory / "mode_comparison_agreement.png"
    mode_rounds_plot_path = output_directory / "mode_comparison_rounds.png"

    generate_negotiation_mode_comparison_report(
        input_path=mode_comparison_path,
        output_path=mode_report_path,
        conflict_plot_path=mode_conflict_plot_path,
        agreement_plot_path=mode_agreement_plot_path,
        rounds_plot_path=mode_rounds_plot_path,
    )

    summary_path = output_directory / "ai_agent_experiment_summary.md"

    _generate_ai_agent_experiment_summary(
        output_path=summary_path,
        config_path=Path(config_path),
        initial_strategy=initial_strategy,
        runs=runs,
        seed=seed,
        monte_carlo_path=monte_carlo_path,
        monte_carlo_report_path=monte_carlo_report_path,
        monte_carlo_conflict_plot_path=monte_carlo_conflict_plot_path,
        monte_carlo_rounds_plot_path=monte_carlo_rounds_plot_path,
        mode_comparison_path=mode_comparison_path,
        mode_report_path=mode_report_path,
        mode_conflict_plot_path=mode_conflict_plot_path,
        mode_agreement_plot_path=mode_agreement_plot_path,
        mode_rounds_plot_path=mode_rounds_plot_path,
    )


def _generate_scenario_variations(
    base_scenario: ScenarioConfig,
    runs: int,
    seed: int,
    output_dir: Path,
) -> list[tuple[int, Path]]:
    """
    Generate deterministic scenario variants by perturbing available water.

    The variation keeps stakeholders fixed and changes available water by a
    deterministic random multiplier. This gives the Monte Carlo experiment
    scenario diversity while remaining reproducible.
    """
    rng = random.Random(seed)
    generated: list[tuple[int, Path]] = []

    for run_index in range(1, runs + 1):
        multiplier = rng.uniform(0.75, 1.15)
        available_water = round(base_scenario.available_water * multiplier, 3)

        scenario = base_scenario.model_copy(
            update={
                "scenario_name": (f"{base_scenario.scenario_name}_mc_{run_index:03d}"),
                "available_water": available_water,
            }
        )

        scenario_path = output_dir / f"scenario_{run_index:03d}.yaml"

        with scenario_path.open("w", encoding="utf-8") as file:
            yaml.safe_dump(
                scenario.model_dump(mode="json"),
                file,
                sort_keys=False,
                allow_unicode=True,
            )

        generated.append((run_index, scenario_path))

    return generated


def _run_rule_based_mode_row(
    run_index: int,
    scenario: ScenarioConfig,
    initial_strategy: str,
) -> dict[str, object]:
    """
    Run deterministic rule-based negotiation for one scenario variant.
    """
    current_strategy = initial_strategy
    final_result: SimulationResult | None = None
    rounds_used = 0

    for round_number in range(1, scenario.max_rounds + 1):
        strategy_function = get_strategy(current_strategy)
        proposal = strategy_function(scenario)
        result = evaluate_proposal(scenario, proposal)

        final_result = result
        rounds_used = round_number

        if result.agreement_reached:
            break

        revised_strategy = choose_revision_strategy(current_strategy)

        if revised_strategy == current_strategy:
            break

        current_strategy = revised_strategy

    if final_result is None:
        raise ValueError("Rule-based negotiation did not produce a result.")

    return {
        "run_index": run_index,
        "mode": "rule_based",
        "scenario_name": scenario.scenario_name,
        "available_water": scenario.available_water,
        "initial_strategy": initial_strategy,
        "agreement_reached": final_result.agreement_reached,
        "rounds_used": rounds_used,
        "final_strategy": current_strategy,
        "final_conflict_score": final_result.conflict_score,
        "final_fairness_score": final_result.fairness_score,
        "final_minimum_satisfaction_score": (final_result.minimum_satisfaction_score),
        "final_shortage_score": final_result.shortage_score,
        "final_mediator_action": "not_applicable",
    }


def _mock_transcript_to_row(
    run_index: int,
    initial_strategy: str,
    available_water: float,
    transcript,
) -> dict[str, object]:
    """
    Convert a mock LLM negotiation transcript into a comparison row.
    """
    final_round = transcript.rounds[-1]
    final_result = _get_selected_final_result(final_round)

    mediator_recommendation = final_round.mediator_recommendation
    final_mediator_action = (
        mediator_recommendation.action
        if mediator_recommendation is not None
        else "none"
    )

    return {
        "run_index": run_index,
        "mode": "mock_llm",
        "scenario_name": transcript.scenario_name,
        "available_water": available_water,
        "initial_strategy": initial_strategy,
        "agreement_reached": transcript.agreement_reached,
        "rounds_used": transcript.rounds_used,
        "final_strategy": final_round.strategy,
        "final_conflict_score": final_result.conflict_score,
        "final_fairness_score": final_result.fairness_score,
        "final_minimum_satisfaction_score": (final_result.minimum_satisfaction_score),
        "final_shortage_score": final_result.shortage_score,
        "final_mediator_action": final_mediator_action,
    }


def _get_selected_final_result(round_transcript) -> SimulationResult:
    """
    Return the final result selected by the mediator for a round.

    If the mediator chose the counterproposal candidate, use its result.
    Otherwise use the normal round result.
    """
    mediator_recommendation = round_transcript.mediator_recommendation

    if (
        mediator_recommendation is not None
        and mediator_recommendation.action == "use_counterproposal_candidate"
        and round_transcript.counterproposal_adjusted_result is not None
    ):
        return round_transcript.counterproposal_adjusted_result

    return round_transcript.result


def _generate_monte_carlo_report(
    dataframe: pd.DataFrame,
    output_path: Path,
    conflict_plot_path: Path,
    rounds_plot_path: Path,
) -> None:
    """
    Generate a Markdown report and plots for Monte Carlo mock LLM results.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    conflict_plot_path.parent.mkdir(parents=True, exist_ok=True)
    rounds_plot_path.parent.mkdir(parents=True, exist_ok=True)

    _plot_histogram(
        values=dataframe["final_conflict_score"],
        title="Monte Carlo final conflict score",
        xlabel="Final conflict score",
        output_path=conflict_plot_path,
    )

    _plot_histogram(
        values=dataframe["rounds_used"],
        title="Monte Carlo rounds used",
        xlabel="Rounds used",
        output_path=rounds_plot_path,
    )

    agreement_rate = float(dataframe["agreement_reached"].astype(bool).mean())
    average_conflict = float(dataframe["final_conflict_score"].mean())
    average_rounds = float(dataframe["rounds_used"].mean())

    markdown = "\n".join(
        [
            "# Monte Carlo Mock LLM Negotiation Report",
            "",
            "This report summarizes repeated deterministic mock LLM-style "
            "negotiation runs over perturbed drought scenarios.",
            "",
            "## Summary",
            "",
            f"- Runs: **{len(dataframe)}**",
            f"- Agreement rate: **{agreement_rate:.3f}**",
            f"- Average final conflict score: **{average_conflict:.3f}**",
            f"- Average rounds used: **{average_rounds:.3f}**",
            "",
            "## Plots",
            "",
            "### Final conflict score",
            "",
            f"![Monte Carlo final conflict]({_relative_markdown_path(output_path, conflict_plot_path)})",
            "",
            "### Rounds used",
            "",
            f"![Monte Carlo rounds used]({_relative_markdown_path(output_path, rounds_plot_path)})",
            "",
            "## Detailed results",
            "",
            dataframe.to_markdown(index=False),
            "",
        ]
    )

    output_path.write_text(markdown, encoding="utf-8")


def _plot_histogram(
    values: pd.Series,
    title: str,
    xlabel: str,
    output_path: Path,
) -> None:
    """
    Plot a histogram to a PNG file.
    """
    fig, ax = plt.subplots()
    ax.hist(values, bins=min(10, max(1, len(values))))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _generate_ai_agent_experiment_summary(
    output_path: Path,
    config_path: Path,
    initial_strategy: str,
    runs: int,
    seed: int,
    monte_carlo_path: Path,
    monte_carlo_report_path: Path,
    monte_carlo_conflict_plot_path: Path,
    monte_carlo_rounds_plot_path: Path,
    mode_comparison_path: Path,
    mode_report_path: Path,
    mode_conflict_plot_path: Path,
    mode_agreement_plot_path: Path,
    mode_rounds_plot_path: Path,
) -> None:
    """
    Generate the final summary Markdown file for the full experiment.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# AI-Agent Experiment Summary",
        "",
        "This experiment runs an end-to-end deterministic AI-agent negotiation "
        "workflow for drought water allocation.",
        "",
        "## Configuration",
        "",
        f"- Config: `{config_path.as_posix()}`",
        f"- Initial strategy: `{initial_strategy}`",
        f"- Runs: `{runs}`",
        f"- Seed: `{seed}`",
        "",
        "## Generated artifacts",
        "",
        f"- Monte Carlo CSV: `{_relative_markdown_path(output_path, monte_carlo_path)}`",
        f"- Monte Carlo report: `{_relative_markdown_path(output_path, monte_carlo_report_path)}`",
        f"- Monte Carlo conflict plot: `{_relative_markdown_path(output_path, monte_carlo_conflict_plot_path)}`",
        f"- Monte Carlo rounds plot: `{_relative_markdown_path(output_path, monte_carlo_rounds_plot_path)}`",
        f"- Negotiation mode comparison CSV: `{_relative_markdown_path(output_path, mode_comparison_path)}`",
        f"- Negotiation mode comparison report: `{_relative_markdown_path(output_path, mode_report_path)}`",
        f"- Mode comparison conflict plot: `{_relative_markdown_path(output_path, mode_conflict_plot_path)}`",
        f"- Mode comparison agreement plot: `{_relative_markdown_path(output_path, mode_agreement_plot_path)}`",
        f"- Mode comparison rounds plot: `{_relative_markdown_path(output_path, mode_rounds_plot_path)}`",
        "",
        "## Interpretation",
        "",
        "The workflow combines stochastic scenario variation with deterministic "
        "mock LLM-style negotiation. This makes the experiment reproducible "
        "while still allowing outcome distributions to be analyzed.",
        "",
        "The comparison report shows whether the agent-style layer, mediator "
        "actions, and counterproposal handling change outcomes compared with "
        "a rule-based negotiation baseline.",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _relative_markdown_path(
    source_path: Path,
    target_path: Path,
) -> str:
    """
    Return a Markdown-friendly relative path from source file to target file.
    """
    source_directory = source_path.parent.resolve()
    target = target_path.resolve()

    try:
        relative_path = target.relative_to(source_directory)
    except ValueError:
        relative_path = target

    return relative_path.as_posix()
