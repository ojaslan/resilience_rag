from rag.ingestor import DocumentIngestor
from rag.embedder import VectorEmbedder

ingestor = DocumentIngestor()
chunks = ingestor.ingest()
print(f'Chunks: {len(chunks)}')

embedder = VectorEmbedder()
embedder.build_store(chunks)
print('Done! Vector store ready.')
