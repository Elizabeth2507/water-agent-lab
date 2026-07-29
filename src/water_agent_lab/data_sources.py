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


class VigiEauDataSource:
    """
    VigiEau drought restriction data source skeleton.

    This class prepares the project for future live VigiEau API integration.
    For now, it can transform a simplified local VigiEau-style sample response
    into a ScenarioConfig.
    """

    BASE_URL = "https://api.vigieau.beta.gouv.fr"

    DEFAULT_REQUESTS = {
        "agriculture": 50.0,
        "urban": 35.0,
        "industry": 25.0,
        "ecosystem": 20.0,
    }

    DEFAULT_MINIMUMS = {
        "agriculture": 35.0,
        "urban": 28.0,
        "industry": 15.0,
        "ecosystem": 18.0,
    }

    DROUGHT_LEVEL_MAPPING = {
        "vigilance": "mild",
        "alerte": "moderate",
        "alerte_renforcee": "severe",
        "crise": "extreme",
    }

    def __init__(
        self,
        sample_response_path: str | Path | None = None,
        api_base_url: str = BASE_URL,
    ) -> None:
        self.sample_response_path = (
            Path(sample_response_path) if sample_response_path is not None else None
        )
        self.api_base_url = api_base_url

    def metadata(self) -> DataSourceMetadata:
        return DataSourceMetadata(
            source_name="vigieau",
            source_type="public_api_skeleton",
            source_path=(
                str(self.sample_response_path)
                if self.sample_response_path is not None
                else None
            ),
            source_url=self.api_base_url,
            description=(
                "Skeleton adapter for VigiEau drought restriction data. "
                "Currently supports local simplified sample responses."
            ),
        )

    def load_sample_response(self) -> dict[str, Any]:
        """
        Load a simplified local VigiEau-style sample response.
        """
        if self.sample_response_path is None:
            raise ValueError("No sample_response_path was provided.")

        with self.sample_response_path.open("r", encoding="utf-8") as file:
            raw_response = json.load(file)

        if not isinstance(raw_response, dict):
            raise ValueError("VigiEau sample response must contain a JSON object.")

        return raw_response

    def restriction_level_to_drought_level(self, restriction_level: str) -> str:
        """
        Map a VigiEau-style restriction level to an internal drought level.
        """
        return self.DROUGHT_LEVEL_MAPPING.get(restriction_level, "unknown")

    def response_to_scenario(self, response: dict[str, Any]) -> ScenarioConfig:
        """
        Convert a simplified VigiEau-style response into a ScenarioConfig.
        """
        restriction_level = str(response["restriction_level"])
        drought_level = self.restriction_level_to_drought_level(restriction_level)

        profiles = response["profiles"]

        stakeholders = []

        for stakeholder_name, profile_data in profiles.items():
            stakeholders.append(
                {
                    "name": stakeholder_name,
                    "requested_water": self.DEFAULT_REQUESTS[stakeholder_name],
                    "minimum_acceptable_water": self.DEFAULT_MINIMUMS[stakeholder_name],
                    "priority": profile_data["priority"],
                }
            )

        scenario_data = {
            "scenario_name": (
                f"{response['region'].lower()}_{drought_level}_vigieau_sample"
            ),
            "country": response["country"],
            "region": response["region"],
            "drought_level": drought_level,
            "available_water": response["available_water_proxy"],
            "max_rounds": response["max_rounds"],
            "stakeholders": stakeholders,
        }

        return ScenarioConfig.model_validate(scenario_data)

    def load_scenario(self) -> ScenarioConfig:
        """
        Load a scenario from the local sample response.
        """
        response = self.load_sample_response()
        return self.response_to_scenario(response)
