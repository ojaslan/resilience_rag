import random
import logging

logger = logging.getLogger(__name__)


class SimulatedAPIError(Exception):
    """Raised when chaos engineering simulates a Groq API outage."""
    pass


def maybe_raise_api_error(config: dict = None):
    """
    Randomly raises an exception to simulate Groq API failures.
    Config: probability, error_messages
    """
    config = config or {}
    probability = config.get("probability", 0.3)
    if random.random() > probability:
        return

    messages = config.get("error_messages", [
        "503 Service Unavailable: Groq API is down.",
        "429 Too Many Requests: Groq rate limit exceeded.",
        "Connection timeout after 30s.",
        "500 Internal Server Error from Groq upstream.",
        "413 Request Entity Too Large: token limit exceeded.",
    ])
    msg = random.choice(messages)
    logger.warning(f"[CHAOS:api_failure] Raising simulated Groq error: {msg}")
    raise SimulatedAPIError(msg)
