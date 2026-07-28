from water_agent_lab.dashboard import summarize_registry


def test_summarize_registry() -> None:
    records = [
        {
            "run_id": "run-1",
            "command": "run-all",
            "outputs": {
                "results": "outputs/results.csv",
            },
        },
        {
            "run_id": "run-2",
            "command": "negotiate-multi",
            "outputs": {
                "negotiation_history": "outputs/history.json",
            },
        },
        {
            "run_id": "run-3",
            "command": "reproduce-run-all",
            "reproduced_from_run_id": "run-1",
            "outputs": {
                "results": "outputs/reproduced_results.csv",
            },
        },
    ]

    summary = summarize_registry(records)

    assert summary["total_runs"] == 3
    assert summary["command_counts"]["run-all"] == 1
    assert summary["command_counts"]["negotiate-multi"] == 1
    assert summary["command_counts"]["reproduce-run-all"] == 1
    assert summary["reproduced_runs"] == 1
    assert summary["output_counts"]["results"] == 2
    assert summary["output_counts"]["negotiation_history"] == 1
    assert summary["latest_run"]["run_id"] == "run-3"


def test_summarize_empty_registry() -> None:
    summary = summarize_registry([])

    assert summary["total_runs"] == 0
    assert summary["command_counts"] == {}
    assert summary["reproduced_runs"] == 0
    assert summary["output_counts"] == {}
    assert summary["latest_run"] is None
