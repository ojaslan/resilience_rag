from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from typing import List


class SessionMemory:
    """Manages per-session conversation memory."""

    _sessions: dict = {}

    @classmethod
    def get(cls, session_id: str = "default") -> ConversationBufferWindowMemory:
        if session_id not in cls._sessions:
            cls._sessions[session_id] = ConversationBufferWindowMemory(
                k=10,
                memory_key="chat_history",
                return_messages=True,
                output_key="answer",
            )
        return cls._sessions[session_id]

    @classmethod
    def clear(cls, session_id: str = "default"):
        if session_id in cls._sessions:
            cls._sessions[session_id].clear()

    @classmethod
    def get_history(cls, session_id: str = "default") -> List[BaseMessage]:
        memory = cls.get(session_id)
        return memory.chat_memory.messages

    @classmethod
    def all_sessions(cls) -> List[str]:
        return list(cls._sessions.keys())
