import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError


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
