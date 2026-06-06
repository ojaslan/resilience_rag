import logging
import time
from typing import Dict, Any, List

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

from config.settings import settings
from agent.prompts import AGENT_SYSTEM_PROMPT
from agent.memory import SimpleMemory
from agent.tools import retrieve_documents, list_sources, set_retriever
from guardrails.input_guard import InputGuard
from guardrails.output_guard import OutputGuard
from chaos.engine import ChaosEngine
from rag.embedder import VectorEmbedder
from rag.retriever import DocumentRetriever

logger = logging.getLogger(__name__)


class AgentRunner:
    """Wires: RAG → Guardrails(in) → Groq Agent → Guardrails(out) + Chaos"""

    def __init__(self):
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.2,
            max_tokens=1024,
        )
        self.input_guard = InputGuard()
        self.output_guard = OutputGuard()
        self.chaos = ChaosEngine()

        embedder = VectorEmbedder()
        store = embedder.get_or_load()
        retriever = DocumentRetriever(store)
        set_retriever(retriever)
        self.retriever = retriever

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools([retrieve_documents, list_sources])

    def run(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        start = time.time()
        result = {
            "answer": "", "sources": [],
            "guardrail_triggered": False, "guardrail_reason": None,
            "chaos_active": self.chaos.enabled,
            "chaos_events": [], "latency_ms": 0,
            "model": settings.GROQ_MODEL,
        }

        # Input guardrail
        valid, reason = self.input_guard.validate(query)
        if not valid:
            result.update(answer=f"⚠️ Input blocked: {reason}",
                          guardrail_triggered=True, guardrail_reason=reason)
            return result

        query = self.input_guard.sanitize(query)

        try:
            def _call():
                # Step 1: retrieve docs
                docs = self.retriever.retrieve(query)
                context = self.retriever.format_context(docs)

                # Step 2: build messages
                messages = [
                    SystemMessage(content=AGENT_SYSTEM_PROMPT + f"\n\nContext:\n{context}"),
                    HumanMessage(content=query),
                ]

                # Step 3: call Groq
                response = self.llm.invoke(messages)
                return response.content

            answer = self.chaos.inject(_call) if self.chaos.enabled else _call()

        except Exception as e:
            logger.error(f"Agent error: {e}")
            result.update(answer=f"⚠️ Agent error: {e}",
                          guardrail_triggered=True, guardrail_reason=str(e),
                          latency_ms=round((time.time() - start) * 1000))
            return result

        # Output guardrail
        out_valid, out_reason = self.output_guard.validate(answer)
        if not out_valid:
            result.update(answer=f"⚠️ Output blocked: {out_reason}",
                          guardrail_triggered=True, guardrail_reason=out_reason)
        else:
            result["answer"] = answer

        SimpleMemory.add(session_id, query, result["answer"])
        result["chaos_events"] = self.chaos.get_log()[-5:]
        result["latency_ms"] = round((time.time() - start) * 1000)
        return result
