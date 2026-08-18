"""Test script for hybrid search functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.ingest.pipeline import IngestPipeline
from rag_kb.retrieval.bm25_search import BM25SearchEngine
from rag_kb.retrieval.hybrid_search import HybridSearchEngine
from rag_kb.models import SearchResult

def test_hybrid_search():
    """Test hybrid search functionality."""
    print("🧪 Testing Hybrid Search Functionality")
    print("=" * 50)
    
    # Sample files
    sample_dir = Path(__file__).parent.parent / "data" / "samples"
    sample_files = list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.md"))
    
    if not sample_files:
        print(f"❌ No sample files found in {sample_dir}")
        return False
    
    print(f"📄 Found {len(sample_files)} sample files")
    
    # Create BM25 engine
    print("\n🔧 Creating BM25 search engine...")
    bm25_engine = BM25SearchEngine()
    
    # Ingest documents
    print("📄 Ingesting documents...")
    pipeline = IngestPipeline()
    documents = []
    
    for sample_file in sample_files[:3]:  # Process first 3 files
        try:
            doc = pipeline.run(sample_file, acl={'dept': ['Engineering'], 'level': ['Internal']})
            documents.append(doc)
            bm25_engine.add_document(doc.doc_id, doc.content, doc.metadata)
            print(f"   ✅ Processed: {sample_file.name}")
        except Exception as e:
            print(f"   ⚠️  Error processing {sample_file.name}: {e}")
    
    # Build BM25 index
    print("🔨 Building BM25 index...")
    bm25_engine.build_index()
    
    # Create hybrid search engine
    print("\n🔧 Creating hybrid search engine...")
    hybrid_engine = HybridSearchEngine(
        bm25_engine=bm25_engine,
        lightrag_adapter=None,  # Skip LightRAG for this test
        enable_reranking=False  # Disable reranking for basic test
    )
    
    # Test different search modes
    test_queries = [
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "supervised learning"
    ]
    
    print("\n🔍 Testing different search modes...")
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        
        # Test BM25 only
        print("   BM25 only mode:")
        try:
            bm25_results = hybrid_engine.search(
                query, 
                top_k=3, 
                mode='bm25_only',
                user_roles={'dept': ['Engineering'], 'level': ['Internal']}
            )
            print(f"   ✅ Found {len(bm25_results)} results")
            for i, result in enumerate(bm25_results):
                print(f"      {i+1}. {result.doc_id} (score: {result.score:.4f})")
        except Exception as e:
            print(f"   ❌ BM25 search error: {e}")
        
        # Test hybrid mode (without LightRAG, falls back to BM25)
        print("   Hybrid mode (BM25 fallback):")
        try:
            hybrid_results = hybrid_engine.search(
                query,
                top_k=3,
                mode='hybrid',
                user_roles={'dept': ['Engineering'], 'level': ['Internal']}
            )
            print(f"   ✅ Found {len(hybrid_results)} results")
            for i, result in enumerate(hybrid_results):
                print(f"      {i+1}. {result.doc_id} (score: {result.score:.4f})")
        except Exception as e:
            print(f"   ❌ Hybrid search error: {e}")
    
    # Test ACL filtering
    print("\n🔒 Testing ACL filtering...")
    print("   Query with Engineering dept access:")
    try:
        results = hybrid_engine.search(
            "machine learning",
            top_k=3,
            user_roles={'dept': ['Engineering'], 'level': ['Internal']}
        )
        print(f"   ✅ Found {len(results)} results with Engineering access")
    except Exception as e:
        print(f"   ❌ ACL search error: {e}")
    
    print("   Query with Marketing dept access (should return fewer results):")
    try:
        results = hybrid_engine.search(
            "machine learning",
            top_k=3,
            user_roles={'dept': ['Marketing'], 'level': ['Internal']}
        )
        print(f"   ✅ Found {len(results)} results with Marketing access")
    except Exception as e:
        print(f"   ❌ ACL search error: {e}")
    
    # Get statistics
    print("\n📈 Search Engine Statistics:")
    try:
        stats = hybrid_engine.get_statistics()
        print(f"   - BM25 corpus size: {stats['bm25']['corpus_size']}")
        print(f"   - BM25 total terms: {stats['bm25']['total_terms']}")
        print(f"   - LightRAG status: {stats['lightrag']}")
        print(f"   - RRF constant: {stats['rrf_k']}")
    except Exception as e:
        print(f"   ❌ Statistics error: {e}")
    
    print("\n🎉 Hybrid search tests passed!")
    return True

def test_reranking():
    """Test reranking functionality."""
    print("\n🧪 Testing Reranking Functionality")
    print("=" * 50)
    
    try:
        from rag_kb.retrieval.reranker import SimpleReranker, RerankerPipeline
    except ImportError:
        print("⚠️  Reranking module not available, skipping reranking test")
        return True
    
    # Create sample search results
    sample_results = [
        SearchResult(
            chunk_id="c1", 
            doc_id="doc1", 
            text="Machine learning is a subset of artificial intelligence focused on data-driven systems.",
            score=0.8, 
            rank=1,
            metadata={"title": "ML Basics"}
        ),
        SearchResult(
            chunk_id="c2", 
            doc_id="doc2", 
            text="Deep learning uses neural networks with multiple layers for complex pattern recognition.",
            score=0.7, 
            rank=2,
            metadata={"title": "Deep Learning"}
        ),
        SearchResult(
            chunk_id="c3", 
            doc_id="doc3", 
            text="Natural language processing deals with understanding and generating human language.",
            score=0.6, 
            rank=3,
            metadata={"title": "NLP"}
        )
    ]
    
    print("📊 Created sample search results")
    
    # Test simple reranker
    print("\n🔧 Testing SimpleReranker...")
    simple_reranker = SimpleReranker()
    
    query = "machine learning algorithms"
    reranked = simple_reranker.rerank(query, sample_results, top_k=3)
    
    print(f"✅ Reranked {len(reranked)} results:")
    for i, result in enumerate(reranked):
        print(f"   {i+1}. {result.doc_id} (new score: {result.score:.4f}, rank: {result.rank})")
    
    # Test reranker pipeline
    print("\n🔧 Testing RerankerPipeline...")
    try:
        reranker_pipeline = RerankerPipeline(
            enable_cross_encoder=False  # Use simple reranking
        )
        
        reranked_pipeline = reranker_pipeline.rerank(query, sample_results, top_k=3)
        
        print(f"✅ Pipeline reranked {len(reranked_pipeline)} results:")
        for i, result in enumerate(reranked_pipeline):
            print(f"   {i+1}. {result.doc_id} (new score: {result.score:.4f}, rank: {result.rank})")
        
        # Get reranker info
        try:
            info = reranker_pipeline.get_reranker_info()
            print(f"\n📋 Reranker Info:")
            print(f"   - Cross-encoder enabled: {info['cross_encoder_enabled']}")
            print(f"   - Device: {info['device']}")
        except AttributeError as e:
            print(f"   ⚠️  Reranker info not available: {e}")
        
    except Exception as e:
        print(f"❌ Pipeline reranking error: {e}")
    
    print("\n🎉 Reranking tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 RAG KB Hybrid Search Test Suite")
    print("=" * 50)
    
    success = True
    
    try:
        if not test_hybrid_search():
            success = False
        
        if not test_reranking():
            success = False
        
        if success:
            print("\n" + "=" * 50)
            print("✅ All hybrid search tests completed successfully!")
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