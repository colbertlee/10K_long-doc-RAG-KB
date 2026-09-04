"""Test retrieval functionality to diagnose the issue."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.config import settings


async def test_retrieval():
    """Test if LightRAG can retrieve context from the knowledge base."""
    
    print("=" * 60)
    print("Testing LightRAG Retrieval Functionality")
    print("=" * 60)
    
    # Initialize LightRAG adapter
    rag = LightRAGAdapter()
    await rag.ensure_initialized()
    
    # Test queries
    test_queries = [
        "机器学习是什么？",
        "Machine learning basics",
        "文档中有哪些内容？",
        "test document content"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing query: {query}")
        print('='*60)
        
        try:
            # Test with only_need_context=True to see what context is retrieved
            from lightrag import QueryParam
            context_result = await rag.rag.aquery(
                query,
                param=QueryParam(mode="naive", only_need_context=True, enable_rerank=False)
            )
            print(f"Context retrieved: {context_result[:500] if context_result else 'None'}...")
            
            # Test with only_need_context=False to see the full response
            full_result = await rag.rag.aquery(
                query,
                param=QueryParam(mode="naive", only_need_context=False, enable_rerank=False)
            )
            print(f"Full response: {full_result[:500] if full_result else 'None'}...")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Check if there are documents in the knowledge base
    print(f"\n{'='*60}")
    print("Checking Knowledge Base Status")
    print('='*60)
    
    try:
        # Check the working directory
        working_dir = Path(settings.lightrag_working_dir)
        print(f"Working directory: {working_dir}")
        print(f"Working directory exists: {working_dir.exists()}")
        
        if working_dir.exists():
            json_files = list(working_dir.glob("*.json"))
            print(f"JSON files in working directory: {len(json_files)}")
            for json_file in json_files:
                print(f"  - {json_file.name} ({json_file.stat().st_size} bytes)")
        
    except Exception as e:
        print(f"Error checking knowledge base: {e}")


if __name__ == "__main__":
    asyncio.run(test_retrieval())