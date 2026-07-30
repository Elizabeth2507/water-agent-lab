from water_agent_lab.agent_memory import AgentMemory
from water_agent_lab.agent_transcript import AgentNegotiationTranscript


def build_memory_from_transcript(
    transcript: AgentNegotiationTranscript,
) -> AgentMemory:
    """
    Build structured agent memory from a negotiation transcript.
    """
    memory = AgentMemory()

    for round_transcript in transcript.rounds:
        round_number = round_transcript.round_number

        for decision in round_transcript.decisions:
            event_type = "rejection" if decision.status == "rejected" else "decision"

            importance = 0.9 if decision.status == "rejected" else 0.6

            memory.add(
                round_number=round_number,
                stakeholder_name=decision.stakeholder_name,
                event_type=event_type,
                content=decision.argument,
                importance=importance,
            )

        for message in round_transcript.messages:
            memory.add(
                round_number=round_number,
                stakeholder_name=message.sender,
                event_type="message",
                content=message.content,
                importance=0.5,
            )

    return memory
