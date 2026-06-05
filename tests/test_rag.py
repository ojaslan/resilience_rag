import pytest
from unittest.mock import MagicMock, patch
from langchain.schema import Document

from rag.ingestor import DocumentIngestor
from rag.retriever import DocumentRetriever


def test_ingestor_chunk_documents():
    ingestor = DocumentIngestor()
    docs = [Document(page_content="Hello world. " * 100, metadata={"source": "test.txt"})]
    chunks = ingestor.chunk_documents(docs)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 600  # chunk_size + some overhead


def test_ingestor_empty_directory(tmp_path):
    ingestor = DocumentIngestor()
    docs = ingestor.load_directory(str(tmp_path))
    assert docs == []


def test_retriever_format_context():
    mock_store = MagicMock()
    retriever = DocumentRetriever(mock_store)
    docs = [
        Document(page_content="Agentic AI is powerful.", metadata={"source": "doc1.pdf"}),
        Document(page_content="RAG improves accuracy.", metadata={"source": "doc2.pdf"}),
    ]
    context = retriever.format_context(docs)
    assert "Doc 1" in context
    assert "doc1.pdf" in context
    assert "Agentic AI is powerful." in context


def test_retriever_empty_docs():
    mock_store = MagicMock()
    retriever = DocumentRetriever(mock_store)
    context = retriever.format_context([])
    assert "No relevant documents" in context


def test_retriever_handles_store_error():
    mock_store = MagicMock()
    mock_store.similarity_search.side_effect = Exception("DB error")
    retriever = DocumentRetriever(mock_store)
    docs = retriever.retrieve("some query")
    assert docs == []
