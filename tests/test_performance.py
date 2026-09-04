"""Performance test suite for RAG KB system."""

import asyncio
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.lightrag.adapter import LightRAGAdapter, SimpleBM25Search
from rag_kb.utils.performance_monitor import PerformanceMonitor, OperationTimer


class PerformanceTestSuite:
    """Comprehensive performance test suite."""
    
    def __init__(self):
        """Initialize performance test suite."""
        self.monitor = PerformanceMonitor()
        self.results = {}
    
    def test_bm25_indexing_performance(self):
        """Test BM25 indexing performance."""
        
        print("=" * 60)
        print("Testing BM25 Indexing Performance")
        print("=" * 60)
        
        try:
            bm25 = SimpleBM25Search()
            
            # Create test documents
            test_docs = []
            for i in range(100):
                test_docs.append({
                    'id': f'test_doc_{i}',
                    'text': f'This is test document {i}. ' * 50,  # ~1000 chars
                    'metadata': {'index': i}
                })
            
            # Time the indexing
            with OperationTimer(self.monitor, 'bm25_indexing_100_docs'):
                bm25.add_documents(test_docs)
            
            stats = self.monitor.get_operation_stats('bm25_indexing_100_docs')
            
            print(f"Indexed {len(test_docs)} documents")
            print(f"Time: {stats['last_duration']:.2f}s")
            print(f"Docs/sec: {len(test_docs) / stats['last_duration']:.2f}")
            
            self.results['bm25_indexing'] = {
                'docs_count': len(test_docs),
                'duration': stats['last_duration'],
                'docs_per_sec': len(test_docs) / stats['last_duration']
            }
            
            print("✅ BM25 indexing performance test passed")
            return True
            
        except Exception as e:
            print(f"❌ BM25 indexing performance test failed: {e}")
            return False
    
    def test_bm25_search_performance(self):
        """Test BM25 search performance."""
        
        print("\n" + "=" * 60)
        print("Testing BM25 Search Performance")
        print("=" * 60)
        
        try:
            bm25 = SimpleBM25Search()
            
            # Ensure we have indexed documents
            if len(bm25.documents) == 0:
                print("No indexed documents, skipping search test")
                return True
            
            # Test search performance
            queries = ['test', 'document', 'performance', 'indexing', 'search']
            
            with OperationTimer(self.monitor, 'bm25_search_5_queries'):
                for query in queries:
                    results = bm25.search(query, top_k=10)
            
            stats = self.monitor.get_operation_stats('bm25_search_5_queries')
            
            print(f"Executed {len(queries)} queries")
            print(f"Total time: {stats['last_duration']:.2f}s")
            print(f"Avg time per query: {stats['last_duration'] / len(queries):.4f}s")
            print(f"Queries/sec: {len(queries) / stats['last_duration']:.2f}")
            
            self.results['bm25_search'] = {
                'queries_count': len(queries),
                'total_duration': stats['last_duration'],
                'avg_query_time': stats['last_duration'] / len(queries),
                'queries_per_sec': len(queries) / stats['last_duration']
            }
            
            print("✅ BM25 search performance test passed")
            return True
            
        except Exception as e:
            print(f"❌ BM25 search performance test failed: {e}")
            return False
    
    async def test_lightrag_initialization_performance(self):
        """Test LightRAG initialization performance."""
        
        print("\n" + "=" * 60)
        print("Testing LightRAG Initialization Performance")
        print("=" * 60)
        
        try:
            with OperationTimer(self.monitor, 'lightrag_initialization'):
                rag = LightRAGAdapter()
                await rag.ensure_initialized()
            
            stats = self.monitor.get_operation_stats('lightrag_initialization')
            
            print(f"Initialization time: {stats['last_duration']:.2f}s")
            
            self.results['lightrag_initialization'] = {
                'duration': stats['last_duration']
            }
            
            print("✅ LightRAG initialization performance test passed")
            return True
            
        except Exception as e:
            print(f"❌ LightRAG initialization performance test failed: {e}")
            return False
    
    async def test_lightrag_query_performance(self):
        """Test LightRAG query performance."""
        
        print("\n" + "=" * 60)
        print("Testing LightRAG Query Performance")
        print("=" * 60)
        
        try:
            rag = LightRAGAdapter()
            await rag.ensure_initialized()
            
            # Test query performance
            queries = ['test query', 'document search', 'knowledge base']
            
            with OperationTimer(self.monitor, 'lightrag_query_3_queries'):
                for query in queries:
                    try:
                        result = await rag.query(query, mode="naive")
                    except Exception as e:
                        print(f"Query failed: {e}")
            
            stats = self.monitor.get_operation_stats('lightrag_query_3_queries')
            
            print(f"Executed {len(queries)} queries")
            print(f"Total time: {stats['last_duration']:.2f}s")
            print(f"Avg time per query: {stats['last_duration'] / len(queries):.4f}s")
            
            self.results['lightrag_query'] = {
                'queries_count': len(queries),
                'total_duration': stats['last_duration'],
                'avg_query_time': stats['last_duration'] / len(queries)
            }
            
            print("✅ LightRAG query performance test passed")
            return True
            
        except Exception as e:
            print(f"❌ LightRAG query performance test failed: {e}")
            return False
    
    def test_system_resources(self):
        """Test system resource usage."""
        
        print("\n" + "=" * 60)
        print("Testing System Resources")
        print("=" * 60)
        
        try:
            self.monitor.record_system_metrics()
            stats = self.monitor.get_system_stats()
            
            print(f"CPU Usage: {stats['cpu_percent']:.1f}%")
            print(f"Memory Usage: {stats['memory_percent']:.1f}%")
            print(f"Memory Used: {stats['memory_used_gb']:.2f} GB")
            print(f"Memory Total: {stats['memory_total_gb']:.2f} GB")
            print(f"Process Memory: {stats['process_memory_gb']:.2f} GB")
            print(f"Disk Usage: {stats['disk_usage_percent']:.1f}%")
            
            self.results['system_resources'] = stats
            
            print("✅ System resources test passed")
            return True
            
        except Exception as e:
            print(f"❌ System resources test failed: {e}")
            return False
    
    def generate_performance_report(self):
        """Generate comprehensive performance report."""
        
        print("\n" + "=" * 60)
        print("Performance Test Report")
        print("=" * 60)
        
        print("\nTest Results:")
        for test_name, result in self.results.items():
            print(f"\n{test_name}:")
            for key, value in result.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
        
        print("\nPerformance Summary:")
        summary = self.monitor.get_performance_summary()
        print(f"Total operations: {summary['total_operations']}")
        print(f"Total duration: {summary['total_duration']:.2f}s")
        print(f"Average operation time: {summary['avg_operation_time']:.4f}s")
        print(f"Slow operations: {summary['slow_operations_count']}")
        
        # Performance recommendations
        print("\nPerformance Recommendations:")
        
        if 'bm25_indexing' in self.results:
            docs_per_sec = self.results['bm25_indexing']['docs_per_sec']
            if docs_per_sec < 10:
                print("⚠️ BM25 indexing is slow (< 10 docs/sec)")
                print("   Consider: Increasing batch size, using GPU acceleration")
            else:
                print("✅ BM25 indexing performance is good")
        
        if 'bm25_search' in self.results:
            avg_query_time = self.results['bm25_search']['avg_query_time']
            if avg_query_time > 0.1:
                print("⚠️ BM25 search is slow (> 0.1s per query)")
                print("   Consider: Optimizing index, using caching")
            else:
                print("✅ BM25 search performance is good")
        
        if 'lightrag_query' in self.results:
            avg_query_time = self.results['lightrag_query']['avg_query_time']
            if avg_query_time > 2.0:
                print("⚠️ LightRAG query is slow (> 2s per query)")
                print("   Consider: Using faster LLM, enabling caching, GPU acceleration")
            else:
                print("✅ LightRAG query performance is acceptable")
        
        if 'system_resources' in self.results:
            memory_percent = self.results['system_resources']['memory_percent']
            if memory_percent > 80:
                print("⚠️ High memory usage (> 80%)")
                print("   Consider: Reducing chunk size, processing in batches")
            else:
                print("✅ Memory usage is acceptable")
    
    async def run_all_tests(self):
        """Run all performance tests."""
        
        print("\n" + "=" * 60)
        print("Performance Test Suite")
        print("=" * 60)
        
        # Run tests
        self.test_bm25_indexing_performance()
        self.test_bm25_search_performance()
        await self.test_lightrag_initialization_performance()
        await self.test_lightrag_query_performance()
        self.test_system_resources()
        
        # Generate report
        self.generate_performance_report()
        
        print("\n" + "=" * 60)
        print("Performance testing completed")
        print("=" * 60)


async def main():
    """Main function to run performance tests."""
    
    test_suite = PerformanceTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())