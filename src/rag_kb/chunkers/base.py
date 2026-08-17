"""Base chunker interface for document chunking."""

from abc import ABC, abstractmethod
from typing import List
from rag_kb.models import Document, Chunk


class BaseChunker(ABC):
    """Abstract base class for document chunkers."""
    
    @abstractmethod
    def chunk(self, doc: Document) -> List[Chunk]:
        """Split a Document into semantic Chunks."""
        ...