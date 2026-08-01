import pytest

from water_agent_lab.agent_models import AgentProfile
from water_agent_lab.llm_backends import MockLLMBackend
from water_agent_lab.llm_stakeholder_agent import (
    LLMStakeholderAgent,
    build_default_agent_profile,
    decisions_to_rows,
    evaluate_llm_stakeholder_responses,
)
from water_agent_lab.models import AllocationProposal, ScenarioConfig, StakeholderConfig
from water_agent_lab.llm_backends import LLMGenerationResponse
from water_agent_lab.agent_memory import AgentMemory
from water_agent_lab.agent_models import AgentState
from water_agent_lab.config import load_scenario_config
from water_agent_lab.simulator import proportional_allocation


# class InvalidBackend:
#     def generate(self, prompt: str) -> str:
#         return "not valid json"


class InvalidBackend:
    def generate(self, prompt: str) -> LLMGenerationResponse:
        return LLMGenerationResponse(
            text="not valid json",
            model_name="invalid-mock",
            backend_name="invalid",
        )


def make_stakeholder() -> StakeholderConfig:
    return StakeholderConfig(
        name="agriculture",
        requested_water=50.0,
        minimum_acceptable_water=35.0,
        priority=0.8,
    )


def make_proposal() -> AllocationProposal:
    return AllocationProposal(
        allocations={
            "agriculture": 38.0,
        }
    )


def make_concerned_backend() -> MockLLMBackend:
    return MockLLMBackend(
        response_text="""
        {
          "stakeholder_name": "unknown",
          "status": "concerned",
          "argument": "The allocation is usable but lower than requested.",
          "requested_extra_water": 5.0,
          "willingness_to_compromise": 0.6
        }
        """
    )


def make_rejected_backend() -> MockLLMBackend:
    return MockLLMBackend(
        response_text="""
        {
          "stakeholder_name": "unknown",
          "status": "rejected",
          "argument": "The allocation is below the minimum acceptable level.",
          "requested_extra_water": 10.0,
          "willingness_to_compromise": 0.2
        }
        """
    )


def test_build_default_agent_profile() -> None:
    stakeholder = make_stakeholder()

    profile = build_default_agent_profile(stakeholder)

    assert profile.name == "agriculture"
    assert "agriculture" in profile.role
    assert profile.goals
    assert profile.constraints
    assert profile.negotiation_style == "balanced"


def test_llm_stakeholder_agent_returns_valid_decision() -> None:
    stakeholder = make_stakeholder()
    proposal = make_proposal()

    profile = AgentProfile(
        name="agriculture",
        role="Represents agricultural water users",
        goals=["Protect crop irrigation needs"],
        constraints=["Can accept limited reductions during drought"],
        negotiation_style="pragmatic",
    )

    agent = LLMStakeholderAgent(
        profile=profile,
        backend=make_concerned_backend(),
    )

    decision = agent.evaluate_allocation(
        stakeholder=stakeholder,
        proposal=proposal,
    )

    assert decision.stakeholder_name == "agriculture"
    assert decision.status == "concerned"
    assert decision.argument
    assert decision.requested_extra_water == 5.0
    assert decision.willingness_to_compromise == 0.6


def test_llm_stakeholder_agent_updates_state_after_rejection() -> None:
    stakeholder = StakeholderConfig(
        name="ecosystem",
        requested_water=20.0,
        minimum_acceptable_water=18.0,
        priority=1.0,
    )

    proposal = AllocationProposal(
        allocations={
            "ecosystem": 0.0,
        }
    )

    profile = AgentProfile(
        name="ecosystem",
        role="Represents ecological water needs",
        goals=["Protect river flow and biodiversity"],
        constraints=["Cannot accept severe ecological damage"],
        negotiation_style="firm",
    )

    agent = LLMStakeholderAgent(
        profile=profile,
        backend=make_rejected_backend(),
    )

    decision = agent.evaluate_allocation(
        stakeholder=stakeholder,
        proposal=proposal,
    )

    assert decision.stakeholder_name == "ecosystem"
    assert decision.status == "rejected"
    assert agent.state.last_status == "rejected"
    assert agent.state.frustration > 0.0
    assert agent.state.trust_in_mediator < 0.5


def test_llm_stakeholder_agent_rejects_invalid_backend_response() -> None:
    stakeholder = make_stakeholder()
    proposal = make_proposal()

    profile = AgentProfile(
        name="agriculture",
        role="Represents agricultural water users",
    )

    agent = LLMStakeholderAgent(
        profile=profile,
        backend=InvalidBackend(),
    )

    with pytest.raises(ValueError, match="does not contain a JSON object"):
        agent.evaluate_allocation(
            stakeholder=stakeholder,
            proposal=proposal,
        )


