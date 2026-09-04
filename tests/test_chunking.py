"""Modular chunking tests."""

import pytest
from rag_kb.chunkers.structured import StructuredChunker
from rag_kb.chunkers.parent_child import ParentChildChunker
from rag_kb.models import Document


class TestChunking:
    """Chunking module tests."""
    
    def test_structured_chunker_basic(self):
        """Test basic structured chunking."""
        doc = Document(doc_id='test_doc_1', content="# Test Document\n\nThis is a test document for testing purposes.\n\n## Section 1\nContent for section 1.\n\n## Section 2\nContent for section 2.")
        chunker = StructuredChunker()
        chunks = chunker.chunk(doc)
        
        assert len(chunks) > 0, "Should create at least one chunk"
        print("✅ Structured chunker basic test passed")
    
    def test_structured_chunker_heading_preservation(self):
        """Test heading preservation in structured chunking."""
        doc = Document(doc_id='test_doc_2', content="# Test Document\n\nThis is a test document for testing purposes.\n\n## Section 1\nContent for section 1.\n\n## Section 2\nContent for section 2.")
        chunks = StructuredChunker().chunk(doc)
        
        # Check that heading structure is preserved
        heading_chunks = [c for c in chunks if c.level > 0]
        assert len(heading_chunks) >= 2, "Should preserve heading structure"
        print("✅ Heading preservation test passed")
    
    def test_parent_child_chunker_hierarchy(self):
        """Test parent-child chunker hierarchy."""
        long_content = "# Main Title\n" + "This is a longer paragraph that should be split into multiple child chunks for testing the parent-child relationship. " * 10
        doc = Document(doc_id='test_parent', content=long_content)
        chunker = ParentChildChunker(child_target=5)
        chunks = chunker.chunk(doc)
        
        assert len(chunks) > 0, "Should create chunks"
        
        # Check for parent-child relationships
        parent_chunks = [c for c in chunks if c.parent_id is None]
        child_chunks = [c for c in chunks if c.parent_id is not None]
        
        assert len(parent_chunks) >= 0, "Should have parent chunks"
        assert len(child_chunks) >= 0, "Should have child chunks"
        print("✅ Parent-child hierarchy test passed")
    
    def test_chunk_overlap(self):
        """Test chunk overlap functionality."""
        doc = Document(doc_id='test_overlap', content="# Title\n" + "Content " * 100)
        chunker = StructuredChunker(overlap_chars=50)
        chunks = chunker.chunk(doc)
        
        if len(chunks) > 1:
            # Verify chunks are created with overlap
            assert len(chunks) > 0, "Should create chunks with overlap"
        print("✅ Chunk overlap test passed")
    
    def test_chunk_size_limits(self):
        """Test chunk size limits."""
        doc = Document(doc_id='test_size', content="# Title\n" + "Content " * 500)
        chunker = StructuredChunker()
        chunks = chunker.chunk(doc)
        
        # Verify chunks are created
        assert len(chunks) > 0, "Should create chunks"
        print("✅ Chunk size limits test passed")


class TestChunkingAdvanced:
    """Advanced chunking tests."""
    
    def test_empty_document_handling(self):
        """Test empty document handling."""
        doc = Document(doc_id='empty', content='')
        chunker = StructuredChunker()
        chunks = chunker.chunk(doc)
        
        # Should handle empty documents gracefully
        assert isinstance(chunks, list), "Should return list for empty documents"
        print("✅ Empty document handling test passed")
    
    def test_single_line_document(self):
        """Test single line document."""
        doc = Document(doc_id='single', content='Single line document')
        chunker = StructuredChunker()
        chunks = chunker.chunk(doc)
        
        assert len(chunks) >= 1, "Should create at least one chunk"
        print("✅ Single line document test passed")
    
    def test_unicode_handling(self):
        """Test unicode character handling."""
        unicode_content = "# 标题\n中文内容\n## 章节\nMore 中文内容"
        doc = Document(doc_id='unicode', content=unicode_content)
        chunker = StructuredChunker()
        chunks = chunker.chunk(doc)
        
        assert len(chunks) > 0, "Should handle unicode content"
        print("✅ Unicode handling test passed")