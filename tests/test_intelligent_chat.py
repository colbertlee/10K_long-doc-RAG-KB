"""Test intelligent chat functionality with BM25 fallback."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.lightrag.adapter import LightRAGAdapter


async def test_intelligent_chat():
    """Test intelligent chat functionality."""
    
    print("=" * 60)
    print("Testing Intelligent Chat Functionality")
    print("=" * 60)
    
    try:
        # Create adapter
        rag = LightRAGAdapter()
        await rag.ensure_initialized()
        
        print(f"\nLightRAG working directory: {rag.working_dir}")
        print(f"BM25 index exists: {rag.bm25_index_path.exists()}")
        print(f"Documents in BM25 index: {len(rag.bm25_search.documents)}")
        
        # Test queries
        test_queries = [
            "什么是机器学习",
            "深度学习有哪些应用",
            "自然语言处理的主要任务是什么"
        ]
        
        print("\n" + "=" * 60)
        print("Testing Chat Queries")
        print("=" * 60)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Query {i}: {query} ---")
            
            try:
                # Test BM25 search first
                print("Step 1: BM25 search...")
                bm25_results = rag.bm25_search.search(query, top_k=2)
                print(f"BM25 results: {len(bm25_results)}")
                if bm25_results:
                    for j, result in enumerate(bm25_results, 1):
                        print(f"  {j}. {result['id']} (score: {result['score']})")
                
                # Test LightRAG query with BM25 fallback
                print("\nStep 2: LightRAG query with BM25 fallback...")
                answer = await asyncio.wait_for(
                    rag.query(query, mode="naive"),
                    timeout=60  # 1 minute timeout
                )
                
                print(f"Answer length: {len(answer) if answer else 0}")
                print(f"Answer preview: {answer[:300] if answer else 'empty'}...")
                
                # Check if answer is meaningful
                if answer and len(answer) > 50:
                    print("✅ Query successful - meaningful answer received")
                elif answer and "抱歉" in answer:
                    print("⚠️ Query returned error message")
                else:
                    print("❌ Query returned empty or insufficient answer")
                
            except asyncio.TimeoutError:
                print("❌ Query timeout")
            except Exception as e:
                print(f"❌ Query error: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ Intelligent chat test completed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error during intelligent chat test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_intelligent_chat())
    sys.exit(0 if result else 1)