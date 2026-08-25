"""
Synchronous Document Reindexing Script
Non-async version to avoid event loop conflicts
"""

import json
from pathlib import Path
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.config import settings


def reindex_documents_sync():
    """Reindex all documents from registry into LightRAG (synchronous)"""
    print("Starting document reindexing (synchronous)...")
    
    # Load document registry
    registry_file = Path(settings.data_dir) / 'document_registry.json'
    
    if not registry_file.exists():
        print(f"Document registry not found at {registry_file}")
        return False
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    print(f"Found {len(registry)} documents in registry")
    
    # Initialize LightRAG adapter (synchronous)
    rag = LightRAGAdapter()
    
    # Convert to document format
    documents = []
    for doc_id, doc_data in registry.items():
        content = doc_data.get('content', '')
        if content.strip():  # Only process documents with content
            documents.append({
                'doc_id': doc_id,
                'content': content,
                'metadata': doc_data.get('metadata', {})
            })
    
    print(f"Processing {len(documents)} documents with content")
    
    # Initialize storages synchronously
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(rag.ensure_initialized())
    except Exception as e:
        print(f"Initialization error: {e}")
    finally:
        loop.close()
    
    # Reindex documents using synchronous insert
    try:
        for doc in documents:
            content = doc.get('content', '')
            doc_id = doc.get('doc_id', '')
            
            if content.strip():
                try:
                    # Create new event loop for each insert
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        loop.run_until_complete(rag.rag.ainsert(content))
                        print(f"Successfully ingested document: {doc_id}")
                    except Exception as e:
                        print(f"Error ingesting document {doc_id}: {e}")
                        import traceback
                        traceback.print_exc()
                    finally:
                        loop.close()
                        
                except Exception as e:
                    print(f"Error processing document {doc_id}: {e}")
                    import traceback
                    traceback.print_exc()
        
        print("✅ Document reindexing completed successfully")
        
        # Check vector database status
        vdb_file = Path(settings.lightrag_working_dir) / 'vdb_chunks.json'
        if vdb_file.exists():
            with open(vdb_file, 'r', encoding='utf-8') as f:
                vdb_data = json.load(f)
            print(f"Vector database: {len(vdb_data)} chunks indexed")
        
        # Check entity and relation files
        entities_file = Path(settings.lightrag_working_dir) / 'kv_store_full_entities.json'
        if entities_file.exists():
            with open(entities_file, 'r', encoding='utf-8') as f:
                entities_data = json.load(f)
            print(f"Knowledge graph: {len(entities_data)} entities extracted")
        
        relations_file = Path(settings.lightrag_working_dir) / 'kv_store_full_relations.json'
        if relations_file.exists():
            with open(relations_file, 'r', encoding='utf-8') as f:
                relations_data = json.load(f)
            print(f"Knowledge graph: {len(relations_data)} relations extracted")
        
        return True
            
    except Exception as e:
        print(f"❌ Error during reindexing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lighting_query_sync():
    """Test LightRAG query after reindexing (synchronous)"""
    print("\nTesting LightRAG query...")
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    rag = LightRAGAdapter()
    
    # Test query
    test_queries = [
        "Machine Learning",
        "监督学习",
        "文档内容"
    ]
    
    for query in test_queries:
        try:
            result = loop.run_until_complete(rag.query(query, mode="naive"))
            print(f"Query: '{query}'")
            print(f"Result: {result[:100]}...")
            print()
        except Exception as e:
            print(f"Query failed: {e}")
    
    loop.close()


def main():
    """Main function"""
    print("=" * 60)
    print("LightRAG Document Reindexing (Synchronous)")
    print("=" * 60)
    print()
    
    # Reindex documents
    success = reindex_documents_sync()
    
    if success:
        # Test queries
        test_lighting_query_sync()
    else:
        print("Reindexing failed, skipping query tests")
    
    print()
    print("=" * 60)
    print("Reindexing process completed")
    print("=" * 60)


if __name__ == "__main__":
    main()