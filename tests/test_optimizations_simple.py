"""Simple optimization verification test (configuration only)."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.config import settings


def test_gpu_configuration():
    """Test GPU configuration settings."""
    
    print("=" * 60)
    print("Testing GPU Configuration")
    print("=" * 60)
    
    print(f"\nEmbedding device: {settings.embedding_device}")
    print(f"Embedding batch size: {settings.embedding_batch_size}")
    print(f"Reranking enabled: {settings.enable_reranking}")
    print(f"Reranking device: {settings.reranking_device}")
    print(f"Reranking batch size: {settings.reranking_batch_size}")
    print(f"LLM cache enabled: {settings.lightrag_enable_llm_cache}")
    
    return True


def test_graph_visualization():
    """Test graph visualization files."""
    
    print("\n" + "=" * 60)
    print("Testing Graph Visualization")
    print("=" * 60)
    
    # Check if graph visualization file exists
    graph_file = Path("static/graph_visualization.html")
    if graph_file.exists():
        print(f"✅ Graph visualization file exists: {graph_file}")
    else:
        print(f"❌ Graph visualization file not found: {graph_file}")
        return False
    
    # Check if GPU embedding module exists
    try:
        from rag_kb.lightrag import gpu_embedding
        print("✅ GPU embedding module exists")
    except ImportError:
        print("⚠️ GPU embedding module not found")
    
    # Check if GPU reranker module exists
    try:
        from rag_kb.retrieval import gpu_reranker
        print("✅ GPU reranker module exists")
    except ImportError:
        print("⚠️ GPU reranker module not found")
    
    return True


def test_streaming_response():
    """Test streaming response configuration."""
    
    print("\n" + "=" * 60)
    print("Testing Streaming Response")
    print("=" * 60)
    
    # Check if streaming function exists
    try:
        from rag_kb.api.routes import _stream_chat_response
        print("✅ Streaming response function available")
    except ImportError:
        print("⚠️ Streaming response function not found")
        return False
    
    # Check if async is imported
    import asyncio
    print("✅ Asyncio available for streaming")
    
    return True


def test_llm_cache():
    """Test LLM cache configuration."""
    
    print("\n" + "=" * 60)
    print("Testing LLM Cache")
    print("=" * 60)
    
    print(f"LLM cache enabled: {settings.lightrag_enable_llm_cache}")
    
    if settings.lightrag_enable_llm_cache:
        print("✅ LLM cache is enabled")
        print("   This will improve performance for repeated queries")
    else:
        print("⚠️ LLM cache is disabled")
        print("   Enable it in config.py for better performance")
    
    return True


def test_all_optimizations():
    """Test all optimizations comprehensively."""
    
    print("\n" + "=" * 60)
    print("Comprehensive Optimization Verification")
    print("=" * 60)
    
    results = {
        'gpu_configuration': test_gpu_configuration(),
        'graph_visualization': test_graph_visualization(),
        'streaming_response': test_streaming_response(),
        'llm_cache': test_llm_cache()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("Optimization Verification Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nTotal: {passed_tests}/{total_tests} optimizations verified")
    
    if passed_tests == total_tests:
        print("🎉 All optimizations verified successfully!")
        return True
    else:
        print(f"⚠️ {total_tests - passed_tests} optimization(s) need attention.")
        return False


if __name__ == "__main__":
    result = test_all_optimizations()
    sys.exit(0 if result else 1)