"""Simple vector-only ingestion for quick document indexing."""

import asyncio
import sys
sys.path.insert(0, 'src')

async def simple_vector_ingest():
    """Simple vector-only ingestion without entity extraction."""
    print("🔄 Simple Vector-Only Ingestion")
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
        
        # Initialize adapter
        adapter = LightRAGAdapter()
        await adapter.ensure_initialized()
        
        # Direct chunk insertion without entity extraction
        print("🔄 Starting vector-only ingestion...")
        success_count = 0
        
        for doc in documents:
            doc_id = doc['doc_id']
            content = doc['content']
            
            try:
                # Simple chunking
                chunk_size = 1000
                chunks = []
                for i in range(0, len(content), chunk_size):
                    chunk_text = content[i:i+chunk_size]
                    chunks.append(chunk_text)
                
                # Insert chunks directly
                for chunk_text in chunks:
                    await adapter.rag.ainsert(chunk_text)
                
                print(f"✅ Successfully indexed: {doc_id}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Failed to index {doc_id}: {e}")
        
        print(f"\n📊 Vector ingestion completed: {success_count}/{len(documents)} documents")
        
        # Check vector index
        chunks_file = Path(settings.lightrag_working_dir) / 'kv_store_text_chunks.json'
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            print(f"📊 Total chunks indexed: {len(chunks)}")
        
        print("\n" + "=" * 60)
        print("✅ Vector-only ingestion completed")
        print("=" * 60)
        
        return success_count > 0
        
    except Exception as e:
        print(f"\n❌ Vector ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_vector_ingest())
    sys.exit(0 if success else 1)