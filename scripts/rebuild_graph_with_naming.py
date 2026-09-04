"""Script to clear LightRAG data and rebuild knowledge graph with proper naming."""

import asyncio
import sys
import shutil
from pathlib import Path
sys.path.insert(0, 'src')

async def clear_and_rebuild():
    """Clear LightRAG data and rebuild knowledge graph."""
    print("🧹 Clearing LightRAG data and rebuilding knowledge graph")
    print("=" * 60)
    
    try:
        from rag_kb.config import settings
        from rag_kb.graph.generator import KnowledgeGraphGenerator
        from rag_kb.lightrag.adapter import LightRAGAdapter
        import json
        
        lightrag_dir = Path(settings.lightrag_working_dir)
        
        # Backup existing data
        if lightrag_dir.exists():
            backup_dir = lightrag_dir.parent / f"{lightrag_dir.name}_backup"
            print(f"📦 Backing up existing data to {backup_dir}")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(lightrag_dir, backup_dir)
        
        # Clear LightRAG data
        print(f"🗑️  Clearing LightRAG data from {lightrag_dir}")
        if lightrag_dir.exists():
            shutil.rmtree(lightrag_dir)
        lightrag_dir.mkdir(parents=True, exist_ok=True)
        
        # Re-ingest documents
        print("🔄 Re-ingesting documents...")
        registry_file = Path(settings.data_dir) / 'document_registry.json'
        
        if not registry_file.exists():
            print("❌ Document registry not found")
            return False
        
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Convert to document format
        documents = []
        for doc_id, doc_data in registry.items():
            documents.append({
                'doc_id': doc_id,
                'content': doc_data.get('content', ''),
                'metadata': doc_data.get('metadata', {}),
                'title': doc_data.get('title', doc_id)
            })
        
        # Re-ingest with proper metadata
        adapter = LightRAGAdapter()
        await adapter.ensure_initialized()
        
        success = await adapter.ingest(documents)
        print(f"📊 Ingestion result: {success}")
        
        # Generate new graph
        print("🔄 Generating new knowledge graph...")
        generator = KnowledgeGraphGenerator()
        await generator.initialize()
        
        graph_data = await generator.generate_graph_from_documents(documents)
        
        print(f"\n📊 New Graph Statistics:")
        print(f"  - Nodes: {graph_data.get('node_count', 0)}")
        print(f"  - Edges: {graph_data.get('edge_count', 0)}")
        
        # Check node names
        print(f"\n🏷️  New Node Names (first 5):")
        nodes = graph_data.get('nodes', [])
        for i, node in enumerate(nodes[:5]):
            node_name = node.get('name', 'N/A')
            node_type = node.get('type', 'N/A')
            print(f"  {i+1}. {node_name} (Type: {node_type})")
        
        print("\n" + "=" * 60)
        print("✅ Knowledge graph rebuild completed")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Rebuild failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(clear_and_rebuild())
    sys.exit(0 if success else 1)