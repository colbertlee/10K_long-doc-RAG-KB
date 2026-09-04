"""Parent-child chunker for hierarchical document chunking."""

import uuid

from rag_kb.chunkers.structured import StructuredChunker
from rag_kb.models import Chunk, Document


class ParentChildChunker(StructuredChunker):
    """Small child chunks for high-precision retrieval; parent chunk
    carries full section context for prompt expansion."""
    
    def __init__(self, parent_target: int = 1200, child_target: int = 250, overlap_chars: int = 40):
        super().__init__(target_tokens=child_target, overlap_chars=overlap_chars)
        self.parent_target = parent_target

    def chunk(self, doc: Document) -> list[Chunk]:
        """Split document into parent-child chunk hierarchy."""
        sections = super().chunk(doc)
        children: list[Chunk] = []
        
        for parent in sections:
            parent.chunk_id = str(uuid.uuid4())
            parent.token_count = len(parent.text) // 4
            words = parent.text.split()
            start = 0
            
            while start < len(words):
                end = min(start + self.target_tokens, len(words))
                child_text = ' '.join(words[start:end])
                children.append(Chunk(
                    chunk_id=str(uuid.uuid4()),
                    doc_id=doc.doc_id,
                    parent_id=parent.chunk_id,
                    text=child_text,
                    level=parent.level,
                    section_path=parent.section_path,
                    token_count=len(child_text) // 4,
                    metadata={'parent_text': parent.text, **doc.metadata},
                ))
                start = end
        
        return children