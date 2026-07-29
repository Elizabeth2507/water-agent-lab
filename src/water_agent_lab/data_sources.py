import json
from typing import Any

from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from water_agent_lab.config import load_scenario_config
from water_agent_lab.models import ScenarioConfig


class DataSourceMetadata(BaseModel):
    """
    Metadata describing where a scenario came from.
    """

    source_name: str
    source_type: str
    source_path: str | None = None
    source_url: str | None = None
    description: str | None = None


class ScenarioDataSource(Protocol):
    """
    Interface for objects that can produce a ScenarioConfig.
    """

    def load_scenario(self) -> ScenarioConfig:
        """
        Load or construct a scenario.
        """

    def metadata(self) -> DataSourceMetadata:
        """
        Return metadata about the scenario source.
        """


class SyntheticScenarioDataSource:
    """
    Scenario data source backed by a local YAML config file.
    """

    def __init__(self, config_path: str | Path) -> None:
        self.config_path = Path(config_path)

    def load_scenario(self) -> ScenarioConfig:
        return load_scenario_config(self.config_path)

    def metadata(self) -> DataSourceMetadata:
        return DataSourceMetadata(
            source_name="synthetic_yaml",
            source_type="local_yaml",
            source_path=self.config_path.as_posix(),
            description="Synthetic scenario loaded from a local YAML config.",
        )


class MockDroughtDataSource:
    """
    Mock drought data source backed by a local JSON snapshot.

    This simulates the shape of a future real-data adapter while keeping tests
    deterministic and offline.
    """

    def __init__(self, snapshot_path: str | Path) -> None:
        self.snapshot_path = Path(snapshot_path)

    def load_raw_snapshot(self) -> dict[str, Any]:
        """
        Load the raw mock drought snapshot.
        """
        with self.snapshot_path.open("r", encoding="utf-8") as file:
            raw_snapshot = json.load(file)

        if not isinstance(raw_snapshot, dict):
            raise ValueError("Mock drought snapshot must contain a JSON object.")

        return raw_snapshot

    def load_scenario(self) -> ScenarioConfig:
        """
        Convert the mock drought snapshot into a ScenarioConfig.
        """
        raw_snapshot = self.load_raw_snapshot()

        scenario_data = {
            "scenario_name": (
                f"{raw_snapshot['region'].lower()}_"
                f"{raw_snapshot['drought_level']}_mock_snapshot"
            ),
            "country": raw_snapshot["country"],
            "region": raw_snapshot["region"],
            "drought_level": raw_snapshot["drought_level"],
            "available_water": raw_snapshot["available_water"],
            "max_rounds": raw_snapshot["max_rounds"],
            "stakeholders": raw_snapshot["stakeholders"],
        }

        return ScenarioConfig.model_validate(scenario_data)

    def metadata(self) -> DataSourceMetadata:
        return DataSourceMetadata(
            source_name="mock_drought_snapshot",
            source_type="local_json_snapshot",
            source_path=self.snapshot_path.as_posix(),
            description=(
                "Mock drought snapshot used to simulate a future real-data source."
            ),
        )
