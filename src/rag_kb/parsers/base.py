"""Base parser interface for document parsing."""

from abc import ABC, abstractmethod
from pathlib import Path

from rag_kb.models import Document


class BaseParser(ABC):
    """Abstract base class for document parsers."""
    
    supported_ext: tuple[str, ...] = ()

    @abstractmethod
    def parse(self, path: Path) -> Document:
        """Return a Document with full text and metadata."""
        ...

    def can_parse(self, path: Path) -> bool:
        """Check if this parser can handle the given file."""
        return path.suffix.lower() in self.supported_ext