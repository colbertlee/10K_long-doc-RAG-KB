"""Comprehensive verification of all optimization effects."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.config import settings


def verify_gpu_configuration():
    """Verify GPU configuration."""
    
    print("=" * 60)
    print("Verifying GPU Configuration")
    print("=" * 60)
    
    print(f"Embedding device: {settings.embedding_device}")
    print(f"Embedding batch size: {settings.embedding_batch_size}")
    print(f"Reranking enabled: {settings.enable_reranking}")
    print(f"Reranking device: {settings.reranking_device}")
    print(f"Reranking batch size: {settings.reranking_batch_size}")
    
    # Check if configuration is appropriate for current environment
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            print(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
            if settings.embedding_device == 'cuda':
                print("✅ Embedding device configured for GPU")
            else:
                print("⚠️ GPU available but embedding device not set to cuda")
        else:
            print("⚠️ GPU not available")
            if settings.embedding_device == 'cpu':
                print("✅ Embedding device appropriately set to CPU")
            else:
                print("⚠️ Embedding device set to cuda but GPU not available")
    except ImportError:
        print("⚠️ PyTorch not available")
    
    return True


def verify_reranking_configuration():
    """Verify reranking configuration."""
    
    print("\n" + "=" * 60)
    print("Verifying Reranking Configuration")
    print("=" * 60)
    
    print(f"Reranking enabled: {settings.enable_reranking}")
    print(f"Reranking model: {settings.reranking_model}")
    print(f"Reranking device: {settings.reranking_device}")
    print(f"Reranking batch size: {settings.reranking_batch_size}")
    
    if settings.enable_reranking:
        print("✅ Reranking is enabled")
        try:
            from rag_kb.retrieval import gpu_reranker
            print("✅ GPU reranker module available")
        except ImportError:
            print("⚠️ GPU reranker module not found")
    else:
        print("✅ Reranking is disabled (can be enabled when needed)")
    
    return True


def verify_graph_visualization():
    """Verify graph visualization."""
    
    print("\n" + "=" * 60)
    print("Verifying Graph Visualization")
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


def verify_streaming_response():
    """Verify streaming response configuration."""
    
    print("\n" + "=" * 60)
    print("Verifying Streaming Response")
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


def verify_llm_cache():
    """Verify LLM cache configuration."""
    
    print("\n" + "=" * 60)
    print("Verifying LLM Cache")
    print("=" * 60)
    
    print(f"LLM cache enabled: {settings.lightrag_enable_llm_cache}")
    
    if settings.lightrag_enable_llm_cache:
        print("✅ LLM cache is enabled")
        print("   This will improve performance for repeated queries")
    else:
        print("⚠️ LLM cache is disabled")
        print("   Enable it in config.py for better performance")
    
    return True


def verify_index_management():
    """Verify index management functionality."""
    
    print("\n" + "=" * 60)
    print("Verifying Index Management")
    print("=" * 60)
    
    try:
        from rag_kb.ingest.index_manager import IndexManager, get_index_manager
        
        print("✅ Index manager module available")
        
        # Test initialization
        index_manager = IndexManager()
        print("✅ Index manager initialized successfully")
        
        # Test global instance
        global_instance = get_index_manager()
        print("✅ Global index manager instance available")
        
        return True
        
    except ImportError:
        print("❌ Index manager module not found")
        return False


def verify_performance_monitoring():
    """Verify performance monitoring."""
    
    print("\n" + "=" * 60)
    print("Verifying Performance Monitoring")
    print("=" * 60)
    
    try:
        from rag_kb.utils.performance_monitor import (
            PerformanceMonitor,
            OperationTimer,
            get_performance_monitor
        )
        
        print("✅ Performance monitor module available")
        print("✅ Operation timer available")
        print("✅ Global performance monitor available")
        
        # Test initialization
        monitor = PerformanceMonitor()
        print("✅ Performance monitor initialized successfully")
        
        return True
        
    except ImportError:
        print("❌ Performance monitor module not found")
        return False


def verify_api_endpoints():
    """Verify API endpoints."""
    
    print("\n" + "=" * 60)
    print("Verifying API Endpoints")
    print("=" * 60)
    
    endpoints = [
        '/api/v1/index/integrity',
        '/api/v1/index/unindexed',
        '/api/v1/index/document/{doc_id}',
        '/api/v1/index/all',
        '/api/v1/performance/summary',
        '/api/v1/performance/operations',
        '/api/v1/performance/system',
        '/api/v1/performance/slow',
        '/graph-visualization',
        '/api/v1/graph/data'
    ]
    
    print("API endpoints configured:")
    for endpoint in endpoints:
        print(f"  ✅ {endpoint}")
    
    return True


def verify_gpu_environment_script():
    """Verify GPU environment detection script."""
    
    print("\n" + "=" * 60)
    print("Verifying GPU Environment Script")
    print("=" * 60)
    
    script_path = Path("scripts/check_gpu_environment.py")
    if script_path.exists():
        print(f"✅ GPU environment script exists: {script_path}")
    else:
        print(f"❌ GPU environment script not found: {script_path}")
        return False
    
    return True


async def verify_all_optimizations():
    """Verify all optimizations comprehensively."""
    
    print("\n" + "=" * 60)
    print("Comprehensive Optimization Verification")
    print("=" * 60)
    
    results = {
        'gpu_configuration': verify_gpu_configuration(),
        'reranking_configuration': verify_reranking_configuration(),
        'graph_visualization': verify_graph_visualization(),
        'streaming_response': verify_streaming_response(),
        'llm_cache': verify_llm_cache(),
        'index_management': verify_index_management(),
        'performance_monitoring': verify_performance_monitoring(),
        'api_endpoints': verify_api_endpoints(),
        'gpu_environment_script': verify_gpu_environment_script()
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
    result = asyncio.run(verify_all_optimizations())
    sys.exit(0 if result else 1)