from water_agent_lab.qwen_backend import QwenLocalBackend
from water_agent_lab.llm_backends import (
    LLMBackend,
    MockLLMBackend,
    StakeholderAwareMockLLMBackend,
)


def create_llm_backend(
    backend_name: str,
    model_name_or_path: str | None = None,
) -> LLMBackend:
    """
    Create an LLM backend by name.

    Supported backends:
    - mock
    - fixed-mock
    - qwen-local
    """
    if backend_name == "mock":
        return StakeholderAwareMockLLMBackend()

    if backend_name == "fixed-mock":
        return MockLLMBackend(
            response_text=(
                '{"stakeholder_name":"mock","status":"accepted",'
                '"argument":"Mock response.","requested_extra_water":0.0,'
                '"willingness_to_compromise":0.9}'
            ),
            model_name="fixed-mock-llm",
            backend_name="fixed-mock",
        )

    if backend_name == "qwen-local":
        if model_name_or_path is None:
            raise ValueError(
                "model_name_or_path is required when backend_name='qwen-local'."
            )

        return QwenLocalBackend(
            model_name_or_path=model_name_or_path,
        )

    raise ValueError(
        f"Unknown LLM backend '{backend_name}'. "
        "Available backends: mock, fixed-mock, qwen-local."
    )
