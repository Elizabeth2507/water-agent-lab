import json
from pathlib import Path

from water_agent_lab.logging_utils import configure_logging, log_event


def test_structured_logging_to_file(tmp_path: Path) -> None:
    log_path = tmp_path / "test.log"
    logger = configure_logging(log_path)

    log_event(
        logger,
        event="test_event",
        message="Test message.",
        scenario_name="test_scenario",
        strategy="proportional",
    )

    lines = log_path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1

    log_data = json.loads(lines[0])

    assert log_data["level"] == "INFO"
    assert log_data["logger"] == "water_agent_lab"
    assert log_data["message"] == "Test message."
    assert log_data["event"] == "test_event"
    assert log_data["context"]["scenario_name"] == "test_scenario"
    assert log_data["context"]["strategy"] == "proportional"
