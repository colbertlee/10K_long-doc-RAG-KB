"""
Simple test to verify LightRAG synchronous insert fix
"""

import asyncio
from pathlib import Path
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.config import settings


async def test_sync_insert():
    """Test synchronous insert method"""
    
    print("=" * 60)
    print("Testing LightRAG Synchronous Insert Fix")
    print("=" * 60)
    
    # Create test document
    test_content = "This is a test document for synchronous insert verification."
    test_file = settings.data_dir / 'test_sync_insert.txt'
    test_file.write_text(test_content, encoding='utf-8')
    
    print(f"Test document created: {test_file}")
    
    # Initialize adapter
    rag = LightRAGAdapter()
    await rag.ensure_initialized()
    
    print(f"Adapter initialized")
    print(f"Has _use_sync_insert: {hasattr(rag, '_use_sync_insert')}")
    if hasattr(rag, '_use_sync_insert'):
        print(f"Sync insert flag: {rag._use_sync_insert}")
    
    # Test ingestion
    print("\nTesting document ingestion...")
    result = await rag.ingest([{
        'doc_id': 'test_sync_001',
        'content': test_content,
        'metadata': {'title': 'Test Sync Insert'}
    }])
    
    if result:
        print("✅ Document ingestion successful")
    else:
        print("❌ Document ingestion failed")
    
    # Cleanup
    test_file.unlink()
    print(f"\nCleanup completed")
    
    return result


if __name__ == "__main__":
    success = asyncio.run(test_sync_insert())
    exit(0 if success else 1)