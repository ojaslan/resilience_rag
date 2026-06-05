import time
import random
import logging

logger = logging.getLogger(__name__)


def inject_latency(config: dict = None):
    """
    Injects an artificial delay to simulate slow API / network conditions.
    Config keys:
      min_delay (float): minimum seconds to sleep. Default 1.0
      max_delay (float): maximum seconds to sleep. Default 5.0
      probability (float): chance of injecting 0.0-1.0. Default 1.0
    """
    config = config or {}
    probability = config.get("probability", 1.0)

    if random.random() > probability:
        return

    min_delay = config.get("min_delay", 1.0)
    max_delay = config.get("max_delay", 5.0)
    delay = random.uniform(min_delay, max_delay)

    logger.warning(f"[CHAOS:latency] Sleeping {delay:.2f}s")
    time.sleep(delay)
