import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from water_agent_lab.agent_models import AgentDecision


ModelT = TypeVar("ModelT", bound=BaseModel)


def extract_json_object(text: str) -> str:
    """
    Extract the first JSON object from an LLM response.

    Supports:
    - raw JSON
    - Markdown fenced JSON
    - explanatory text before or after JSON

    The returned value is a JSON string.
    """
    stripped = text.strip()

    if not stripped:
        raise ValueError("LLM response is empty.")

    fenced_candidates = _extract_markdown_json_blocks(stripped)

    for candidate in fenced_candidates:
        if _looks_like_json_object(candidate):
            return candidate

    balanced_object = _extract_first_balanced_json_object(stripped)

    if balanced_object is None:
        raise ValueError("LLM response does not contain a JSON object.")

    return balanced_object


def parse_json_model(
    text: str,
    model_class: type[ModelT],
    *,
    allow_json_extraction: bool = True,
) -> ModelT:
    """
    Parse an LLM response into a Pydantic model.

    If allow_json_extraction=True, the parser extracts the first JSON object
    from responses that contain Markdown fences or extra text.

    If allow_json_extraction=False, the whole text must be valid JSON.
    """
    candidate_text = (
        extract_json_object(text) if allow_json_extraction else text.strip()
    )

    try:
        raw_data = json.loads(_remove_trailing_commas(candidate_text))
    except json.JSONDecodeError as error:
        raise ValueError("LLM response is not valid JSON.") from error

    try:
        return model_class.model_validate(raw_data)
    except ValidationError as error:
        raise ValueError("LLM response does not match the expected schema.") from error


def parse_agent_decision(
    text: str,
    stakeholder_name: str,
    *,
    allow_json_extraction: bool = True,
) -> AgentDecision:
    """
    Parse an LLM response as an AgentDecision.

    The stakeholder name is enforced from the simulation state instead of
    trusting the backend response.
    """
    candidate_text = (
        extract_json_object(text) if allow_json_extraction else text.strip()
    )

    try:
        raw_data = json.loads(_remove_trailing_commas(candidate_text))
    except json.JSONDecodeError as error:
        raise ValueError("LLM response is not valid JSON.") from error

    if not isinstance(raw_data, dict):
        raise ValueError("LLM response must be a JSON object.")

    raw_data["stakeholder_name"] = stakeholder_name

    try:
        return AgentDecision.model_validate(raw_data)
    except ValidationError as error:
        raise ValueError("LLM response does not match the expected schema.") from error


def _extract_markdown_json_blocks(text: str) -> list[str]:
    """
    Extract JSON-looking content from Markdown code fences.
    """
    pattern = re.compile(
        r"```(?:json)?\s*(.*?)```",
        flags=re.DOTALL | re.IGNORECASE,
    )

    return [
        match.group(1).strip()
        for match in pattern.finditer(text)
        if match.group(1).strip()
    ]


def _extract_first_balanced_json_object(text: str) -> str | None:
    """
    Extract the first balanced JSON object from text.

    The scanner is string-aware, so braces inside JSON strings do not break
    extraction.
    """
    start_index = text.find("{")

    if start_index == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for index in range(start_index, len(text)):
        character = text[index]

        if escape_next:
            escape_next = False
            continue

        if character == "\\":
            escape_next = True
            continue

        if character == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if character == "{":
            depth += 1

        elif character == "}":
            depth -= 1

            if depth == 0:
                return text[start_index : index + 1]

    return None


def _looks_like_json_object(text: str) -> bool:
    """
    Return True when text looks like a JSON object.
    """
    stripped = text.strip()

    return stripped.startswith("{") and stripped.endswith("}")


def _remove_trailing_commas(text: str) -> str:
    """
    Remove simple trailing commas before closing braces or brackets.

    Example:
    {"status": "concerned",}
    becomes:
    {"status": "concerned"}
    """
    return re.sub(r",\s*([}\]])", r"\1", text)
