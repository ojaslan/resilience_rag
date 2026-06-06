import logging
from langchain_core.tools import tool
from typing import Optional

logger = logging.getLogger(__name__)
_retriever = None


def set_retriever(retriever):
    global _retriever
    _retriever = retriever


@tool
def retrieve_documents(query: str) -> str:
    """Searches the knowledge base for documents relevant to the query."""
    if _retriever is None:
        return "Knowledge base not initialized."
    try:
        docs = _retriever.retrieve(query)
        return _retriever.format_context(docs)
    except Exception as e:
        logger.error(f"retrieve_documents error: {e}")
        return f"Retrieval failed: {str(e)}"


@tool
def list_sources(query: Optional[str] = None) -> str:
    """Lists available sources in the knowledge base."""
    if _retriever is None:
        return "Knowledge base not initialized."
    try:
        docstore = _retriever.store.docstore._dict
        sources = set()
        for doc in docstore.values():
            src = doc.metadata.get("source", "unknown")
            sources.add(src)
        if not sources:
            return "No documents found."
        return "Available sources:\n" + "\n".join(f"- {s}" for s in sorted(sources))
    except Exception as e:
        return f"Could not list sources: {e}"
