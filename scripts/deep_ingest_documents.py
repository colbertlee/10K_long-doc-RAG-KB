"""Deep document ingestion script for proper entity extraction."""

import asyncio
import sys
sys.path.insert(0, 'src')

async def deep_ingest_documents():
    """Deep ingest documents with proper LLM configuration."""
    print("🔄 Deep Document Ingestion with Proper LLM Configuration")
    print("=" * 60)
    
    try:
        from rag_kb.lightrag.adapter import LightRAGAdapter
        from rag_kb.config import settings
        import json
        from pathlib import Path
        
        # Load documents from registry
        registry_file = Path(settings.data_dir) / 'document_registry.json'
        
        if not registry_file.exists():
            print("❌ Document registry not found")
            return False
        
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        print(f"📄 Found {len(registry)} documents in registry")
        
        # Convert to document format
        documents = []
        for doc_id, doc_data in registry.items():
            content = doc_data.get('content', '')
            if not content or len(content) < 100:
                print(f"⚠️  Skipping empty or short document: {doc_id}")
                continue
                
            documents.append({
                'doc_id': doc_id,
                'content': content,
                'metadata': doc_data.get('metadata', {}),
                'title': doc_data.get('title', doc_id)
            })
        
        print(f"📊 Processing {len(documents)} valid documents")
        
        # Initialize adapter with new LLM configuration
        adapter = LightRAGAdapter()
        await adapter.ensure_initialized()
        
        # Ingest documents
        print("🔄 Starting deep ingestion...")
        success = await adapter.ingest(documents)
        
        print(f"📊 Ingestion result: {success}")
        
        # Check entity extraction results
        print("\n🔍 Checking entity extraction results...")
        entities_file = Path(settings.lightrag_working_dir) / 'kv_store_full_entities.json'
        relations_file = Path(settings.lightrag_working_dir) / 'kv_store_full_relations.json'
        
        if entities_file.exists():
            with open(entities_file, 'r', encoding='utf-8') as f:
                entities = json.load(f)
            print(f"📊 Entities extracted: {len(entities)}")
            
            # Show sample entities
            for i, (entity_id, entity_data) in enumerate(list(entities.items())[:3]):
                entity_names = entity_data.get('entity_names', [])
                print(f"  {i+1}. {entity_id}: {entity_names}")
        else:
            print("⚠️  No entities file found")
        
        if relations_file.exists():
            with open(relations_file, 'r', encoding='utf-8') as f:
                relations = json.load(f)
            print(f"📊 Relations extracted: {len(relations)}")
        else:
            print("⚠️  No relations file found")
        
        print("\n" + "=" * 60)
        print("✅ Deep ingestion completed")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Deep ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(deep_ingest_documents())
    sys.exit(0 if success else 1)