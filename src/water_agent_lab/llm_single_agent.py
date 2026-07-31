from water_agent_lab.agent_memory import AgentMemory
from water_agent_lab.agent_models import AgentDecision, AgentState
from water_agent_lab.llm_backend_factory import create_llm_backend
from water_agent_lab.llm_stakeholder_agent import (
    LLMStakeholderAgent,
    build_default_agent_profile,
)
from water_agent_lab.models import (
    AllocationProposal,
    ScenarioConfig,
    StakeholderConfig,
)


def find_stakeholder(
    scenario: ScenarioConfig,
    stakeholder_name: str,
) -> StakeholderConfig:
    """
    Find a stakeholder in a scenario by name.
    """
    for stakeholder in scenario.stakeholders:
        if stakeholder.name == stakeholder_name:
            return stakeholder

    available = ", ".join(stakeholder.name for stakeholder in scenario.stakeholders)

    raise ValueError(
        f"Unknown stakeholder '{stakeholder_name}'. "
        f"Available stakeholders: {available}."
    )


def evaluate_single_llm_stakeholder(
    scenario: ScenarioConfig,
    proposal: AllocationProposal,
    stakeholder_name: str,
    backend_name: str,
    model_name_or_path: str | None = None,
    memory: AgentMemory | None = None,
    state: AgentState | None = None,
) -> AgentDecision:
    """
    Evaluate one stakeholder allocation with an LLM backend.
    """
    stakeholder = find_stakeholder(
        scenario=scenario,
        stakeholder_name=stakeholder_name,
    )

    backend = create_llm_backend(
        backend_name=backend_name,
        model_name_or_path=model_name_or_path,
    )

    profile = build_default_agent_profile(stakeholder)

    agent = LLMStakeholderAgent(
        profile=profile,
        backend=backend,
        state=state or AgentState(),
        memory=memory,
    )

    return agent.evaluate_allocation(
        stakeholder=stakeholder,
        proposal=proposal,
        round_number=1,
        scenario=scenario,
    )
