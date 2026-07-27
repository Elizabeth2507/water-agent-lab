import json
import logging
from pathlib import Path
from typing import Any


LOGGER_NAME = "water_agent_lab"


class JsonFormatter(logging.Formatter):
    """
    Format log records as JSON lines.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "event"):
            log_data["event"] = record.event

        if hasattr(record, "context"):
            log_data["context"] = record.context

        return json.dumps(log_data, ensure_ascii=False)


def configure_logging(log_file: str | Path | None = None) -> logging.Logger:
    """
    Configure the WaterAgentLab logger.

    If log_file is provided, logs are written as JSON lines to that file.
    Otherwise, logs are written to the console.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = JsonFormatter()

    if log_file is None:
        handler: logging.Handler = logging.StreamHandler()
    else:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(path, encoding="utf-8")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def log_event(
    logger: logging.Logger,
    event: str,
    message: str,
    **context: Any,
) -> None:
    """
    Log a structured event with optional context.
    """
    logger.info(
        message,
        extra={
            "event": event,
            "context": context,
        },
    )
