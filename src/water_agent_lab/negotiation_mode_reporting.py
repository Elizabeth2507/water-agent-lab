from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


REQUIRED_COLUMNS = {
    "scenario_name",
    "mode",
    "initial_strategy",
    "agreement_reached",
    "rounds_used",
    "final_conflict_score",
}


def generate_negotiation_mode_comparison_report(
    input_path: str | Path,
    output_path: str | Path,
    conflict_plot_path: str | Path | None = None,
    agreement_plot_path: str | Path | None = None,
    rounds_plot_path: str | Path | None = None,
) -> None:
    """
    Generate a Markdown report comparing rule-based and mock LLM negotiation.

    The input CSV is expected to come from Step 82 and should contain one row
    per scenario/mode comparison result.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    dataframe = pd.read_csv(input_file)
    _validate_mode_comparison_dataframe(dataframe)

    conflict_plot_file = (
        Path(conflict_plot_path) if conflict_plot_path is not None else None
    )
    agreement_plot_file = (
        Path(agreement_plot_path) if agreement_plot_path is not None else None
    )
    rounds_plot_file = Path(rounds_plot_path) if rounds_plot_path is not None else None

    summary = summarize_negotiation_modes(dataframe)

    if conflict_plot_file is not None:
        plot_mode_comparison_conflict(
            dataframe=dataframe,
            output_path=conflict_plot_file,
        )

    if agreement_plot_file is not None:
        plot_mode_comparison_agreement(
            dataframe=dataframe,
            output_path=agreement_plot_file,
        )

    if rounds_plot_file is not None:
        plot_mode_comparison_rounds(
            dataframe=dataframe,
            output_path=rounds_plot_file,
        )

    markdown = build_negotiation_mode_report_markdown(
        dataframe=dataframe,
        summary=summary,
        report_path=output_file,
        conflict_plot_path=conflict_plot_file,
        agreement_plot_path=agreement_plot_file,
        rounds_plot_path=rounds_plot_file,
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown, encoding="utf-8")


def summarize_negotiation_modes(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize negotiation outcomes by mode.
    """
    normalized = dataframe.copy()
    normalized["agreement_reached"] = normalized["agreement_reached"].astype(bool)

    aggregations = {
        "scenarios": ("scenario_name", "count"),
        "agreement_rate": ("agreement_reached", "mean"),
        "average_final_conflict": ("final_conflict_score", "mean"),
        "average_rounds_used": ("rounds_used", "mean"),
    }

    if "final_fairness_score" in normalized.columns:
        aggregations["average_final_fairness"] = (
            "final_fairness_score",
            "mean",
        )

    if "final_minimum_satisfaction_score" in normalized.columns:
        aggregations["average_minimum_satisfaction"] = (
            "final_minimum_satisfaction_score",
            "mean",
        )

    if "final_shortage_score" in normalized.columns:
        aggregations["average_shortage"] = (
            "final_shortage_score",
            "mean",
        )

    return (
        normalized.groupby("mode", as_index=False)
        .agg(**aggregations)
        .sort_values("mode")
    )


