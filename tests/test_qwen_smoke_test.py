from water_agent_lab.llm_backends import LLMGenerationRequest
from water_agent_lab.qwen_smoke_test import (
    QwenSmokeTestResult,
    build_qwen_smoke_test_request,
)


def test_build_qwen_smoke_test_request() -> None:
    request = build_qwen_smoke_test_request()

    assert isinstance(request, LLMGenerationRequest)
    assert "valid JSON" in request.system_prompt
    assert "urban" in request.user_prompt
    assert request.temperature == 0.0
    assert request.max_tokens == 256


def test_qwen_smoke_test_result_model_accepts_parse_failure() -> None:
    result = QwenSmokeTestResult(
        model_name="test-model",
        backend_name="qwen-local",
        raw_text="not json",
        parsed_successfully=False,
        parsed_decision=None,
        parse_error="LLM response is not valid JSON.",
    )

    assert result.model_name == "test-model"
    assert result.backend_name == "qwen-local"
    assert result.parsed_successfully is False
    assert result.parse_error == "LLM response is not valid JSON."
