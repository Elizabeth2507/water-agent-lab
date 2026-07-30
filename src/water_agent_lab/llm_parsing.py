import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from water_agent_lab.agent_models import AgentDecision


ModelT = TypeVar("ModelT", bound=BaseModel)


def parse_json_model(text: str, model_class: type[ModelT]) -> ModelT:
    """
    Parse LLM text as JSON and validate it as a Pydantic model.
    """
    try:
        raw_data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("LLM response is not valid JSON.") from error

    try:
        return model_class.model_validate(raw_data)
    except ValidationError as error:
        raise ValueError("LLM response does not match the expected schema.") from error


def parse_agent_decision(
    text: str,
    stakeholder_name: str,
) -> AgentDecision:
    """
    Parse LLM text as an AgentDecision.

    The stakeholder name is enforced from the simulation state instead of
    trusting the backend response.
    """
    try:
        raw_data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("LLM response is not valid JSON.") from error

    if not isinstance(raw_data, dict):
        raise ValueError("LLM response must be a JSON object.")

    raw_data["stakeholder_name"] = stakeholder_name

    try:
        return AgentDecision.model_validate(raw_data)
    except ValidationError as error:
        raise ValueError("LLM response does not match the expected schema.") from error
