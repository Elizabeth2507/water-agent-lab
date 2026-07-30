from typing import Any

from water_agent_lab.agent_models import AgentDecision, AgentProfile, AgentState
from water_agent_lab.llm_backends import LLMBackend
from water_agent_lab.llm_parsing import parse_agent_decision
from water_agent_lab.llm_prompts import (
    build_stakeholder_system_prompt,
    build_stakeholder_user_prompt,
)
from water_agent_lab.models import AllocationProposal, ScenarioConfig, StakeholderConfig


def build_default_agent_profile(stakeholder: StakeholderConfig) -> AgentProfile:
    """
    Build a simple default LLM-agent profile for a stakeholder.

    This keeps the LLM stakeholder agent usable even before richer profile
    loading is added.
    """
    return AgentProfile(
        name=stakeholder.name,
        role=f"Represents {stakeholder.name} water interests",
        goals=[
            f"Protect the minimum water needs of {stakeholder.name}.",
            "Negotiate under drought constraints.",
        ],
        constraints=[
            "Available water is limited.",
            "Other stakeholders also have minimum acceptable needs.",
        ],
        negotiation_style="balanced",
    )


class LLMStakeholderAgent:
    """
    Stakeholder agent backed by an LLM-style backend.

    The backend can be a real local/API model or a deterministic mock backend.
    The backend response is parsed and validated into an AgentDecision.
    """

    def __init__(
        self,
        profile: AgentProfile,
        backend: LLMBackend,
        state: AgentState | None = None,
    ) -> None:
        self.profile = profile
        self.backend = backend
        self.state = state or AgentState()

    def evaluate_allocation(
        self,
        stakeholder: StakeholderConfig,
        proposal: AllocationProposal,
        round_number: int = 1,
    ) -> AgentDecision:
        """
        Evaluate an allocation proposal from this stakeholder's perspective.
        """
        allocated_water = proposal.allocations.get(stakeholder.name, 0.0)

        prompt = self._build_prompt(
            stakeholder=stakeholder,
            allocated_water=allocated_water,
            round_number=round_number,
        )

        generation = self.backend.generate(prompt)

        decision = parse_agent_decision(
            generation.text,
            stakeholder.name,
        )

        self._update_state(decision)

        return decision

    def _build_prompt(
        self,
        stakeholder: StakeholderConfig,
        allocated_water: float,
        round_number: int,
    ) -> str:
        """
        Build the prompt sent to the LLM backend.

        The system prompt uses the stakeholder profile. The user prompt contains
        the concrete allocation situation.
        """
        system_prompt = build_stakeholder_system_prompt(
            profile=self.profile,
        )

        user_prompt = build_stakeholder_user_prompt(
            stakeholder=stakeholder,
            state=self.state,
            allocated_water=allocated_water,
            round_number=round_number,
        )

        return f"{system_prompt}\n\n{user_prompt}"

    def _update_state(self, decision: AgentDecision) -> None:
        """
        Update lightweight internal state after a stakeholder decision.
        """
        self.state.last_status = decision.status

        if decision.status == "rejected":
            self.state.frustration = min(
                1.0,
                self.state.frustration + 0.2,
            )
            self.state.trust_in_mediator = max(
                0.0,
                self.state.trust_in_mediator - 0.1,
            )

        elif decision.status == "concerned":
            self.state.frustration = min(
                1.0,
                self.state.frustration + 0.1,
            )

        elif decision.status == "accepted":
            self.state.frustration = max(
                0.0,
                self.state.frustration - 0.1,
            )
            self.state.trust_in_mediator = min(
                1.0,
                self.state.trust_in_mediator + 0.1,
            )


def evaluate_llm_stakeholder_responses(
    scenario: ScenarioConfig,
    proposal: AllocationProposal,
    backend: LLMBackend,
    round_number: int = 1,
    profiles: dict[str, AgentProfile] | None = None,
) -> list[AgentDecision]:
    """
    Evaluate all stakeholders in a scenario using LLMStakeholderAgent.
    """
    decisions: list[AgentDecision] = []

    for stakeholder in scenario.stakeholders:
        profile = _get_profile_for_stakeholder(
            stakeholder=stakeholder,
            profiles=profiles,
        )

        agent = LLMStakeholderAgent(
            profile=profile,
            backend=backend,
        )

        decision = agent.evaluate_allocation(
            stakeholder=stakeholder,
            proposal=proposal,
            round_number=round_number,
        )

        decisions.append(decision)

    return decisions


def _get_profile_for_stakeholder(
    stakeholder: StakeholderConfig,
    profiles: dict[str, AgentProfile] | None,
) -> AgentProfile:
    """
    Return an explicit profile if available, otherwise build a default one.
    """
    if profiles is None:
        return build_default_agent_profile(stakeholder)

    return profiles.get(
        stakeholder.name,
        build_default_agent_profile(stakeholder),
    )


def decisions_to_rows(
    decisions: list[AgentDecision],
) -> list[dict[str, Any]]:
    """
    Convert AgentDecision objects into simple serializable rows.
    """
    return [decision.model_dump() for decision in decisions]
