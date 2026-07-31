import json

from water_agent_lab.agent_memory import AgentMemory
from water_agent_lab.agent_models import AgentDecision, AgentState
from water_agent_lab.llm_backends import MockLLMBackend
from water_agent_lab.llm_stakeholder_agent import (
    LLMStakeholderAgent,
    build_default_agent_profile,
)
from water_agent_lab.models import AllocationProposal, ScenarioConfig, StakeholderConfig
from water_agent_lab.llm_backend_factory import create_llm_backend


def build_mock_decision_response_text(
    stakeholder: StakeholderConfig,
    allocated_water: float,
) -> str:
    """
    Build a deterministic mock LLM response for one stakeholder.

    This simulates an LLM-style JSON response without calling a real model.
    """
    if allocated_water < stakeholder.minimum_acceptable_water:
        status = "rejected"
        argument = (
            "The proposed allocation is below the minimum acceptable water level."
        )
        requested_extra_water = stakeholder.minimum_acceptable_water - allocated_water
        willingness_to_compromise = 0.2

    elif allocated_water < stakeholder.requested_water:
        status = "concerned"
        argument = (
            "The allocation is above the minimum acceptable level, "
            "but still lower than the requested amount."
        )
        requested_extra_water = stakeholder.requested_water - allocated_water
        willingness_to_compromise = 0.6

    else:
        status = "accepted"
        argument = "The allocation is acceptable under the current drought constraints."
        requested_extra_water = 0.0
        willingness_to_compromise = 0.8

    return json.dumps(
        {
            "stakeholder_name": stakeholder.name,
            "status": status,
            "argument": argument,
            "requested_extra_water": requested_extra_water,
            "willingness_to_compromise": willingness_to_compromise,
        }
    )


def run_mock_llm_stakeholder_responses(
    scenario: ScenarioConfig,
    proposal: AllocationProposal,
    round_number: int = 1,
    memory: AgentMemory | None = None,
    agent_states: dict[str, AgentState] | None = None,
) -> list[AgentDecision]:
    """
    Evaluate all stakeholders using LLMStakeholderAgent with MockLLMBackend.

    This gives deterministic, testable LLM-style stakeholder decisions.

    If agent_states is provided, each stakeholder keeps state across rounds.
    """
    decisions: list[AgentDecision] = []

    for stakeholder in scenario.stakeholders:
        allocated_water = proposal.allocations.get(stakeholder.name, 0.0)

        response_text = build_mock_decision_response_text(
            stakeholder=stakeholder,
            allocated_water=allocated_water,
        )

        backend = MockLLMBackend(
            response_text=response_text,
        )

        profile = build_default_agent_profile(stakeholder)

        state = (
            agent_states.get(stakeholder.name, AgentState()).model_copy()
            if agent_states is not None
            else AgentState()
        )

        agent = LLMStakeholderAgent(
            profile=profile,
            backend=backend,
            state=state,
            memory=memory,
        )

        decision = agent.evaluate_allocation(
            stakeholder=stakeholder,
            proposal=proposal,
            round_number=round_number,
            scenario=scenario,
        )

        if agent_states is not None:
            agent_states[stakeholder.name] = agent.state.model_copy()

        decisions.append(decision)

    return decisions


def run_llm_stakeholder_responses(
    scenario: ScenarioConfig,
    proposal: AllocationProposal,
    backend_name: str,
    model_name_or_path: str | None = None,
    round_number: int = 1,
    memory: AgentMemory | None = None,
    agent_states: dict[str, AgentState] | None = None,
) -> list[AgentDecision]:
    """
    Run stakeholder responses using a configurable LLM backend.

    The backend is created once and reused for all stakeholders. This is
    important for local models such as Qwen because loading the model once per
    stakeholder would be too slow.

    Supported backends are provided by create_llm_backend():
    - mock
    - fixed-mock
    - qwen-local
    """
    backend = create_llm_backend(
        backend_name=backend_name,
        model_name_or_path=model_name_or_path,
    )

    decisions: list[AgentDecision] = []

    for stakeholder in scenario.stakeholders:
        profile = build_default_agent_profile(stakeholder)

        state = (
            agent_states.get(stakeholder.name, AgentState()).model_copy()
            if agent_states is not None
            else AgentState()
        )

        agent = LLMStakeholderAgent(
            profile=profile,
            backend=backend,
            state=state,
            memory=memory,
        )

        decision = agent.evaluate_allocation(
            stakeholder=stakeholder,
            proposal=proposal,
            round_number=round_number,
            scenario=scenario,
        )

        if agent_states is not None:
            agent_states[stakeholder.name] = agent.state.model_copy()

        decisions.append(decision)

    return decisions


def llm_decisions_to_rows(
    decisions: list[AgentDecision],
) -> list[dict[str, object]]:
    """
    Convert LLM stakeholder decisions into simple serializable rows.
    """
    return [decision.model_dump() for decision in decisions]
