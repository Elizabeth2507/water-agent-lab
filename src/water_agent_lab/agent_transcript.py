import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from water_agent_lab.agent_models import AgentDecision, AgentMessage, AgentState
from water_agent_lab.mediator import MediatorRecommendation
from water_agent_lab.models import AllocationProposal, SimulationResult


class AgentRoundTranscript(BaseModel):
    """
    Transcript for one AI-agent negotiation round.
    """

    round_number: int = Field(gt=0)
    strategy: str
    proposal: AllocationProposal
    decisions: list[AgentDecision]
    messages: list[AgentMessage] = Field(default_factory=list)
    result: SimulationResult
    memory_summary: str | None = None
    agent_states: dict[str, AgentState] = Field(default_factory=dict)
    mediator_recommendation: MediatorRecommendation | None = None
    counterproposal_summary: Any | None = None
    counterproposal_adjusted_proposal: AllocationProposal | None = None
    counterproposal_adjusted_result: SimulationResult | None = None
    normal_revised_strategy: str | None = None
    normal_revised_proposal: AllocationProposal | None = None
    normal_revised_result: SimulationResult | None = None


class AgentNegotiationTranscript(BaseModel):
    """
    Full transcript for an AI-agent negotiation.
    """

    scenario_name: str
    country: str
    region: str
    drought_level: str
    initial_strategy: str
    agreement_reached: bool
    rounds_used: int = Field(gt=0)
    max_rounds: int = Field(gt=0)
    backend_name: str
    model_name: str
    rounds: list[AgentRoundTranscript]


def save_agent_transcript_json(
    transcript: AgentNegotiationTranscript,
    output_path: str | Path,
) -> None:
    """
    Save an AI-agent negotiation transcript as JSON.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            transcript.model_dump(),
            file,
            indent=2,
            ensure_ascii=False,
        )


def load_agent_transcript_json(
    input_path: str | Path,
) -> AgentNegotiationTranscript:
    """
    Load an AI-agent negotiation transcript from JSON.
    """
    path = Path(input_path)

    with path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    return AgentNegotiationTranscript.model_validate(raw_data)
