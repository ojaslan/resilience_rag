import logging
import yaml
from pathlib import Path
from typing import Tuple, List

from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)

RULES_PATH = Path(__file__).parent / "rules.yaml"


def _load_rules() -> dict:
    if RULES_PATH.exists():
        with open(RULES_PATH) as f:
            return yaml.safe_load(f)
    return {}


class AgentResponse(BaseModel):
    """Pydantic schema for validating agent output structure."""
    answer: str
    sources: List[str] = []
    confidence: float = 1.0

    @field_validator("answer")
    @classmethod
    def answer_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Answer must not be empty.")
        return v

    @field_validator("confidence")
    @classmethod
    def confidence_range(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0 and 1.")
        return v


class OutputGuard:
    """Validates LLM output for safety, quality, and format compliance."""

    def __init__(self):
        rules = _load_rules()
        self.hallucination_phrases: List[str] = rules.get("hallucination_phrases", [])
        self.max_output_length: int = rules.get("max_output_length", 4000)

    def validate(self, output: str) -> Tuple[bool, str]:
        """
        Returns (is_valid, reason).
        """
        if not output or not output.strip():
            return False, "Output is empty."

        if len(output) > self.max_output_length:
            return False, f"Output too long ({len(output)} chars)."

        for phrase in self.hallucination_phrases:
            if phrase.lower() in output.lower():
                logger.warning(f"Potential hallucination phrase detected: '{phrase}'")
                return False, f"Output may contain unreliable content: '{phrase}'"

        return True, "OK"

    def validate_structured(self, data: dict) -> Tuple[bool, str]:
        """Validate structured output against AgentResponse schema."""
        try:
            AgentResponse(**data)
            return True, "OK"
        except Exception as e:
            return False, str(e)
