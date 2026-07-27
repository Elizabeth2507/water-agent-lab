from pathlib import Path

import pandas as pd


REQUIRED_REPORT_COLUMNS = {
    "scenario_name",
    "drought_level",
    "strategy",
    "fairness_score",
    "conflict_score",
    "minimum_satisfaction_score",
    "shortage_score",
    "agreement_reached",
}


def load_experiment_results(input_path: str | Path) -> pd.DataFrame:
    """
    Load experiment results from a CSV file.

    The expected input is usually produced by the `run-all` command.
    """
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Experiment results file not found: {path}")

    dataframe = pd.read_csv(path)

    missing_columns = REQUIRED_REPORT_COLUMNS - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    return dataframe


def normalize_agreement_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Convert agreement_reached to a boolean-like column.

    This makes the report robust whether the CSV stores booleans as:
    True/False, true/false, 1/0, or yes/no.
    """
    normalized = dataframe.copy()

    normalized["agreement_reached"] = (
        normalized["agreement_reached"]
        .astype(str)
        .str.lower()
        .isin({"true", "1", "yes"})
    )

    return normalized


def summarize_by_strategy(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize experiment results by allocation strategy.
    """
    normalized = normalize_agreement_column(dataframe)

    return (
        normalized.groupby("strategy")
        .agg(
            runs=("scenario_name", "count"),
            agreement_rate=("agreement_reached", "mean"),
            average_fairness=("fairness_score", "mean"),
            average_conflict=("conflict_score", "mean"),
            average_minimum_satisfaction=(
                "minimum_satisfaction_score",
                "mean",
            ),
            average_shortage=("shortage_score", "mean"),
        )
        .reset_index()
    )


def summarize_by_drought_level(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize experiment results by drought level.
    """
    normalized = normalize_agreement_column(dataframe)

    return (
        normalized.groupby("drought_level")
        .agg(
            runs=("scenario_name", "count"),
            agreement_rate=("agreement_reached", "mean"),
            average_fairness=("fairness_score", "mean"),
            average_conflict=("conflict_score", "mean"),
            average_minimum_satisfaction=(
                "minimum_satisfaction_score",
                "mean",
            ),
            average_shortage=("shortage_score", "mean"),
        )
        .reset_index()
    )


def find_best_strategy_by_conflict(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Find the best strategy for each scenario using conflict score first.

    Tie-breaking order:
    1. lower conflict score
    2. higher minimum satisfaction score
    3. higher fairness score
    4. lower shortage score
    """
    sorted_dataframe = dataframe.sort_values(
        by=[
            "scenario_name",
            "conflict_score",
            "minimum_satisfaction_score",
            "fairness_score",
            "shortage_score",
        ],
        ascending=[
            True,
            True,
            False,
            False,
            True,
        ],
    )

    return sorted_dataframe.groupby("scenario_name").head(1).reset_index(drop=True)


def dataframe_to_markdown_table(dataframe: pd.DataFrame) -> str:
    """
    Convert a dataframe to a Markdown table.

    Values are rounded to make reports easier to read.
    """
    display_dataframe = dataframe.copy()

    numeric_columns = display_dataframe.select_dtypes(include=["float"]).columns

    for column in numeric_columns:
        display_dataframe[column] = display_dataframe[column].round(3)

    return display_dataframe.to_markdown(index=False)


def generate_experiment_report(
    input_path: str | Path,
    output_path: str | Path,
) -> None:
    """
    Generate a Markdown experiment summary report from a CSV results file.
    """
    dataframe = load_experiment_results(input_path)

    strategy_summary = summarize_by_strategy(dataframe)
    drought_summary = summarize_by_drought_level(dataframe)
    best_strategies = find_best_strategy_by_conflict(dataframe)

    drought_levels = ", ".join(
        sorted(dataframe["drought_level"].astype(str).unique())
    )

    content_parts = [
        "# WaterAgentLab Experiment Report",
        "",
        "This report summarizes allocation strategy results produced by WaterAgentLab.",
        "",
        "## Input file",
        "",
        "```text",
        str(input_path),
        "```",
        "",
        "## Overview",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Number of rows | `{len(dataframe)}` |",
        f"| Number of scenarios | `{dataframe['scenario_name'].nunique()}` |",
        f"| Number of strategies | `{dataframe['strategy'].nunique()}` |",
        f"| Drought levels | `{drought_levels}` |",
        "",
        "## Summary by strategy",
        "",
        dataframe_to_markdown_table(strategy_summary),
        "",
        "## Summary by drought level",
        "",
        dataframe_to_markdown_table(drought_summary),
        "",
        "## Best strategy per scenario",
        "",
        "The best strategy is selected by:",
        "",
        "1. Lower conflict score",
        "2. Higher minimum satisfaction score",
        "3. Higher fairness score",
        "4. Lower shortage score",
        "",
        dataframe_to_markdown_table(best_strategies),
        "",
        "## Interpretation guide",
        "",
        "| Metric | Meaning |",
        "|---|---|",
        "| `agreement_rate` | Share of runs where all stakeholders met minimum acceptable water |",
        "| `average_fairness` | Average fairness score across scenarios |",
        "| `average_conflict` | Average share of stakeholders below minimum acceptable water |",
        "| `average_minimum_satisfaction` | Average satisfaction of minimum needs |",
        "| `average_shortage` | Average shortage pressure |",
        "",
        "A lower conflict score is usually the most important signal because it means fewer stakeholders fall below their minimum acceptable water.",
        "",
    ]

    content = "\n".join(content_parts)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")