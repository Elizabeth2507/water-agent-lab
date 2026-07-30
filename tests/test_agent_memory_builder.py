from water_agent_lab.agent_memory_builder import build_memory_from_transcript
from water_agent_lab.llm_negotiation import run_mock_llm_multi_round_negotiation


def test_build_memory_from_transcript() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    memory = build_memory_from_transcript(transcript)

    assert len(memory.entries) > 0

    stakeholder_names = {entry.stakeholder_name for entry in memory.entries}

    assert "agriculture" in stakeholder_names
    assert "ecosystem" in stakeholder_names


def test_memory_from_transcript_contains_rejections() -> None:
    transcript = run_mock_llm_multi_round_negotiation(
        config_path="configs/drought_mvp.yaml",
        initial_strategy="proportional",
    )

    memory = build_memory_from_transcript(transcript)

    rejection_entries = [
        entry for entry in memory.entries if entry.event_type == "rejection"
    ]

    assert len(rejection_entries) > 0
    assert all(entry.importance >= 0.7 for entry in rejection_entries)
