import pytest
from pydantic import ValidationError

from water_agent_lab.llm_backends import (
    LLMGenerationRequest,
    MockLLMBackend,
    StakeholderAwareMockLLMBackend,
)
from water_agent_lab.llm_parsing import parse_agent_decision


def test_llm_generation_request_defaults() -> None:
    request = LLMGenerationRequest(
        system_prompt="You are a stakeholder agent.",
        user_prompt="Evaluate this proposal.",
    )

    assert request.temperature == 0.0
    assert request.max_tokens == 512


def test_llm_generation_request_validates_temperature() -> None:
    with pytest.raises(ValidationError):
        LLMGenerationRequest(
            system_prompt="System",
            user_prompt="User",
            temperature=-0.1,
        )

    with pytest.raises(ValidationError):
        LLMGenerationRequest(
            system_prompt="System",
            user_prompt="User",
            temperature=2.5,
        )


def test_llm_generation_request_validates_max_tokens() -> None:
    with pytest.raises(ValidationError):
        LLMGenerationRequest(
            system_prompt="System",
            user_prompt="User",
            max_tokens=0,
        )


def test_mock_llm_backend_returns_fixed_response() -> None:
    backend = MockLLMBackend(
        response_text='{"status": "concerned"}',
        model_name="test-model",
    )

    request = LLMGenerationRequest(
        system_prompt="You are agriculture.",
        user_prompt="Evaluate allocation.",
    )

    response = backend.generate(request)

    assert response.text == '{"status": "concerned"}'
    assert response.model_name == "test-model"
    assert response.backend_name == "mock"


def test_mock_llm_backend_records_requests() -> None:
    backend = MockLLMBackend(response_text="ok")

    request = LLMGenerationRequest(
        system_prompt="System prompt",
        user_prompt="User prompt",
    )

    backend.generate(request)

    assert len(backend.requests) == 1
    assert backend.requests[0].system_prompt == "System prompt"
    assert backend.requests[0].user_prompt == "User prompt"


def test_stakeholder_aware_mock_backend_returns_concerned_decision() -> None:
    backend = StakeholderAwareMockLLMBackend()

    request = LLMGenerationRequest(
        system_prompt="You are a stakeholder agent.",
        user_prompt="""
{
  "stakeholder": {
    "name": "urban",
    "requested_water": 35.0,
    "minimum_acceptable_water": 28.0,
    "allocated_water": 30.0
  }
}
""",
    )

    response = backend.generate(request)

    decision = parse_agent_decision(
        text=response.text,
        stakeholder_name="urban",
    )

    assert decision.stakeholder_name == "urban"
    assert decision.status == "concerned"
    assert decision.requested_extra_water == 5.0
    assert decision.willingness_to_compromise == 0.6


def test_stakeholder_aware_mock_backend_rejects_below_minimum() -> None:
    backend = StakeholderAwareMockLLMBackend()

    request = LLMGenerationRequest(
        system_prompt="You are a stakeholder agent.",
        user_prompt="""
{
  "stakeholder": {
    "name": "ecosystem",
    "requested_water": 20.0,
    "minimum_acceptable_water": 18.0,
    "allocated_water": 15.0
  }
}
""",
    )

    response = backend.generate(request)

    decision = parse_agent_decision(
        text=response.text,
        stakeholder_name="ecosystem",
    )

    assert decision.stakeholder_name == "ecosystem"
    assert decision.status == "rejected"
    assert decision.requested_extra_water == 3.0
    assert decision.willingness_to_compromise == 0.3


def test_stakeholder_aware_mock_backend_accepts_near_request() -> None:
    backend = StakeholderAwareMockLLMBackend()

    request = LLMGenerationRequest(
        system_prompt="You are a stakeholder agent.",
        user_prompt="""
{
  "stakeholder": {
    "name": "industry",
    "requested_water": 25.0,
    "minimum_acceptable_water": 15.0,
    "allocated_water": 23.0
  }
}
""",
    )

    response = backend.generate(request)

    decision = parse_agent_decision(
        text=response.text,
        stakeholder_name="industry",
    )

    assert decision.stakeholder_name == "industry"
    assert decision.status == "accepted"
    assert decision.requested_extra_water == 0.0
    assert decision.willingness_to_compromise == 0.9


def test_stakeholder_aware_mock_backend_records_requests() -> None:
    backend = StakeholderAwareMockLLMBackend()

    request = LLMGenerationRequest(
        system_prompt="System prompt.",
        user_prompt="""
{
  "stakeholder": {
    "name": "urban",
    "requested_water": 35.0,
    "minimum_acceptable_water": 28.0,
    "allocated_water": 30.0
  }
}
""",
    )

    backend.generate(request)

    assert backend.requests == [request]
