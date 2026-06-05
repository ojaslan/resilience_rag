import logging
import random
import yaml
from pathlib import Path
from typing import Callable, Any

from config.settings import settings

logger = logging.getLogger(__name__)

SCENARIOS_PATH = Path(__file__).parent / "scenarios.yaml"


def _load_scenarios() -> dict:
    if SCENARIOS_PATH.exists():
        with open(SCENARIOS_PATH) as f:
            return yaml.safe_load(f)
    return {}


class ChaosEngine:
    """
    Orchestrates fault injection. Wraps any callable with configurable chaos.
    Supports: latency, bad_data, api_failure.
    """

    def __init__(self, enabled: bool = None):
        self.enabled = enabled if enabled is not None else settings.CHAOS_ENABLED
        self.scenarios = _load_scenarios()
        self.active_faults: list = []
        self.event_log: list = []

    def enable(self):
        self.enabled = True
        logger.warning("Chaos Engineering ENABLED")

    def disable(self):
        self.enabled = False
        self.active_faults = []
        logger.info("Chaos Engineering disabled")

    def set_faults(self, faults: list):
        """Set active fault types: e.g. ['latency', 'bad_data']"""
        self.active_faults = faults
        logger.warning(f"Active chaos faults: {faults}")

    def inject(self, func: Callable, *args, fault_type: str = None, **kwargs) -> Any:
        """
        Wraps a function call with chaos injection.
        fault_type overrides active_faults if provided.
        """
        if not self.enabled:
            return func(*args, **kwargs)

        faults = [fault_type] if fault_type else self.active_faults

        for fault in faults:
            if fault == "latency":
                from chaos.faults.latency import inject_latency
                inject_latency(self.scenarios.get("latency", {}))
                self._log_event("latency", "Injected artificial delay")

            elif fault == "api_failure":
                from chaos.faults.api_failure import maybe_raise_api_error
                maybe_raise_api_error(self.scenarios.get("api_failure", {}))
                self._log_event("api_failure", "Simulated API outage")

        result = func(*args, **kwargs)

        if "bad_data" in faults:
            from chaos.faults.bad_data import corrupt_documents
            result = corrupt_documents(result, self.scenarios.get("bad_data", {}))
            self._log_event("bad_data", "Corrupted retrieved documents")

        return result

    def _log_event(self, fault: str, description: str):
        import datetime
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "fault": fault,
            "description": description,
        }
        self.event_log.append(entry)
        logger.warning(f"[CHAOS] {fault}: {description}")

    def get_log(self) -> list:
        return self.event_log

    def clear_log(self):
        self.event_log = []
