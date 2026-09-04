"""Direct chunk insertion for all documents."""

import asyncio
import sys
sys.path.insert(0, 'src')

async def direct_chunk_insertion():
    """Direct chunk insertion for all documents."""
    print("🔄 Direct Chunk Insertion for All Documents")
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
        
        # Initialize adapter
        adapter = LightRAGAdapter()
        await adapter.ensure_initialized()
        
        # Process each document
        total_chunks = 0
        vxrail_chunks = 0
        
        for doc_id, doc_data in registry.items():
            content = doc_data.get('content', '')
            title = doc_data.get('title', doc_id)
            
            if not content or len(content) < 100:
                print(f"⚠️  Skipping empty or short document: {doc_id}")
                continue
            
            print(f"📄 Processing: {title}")
            
            # Simple chunking
            chunk_size = 1000
            chunks = []
            for i in range(0, len(content), chunk_size):
                chunk_text = content[i:i+chunk_size]
                chunks.append(chunk_text)
            
            # Insert chunks directly
            for chunk_text in chunks:
                try:
                    await adapter.rag.ainsert(chunk_text)
                    total_chunks += 1
                    if 'vxrail' in chunk_text.lower():
                        vxrail_chunks += 1
                except Exception as e:
                    print(f"❌ Failed to insert chunk: {e}")
            
            print(f"✅ Inserted {len(chunks)} chunks for {title}")
        
        print(f"\n📊 Total chunks inserted: {total_chunks}")
        print(f"📊 VxRail chunks: {vxrail_chunks}")
        
        # Check what was indexed
        docs_file = Path(settings.lightrag_working_dir) / 'kv_store_full_docs.json'
        if docs_file.exists():
            with open(docs_file, 'r', encoding='utf-8') as f:
                indexed_docs = json.load(f)
            print(f"📊 Documents indexed in LightRAG: {len(indexed_docs)}")
        
        print("\n" + "=" * 60)
        print("✅ Direct chunk insertion completed")
        print("=" * 60)
        
        return total_chunks > 0
        
    except Exception as e:
        print(f"\n❌ Direct chunk insertion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(direct_chunk_insertion())
    sys.exit(0 if success else 1)