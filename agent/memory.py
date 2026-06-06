from langchain_core.messages import BaseMessage
from typing import List


class SimpleMemory:
    """Simple per-session conversation memory."""
    _sessions: dict = {}

    @classmethod
    def get(cls, session_id: str = "default") -> list:
        if session_id not in cls._sessions:
            cls._sessions[session_id] = []
        return cls._sessions[session_id]

    @classmethod
    def add(cls, session_id: str, human: str, ai: str):
        history = cls.get(session_id)
        history.append({"human": human, "ai": ai})
        if len(history) > 10:
            history.pop(0)

    @classmethod
    def clear(cls, session_id: str = "default"):
        cls._sessions[session_id] = []

    @classmethod
    def get_history(cls, session_id: str = "default") -> list:
        return cls.get(session_id)

    @classmethod
    def all_sessions(cls) -> List[str]:
        return list(cls._sessions.keys())
