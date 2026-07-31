from pydantic import BaseModel

from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.llm_backends import LLMGenerationRequest
from water_agent_lab.llm_parsing import parse_agent_decision
from water_agent_lab.qwen_backend import OptionalDependencyError, QwenLocalBackend


class QwenSmokeTestResult(BaseModel):
    """
    Result of a local Qwen smoke test.
    """

    model_name: str
    backend_name: str
    raw_text: str
    parsed_successfully: bool
    parsed_decision: AgentDecision | None = None
    parse_error: str | None = None


def build_qwen_smoke_test_request() -> LLMGenerationRequest:
    """
    Build a small structured-output request for local Qwen testing.
    """
    system_prompt = """
You are a stakeholder agent in a drought water-allocation negotiation.

You must return only valid JSON.
Do not include markdown.
Do not include explanations outside JSON.
""".strip()

    user_prompt = """
Evaluate this proposal from the perspective of the urban water stakeholder.

Scenario:
- available_water: 100
- urban requested_water: 35
- urban minimum_acceptable_water: 28
- urban allocated_water: 30

Return JSON with this exact schema:
{
  "stakeholder_name": "urban",
  "status": "accepted | concerned | rejected",
  "argument": "short explanation",
  "requested_extra_water": 0.0,
  "willingness_to_compromise": 0.0
}

Decision rules:
- Use "rejected" if allocated water is below the minimum acceptable water.
- Use "concerned" if allocated water is above minimum but below requested water.
- Use "accepted" if allocation is close to requested water.
""".strip()

    return LLMGenerationRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        max_tokens=256,
    )


def run_qwen_smoke_test(
    model_name_or_path: str,
    max_new_tokens: int = 256,
) -> QwenSmokeTestResult:
    """
    Run a local Qwen smoke test.

    This loads the model, generates one response, and attempts to parse it
    as an AgentDecision.
    """
    try:
        backend = QwenLocalBackend(
            model_name_or_path=model_name_or_path,
            max_new_tokens=max_new_tokens,
        )
    except OptionalDependencyError:
        raise

    request = build_qwen_smoke_test_request()
    response = backend.generate(request)

    try:
        parsed_decision = parse_agent_decision(response.text, "urban")

        return QwenSmokeTestResult(
            model_name=response.model_name,
            backend_name=response.backend_name,
            raw_text=response.text,
            parsed_successfully=True,
            parsed_decision=parsed_decision,
            parse_error=None,
        )

    except ValueError as error:
        return QwenSmokeTestResult(
            model_name=response.model_name,
            backend_name=response.backend_name,
            raw_text=response.text,
            parsed_successfully=False,
            parsed_decision=None,
            parse_error=str(error),
        )
