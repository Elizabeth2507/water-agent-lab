import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


MemoryEventType = Literal[
    "proposal",
    "decision",
    "message",
    "concession",
    "agreement",
    "rejection",
    "summary",
]


class AgentMemoryEntry(BaseModel):
    """
    One structured memory entry for an agent or negotiation.
    """

    round_number: int = Field(gt=0)
    stakeholder_name: str
    event_type: MemoryEventType
    content: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class AgentMemory(BaseModel):
    """
    Structured memory store for AI-agent negotiation.

    This is intentionally simple and deterministic.
    It can later be extended with embeddings, retrieval scores,
    long-term memory, and memory compression.
    """

    entries: list[AgentMemoryEntry] = Field(default_factory=list)

    def add_entry(self, entry: AgentMemoryEntry) -> None:
        """
        Add one memory entry.
        """
        self.entries.append(entry)

    def add(
        self,
        round_number: int,
        stakeholder_name: str,
        event_type: MemoryEventType,
        content: str,
        importance: float = 0.5,
    ) -> None:
        """
        Convenience method for adding a memory entry.
        """
        self.add_entry(
            AgentMemoryEntry(
                round_number=round_number,
                stakeholder_name=stakeholder_name,
                event_type=event_type,
                content=content,
                importance=importance,
            )
        )

    def recent(self, limit: int = 5) -> list[AgentMemoryEntry]:
        """
        Return the most recent memory entries.
        """
        if limit <= 0:
            return []

        return self.entries[-limit:]

    def for_stakeholder(
        self,
        stakeholder_name: str,
        limit: int | None = None,
    ) -> list[AgentMemoryEntry]:
        """
        Return memory entries for a specific stakeholder.
        """
        matching_entries = [
            entry
            for entry in self.entries
            if entry.stakeholder_name == stakeholder_name
        ]

        if limit is None:
            return matching_entries

        if limit <= 0:
            return []

        return matching_entries[-limit:]

    def important(self, threshold: float = 0.7) -> list[AgentMemoryEntry]:
        """
        Return entries with importance greater than or equal to a threshold.
        """
        return [entry for entry in self.entries if entry.importance >= threshold]

    def summarize(
        self,
        stakeholder_name: str | None = None,
        limit: int = 5,
    ) -> str:
        """
        Build a compact text summary of recent memory entries.

        This summary can be inserted into a future LLM prompt.
        """
        if stakeholder_name is None:
            entries = self.recent(limit=limit)
        else:
            entries = self.for_stakeholder(
                stakeholder_name=stakeholder_name,
                limit=limit,
            )

        if not entries:
            return "No relevant memory entries."

        lines = []

        for entry in entries:
            lines.append(
                f"Round {entry.round_number} | "
                f"{entry.stakeholder_name} | "
                f"{entry.event_type} | "
                f"{entry.content}"
            )

        return "\n".join(lines)


def save_agent_memory_json(
    memory: AgentMemory,
    output_path: str | Path,
) -> None:
    """
    Save agent memory to JSON.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            memory.model_dump(),
            file,
            indent=2,
            ensure_ascii=False,
        )


def load_agent_memory_json(
    input_path: str | Path,
) -> AgentMemory:
    """
    Load agent memory from JSON.
    """
    path = Path(input_path)

    with path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    return AgentMemory.model_validate(raw_data)
