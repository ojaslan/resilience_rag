import re
import logging
import yaml
from pathlib import Path
from typing import Tuple, List

logger = logging.getLogger(__name__)

RULES_PATH = Path(__file__).parent / "rules.yaml"


def _load_rules() -> dict:
    if RULES_PATH.exists():
        with open(RULES_PATH) as f:
            return yaml.safe_load(f)
    return {"blocked_patterns": [], "max_input_length": 2000}


class InputGuard:
    """Validates and sanitizes user input before it reaches the agent."""

    def __init__(self):
        rules = _load_rules()
        self.blocked_patterns: List[str] = rules.get("blocked_patterns", [])
        self.max_length: int = rules.get("max_input_length", 2000)

    def validate(self, user_input: str) -> Tuple[bool, str]:
        """
        Returns (is_valid, reason).
        is_valid=True means input is safe to proceed.
        """
        if not user_input or not user_input.strip():
            return False, "Input is empty."

        if len(user_input) > self.max_length:
            return False, f"Input too long ({len(user_input)} chars). Max: {self.max_length}."

        for pattern in self.blocked_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                logger.warning(f"Blocked pattern matched: '{pattern}' in input.")
                return False, f"Input contains disallowed content (pattern: {pattern})."

        return True, "OK"

    def sanitize(self, user_input: str) -> str:
        """Strip leading/trailing whitespace and normalize spaces."""
        return " ".join(user_input.split())
