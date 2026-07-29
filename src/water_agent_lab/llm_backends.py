from typing import Protocol

from pydantic import BaseModel, Field


class LLMGenerationRequest(BaseModel):
    """
    Structured request sent to an LLM backend.
    """

    system_prompt: str
    user_prompt: str
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, gt=0)


class LLMGenerationResponse(BaseModel):
    """
    Structured response returned by an LLM backend.
    """

    text: str
    model_name: str
    backend_name: str


class LLMBackend(Protocol):
    """
    Interface for any LLM backend.

    Future implementations may wrap local Qwen models, hosted APIs,
    or deterministic test backends.
    """

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        """
        Generate text from an LLM request.
        """


class MockLLMBackend:
    """
    Deterministic LLM backend for tests and offline development.

    This backend does not call a real model. It returns a fixed response,
    which makes agent tests reproducible.
    """

    def __init__(
        self,
        response_text: str,
        model_name: str = "mock-llm",
        backend_name: str = "mock",
    ) -> None:
        self.response_text = response_text
        self.model_name = model_name
        self.backend_name = backend_name
        self.requests: list[LLMGenerationRequest] = []

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        self.requests.append(request)

        return LLMGenerationResponse(
            text=self.response_text,
            model_name=self.model_name,
            backend_name=self.backend_name,
        )
