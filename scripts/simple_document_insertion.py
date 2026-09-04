"""Simple document insertion bypassing entity extraction."""

import asyncio
import sys
sys.path.insert(0, 'src')

async def simple_document_insertion():
    """Simple document insertion bypassing entity extraction."""
    print("🔄 Simple Document Insertion (No Entity Extraction)")
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
        
        # Process each document with title metadata
        total_docs = 0
        vxrail_docs = 0
        
        for doc_id, doc_data in registry.items():
            content = doc_data.get('content', '')
            title = doc_data.get('title', doc_id)
            
            if not content or len(content) < 100:
                print(f"⚠️  Skipping empty or short document: {doc_id}")
                continue
            
            print(f"📄 Processing: {title}")
            
            # Format with title for better retrieval
            formatted_content = f"# {title}\n\n{content}"
            
            try:
                await adapter.rag.ainsert(formatted_content)
                total_docs += 1
                if 'vxrail' in content.lower():
                    vxrail_docs += 1
                print(f"✅ Inserted: {title}")
            except Exception as e:
                print(f"❌ Failed to insert {title}: {e}")
        
        print(f"\n📊 Total documents inserted: {total_docs}")
        print(f"📊 VxRail documents: {vxrail_docs}")
        
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
        
        print("\n" + "=" * 60)
        print("✅ Simple document insertion completed")
        print("=" * 60)
        
        return total_docs > 0
        
    except Exception as e:
        print(f"\n❌ Simple document insertion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_document_insertion())
    sys.exit(0 if success else 1)