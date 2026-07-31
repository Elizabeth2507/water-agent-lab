import json
import re
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


class StakeholderAwareMockLLMBackend:
    """
    Mock backend that returns an AgentDecision based on the stakeholder context
    embedded in the prompt.

    This is useful for testing the LLM agent interface without loading a real
    model. It keeps the same backend interface as real LLM backends, but the
    output is deterministic and easy to test.
    """

    backend_name = "stakeholder-aware-mock"
    model_name = "stakeholder-aware-mock-llm"

    def __init__(self) -> None:
        self.requests: list[LLMGenerationRequest] = []

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        self.requests.append(request)

        stakeholder_name = self._extract_string(
            text=request.user_prompt,
            field_name="name",
            default="unknown",
        )
        requested_water = self._extract_number(
            text=request.user_prompt,
            field_name="requested_water",
            default=1.0,
        )
        minimum_acceptable_water = self._extract_number(
            text=request.user_prompt,
            field_name="minimum_acceptable_water",
            default=0.0,
        )
        allocated_water = self._extract_number(
            text=request.user_prompt,
            field_name="allocated_water",
            default=0.0,
        )

        if allocated_water < minimum_acceptable_water:
            status = "rejected"
            requested_extra_water = minimum_acceptable_water - allocated_water
            willingness_to_compromise = 0.3
            argument = (
                f"{stakeholder_name} rejects the proposal because allocated "
                "water is below the minimum acceptable level."
            )

        elif allocated_water / max(requested_water, 1.0) < 0.9:
            status = "concerned"
            requested_extra_water = requested_water - allocated_water
            willingness_to_compromise = 0.6
            argument = (
                f"{stakeholder_name} is concerned because the allocation is "
                "above the minimum but still below the requested amount."
            )

        else:
            status = "accepted"
            requested_extra_water = 0.0
            willingness_to_compromise = 0.9
            argument = (
                f"{stakeholder_name} accepts the proposal because the "
                "allocation is close to the requested amount."
            )

        response = {
            "stakeholder_name": stakeholder_name,
            "status": status,
            "argument": argument,
            "requested_extra_water": max(requested_extra_water, 0.0),
            "willingness_to_compromise": willingness_to_compromise,
        }

        return LLMGenerationResponse(
            text=json.dumps(response),
            model_name=self.model_name,
            backend_name=self.backend_name,
        )

    @staticmethod
    def _extract_number(
        text: str,
        field_name: str,
        default: float,
    ) -> float:
        """
        Extract a numeric field from the JSON-like context inside the prompt.
        """
        pattern = rf'"{re.escape(field_name)}"\s*:\s*([0-9]+(?:\.[0-9]+)?)'
        match = re.search(pattern, text)

        if match is None:
            return default

        return float(match.group(1))

    @staticmethod
    def _extract_string(
        text: str,
        field_name: str,
        default: str,
    ) -> str:
        """
        Extract a string field from the JSON-like context inside the prompt.
        """
        pattern = rf'"{re.escape(field_name)}"\s*:\s*"([^"]+)"'
        match = re.search(pattern, text)

        if match is None:
            return default

        return match.group(1)
