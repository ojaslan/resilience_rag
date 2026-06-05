import logging
import time
from typing import Dict, Any

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from config.settings import settings
from agent.prompts import AGENT_SYSTEM_PROMPT
from agent.memory import SessionMemory
from agent.tools import retrieve_documents, list_sources, set_retriever
from guardrail.input_guard import InputGuard
from guardrail.output_guard import OutputGuard
from chaos.engine import ChaosEngine
from rag.embedder import VectorEmbedder
from rag.retriever import DocumentRetriever

logger = logging.getLogger(__name__)


class AgentRunner:
    """Wires together: RAG → Guardrails (in) → Groq Agent → Guardrails (out) + Chaos"""

    def __init__(self):
        # Use Groq LLM via langchain-groq
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.2,
            max_tokens=1024,
        )
        self.input_guard = InputGuard()
        self.output_guard = OutputGuard()
        self.chaos = ChaosEngine()

        # Bootstrap RAG with HuggingFace embeddings
        embedder = VectorEmbedder()
        store = embedder.get_or_load()
        retriever = DocumentRetriever(store)
        set_retriever(retriever)
        self.retriever = retriever

        tools = [retrieve_documents, list_sources]
        prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        # create_openai_functions_agent works with Groq as it supports the same function calling interface
        agent = create_openai_functions_agent(self.llm, tools, prompt)
        self.executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True,
            handle_parsing_errors=True, max_iterations=5,
        )

    def run(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        start = time.time()
        result = {
            "answer": "", "sources": [],
            "guardrail_triggered": False, "guardrail_reason": None,
            "chaos_active": self.chaos.enabled,
            "chaos_events": [], "latency_ms": 0,
            "model": settings.GROQ_MODEL,
        }

        # --- Input guardrail ---
        valid, reason = self.input_guard.validate(query)
        if not valid:
            result.update(answer=f"⚠️ Input blocked: {reason}",
                          guardrail_triggered=True, guardrail_reason=reason)
            return result

        query = self.input_guard.sanitize(query)
        memory = SessionMemory.get(session_id)
        chat_history = memory.chat_memory.messages

        # --- Run agent (with possible chaos) ---
        try:
            def _call():
                return self.executor.invoke({"input": query, "chat_history": chat_history})

            response = self.chaos.inject(_call) if self.chaos.enabled else _call()
            answer = response.get("output", "No response generated.")

        except Exception as e:
            logger.error(f"Agent error: {e}")
            result.update(answer=f"⚠️ Agent error: {e}",
                          guardrail_triggered=True, guardrail_reason=str(e),
                          latency_ms=round((time.time() - start) * 1000))
            return result

        # --- Output guardrail ---
        out_valid, out_reason = self.output_guard.validate(answer)
        if not out_valid:
            result.update(answer=f"⚠️ Output blocked: {out_reason}",
                          guardrail_triggered=True, guardrail_reason=out_reason)
        else:
            result["answer"] = answer

        memory.save_context({"input": query}, {"answer": result["answer"]})
        result["chaos_events"] = self.chaos.get_log()[-5:]
        result["latency_ms"] = round((time.time() - start) * 1000)
        return result
