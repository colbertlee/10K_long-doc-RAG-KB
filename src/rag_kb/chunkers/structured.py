"""Structure-aware chunker for semantic document chunking."""

import re
import uuid
from typing import List
from rag_kb.models import Document, Chunk
from rag_kb.chunkers.base import BaseChunker


class StructuredChunker(BaseChunker):
    """Structure-aware chunker: split by H1..H6, merge small paragraphs,
    keep overlapping windows between sections."""
    
    def __init__(self, target_tokens: int = 400, overlap_chars: int = 60):
        self.target_tokens = target_tokens
        self.overlap_chars = overlap_chars

    def _heading_level(self, line: str) -> int:
        """Extract heading level from markdown-style headers."""
        m = re.match(r'^(#{1,6})\s+', line)
        return len(m.group(1)) if m else 0

    def chunk(self, doc: Document) -> List[Chunk]:
        """Split document into semantic chunks based on structure."""
        chunks: List[Chunk] = []
        section_path: List[str] = []
        buffer = ''
        current_title = ''
        current_level = 0

        for line in doc.content.splitlines():
            level = self._heading_level(line)
            if level:
                if buffer.strip():
                    chunks.append(self._make_chunk(doc, buffer, current_title, section_path, current_level))
                    buffer = buffer[-self.overlap_chars:] if self.overlap_chars else ''
                current_title = line.strip().lstrip('#').strip()
                section_path = section_path[:level - 1] + [current_title]
                current_level = level
            else:
                buffer += line + '\n'

        if buffer.strip():
            chunks.append(self._make_chunk(doc, buffer, current_title, section_path, current_level))
        return chunks

    def _make_chunk(self, doc, text, title, path, level):
        """Create a Chunk object from the given parameters."""
        return Chunk(
            chunk_id=str(uuid.uuid4()),
            doc_id=doc.doc_id,
            text=text.strip(),
            level=level,
            section_path=path,
            token_count=len(text) // 4,
            metadata={**doc.metadata, 'title': title},
        )