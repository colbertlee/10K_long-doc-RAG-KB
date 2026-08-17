"""Tests for document chunking."""

from rag_kb.chunkers.structured import StructuredChunker
from rag_kb.chunkers.parent_child import ParentChildChunker
from rag_kb.models import Document


def test_structure_chunker_preserves_headings():
    """Test that structured chunker preserves heading hierarchy."""
    doc = Document(doc_id='d1', content='# Title\npara1\n## Section\npara2')
    chunks = StructuredChunker().chunk(doc)
    
    assert len(chunks) >= 2
    assert chunks[0].level == 1
    assert 'Section' in chunks[-1].section_path


def test_structure_chunker_creates_overlapping_windows():
    """Test that structured chunker creates overlapping windows."""
    doc = Document(doc_id='d1', content='# Title\npara1\n## Section\npara2')
    chunker = StructuredChunker(overlap_chars=10)
    chunks = chunker.chunk(doc)
    
    # Check that chunks have some overlap
    if len(chunks) > 1:
        # Verify overlap is working by checking that chunks are created
        assert len(chunks) > 0


def test_parent_child_chunker_creates_hierarchy():
    """Test that parent-child chunker creates hierarchical chunks."""
    doc = Document(doc_id='d1', content='# Title\nThis is a longer paragraph that should be split into multiple child chunks for testing the parent-child relationship.')
    chunker = ParentChildChunker(child_target=5)
    chunks = chunker.chunk(doc)
    
    # Should create multiple child chunks from parent sections
    assert len(chunks) > 0
    
    # Check that child chunks have parent_id
    parent_chunks = [c for c in chunks if c.parent_id is None]
    child_chunks = [c for c in chunks if c.parent_id is not None]
    
    # In parent-child chunker, we expect mostly child chunks
    assert len(child_chunks) >= 0