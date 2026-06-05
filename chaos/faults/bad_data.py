import random
import logging
from typing import List
from langchain.schema import Document

logger = logging.getLogger(__name__)

NOISE_PHRASES = [
    "CORRUPTED_DATA_INJECTED",
    "ERROR: document unreadable",
    "NULL_REFERENCE_EXCEPTION",
    "⚠️ DATA INTEGRITY FAILURE ⚠️",
    "[[REDACTED]]",
]


def corrupt_documents(docs: any, config: dict = None) -> any:
    """
    Randomly corrupts retrieved documents to simulate bad data scenarios.
    Works if docs is a list of Document objects or a list of strings.
    Config keys:
      corruption_rate (float): fraction of docs to corrupt. Default 0.5
      mode (str): 'replace' | 'append' | 'empty'. Default 'append'
    """
    config = config or {}
    rate = config.get("corruption_rate", 0.5)
    mode = config.get("mode", "append")

    if not isinstance(docs, list):
        return docs

    corrupted = []
    for doc in docs:
        if random.random() < rate:
            noise = random.choice(NOISE_PHRASES)
            logger.warning(f"[CHAOS:bad_data] Corrupting doc with: {noise}")

            if isinstance(doc, Document):
                if mode == "replace":
                    doc = Document(page_content=noise, metadata=doc.metadata)
                elif mode == "empty":
                    doc = Document(page_content="", metadata=doc.metadata)
                else:
                    doc = Document(
                        page_content=doc.page_content + f"\n\n{noise}",
                        metadata=doc.metadata,
                    )
            elif isinstance(doc, str):
                doc = doc + f"\n{noise}" if mode == "append" else noise

        corrupted.append(doc)

    return corrupted