def test_evaluate_llm_stakeholder_responses_returns_one_decision_per_stakeholder() -> (
    None
):
    scenario = ScenarioConfig(
        scenario_name="test_scenario",
        country="France",
        region="Occitanie",
        drought_level="moderate",
        available_water=100.0,
        max_rounds=3,
        stakeholders=[
            StakeholderConfig(
                name="agriculture",
                requested_water=50.0,
                minimum_acceptable_water=35.0,
                priority=0.8,
            ),
            StakeholderConfig(
                name="urban",
                requested_water=35.0,
                minimum_acceptable_water=28.0,
                priority=0.9,
            ),
        ],
    )

    proposal = AllocationProposal(
        allocations={
            "agriculture": 38.0,
            "urban": 27.0,
        }
    )

    decisions = evaluate_llm_stakeholder_responses(
        scenario=scenario,
        proposal=proposal,
        backend=make_concerned_backend(),
    )

    assert len(decisions) == 2
    assert {decision.stakeholder_name for decision in decisions} == {
        "agriculture",
        "urban",
    }

    for decision in decisions:
        assert decision.status == "concerned"
        assert decision.argument


def test_decisions_to_rows() -> None:
    scenario = ScenarioConfig(
        scenario_name="test_scenario",
        country="France",
        region="Occitanie",
        drought_level="moderate",
        available_water=100.0,
        max_rounds=3,
        stakeholders=[
            make_stakeholder(),
        ],
    )

    proposal = make_proposal()

    decisions = evaluate_llm_stakeholder_responses(
        scenario=scenario,
        proposal=proposal,
        backend=make_concerned_backend(),
    )

    rows = decisions_to_rows(decisions)

    assert len(rows) == 1
    assert rows[0]["stakeholder_name"] == "agriculture"
    assert rows[0]["status"] == "concerned"
    assert "argument" in rows[0]


def test_llm_stakeholder_agent_includes_memory_in_prompt() -> None:
    backend = MockLLMBackend(
        response_text="""
        {
          "stakeholder_name": "agriculture",
          "status": "concerned",
          "argument": "The proposal improved but remains difficult.",
          "requested_extra_water": 2.0,
          "willingness_to_compromise": 0.7
        }
        """
    )

    memory = AgentMemory()
    memory.add(
        round_number=1,
        stakeholder_name="agriculture",
        event_type="rejection",
        content="Agriculture rejected the first proposal.",
        importance=0.9,
    )

    profile = AgentProfile(
        name="agriculture",
        role="Agricultural water user",
        goals=["Protect crop production"],
        constraints=["Avoid allocation below irrigation minimum"],
    )

    agent = LLMStakeholderAgent(
        profile=profile,
        state=AgentState(),
        backend=backend,
        memory=memory,
    )

    scenario = load_scenario_config("configs/drought_mvp.yaml")
    stakeholder = scenario.stakeholders[0]
    proposal = proportional_allocation(scenario)

    decision = agent.evaluate_allocation(
        scenario=scenario,
        stakeholder=stakeholder,
        proposal=proposal,
    )

    assert decision.status == "concerned"
    assert len(backend.requests) == 1
    assert "Agriculture rejected the first proposal" in backend.requests[0].user_prompt


class ConstraintViolatingBackend:
    def __init__(self) -> None:
        self.requests = []

    def generate(self, request):
        self.requests.append(request)

        return LLMGenerationResponse(
            text="""
{
  "stakeholder_name": "urban",
  "status": "accepted",
  "argument": "The allocation respects the minimum acceptable water needs.",
  "requested_extra_water": 0.0,
  "willingness_to_compromise": 0.9
}
""",
            model_name="constraint-violating-backend",
            backend_name="constraint-violating-backend",
        )


def test_llm_stakeholder_agent_repairs_constraint_violating_decision() -> None:
    stakeholder = StakeholderConfig(
        name="urban",
        requested_water=35.0,
        minimum_acceptable_water=28.0,
        priority=0.9,
    )

    proposal = AllocationProposal(
        allocations={
            "urban": 26.923076923076923,
        }
    )

    profile = AgentProfile(
        name="urban",
        role="Represents urban water users",
    )

    agent = LLMStakeholderAgent(
        profile=profile,
        backend=ConstraintViolatingBackend(),
    )

    decision = agent.evaluate_allocation(
        stakeholder=stakeholder,
        proposal=proposal,
    )

    assert decision.stakeholder_name == "urban"
    assert decision.status == "rejected"
    assert decision.requested_extra_water == pytest.approx(
        28.0 - 26.923076923076923
    )

    assert agent.last_validation_result is not None
    assert agent.last_validation_result.was_repaired is True