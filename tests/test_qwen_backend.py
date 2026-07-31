import builtins

import pytest

from water_agent_lab.llm_backends import LLMGenerationRequest
from water_agent_lab.qwen_backend import OptionalDependencyError, QwenLocalBackend


def test_qwen_backend_class_can_be_imported() -> None:
    assert QwenLocalBackend is not None


def test_qwen_backend_raises_clear_error_when_transformers_missing(
    monkeypatch,
) -> None:
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "transformers":
            raise ImportError("No module named transformers")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(OptionalDependencyError, match="QwenLocalBackend requires"):
        QwenLocalBackend(
            model_name_or_path="Qwen/Qwen2.5-1.5B-Instruct",
        )


def test_generation_request_is_compatible_with_qwen_backend_interface() -> None:
    request = LLMGenerationRequest(
        system_prompt="You are a test assistant.",
        user_prompt="Return JSON only.",
        temperature=0.0,
        max_tokens=128,
    )

    assert request.system_prompt == "You are a test assistant."
    assert request.user_prompt == "Return JSON only."
    assert request.temperature == 0.0
    assert request.max_tokens == 128
