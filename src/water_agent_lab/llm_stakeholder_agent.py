from typing import Any

from water_agent_lab.agent_memory import AgentMemory
from water_agent_lab.agent_models import AgentDecision, AgentProfile, AgentState
from water_agent_lab.llm_backends import LLMBackend, LLMGenerationRequest
from water_agent_lab.llm_parsing import parse_agent_decision
from water_agent_lab.llm_prompts import (
    build_stakeholder_system_prompt,
    build_stakeholder_user_prompt,
)
from water_agent_lab.models import AllocationProposal, ScenarioConfig, StakeholderConfig
from water_agent_lab.agent_state_manager import update_agent_state_from_decision


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
        memory: AgentMemory | None = None,
    ) -> None:
        self.profile = profile
        self.backend = backend
        self.state = state or AgentState()
        self.memory = memory

    def evaluate_allocation(
        self,
        stakeholder: StakeholderConfig,
        proposal: AllocationProposal,
        round_number: int = 1,
        scenario: ScenarioConfig | None = None,
    ) -> AgentDecision:
        """
        Evaluate an allocation proposal from this stakeholder's perspective.
        """
        request = self._build_request(
            stakeholder=stakeholder,
            proposal=proposal,
            round_number=round_number,
            scenario=scenario,
        )

        generation = self.backend.generate(request)

        decision = parse_agent_decision(
            generation.text,
            stakeholder.name,
        )

        self._update_state(decision)
        self._record_decision_in_memory(
            decision=decision,
            round_number=round_number,
        )

        return decision

    def evaluate_proposal(
        self,
        scenario: ScenarioConfig,
        stakeholder: StakeholderConfig,
        proposal: AllocationProposal,
        round_number: int = 1,
    ) -> AgentDecision:
        """
        Compatibility wrapper for older code that calls evaluate_proposal().
        """
        return self.evaluate_allocation(
            stakeholder=stakeholder,
            proposal=proposal,
            round_number=round_number,
            scenario=scenario,
        )

    def _build_request(
        self,
        stakeholder: StakeholderConfig,
        proposal: AllocationProposal,
        round_number: int,
        scenario: ScenarioConfig | None = None,
    ) -> LLMGenerationRequest:
        """
        Build the structured request sent to the LLM backend.

        The system prompt contains the stable agent role.
        The user prompt contains the scenario, proposal, state, and memory context.
        """
        system_prompt = build_stakeholder_system_prompt(
            profile=self.profile,
        )

        user_prompt = build_stakeholder_user_prompt(
            scenario=scenario,
            stakeholder=stakeholder,
            proposal=proposal,
            state=self.state,
            round_number=round_number,
            memory=self.memory,
        )

        return LLMGenerationRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def _update_state(self, decision: AgentDecision) -> None:
        """
        Update lightweight internal state after a stakeholder decision.
        """
        self.state = update_agent_state_from_decision(
            state=self.state,
            decision=decision,
        )

    # def _update_state(self, decision: AgentDecision) -> None:
    #     """
    #     Update lightweight internal state after a stakeholder decision.
    #     """
    #     self.state.last_status = decision.status

    #     if decision.status == "rejected":
    #         self.state.frustration = min(
    #             1.0,
    #             self.state.frustration + 0.2,
    #         )
    #         self.state.trust_in_mediator = max(
    #             0.0,
    #             self.state.trust_in_mediator - 0.1,
    #         )

    #     elif decision.status == "concerned":
    #         self.state.frustration = min(
    #             1.0,
    #             self.state.frustration + 0.1,
    #         )

    #     elif decision.status == "accepted":
    #         self.state.frustration = max(
    #             0.0,
    #             self.state.frustration - 0.1,
    #         )
    #         self.state.trust_in_mediator = min(
    #             1.0,
    #             self.state.trust_in_mediator + 0.1,
    #         )

    def _record_decision_in_memory(
        self,
        decision: AgentDecision,
        round_number: int,
    ) -> None:
        """
        Record the decision in optional memory if the memory object supports it.
        """
        if self.memory is None:
            return

        add_method = getattr(self.memory, "add", None)

        if callable(add_method):
            add_method(
                round_number=round_number,
                stakeholder_name=decision.stakeholder_name,
                event_type=_memory_event_type_from_decision(decision),
                content=decision.argument,
                importance=decision.willingness_to_compromise,
            )
            return

        payload = {
            "round_number": round_number,
            "stakeholder_name": decision.stakeholder_name,
            "status": decision.status,
            "argument": decision.argument,
            "requested_extra_water": decision.requested_extra_water,
            "willingness_to_compromise": decision.willingness_to_compromise,
        }

        for method_name in (
            "add_decision",
            "remember_decision",
            "add_event",
            "append",
        ):
            method = getattr(self.memory, method_name, None)

            if not callable(method):
                continue

            try:
                method(payload)
                return
            except TypeError:
                try:
                    method(decision)
                    return
                except TypeError:
                    continue


def evaluate_llm_stakeholder_responses(
    scenario: ScenarioConfig,
    proposal: AllocationProposal,
    backend: LLMBackend,
    round_number: int = 1,
    profiles: dict[str, AgentProfile] | None = None,
    memories: dict[str, AgentMemory] | None = None,
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

        memory = _get_memory_for_stakeholder(
            stakeholder=stakeholder,
            memories=memories,
        )

        agent = LLMStakeholderAgent(
            profile=profile,
            backend=backend,
            state=AgentState(),
            memory=memory,
        )

        decision = agent.evaluate_allocation(
            stakeholder=stakeholder,
            proposal=proposal,
            round_number=round_number,
            scenario=scenario,
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


def _get_memory_for_stakeholder(
    stakeholder: StakeholderConfig,
    memories: dict[str, AgentMemory] | None,
) -> AgentMemory | None:
    """
    Return stakeholder memory if available.
    """
    if memories is None:
        return None

    return memories.get(stakeholder.name)


def _memory_event_type_from_decision(decision: AgentDecision) -> str:
    """
    Convert an AgentDecision status into a valid AgentMemory event type.
    """
    if decision.status == "rejected":
        return "rejection"

    if decision.status == "accepted":
        return "agreement"

    return "decision"


def decisions_to_rows(
    decisions: list[AgentDecision],
) -> list[dict[str, Any]]:
    """
    Convert AgentDecision objects into simple serializable rows.
    """
    return [decision.model_dump() for decision in decisions]
