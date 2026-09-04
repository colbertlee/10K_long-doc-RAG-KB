"""Simple test for advanced RAG features without full dependencies."""

import asyncio
import sys
sys.path.insert(0, 'src')

async def test_basic_functionality():
    """Test basic functionality of advanced features."""
    print("🚀 Advanced RAG Features - Basic Functionality Test")
    print("=" * 60)
    
    # Test 1: Module imports
    print("\n1. Testing module imports...")
    try:
        from rag_kb.retrieval import HybridSearchEngine, RerankerFactory
        from rag_kb.evaluation import RAGASEvaluator
        print("✅ All modules imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Hybrid search initialization
    print("\n2. Testing hybrid search initialization...")
    try:
        hybrid_engine = HybridSearchEngine()
        await hybrid_engine.initialize()
        print("✅ Hybrid search engine initialized")
    except Exception as e:
        print(f"❌ Hybrid search initialization failed: {e}")
        return False
    
    # Test 3: Reranker creation
    print("\n3. Testing reranker creation...")
    try:
        reranker = RerankerFactory.create_reranker(use_bge=False)  # Use rule-based
        await reranker.initialize()
        print(f"✅ Reranker created: {type(reranker).__name__}")
    except Exception as e:
        print(f"❌ Reranker creation failed: {e}")
        return False
    
    # Test 4: RAGAS evaluator initialization
    print("\n4. Testing RAGAS evaluator initialization...")
    try:
        evaluator = RAGASEvaluator(use_ragas=False)  # Use fallback
        await evaluator.initialize()
        print(f"✅ RAGAS evaluator initialized (fallback mode)")
    except Exception as e:
        print(f"❌ RAGAS evaluator initialization failed: {e}")
        return False
    
    # Test 5: Simple search test
    print("\n5. Testing simple vector search...")
    try:
        results = await hybrid_engine.search("Dell server", top_k=2, mode="vector")
        print(f"✅ Vector search returned {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"   {i}. Score: {result.score:.3f} | Source: {result.source}")
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False
    
    # Test 6: Simple reranking test
    print("\n6. Testing simple reranking...")
    try:
        from rag_kb.retrieval import SearchResult
        mock_results = [
            SearchResult(doc_id="1", content="Dell servers are great", score=0.5, source="vector"),
            SearchResult(doc_id="2", content="Server management tools", score=0.4, source="vector")
        ]
        reranked = await reranker.rerank("Dell server features", mock_results, top_k=2)
        print(f"✅ Reranking completed, returned {len(reranked)} results")
        for i, result in enumerate(reranked, 1):
            print(f"   {i}. Score: {result.score:.3f} | {result.content[:40]}...")
    except Exception as e:
        print(f"❌ Reranking test failed: {e}")
        return False
    
    # Test 7: Simple evaluation test
    print("\n7. Testing simple evaluation...")
    try:
        evaluator.add_evaluation_case(
            question="What is Dell?",
            contexts=["Dell is a technology company"],
            answer="Dell is a technology company",
            ground_truth="Dell is a computer technology company"
        )
        results = await evaluator.evaluate()
        print(f"✅ Evaluation completed")
        print(f"   Overall score: {results.get('overall_score', 0):.3f}")
        print(f"   Method: {results.get('method', 'unknown')}")
    except Exception as e:
        print(f"❌ Evaluation test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All basic functionality tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)