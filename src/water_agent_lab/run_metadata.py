from datetime import datetime, timezone
from uuid import uuid4


def create_run_metadata(command: str) -> dict[str, str]:
    """
    Create metadata for one CLI run.
    """
    return {
        "run_id": str(uuid4()),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": command,
    }
