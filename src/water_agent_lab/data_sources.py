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
