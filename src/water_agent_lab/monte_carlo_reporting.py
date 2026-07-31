from pathlib import Path

import pandas as pd

from water_agent_lab.reporting import dataframe_to_markdown_table


REQUIRED_MONTE_CARLO_COLUMNS = {
    "run_index",
    "scenario_name",
    "available_water",
    "initial_strategy",
    "agreement_reached",
    "rounds_used",
    "final_conflict_score",
    "final_fairness_score",
    "final_minimum_satisfaction_score",
    "final_shortage_score",
    "final_mediator_action",
}


def load_monte_carlo_results(input_path: str | Path) -> pd.DataFrame:
    """
    Load Monte Carlo results from CSV.
    """
    path = Path(input_path)
    dataframe = pd.read_csv(path)

    missing_columns = REQUIRED_MONTE_CARLO_COLUMNS - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required Monte Carlo columns: {missing}")

    return dataframe


def summarize_monte_carlo_results(dataframe: pd.DataFrame) -> dict[str, float | int]:
    """
    Compute high-level Monte Carlo summary statistics.
    """
    agreement_series = dataframe["agreement_reached"].astype(str).str.lower()

    agreement_count = int(agreement_series.isin({"true", "1", "yes"}).sum())
    total_runs = int(len(dataframe))

    return {
        "total_runs": total_runs,
        "agreement_count": agreement_count,
        "agreement_rate": agreement_count / total_runs if total_runs > 0 else 0.0,
        "average_final_conflict": float(dataframe["final_conflict_score"].mean()),
        "average_final_fairness": float(dataframe["final_fairness_score"].mean()),
        "average_minimum_satisfaction": float(
            dataframe["final_minimum_satisfaction_score"].mean()
        ),
        "average_shortage": float(dataframe["final_shortage_score"].mean()),
        "average_rounds_used": float(dataframe["rounds_used"].mean()),
    }


def build_mediator_action_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Count final mediator actions.
    """
    action_counts = (
        dataframe["final_mediator_action"]
        .value_counts()
        .rename_axis("mediator_action")
        .reset_index(name="count")
    )

    action_counts["share"] = action_counts["count"] / len(dataframe)

    return action_counts


def generate_monte_carlo_report(
    input_path: str | Path,
    output_path: str | Path,
) -> None:
    """
    Generate a Markdown report from Monte Carlo results.
    """
    dataframe = load_monte_carlo_results(input_path)
    summary = summarize_monte_carlo_results(dataframe)
    mediator_actions = build_mediator_action_summary(dataframe)

    summary_table = pd.DataFrame(
        [
            {"metric": "total_runs", "value": summary["total_runs"]},
            {"metric": "agreement_count", "value": summary["agreement_count"]},
            {"metric": "agreement_rate", "value": f"{summary['agreement_rate']:.2f}"},
            {
                "metric": "average_final_conflict",
                "value": f"{summary['average_final_conflict']:.3f}",
            },
            {
                "metric": "average_final_fairness",
                "value": f"{summary['average_final_fairness']:.3f}",
            },
            {
                "metric": "average_minimum_satisfaction",
                "value": f"{summary['average_minimum_satisfaction']:.3f}",
            },
            {
                "metric": "average_shortage",
                "value": f"{summary['average_shortage']:.3f}",
            },
            {
                "metric": "average_rounds_used",
                "value": f"{summary['average_rounds_used']:.2f}",
            },
        ]
    )

    content = f"""# Monte Carlo Mock LLM Negotiation Report

This report summarizes repeated mock LLM negotiations over scenario variations.

## Summary

{dataframe_to_markdown_table(summary_table)}

## Final mediator actions

{dataframe_to_markdown_table(mediator_actions)}

## Interpretation

Monte Carlo simulation helps evaluate how robust the negotiation system is under small changes in scenario conditions.

A high agreement rate suggests that the negotiation mechanism often finds acceptable allocations.

A high average conflict score suggests that stakeholders frequently remain below minimum acceptable water levels.

Average rounds used indicates how quickly negotiations converge.

"""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
