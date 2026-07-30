from pathlib import Path

import pytest
from pydantic import ValidationError

from water_agent_lab.agent_memory import (
    AgentMemory,
    AgentMemoryEntry,
    load_agent_memory_json,
    save_agent_memory_json,
)


def test_agent_memory_entry_validates_importance() -> None:
    with pytest.raises(ValidationError):
        AgentMemoryEntry(
            round_number=1,
            stakeholder_name="agriculture",
            event_type="decision",
            content="Agriculture rejected the proposal.",
            importance=1.5,
        )


def test_agent_memory_add_entry() -> None:
    memory = AgentMemory()

    memory.add(
        round_number=1,
        stakeholder_name="agriculture",
        event_type="decision",
        content="Agriculture rejected the proposal.",
        importance=0.8,
    )

    assert len(memory.entries) == 1
    assert memory.entries[0].stakeholder_name == "agriculture"
    assert memory.entries[0].event_type == "decision"


def test_agent_memory_recent_entries() -> None:
    memory = AgentMemory()

    memory.add(1, "agriculture", "decision", "Round 1 decision")
    memory.add(2, "urban", "decision", "Round 2 decision")
    memory.add(3, "ecosystem", "decision", "Round 3 decision")

    recent_entries = memory.recent(limit=2)

    assert len(recent_entries) == 2
    assert recent_entries[0].round_number == 2
    assert recent_entries[1].round_number == 3


def test_agent_memory_for_stakeholder() -> None:
    memory = AgentMemory()

    memory.add(1, "agriculture", "decision", "Agriculture rejected.")
    memory.add(1, "urban", "decision", "Urban was concerned.")
    memory.add(2, "agriculture", "concession", "Agriculture received more water.")

    agriculture_memory = memory.for_stakeholder("agriculture")

    assert len(agriculture_memory) == 2
    assert all(entry.stakeholder_name == "agriculture" for entry in agriculture_memory)


def test_agent_memory_important_entries() -> None:
    memory = AgentMemory()

    memory.add(1, "agriculture", "decision", "Low importance.", importance=0.3)
    memory.add(1, "ecosystem", "rejection", "High importance.", importance=0.9)

    important_entries = memory.important(threshold=0.7)

    assert len(important_entries) == 1
    assert important_entries[0].stakeholder_name == "ecosystem"


def test_agent_memory_summarize() -> None:
    memory = AgentMemory()

    memory.add(
        1,
        "agriculture",
        "decision",
        "Agriculture rejected because allocation was below minimum.",
    )

    summary = memory.summarize(stakeholder_name="agriculture")

    assert "Round 1" in summary
    assert "agriculture" in summary
    assert "below minimum" in summary


def test_agent_memory_summarize_empty_memory() -> None:
    memory = AgentMemory()

    assert memory.summarize() == "No relevant memory entries."


def test_save_and_load_agent_memory(tmp_path: Path) -> None:
    memory = AgentMemory()

    memory.add(
        round_number=1,
        stakeholder_name="ecosystem",
        event_type="rejection",
        content="Ecosystem rejected because allocation was below ecological minimum.",
        importance=0.9,
    )

    output_path = tmp_path / "agent_memory.json"

    save_agent_memory_json(
        memory=memory,
        output_path=output_path,
    )

    loaded_memory = load_agent_memory_json(output_path)

    assert len(loaded_memory.entries) == 1
    assert loaded_memory.entries[0].stakeholder_name == "ecosystem"
    assert loaded_memory.entries[0].importance == 0.9