def build_negotiation_mode_report_markdown(
    dataframe: pd.DataFrame,
    summary: pd.DataFrame,
    report_path: Path,
    conflict_plot_path: Path | None = None,
    agreement_plot_path: Path | None = None,
    rounds_plot_path: Path | None = None,
) -> str:
    """
    Build the Markdown content for the negotiation mode comparison report.
    """
    lines: list[str] = [
        "# Negotiation Mode Comparison Report",
        "",
        "This report compares deterministic rule-based negotiation with "
        "mock LLM-style negotiation across drought scenarios.",
        "",
        "The goal is to understand whether the agent-style negotiation layer "
        "changes outcomes such as agreement rate, final conflict score, and "
        "number of rounds used.",
        "",
        "## Summary by mode",
        "",
        summary.to_markdown(index=False),
        "",
    ]

    best_agreement_mode = _get_best_mode(
        summary=summary,
        column="agreement_rate",
        higher_is_better=True,
    )
    best_conflict_mode = _get_best_mode(
        summary=summary,
        column="average_final_conflict",
        higher_is_better=False,
    )
    best_rounds_mode = _get_best_mode(
        summary=summary,
        column="average_rounds_used",
        higher_is_better=False,
    )

    lines.extend(
        [
            "## Main findings",
            "",
            f"- Highest agreement rate: **{best_agreement_mode}**.",
            f"- Lowest average final conflict: **{best_conflict_mode}**.",
            f"- Fewest average rounds used: **{best_rounds_mode}**.",
            "",
            "These findings should be interpreted as deterministic simulation "
            "results, not as real-world policy conclusions.",
            "",
        ]
    )

    plot_entries = [
        ("Final conflict by mode", conflict_plot_path),
        ("Agreement rate by mode", agreement_plot_path),
        ("Average rounds used by mode", rounds_plot_path),
    ]

    if any(path is not None for _, path in plot_entries):
        lines.extend(["## Plots", ""])

        for title, plot_path in plot_entries:
            if plot_path is None:
                continue

            relative_path = _markdown_relative_path(
                source_path=report_path,
                target_path=plot_path,
            )

            lines.extend(
                [
                    f"### {title}",
                    "",
                    f"![{title}]({relative_path})",
                    "",
                ]
            )
    display_dataframe = dataframe.copy()

    preferred_columns = [
        "run_index",
        "scenario_name",
        "mode",
        "available_water",
        "initial_strategy",
        "final_strategy",
        "agreement_reached",
        "rounds_used",
        "final_conflict_score",
        "final_fairness_score",
        "final_minimum_satisfaction_score",
        "final_shortage_score",
        "final_mediator_action",
    ]

    existing_columns = [
        column for column in preferred_columns if column in display_dataframe.columns
    ]

    display_dataframe = display_dataframe[existing_columns]
    lines.extend(
        [
            "## Detailed results",
            "",
            dataframe.to_markdown(index=False),
            "",
            "## Interpretation",
            "",
            "The rule-based mode represents a transparent deterministic baseline. "
            "The mock LLM-style mode adds an agent-style layer with stakeholder "
            "decisions, mediator recommendations, and counterproposal pressure. "
            "A difference between the two modes indicates that the negotiation "
            "protocol can affect the final allocation trajectory, even when the "
            "LLM backend is deterministic and offline.",
            "",
        ]
    )

    return "\n".join(lines)


def plot_mode_comparison_conflict(
    dataframe: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Plot average final conflict score by negotiation mode.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    summary = summarize_negotiation_modes(dataframe)

    fig, ax = plt.subplots()
    ax.bar(
        summary["mode"],
        summary["average_final_conflict"],
    )
    ax.set_title("Average final conflict by negotiation mode")
    ax.set_xlabel("Negotiation mode")
    ax.set_ylabel("Average final conflict score")
    fig.tight_layout()
    fig.savefig(output_file)
    plt.close(fig)


def plot_mode_comparison_agreement(
    dataframe: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Plot agreement rate by negotiation mode.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    summary = summarize_negotiation_modes(dataframe)

    fig, ax = plt.subplots()
    ax.bar(
        summary["mode"],
        summary["agreement_rate"],
    )
    ax.set_title("Agreement rate by negotiation mode")
    ax.set_xlabel("Negotiation mode")
    ax.set_ylabel("Agreement rate")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(output_file)
    plt.close(fig)


def plot_mode_comparison_rounds(
    dataframe: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Plot average rounds used by negotiation mode.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    summary = summarize_negotiation_modes(dataframe)

    fig, ax = plt.subplots()
    ax.bar(
        summary["mode"],
        summary["average_rounds_used"],
    )
    ax.set_title("Average rounds used by negotiation mode")
    ax.set_xlabel("Negotiation mode")
    ax.set_ylabel("Average rounds used")
    fig.tight_layout()
    fig.savefig(output_file)
    plt.close(fig)


def _validate_mode_comparison_dataframe(dataframe: pd.DataFrame) -> None:
    """
    Validate that the input CSV contains the required columns.
    """
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Negotiation mode comparison CSV is missing required columns: {missing}"
        )


def _get_best_mode(
    summary: pd.DataFrame,
    column: str,
    higher_is_better: bool,
) -> str:
    """
    Return the mode with the best value for a given summary column.
    """
    if summary.empty:
        return "unknown"

    index = summary[column].idxmax() if higher_is_better else summary[column].idxmin()

    return str(summary.loc[index, "mode"])


def _markdown_relative_path(
    source_path: Path,
    target_path: Path,
) -> str:
    """
    Return a Markdown-friendly relative path from the report to an asset.
    """
    source_directory = source_path.parent.resolve()
    target = target_path.resolve()

    try:
        relative_path = target.relative_to(source_directory)
    except ValueError:
        relative_path = Path(*Path(target).parts[len(Path.cwd().resolve().parts) :])

    return relative_path.as_posix()
