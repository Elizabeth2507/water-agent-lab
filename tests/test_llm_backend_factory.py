import pytest

from water_agent_lab.llm_backend_factory import create_llm_backend
from water_agent_lab.llm_backends import (
    MockLLMBackend,
    StakeholderAwareMockLLMBackend,
)


def test_create_mock_backend() -> None:
    backend = create_llm_backend("mock")

    assert isinstance(backend, StakeholderAwareMockLLMBackend)


def test_create_fixed_mock_backend() -> None:
    backend = create_llm_backend("fixed-mock")

    assert isinstance(backend, MockLLMBackend)


def test_create_qwen_backend_requires_model_name() -> None:
    with pytest.raises(ValueError, match="model_name_or_path is required"):
        create_llm_backend("qwen-local")


def test_create_unknown_backend_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown LLM backend"):
        create_llm_backend("unknown")
