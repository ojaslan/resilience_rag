import logging
import time
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from config.settings import settings

logger = logging.getLogger(__name__)


class DocumentRetriever:
    def __init__(self, store: FAISS):
        self.store = store
        self.k = settings.MAX_RETRIEVAL_DOCS

    def retrieve(self, query: str, k: int = None) -> List[Document]:
        k = k or self.k
        start = time.time()
        try:
            docs = self.store.similarity_search(query, k=k)
            elapsed = round((time.time() - start) * 1000, 2)
            logger.info(f"Retrieved {len(docs)} docs in {elapsed}ms")
            return docs
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []

    def retrieve_with_scores(self, query: str, k: int = None) -> List[Tuple[Document, float]]:
        k = k or self.k
        try:
            return self.store.similarity_search_with_score(query, k=k)
        except Exception as e:
            logger.error(f"Scored retrieval failed: {e}")
            return []

    def format_context(self, docs: List[Document]) -> str:
        if not docs:
            return "No relevant documents found."
        parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            parts.append(f"[Doc {i} | {source}]\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)
