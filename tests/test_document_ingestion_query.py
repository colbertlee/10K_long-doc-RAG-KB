"""
Test document ingestion and query functionality
"""

import asyncio
import json
from pathlib import Path
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.config import settings


async def test_document_ingestion_and_query():
    """Test that documents are properly ingested and can be queried"""
    
    print("=" * 60)
    print("Document Ingestion and Query Test")
    print("=" * 60)
    
    # Test document
    test_document = {
        'doc_id': 'test_doc_001',
        'content': 'Machine learning is a subset of artificial intelligence that enables systems to learn from data. It includes supervised learning, unsupervised learning, and deep learning.',
        'metadata': {
            'title': 'Test Document',
            'source': 'test'
        }
    }
    
    print(f"\n1. Testing document ingestion...")
    print(f"   Document ID: {test_document['doc_id']}")
    print(f"   Content length: {len(test_document['content'])}")
    
    # Initialize LightRAG adapter
    rag = LightRAGAdapter()
    await rag.ensure_initialized()
    
    # Ingest document
    print(f"\n2. Ingesting document...")
    ingest_result = await rag.ingest([test_document])
    print(f"   Ingest result: {ingest_result}")
    
    # Test queries
    test_queries = [
        "What is machine learning?",
        "machine learning",
        "supervised learning",
        "artificial intelligence"
    ]
    
    print(f"\n3. Testing queries...")
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        try:
            result = await rag.query(query, mode="naive")
            print(f"   Result length: {len(result) if result else 0}")
            print(f"   Result preview: {result[:100] if result else 'empty'}...")
            
            # Check if result is meaningful
            if result and "知识库中未找到相关信息" not in result:
                print(f"   ✅ Query successful!")
            else:
                print(f"   ❌ Query failed or no relevant info")
        except Exception as e:
            print(f"   ❌ Query error: {e}")
    
    # Check vector database
    print(f"\n4. Checking vector database...")
    vdb_file = Path(settings.lightrag_working_dir) / 'vdb_chunks.json'
    if vdb_file.exists():
        with open(vdb_file, 'r', encoding='utf-8') as f:
            vdb_data = json.load(f)
        print(f"   Vector database entries: {len(vdb_data.get('data', []))}")
        if vdb_data.get('data'):
            print(f"   Sample entry ID: {vdb_data['data'][0].get('__id__', 'N/A')}")
    else:
        print(f"   ❌ Vector database not found")
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_document_ingestion_and_query())