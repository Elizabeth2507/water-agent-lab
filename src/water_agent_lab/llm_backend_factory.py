from water_agent_lab.llm_backends import MockLLMBackend
from water_agent_lab.qwen_backend import QwenLocalBackend


def create_llm_backend(
    backend_name: str,
    model_name_or_path: str | None = None,
):
    """
    Create an LLM backend by name.
    """
    if backend_name == "mock":
        return MockLLMBackend(
            response_text="""
{
  "stakeholder_name": "mock",
  "status": "concerned",
  "argument": "This is a deterministic mock stakeholder decision.",
  "requested_extra_water": 1.0,
  "willingness_to_compromise": 0.5
}
""".strip(),
            model_name="mock-llm",
            backend_name="mock",
        )

    if backend_name == "qwen-local":
        if model_name_or_path is None:
            raise ValueError("model_name_or_path is required for qwen-local.")

        return QwenLocalBackend(
            model_name_or_path=model_name_or_path,
        )

    raise ValueError(
        f"Unknown LLM backend '{backend_name}'. Available backends: mock, qwen-local."
    )
