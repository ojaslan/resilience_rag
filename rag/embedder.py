import logging
import os
import json
import hashlib
from typing import List, Optional

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings

from config.settings import settings

logger = logging.getLogger(__name__)


class SimpleEmbeddings(Embeddings):
    """
    Lightweight TF-IDF style embeddings — zero extra dependencies.
    Works with only langchain installed. Good enough for demos & projects.
    """

    def __init__(self, dim: int = 384):
        self.dim = dim
        self.vocab: dict = {}

    def _tokenize(self, text: str) -> List[str]:
        import re
        text = text.lower()
        return re.findall(r'\b[a-z]{2,}\b', text)

    def _get_token_id(self, token: str) -> int:
        if token not in self.vocab:
            self.vocab[token] = int(hashlib.md5(token.encode()).hexdigest(), 16) % self.dim
        return self.vocab[token]

    def _embed(self, text: str) -> List[float]:
        import math
        vec = [0.0] * self.dim
        tokens = self._tokenize(text)
        if not tokens:
            return vec
        for token in tokens:
            idx = self._get_token_id(token)
            vec[idx] += 1.0
        # Normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


class VectorEmbedder:
    """Embeds document chunks using SimpleEmbeddings and stores in FAISS.
    No extra dependencies needed beyond langchain and faiss-cpu.
    """

    def __init__(self):
        self.embeddings = SimpleEmbeddings(dim=384)
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        self.index_path = os.path.join(self.persist_dir, "faiss_index")
        self._store: Optional[FAISS] = None

    def build_store(self, chunks: List[Document]) -> FAISS:
        logger.info(f"Building FAISS store with {len(chunks)} chunks...")
        self._store = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings,
        )
        os.makedirs(self.persist_dir, exist_ok=True)
        self._store.save_local(self.index_path)
        logger.info(f"FAISS store saved to {self.index_path}")
        return self._store

    def load_store(self) -> FAISS:
        logger.info(f"Loading FAISS store from {self.index_path}")
        self._store = FAISS.load_local(
            self.index_path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        return self._store

    def get_or_load(self) -> FAISS:
        if self._store is None:
            if os.path.exists(self.index_path):
                self._store = self.load_store()
            else:
                logger.warning("No FAISS index found. Creating empty store.")
                dummy = [Document(page_content="init", metadata={})]
                self._store = FAISS.from_documents(dummy, self.embeddings)
        return self._store

    def add_documents(self, chunks: List[Document]):
        store = self.get_or_load()
        store.add_documents(chunks)
        store.save_local(self.index_path)
        logger.info(f"Added {len(chunks)} chunks to FAISS store.")
