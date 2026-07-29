import pytest
from pydantic import ValidationError

from water_agent_lab.llm_backends import (
    LLMGenerationRequest,
    MockLLMBackend,
)


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
