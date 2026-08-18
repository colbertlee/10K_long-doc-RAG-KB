"""Test script for document ingestion functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.ingest.pipeline import IngestPipeline
from rag_kb.parsers.registry import PARSER_REGISTRY
from rag_kb.chunkers.structured import StructuredChunker
from rag_kb.chunkers.parent_child import ParentChildChunker

def test_basic_ingestion():
    """Test basic document ingestion."""
    print("🧪 Testing Basic Document Ingestion")
    print("=" * 50)
    
    # Sample file
    sample_file = Path(__file__).parent.parent / "data" / "samples" / "sample_document.txt"
    
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    print(f"📄 Processing file: {sample_file}")
    
    # Test parsing
    print("\n🔍 Testing Document Parsing...")
    parser = next((p for p in PARSER_REGISTRY if p.can_parse(sample_file)), None)
    if not parser:
        print(f"❌ No parser found for {sample_file.suffix}")
        return False
    
    print(f"✅ Using parser: {parser.__class__.__name__}")
    
    # Test ingestion pipeline
    print("\n⚙️  Testing Ingestion Pipeline...")
    pipeline = IngestPipeline()
    
    try:
        doc = pipeline.run(sample_file, acl={'dept': ['Engineering'], 'level': ['Internal']})
        print(f"✅ Document processed successfully")
        print(f"   - Document ID: {doc.doc_id}")
        print(f"   - Title: {doc.title}")
        print(f"   - Content length: {len(doc.content)} characters")
        print(f"   - ACL: {doc.acl}")
        print(f"   - Metadata: {doc.metadata}")
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        return False
    
    # Test chunking
    print("\n🔪 Testing Document Chunking...")
    
    # Test structured chunking
    print("   Testing StructuredChunker...")
    structured_chunker = StructuredChunker(target_tokens=400, overlap_chars=60)
    chunks = structured_chunker.chunk(doc)
    print(f"   ✅ Structured chunking created {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"   Chunk {i+1}:")
        print(f"     - ID: {chunk.chunk_id}")
        print(f"     - Level: {chunk.level}")
        print(f"     - Section path: {chunk.section_path}")
        print(f"     - Token count: {chunk.token_count}")
        print(f"     - Text preview: {chunk.text[:100]}...")
    
    # Test parent-child chunking
    print("\n   Testing ParentChildChunker...")
    parent_child_chunker = ParentChildChunker(parent_target=1200, child_target=250, overlap_chars=40)
    pc_chunks = parent_child_chunker.chunk(doc)
    print(f"   ✅ Parent-child chunking created {len(pc_chunks)} chunks")
    
    parent_count = sum(1 for c in pc_chunks if c.parent_id is None)
    child_count = len(pc_chunks) - parent_count
    print(f"   - Parent chunks: {parent_count}")
    print(f"   - Child chunks: {child_count}")
    
    print("\n🎉 All ingestion tests passed!")
    return True

def test_bm25_indexing():
    """Test BM25 indexing with ingested document."""
    print("\n🧪 Testing BM25 Indexing")
    print("=" * 50)
    
    try:
        from rag_kb.retrieval.bm25_search import BM25SearchEngine
    except ImportError:
        print("⚠️  BM25 module not available, skipping BM25 test")
        return True
    
    # Sample file
    sample_file = Path(__file__).parent.parent / "data" / "samples" / "sample_document.txt"
    
    # Create BM25 engine
    print("🔧 Creating BM25 search engine...")
    bm25_engine = BM25SearchEngine()
    
    # Ingest document
    print("📄 Ingesting document...")
    pipeline = IngestPipeline()
    doc = pipeline.run(sample_file, acl={'dept': ['Engineering'], 'level': ['Internal']})
    
    # Add to BM25 index
    print("📊 Adding document to BM25 index...")
    bm25_engine.add_document(doc.doc_id, doc.content, doc.metadata)
    
    # Build index
    print("🔨 Building BM25 index...")
    bm25_engine.build_index()
    
    # Test search
    print("🔍 Testing BM25 search...")
    results = bm25_engine.search("machine learning", top_k=3)
    
    print(f"✅ Search returned {len(results)} results:")
    for doc_id, score in results:
        print(f"   - {doc_id}: {score:.4f}")
    
    # Get statistics
    stats = bm25_engine.get_statistics()
    print(f"\n📈 BM25 Statistics:")
    print(f"   - Corpus size: {stats['corpus_size']}")
    print(f"   - Average doc length: {stats['avg_doc_len']:.2f}")
    print(f"   - Total terms: {stats['total_terms']}")
    
    print("\n🎉 BM25 indexing test passed!")
    return True

if __name__ == "__main__":
    print("🚀 RAG KB Ingestion Test Suite")
    print("=" * 50)
    
    success = True
    
    try:
        if not test_basic_ingestion():
            success = False
        
        if not test_bm25_indexing():
            success = False
        
        if success:
            print("\n" + "=" * 50)
            print("✅ All tests completed successfully!")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed")
            print("=" * 50)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)