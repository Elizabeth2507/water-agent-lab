from collections.abc import Callable
from pathlib import Path

from water_agent_lab.data_sources import (
    HubEauHydrometryDataSource,
    MockDroughtDataSource,
    ScenarioDataSource,
    SyntheticScenarioDataSource,
    VigiEauDataSource,
)


DataSourceFactory = Callable[[Path], ScenarioDataSource]


DATA_SOURCE_REGISTRY: dict[str, DataSourceFactory] = {
    "synthetic": lambda path: SyntheticScenarioDataSource(path),
    "mock": lambda path: MockDroughtDataSource(path),
    "vigieau-sample": lambda path: VigiEauDataSource(sample_response_path=path),
    "hubeau-sample": lambda path: HubEauHydrometryDataSource(sample_response_path=path),
}


def get_data_source_names() -> list[str]:
    """
    Return available data source names.
    """
    return list(DATA_SOURCE_REGISTRY.keys())


def get_data_source(source_name: str, path: str | Path) -> ScenarioDataSource:
    """
    Create a data source instance by name.
    """
    try:
        factory = DATA_SOURCE_REGISTRY[source_name]
    except KeyError as error:
        available = ", ".join(get_data_source_names())
        raise ValueError(
            f"Unknown data source '{source_name}'. Available data sources: {available}."
        ) from error

    return factory(Path(path))
