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
    return {}


class OutputGuard:
    def __init__(self):
        rules = _load_rules()
        self.hallucination_phrases: List[str] = rules.get("hallucination_phrases", [])
        self.max_output_length: int = rules.get("max_output_length", 4000)

    def validate(self, output: str) -> Tuple[bool, str]:
        if not output or not output.strip():
            return False, "Output is empty."
        if len(output) > self.max_output_length:
            return False, f"Output too long."
        for phrase in self.hallucination_phrases:
            if phrase.lower() in output.lower():
                return False, f"Output may contain unreliable content."
        return True, "OK"
