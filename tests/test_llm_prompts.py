from water_agent_lab.agent_models import AgentProfile, AgentState
from water_agent_lab.config import load_scenario_config
from water_agent_lab.llm_prompts import (
    build_stakeholder_system_prompt,
    build_stakeholder_user_prompt,
)
from water_agent_lab.simulator import proportional_allocation
from water_agent_lab.agent_memory import AgentMemory


def test_build_stakeholder_system_prompt() -> None:
    profile = AgentProfile(
        name="agriculture",
        role="Agricultural water user",
        goals=["Protect crop production"],
        constraints=["Cannot accept water below irrigation minimum"],
        negotiation_style="pragmatic",
    )

    prompt = build_stakeholder_system_prompt(profile)

    assert "agriculture" in prompt
    assert "Agricultural water user" in prompt
    assert "Protect crop production" in prompt
    assert "valid JSON" in prompt


def test_build_stakeholder_user_prompt() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    stakeholder = scenario.stakeholders[0]
    proposal = proportional_allocation(scenario)
    state = AgentState()

    prompt = build_stakeholder_user_prompt(
        scenario=scenario,
        stakeholder=stakeholder,
        proposal=proposal,
        state=state,
    )

    assert scenario.scenario_name in prompt
    assert stakeholder.name in prompt
    assert "allocated_water" in prompt
    assert "output_schema" in prompt
    assert "accepted | concerned | rejected" in prompt


def test_build_stakeholder_user_prompt_includes_memory() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    stakeholder = scenario.stakeholders[0]
    proposal = proportional_allocation(scenario)
    state = AgentState()

    memory = AgentMemory()
    memory.add(
        round_number=1,
        stakeholder_name=stakeholder.name,
        event_type="rejection",
        content="Agriculture rejected the previous allocation.",
        importance=0.9,
    )

    prompt = build_stakeholder_user_prompt(
        scenario=scenario,
        stakeholder=stakeholder,
        proposal=proposal,
        state=state,
        memory=memory,
    )

    assert "memory_summary" in prompt
    assert "Agriculture rejected the previous allocation" in prompt
    assert "Use the memory summary" in prompt
