from water_agent_lab.run_metadata import create_run_metadata


def test_create_run_metadata() -> None:
    metadata = create_run_metadata(command="simulate")

    assert "run_id" in metadata
    assert "created_at_utc" in metadata
    assert metadata["command"] == "simulate"
    assert len(metadata["run_id"]) > 0
