"""Comprehensive retrieval effectiveness test for indexed content."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.lightrag.adapter import LightRAGAdapter, SimpleBM25Search
from rag_kb.ingest.index_manager import get_index_manager


class RetrievalEffectivenessTest:
    """Test retrieval effectiveness for indexed content."""
    
    def __init__(self):
        """Initialize retrieval effectiveness test."""
        self.rag = None
        self.bm25 = None
        self.index_manager = None
        self.results = {}
    
    async def initialize(self):
        """Initialize all components."""
        print("Initializing components...")
        
        self.rag = LightRAGAdapter()
        await self.rag.ensure_initialized()
        
        self.bm25 = SimpleBM25Search()
        self.bm25_index_path = Path("lightrag_db/bm25_index.json")
        if self.bm25_index_path.exists():
            self.bm25.load_index(self.bm25_index_path)
        
        self.index_manager = get_index_manager()
        
        print("✅ Components initialized")
    
    def check_index_status(self):
        """Check current index status."""
        
        print("\n" + "=" * 60)
        print("Checking Index Status")
        print("=" * 60)
        
        # Check BM25 index
        print(f"\nBM25 Index:")
        print(f"  Documents in index: {len(self.bm25.documents)}")
        terms_count = len(self.bm25.index) if hasattr(self.bm25, 'index') else 'N/A'
        print(f"  Terms in index: {terms_count}")
        
        if self.bm25.documents:
            print(f"  Sample documents:")
            for i, doc in enumerate(self.bm25.documents[:3], 1):
                print(f"    {i}. {doc['id'][:50]}... ({len(doc['text'])} chars)")
        
        # Check LightRAG index
        print(f"\nLightRAG Index:")
        print(f"  Initialized: {self.rag._initialized}")
        
        # Check document registry
        print(f"\nDocument Registry:")
        report = self.index_manager.get_index_integrity_report()
        print(f"  Total uploaded: {report['total_uploaded']}")
        print(f"  Total indexed: {report['total_indexed']}")
        print(f"  Unindexed: {report['unindexed_count']}")
        print(f"  Index health: {report['index_health']}")
        
        self.results['index_status'] = {
            'bm25_docs': len(self.bm25.documents),
            'lightrag_initialized': self.rag._initialized,
            'total_uploaded': report['total_uploaded'],
            'total_indexed': report['total_indexed'],
            'unindexed': report['unindexed_count'],
            'index_health': report['index_health']
        }
    
    def test_bm25_retrieval(self):
        """Test BM25 retrieval effectiveness."""
        
        print("\n" + "=" * 60)
        print("Testing BM25 Retrieval")
        print("=" * 60)
        
        if len(self.bm25.documents) == 0:
            print("⚠️ No documents in BM25 index, skipping BM25 test")
            self.results['bm25_retrieval'] = {'status': 'skipped', 'reason': 'no_documents'}
            return
        
        # Test queries
        test_queries = [
            "test",
            "document",
            "sample",
            "machine learning",
            "knowledge"
        ]
        
        results = {}
        for query in test_queries:
            search_results = self.bm25.search(query, top_k=5)
            results[query] = {
                'count': len(search_results),
                'results': search_results
            }
            print(f"\nQuery: '{query}'")
            print(f"  Results: {len(search_results)}")
            if search_results:
                for i, result in enumerate(search_results[:2], 1):
                    print(f"    {i}. {result['id'][:50]}... (score: {result['score']:.4f})")
        
        self.results['bm25_retrieval'] = {
            'status': 'completed',
            'queries_tested': len(test_queries),
            'results': results
        }
        
        print("\n✅ BM25 retrieval test completed")
    
    async def test_lightrag_retrieval(self):
        """Test LightRAG retrieval effectiveness."""
        
        print("\n" + "=" * 60)
        print("Testing LightRAG Retrieval")
        print("=" * 60)
        
        # Test queries
        test_queries = [
            "test query",
            "document search",
            "knowledge base"
        ]
        
        results = {}
        for query in test_queries:
            try:
                print(f"\nQuery: '{query}'")
                answer = await self.rag.query(query, mode="naive")
                results[query] = {
                    'answer_length': len(answer) if answer else 0,
                    'answer_preview': answer[:200] if answer else 'empty',
                    'has_context': '[no-context]' not in (answer or '')
                }
                print(f"  Answer length: {len(answer) if answer else 0}")
                print(f"  Has context: {results[query]['has_context']}")
                print(f"  Preview: {answer[:100] if answer else 'empty'}...")
            except Exception as e:
                print(f"  Error: {e}")
                results[query] = {
                    'error': str(e),
                    'answer_length': 0,
                    'has_context': False
                }
        
        self.results['lightrag_retrieval'] = {
            'status': 'completed',
            'queries_tested': len(test_queries),
            'results': results
        }
        
        print("\n✅ LightRAG retrieval test completed")
    
    async def test_bm25_fallback(self):
        """Test BM25 fallback mechanism."""
        
        print("\n" + "=" * 60)
        print("Testing BM25 Fallback")
        print("=" * 60)
        
        if len(self.bm25.documents) == 0:
            print("⚠️ No documents in BM25 index, skipping fallback test")
            self.results['bm25_fallback'] = {'status': 'skipped', 'reason': 'no_documents'}
            return
        
        # Test with a query that might trigger fallback
        test_query = "test query"
        
        print(f"\nTesting query: '{test_query}'")
        
        # Direct BM25 search
        bm25_results = self.bm25.search(test_query, top_k=3)
        print(f"BM25 results: {len(bm25_results)}")
        
        if bm25_results:
            print("BM25 search results:")
            for i, result in enumerate(bm25_results[:2], 1):
                print(f"  {i}. {result['id'][:50]}... (score: {result['score']:.4f})")
        
        self.results['bm25_fallback'] = {
            'status': 'completed',
            'query': test_query,
            'bm25_results_count': len(bm25_results),
            'bm25_available': len(bm25_results) > 0
        }
        
        print("\n✅ BM25 fallback test completed")
    
    async def test_end_to_end_retrieval(self):
        """Test end-to-end retrieval workflow."""
        
        print("\n" + "=" * 60)
        print("Testing End-to-End Retrieval")
        print("=" * 60)
        
        # Simulate a complete user query workflow
        test_query = "test document"
        
        print(f"\nSimulating user query: '{test_query}'")
        
        # Step 1: Check if query can be answered
        print("\nStep 1: Attempting to answer query...")
        try:
            answer = await self.rag.query(test_query, mode="naive")
            print(f"  Answer received: {len(answer) if answer else 0} chars")
            print(f"  Has context: {'[no-context]' not in (answer or '')}")
            
            # Step 2: Check BM25 fallback
            if '[no-context]' in (answer or ''):
                print("\nStep 2: LightRAG returned no context, checking BM25 fallback...")
                bm25_results = self.bm25.search(test_query, top_k=3)
                print(f"  BM25 results: {len(bm25_results)}")
                
                if bm25_results:
                    print("  ✅ BM25 fallback available")
                    print(f"  Top result: {bm25_results[0]['id'][:50]}...")
                else:
                    print("  ⚠️ BM25 fallback also returned no results")
            else:
                print("\nStep 2: LightRAG returned context successfully")
            
            self.results['end_to_end'] = {
                'status': 'completed',
                'query': test_query,
                'answer_length': len(answer) if answer else 0,
                'has_context': '[no-context]' not in (answer or ''),
                'bm25_fallback_used': '[no-context]' in (answer or '')
            }
            
        except Exception as e:
            print(f"  Error: {e}")
            self.results['end_to_end'] = {
                'status': 'error',
                'error': str(e)
            }
        
        print("\n✅ End-to-end retrieval test completed")
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        
        print("\n" + "=" * 60)
        print("Retrieval Effectiveness Test Report")
        print("=" * 60)
        
        print("\nIndex Status:")
        if 'index_status' in self.results:
            status = self.results['index_status']
            print(f"  BM25 documents: {status['bm25_docs']}")
            print(f"  LightRAG initialized: {status['lightrag_initialized']}")
            print(f"  Total uploaded: {status['total_uploaded']}")
            print(f"  Total indexed: {status['total_indexed']}")
            print(f"  Unindexed: {status['unindexed']}")
            print(f"  Index health: {status['index_health']}")
        
        print("\nBM25 Retrieval:")
        if 'bm25_retrieval' in self.results:
            bm25 = self.results['bm25_retrieval']
            print(f"  Status: {bm25['status']}")
            if bm25['status'] == 'completed':
                print(f"  Queries tested: {bm25['queries_tested']}")
                successful_queries = sum(1 for r in bm25['results'].values() if r['count'] > 0)
                print(f"  Successful queries: {successful_queries}/{bm25['queries_tested']}")
        
        print("\nLightRAG Retrieval:")
        if 'lightrag_retrieval' in self.results:
            lightrag = self.results['lightrag_retrieval']
            print(f"  Status: {lightrag['status']}")
            if lightrag['status'] == 'completed':
                print(f"  Queries tested: {lightrag['queries_tested']}")
                successful_queries = sum(1 for r in lightrag['results'].values() if r['has_context'])
                print(f"  Queries with context: {successful_queries}/{lightrag['queries_tested']}")
        
        print("\nBM25 Fallback:")
        if 'bm25_fallback' in self.results:
            fallback = self.results['bm25_fallback']
            print(f"  Status: {fallback['status']}")
            if fallback['status'] == 'completed':
                print(f"  BM25 available: {fallback['bm25_available']}")
        
        print("\nEnd-to-End Retrieval:")
        if 'end_to_end' in self.results:
            e2e = self.results['end_to_end']
            print(f"  Status: {e2e['status']}")
            if e2e['status'] == 'completed':
                print(f"  Answer length: {e2e['answer_length']}")
                print(f"  Has context: {e2e['has_context']}")
                print(f"  BM25 fallback used: {e2e['bm25_fallback_used']}")
        
        # Recommendations
        print("\nRecommendations:")
        
        if 'index_status' in self.results:
            status = self.results['index_status']
            if status['unindexed'] > 0:
                print("⚠️ There are unindexed documents")
                print("   Run: curl -X POST http://localhost:8000/api/v1/index/all")
        
        if 'bm25_retrieval' in self.results:
            bm25 = self.results['bm25_retrieval']
            if bm25['status'] == 'skipped':
                print("⚠️ BM25 index is empty")
                print("   Upload and index documents to enable BM25 search")
        
        if 'lightrag_retrieval' in self.results:
            lightrag = self.results['lightrag_retrieval']
            if lightrag['status'] == 'completed':
                successful_queries = sum(1 for r in lightrag['results'].values() if r['has_context'])
                if successful_queries == 0:
                    print("⚠️ LightRAG queries returned no context")
                    print("   Ensure documents are properly indexed in LightRAG")
    
    async def run_all_tests(self):
        """Run all retrieval effectiveness tests."""
        
        print("\n" + "=" * 60)
        print("Retrieval Effectiveness Test Suite")
        print("=" * 60)
        
        await self.initialize()
        self.check_index_status()
        self.test_bm25_retrieval()
        await self.test_lightrag_retrieval()
        await self.test_bm25_fallback()
        await self.test_end_to_end_retrieval()
        self.generate_test_report()
        
        print("\n" + "=" * 60)
        print("Retrieval effectiveness testing completed")
        print("=" * 60)


async def main():
    """Main function to run retrieval effectiveness tests."""
    
    test_suite = RetrievalEffectivenessTest()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())