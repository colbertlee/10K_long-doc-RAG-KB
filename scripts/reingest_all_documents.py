"""Re-ingest all documents from registry to LightRAG."""

import asyncio
import sys
sys.path.insert(0, 'src')

async def reingest_all_documents():
    """Re-ingest all documents from registry to LightRAG."""
    print("🔄 Re-ingesting All Documents to LightRAG")
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
        
        # Re-ingest documents
        print("🔄 Starting re-ingestion...")
        success = await adapter.ingest(documents)
        
        print(f"📊 Re-ingestion result: {success}")
        
        # Check what was indexed
        docs_file = Path(settings.lightrag_working_dir) / 'kv_store_full_docs.json'
        if docs_file.exists():
            with open(docs_file, 'r', encoding='utf-8') as f:
                indexed_docs = json.load(f)
            print(f"📊 Documents indexed in LightRAG: {len(indexed_docs)}")
            
            # Show indexed document titles
            for doc_id, doc_data in list(indexed_docs.items())[:5]:
                content_preview = doc_data.get('content', '')[:100]
                print(f"  - {doc_id}: {content_preview}...")
        
        # Check for VxRail content
        vxrail_found = False
        for doc_id, doc_data in indexed_docs.items():
            content = doc_data.get('content', '').lower()
            if 'vxrail' in content:
                vxrail_found = True
                print(f"✅ VxRail content found in document: {doc_id}")
                break
        
        if not vxrail_found:
            print("⚠️  VxRail content not found in indexed documents")
        
        print("\n" + "=" * 60)
        print("✅ Re-ingestion completed")
        print("=" * 60)
        
        return success
        
    except Exception as e:
        print(f"\n❌ Re-ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(reingest_all_documents())
    sys.exit(0 if success else 1)