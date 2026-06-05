import logging
from langchain.tools import tool
from typing import Optional

logger = logging.getLogger(__name__)

_retriever = None


def set_retriever(retriever):
    global _retriever
    _retriever = retriever


@tool
def retrieve_documents(query: str) -> str:
    """
    Searches the knowledge base for documents relevant to the query.
    Use this tool whenever the user asks a question that requires factual information.
    Input: a search query string.
    Output: relevant document excerpts.
    """
    if _retriever is None:
        return "Knowledge base not initialized. Please ingest documents first."
    try:
        docs = _retriever.retrieve(query)
        return _retriever.format_context(docs)
    except Exception as e:
        logger.error(f"retrieve_documents tool error: {e}")
        return f"Retrieval failed: {str(e)}"


@tool
def list_sources(query: Optional[str] = None) -> str:
    """
    Lists the sources available in the knowledge base.
    Use when the user asks what documents or sources are available.
    """
    if _retriever is None:
        return "Knowledge base not initialized."
    try:
        store = _retriever.store
        results = store.get()
        sources = set()
        for meta in results.get("metadatas", []):
            src = meta.get("source", "unknown")
            sources.add(src)
        if not sources:
            return "No documents found in the knowledge base."
        return "Available sources:\n" + "\n".join(f"- {s}" for s in sorted(sources))
    except Exception as e:
        return f"Could not list sources: {e}"
