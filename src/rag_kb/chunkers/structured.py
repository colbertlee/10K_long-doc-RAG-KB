"""Structure-aware chunker for semantic document chunking."""

import re
import uuid

from rag_kb.chunkers.base import BaseChunker
from rag_kb.models import Chunk


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

    def chunk(self, doc, metadata=None) -> list[Chunk]:
        """Split document into semantic chunks based on structure.
        
        Args:
            doc: Either a Document object or a content string
            metadata: Optional metadata dictionary
            
        Returns:
            List of Chunk objects
        """
        # Handle both Document object and string content
        if isinstance(doc, str):
            content = doc
            doc_metadata = metadata or {}
            doc_id = doc_metadata.get('doc_id', str(uuid.uuid4()))
        else:
            content = doc.content
            doc_metadata = doc.metadata
            doc_id = doc.doc_id
        
        chunks: list[Chunk] = []
        section_path: list[str] = []
        buffer = ''
        current_title = ''
        current_level = 0

        for line in content.splitlines():
            level = self._heading_level(line)
            if level:
                if buffer.strip():
                    chunks.append(self._make_chunk(doc_id, buffer, current_title, section_path, current_level, doc_metadata))
                    buffer = buffer[-self.overlap_chars:] if self.overlap_chars else ''
                current_title = line.strip().lstrip('#').strip()
                section_path = section_path[:level - 1] + [current_title]
                current_level = level
            else:
                buffer += line + '\n'

        if buffer.strip():
            chunks.append(self._make_chunk(doc_id, buffer, current_title, section_path, current_level, doc_metadata))
        return chunks

    def _make_chunk(self, doc_id, text, title, path, level, metadata):
        """Create a Chunk object from the given parameters with enhanced citation metadata."""
        # Enhanced metadata for citation tracking
        enhanced_metadata = {
            **metadata,
            'title': title,
            'chapter': title if title else metadata.get('chapter', '未知章节'),
            'section': ' > '.join(path) if path else metadata.get('section', '未知章节'),
            'section_path': path,
            'level': level,
            'page': metadata.get('page', metadata.get('pages', '未知页码')),
            'source': metadata.get('source', '未知来源'),
            'filename': metadata.get('filename', metadata.get('title', '未知文档')),
        }
        
        return Chunk(
            chunk_id=str(uuid.uuid4()),
            doc_id=doc_id,
            text=text.strip(),
            level=level,
            section_path=path,
            token_count=len(text) // 4,
            metadata=enhanced_metadata,
        )