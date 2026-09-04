"""Base chunker interface for document chunking."""

from abc import ABC, abstractmethod

from rag_kb.models import Chunk, Document


class BaseChunker(ABC):
    """Abstract base class for document chunkers."""
    
    @abstractmethod
    def chunk(self, doc: Document) -> list[Chunk]:
        """Split a Document into semantic Chunks."""
        ...