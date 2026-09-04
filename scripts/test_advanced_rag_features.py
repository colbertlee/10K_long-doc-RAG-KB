"""Test script for advanced RAG features: hybrid search, reranking, and RAGAS evaluation."""

import asyncio
import sys
sys.path.insert(0, 'src')

from rag_kb.retrieval import HybridSearchEngine, RerankerFactory
from rag_kb.evaluation import RAGASEvaluator, RAGQualityMonitor


async def test_hybrid_search():
    """Test hybrid search with BM25 + vector fusion."""
    print("=" * 60)
    print("Testing Hybrid Search (Vector Search + RRF Fusion)")
    print("=" * 60)
    
    try:
        # Initialize hybrid search engine
        hybrid_engine = HybridSearchEngine()
        await hybrid_engine.initialize()
        
        # Test query
        query = "Dell PowerEdge server specifications"
        print(f"\nQuery: {query}")
        
        # Test vector search (BM25 requires document indexing)
        print("\n1. Vector Search:")
        vector_results = await hybrid_engine.search(query, top_k=3, mode="vector")
        for i, result in enumerate(vector_results, 1):
            print(f"   {i}. Score: {result.score:.3f} | Source: {result.source}")
            print(f"      Content: {result.content[:100]}...")
        
        print("\n2. Hybrid Search (Vector only for now):")
        hybrid_results = await hybrid_engine.search(query, top_k=3, mode="hybrid")
        for i, result in enumerate(hybrid_results, 1):
            print(f"   {i}. Score: {result.score:.3f} | Source: {result.source}")
            print(f"      Content: {result.content[:100]}...")
        
        print("\n✅ Hybrid search test completed successfully!")
        print("Note: BM25 search requires document indexing to be fully functional.")
        return True
        
    except Exception as e:
        print(f"\n❌ Hybrid search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_reranking():
    """Test BGE-Reranker integration."""
    print("\n" + "=" * 60)
    print("Testing BGE-Reranker Integration")
    print("=" * 60)
    
    try:
        # Create reranker (will fallback to rule-based if BGE not available)
        reranker = RerankerFactory.create_reranker(use_bge=True)
        await reranker.initialize()
        
        print(f"Reranker type: {type(reranker).__name__}")
        
        # Mock search results for testing
        from rag_kb.retrieval import SearchResult
        mock_results = [
            SearchResult(
                doc_id="doc1",
                content="Dell PowerEdge servers are enterprise-grade servers designed for data centers.",
                score=0.5,
                source="hybrid"
            ),
            SearchResult(
                doc_id="doc2", 
                content="The PowerEdge R750 is a 2U rack server with Intel Xeon processors.",
                score=0.4,
                source="hybrid"
            ),
            SearchResult(
                doc_id="doc3",
                content="Storage solutions include SAN, NAS, and direct-attached storage options.",
                score=0.3,
                source="hybrid"
            )
        ]
        
        query = "What are Dell PowerEdge server specifications?"
        print(f"\nQuery: {query}")
        
        print("\nBefore reranking:")
        for i, result in enumerate(mock_results, 1):
            print(f"   {i}. Score: {result.score:.3f} | {result.content[:60]}...")
        
        # Apply reranking
        reranked = await reranker.rerank(query, mock_results, top_k=3)
        
        print("\nAfter reranking:")
        for i, result in enumerate(reranked, 1):
            print(f"   {i}. Score: {result.score:.3f} | {result.content[:60]}...")
        
        print("\n✅ Reranking test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Reranking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ragas_evaluation():
    """Test RAGAS evaluation framework."""
    print("\n" + "=" * 60)
    print("Testing RAGAS Evaluation Framework")
    print("=" * 60)
    
    try:
        # Initialize evaluator
        evaluator = RAGASEvaluator(use_ragas=True)
        await evaluator.initialize()
        
        print(f"Evaluator type: {'RAGAS' if evaluator.use_ragas else 'Fallback'}")
        
        # Add evaluation cases
        print("\nAdding evaluation cases...")
        
        # Case 1: Good quality
        evaluator.add_evaluation_case(
            question="What is Dell PowerEdge?",
            contexts=[
                "Dell PowerEdge is a line of enterprise-grade servers designed for data centers and cloud computing.",
                "PowerEdge servers feature Intel Xeon processors, high memory capacity, and advanced management capabilities."
            ],
            answer="Dell PowerEdge is a line of enterprise-grade servers designed for data centers and cloud computing, featuring Intel Xeon processors and advanced management capabilities.",
            ground_truth="Dell PowerEdge is Dell's enterprise server line designed for data centers."
        )
        
        # Case 2: Medium quality
        evaluator.add_evaluation_case(
            question="How much memory can PowerEdge servers support?",
            contexts=[
                "PowerEdge servers support up to 64TB of memory in some configurations.",
                "Memory capacity varies by model, with entry-level servers supporting less memory."
            ],
            answer="PowerEdge servers can support significant memory capacity, with some models supporting up to 64TB.",
            ground_truth="PowerEdge servers can support up to 64TB of memory."
        )
        
        # Case 3: Lower quality
        evaluator.add_evaluation_case(
            question="What management features do PowerEdge servers have?",
            contexts=[
                "PowerEdge servers include iDRAC for remote management.",
                "OpenManage software provides comprehensive server management capabilities."
            ],
            answer="PowerEdge servers have good management features.",
            ground_truth="PowerEdge servers include iDRAC for remote management and OpenManage software for comprehensive management."
        )
        
        # Get summary
        summary = evaluator.get_evaluation_summary()
        print(f"Evaluation summary: {summary}")
        
        # Run evaluation
        print("\nRunning evaluation...")
        results = await evaluator.evaluate()
        
        print("\nEvaluation Results:")
        for metric, value in results.items():
            if isinstance(value, float):
                print(f"   {metric}: {value:.3f}")
            else:
                print(f"   {metric}: {value}")
        
        # Test quality monitoring
        print("\nTesting quality monitoring...")
        monitor = RAGQualityMonitor(evaluator)
        
        quality_assessment = await monitor.monitor_quality(
            question="What is the latest PowerEdge model?",
            contexts=["The latest PowerEdge models include the R750 and R850 series."],
            answer="The latest PowerEdge models are the R750 and R850 series."
        )
        
        print(f"Quality assessment: {quality_assessment}")
        
        # Get trends
        trends = monitor.get_quality_trends()
        print(f"Quality trends: {trends}")
        
        print("\n✅ RAGAS evaluation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ RAGAS evaluation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integrated_pipeline():
    """Test the complete integrated pipeline."""
    print("\n" + "=" * 60)
    print("Testing Integrated Pipeline (Hybrid Search + Reranking + Evaluation)")
    print("=" * 60)
    
    try:
        # Initialize components
        hybrid_engine = HybridSearchEngine()
        await hybrid_engine.initialize()
        
        reranker = RerankerFactory.create_reranker(use_bge=True)
        await reranker.initialize()
        
        evaluator = RAGASEvaluator(use_ragas=True)
        await evaluator.initialize()
        
        # Test query
        query = "Dell server management features"
        print(f"Query: {query}")
        
        # Step 1: Hybrid search
        print("\nStep 1: Hybrid search...")
        search_results = await hybrid_engine.search(query, top_k=5, mode="hybrid")
        print(f"Found {len(search_results)} results")
        
        # Step 2: Reranking
        print("\nStep 2: Reranking...")
        reranked_results = await reranker.rerank(query, search_results, top_k=3)
        print(f"Reranked to top {len(reranked_results)} results")
        
        # Step 3: Quality evaluation
        print("\nStep 3: Quality evaluation...")
        if reranked_results:
            evaluator.add_evaluation_case(
                question=query,
                contexts=[r.content for r in reranked_results],
                answer=reranked_results[0].content if reranked_results else "No answer generated"
            )
            
            evaluation_results = await evaluator.evaluate()
            print(f"Evaluation results: {evaluation_results}")
        
        print("\n✅ Integrated pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integrated pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🚀 Advanced RAG Features Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Hybrid search
    results.append(await test_hybrid_search())
    
    # Test 2: Reranking
    results.append(await test_reranking())
    
    # Test 3: RAGAS evaluation
    results.append(await test_ragas_evaluation())
    
    # Test 4: Integrated pipeline
    results.append(await test_integrated_pipeline())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if all(results):
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
    
    return all(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)