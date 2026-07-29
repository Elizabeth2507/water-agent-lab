from typing import Literal

from pydantic import BaseModel, Field, model_validator


AgentStatus = Literal["accepted", "concerned", "rejected"]
MessageType = Literal[
    "proposal",
    "response",
    "counterproposal",
    "mediator_summary",
    "system",
]


class AgentProfile(BaseModel):
    """
    Stable identity and goals of a stakeholder agent.

    This profile should not change during a negotiation.
    """

    name: str
    role: str
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    negotiation_style: str = "balanced"


class AgentState(BaseModel):
    """
    Mutable internal state of an agent during a negotiation.
    """

    frustration: float = Field(default=0.0, ge=0.0, le=1.0)
    trust_in_mediator: float = Field(default=0.5, ge=0.0, le=1.0)
    concessions_made: int = Field(default=0, ge=0)
    last_status: AgentStatus | None = None


class AgentMessage(BaseModel):
    """
    Structured message exchanged during a negotiation.
    """

    sender: str
    recipient: str
    round_number: int = Field(gt=0)
    message_type: MessageType
    content: str
    requested_water_change: float | None = None

    @model_validator(mode="after")
    def counterproposal_requires_requested_change(self) -> "AgentMessage":
        if (
            self.message_type == "counterproposal"
            and self.requested_water_change is None
        ):
            raise ValueError("counterproposal messages require requested_water_change")
        return self


class AgentDecision(BaseModel):
    """
    Structured decision produced by an agent after evaluating a proposal.
    """

    stakeholder_name: str
    status: AgentStatus
    argument: str
    requested_extra_water: float = Field(default=0.0, ge=0.0)
    willingness_to_compromise: float = Field(default=0.5, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def rejected_decision_requires_argument(self) -> "AgentDecision":
        if self.status == "rejected" and not self.argument.strip():
            raise ValueError("rejected decisions require a non-empty argument")
        return self
