from collections import Counter
from typing import Any


def summarize_registry(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Summarize experiment registry records for dashboard display.
    """
    command_counts = Counter(
        str(record.get("command", "unknown")) for record in records
    )

    reproduced_runs = [
        record for record in records if "reproduced_from_run_id" in record
    ]

    output_counts = Counter()

    for record in records:
        outputs = record.get("outputs", {})

        if isinstance(outputs, dict):
            for output_name in outputs:
                output_counts[output_name] += 1

    latest_run = records[-1] if records else None

    return {
        "total_runs": len(records),
        "command_counts": dict(command_counts),
        "reproduced_runs": len(reproduced_runs),
        "output_counts": dict(output_counts),
        "latest_run": latest_run,
    }
