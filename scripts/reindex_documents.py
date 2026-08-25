"""
Reindex Documents to LightRAG
Script to reindex all documents from registry into LightRAG for proper knowledge graph generation
"""

import asyncio
import json
from pathlib import Path
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.config import settings


async def reindex_documents():
    """Reindex all documents from registry into LightRAG"""
    print("Starting document reindexing...")
    
    # Load document registry
    registry_file = Path(settings.data_dir) / 'document_registry.json'
    
    if not registry_file.exists():
        print(f"Document registry not found at {registry_file}")
        return False
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    print(f"Found {len(registry)} documents in registry")
    
    # Initialize LightRAG adapter
    rag = LightRAGAdapter()
    await rag.ensure_initialized()
    
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
    
    # Reindex documents
    try:
        # Use synchronous insert method to avoid pipeline issues
        for doc in documents:
            content = doc.get('content', '')
            doc_id = doc.get('doc_id', '')
            
            if content.strip():
                try:
                    rag.rag.insert(content)
                    print(f"Successfully ingested document: {doc_id}")
                except Exception as e:
                    print(f"Error ingesting document {doc_id}: {e}")
                    import traceback
                    traceback.print_exc()
        
        success = True
        
        if success:
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
        else:
            print("❌ Document reindexing failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during reindexing: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_lighting_query():
    """Test LightRAG query after reindexing"""
    print("\nTesting LightRAG query...")
    
    rag = LightRAGAdapter()
    
    # Test query
    test_queries = [
        "Machine Learning",
        "监督学习",
        "文档内容"
    ]
    
    for query in test_queries:
        try:
            result = await rag.query(query, mode="naive")
            print(f"Query: '{query}'")
            print(f"Result: {result[:100]}...")
            print()
        except Exception as e:
            print(f"Query failed: {e}")


async def main():
    """Main function"""
    print("=" * 60)
    print("LightRAG Document Reindexing")
    print("=" * 60)
    print()
    
    # Reindex documents
    success = await reindex_documents()
    
    if success:
        # Test queries
        await test_lighting_query()
    else:
        print("Reindexing failed, skipping query tests")
    
    print()
    print("=" * 60)
    print("Reindexing process completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())