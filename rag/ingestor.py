import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from config.settings import settings

logger = logging.getLogger(__name__)


class DocumentIngestor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""],
        )

    def load_directory(self, directory: str = None) -> List[Document]:
        directory = directory or settings.DATA_DIR
        path = Path(directory)
        if not path.exists():
            logger.warning(f"Data directory {directory} does not exist.")
            return []
        docs = []
        for file in path.rglob("*"):
            if file.suffix == ".pdf":
                docs.extend(self._load_pdf(str(file)))
            elif file.suffix in [".txt", ".md"]:
                docs.extend(self._load_text(str(file)))
        logger.info(f"Loaded {len(docs)} raw documents")
        return docs

    def _load_pdf(self, path: str) -> List[Document]:
        try:
            loader = PyPDFLoader(path)
            return loader.load()
        except Exception as e:
            logger.error(f"Failed to load PDF {path}: {e}")
            return []

    def _load_text(self, path: str) -> List[Document]:
        try:
            loader = TextLoader(path, encoding="utf-8")
            return loader.load()
        except Exception as e:
            logger.error(f"Failed to load text {path}: {e}")
            return []

    def chunk_documents(self, docs: List[Document]) -> List[Document]:
        chunks = self.splitter.split_documents(docs)
        logger.info(f"Split into {len(chunks)} chunks")
        return chunks

    def ingest(self, directory: str = None) -> List[Document]:
        docs = self.load_directory(directory)
        return self.chunk_documents(docs)
