"""Test script to verify knowledge graph naming fix."""

import asyncio
import sys
sys.path.insert(0, 'src')

async def test_graph_naming():
    """Test that knowledge graph nodes have meaningful names."""
    print("🧪 Testing Knowledge Graph Naming Fix")
    print("=" * 60)
    
    try:
        from rag_kb.graph.generator import KnowledgeGraphGenerator
        from rag_kb.config import settings
        import json
        from pathlib import Path
        
        # Check document registry
        registry_file = Path(settings.data_dir) / 'document_registry.json'
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            print(f"\n📄 Document Registry ({len(registry)} documents):")
            for doc_id, doc_data in list(registry.items())[:3]:
                title = doc_data.get('title', 'N/A')
                print(f"  - {doc_id}: {title}")
        
        # Initialize graph generator
        generator = KnowledgeGraphGenerator()
        await generator.initialize()
        
        # Generate graph
        print("\n🔄 Generating knowledge graph...")
        graph_data = await generator._extract_graph_data()
        
        print(f"\n📊 Graph Statistics:")
        print(f"  - Nodes: {graph_data.get('node_count', 0)}")
        print(f"  - Edges: {graph_data.get('edge_count', 0)}")
        
        # Check node names
        print(f"\n🏷️  Node Names (first 5):")
        nodes = graph_data.get('nodes', [])
        for i, node in enumerate(nodes[:5]):
            node_id = node.get('id', 'N/A')
            node_name = node.get('name', 'N/A')
            node_type = node.get('type', 'N/A')
            print(f"  {i+1}. ID: {node_id[:20]}... → Name: {node_name} (Type: {node_type})")
            
            # Check if name is meaningful (not just hash)
            if node_name.startswith('doc-') or (len(node_name) == 32 and all(c in '0123456789abcdef' for c in node_name.lower())):
                print(f"     ⚠️  Warning: Node name appears to be a hash")
            else:
                print(f"     ✅ Node name looks meaningful")
        
        # Check edge descriptions
        print(f"\n🔗 Edge Descriptions (first 3):")
        edges = graph_data.get('edges', [])
        for i, edge in enumerate(edges[:3]):
            source_name = edge.get('source_name', edge.get('source', 'N/A'))
            target_name = edge.get('target_name', edge.get('target', 'N/A'))
            description = edge.get('description', 'N/A')
            print(f"  {i+1}. {source_name} → {target_name}")
            print(f"     Description: {description}")
        
        # Test simple graph as fallback
        print(f"\n🔄 Testing simple graph fallback...")
        simple_graph = await generator._create_simple_graph()
        print(f"  - Simple graph nodes: {simple_graph.get('node_count', 0)}")
        
        print(f"\n🏷️  Simple Graph Node Names (first 3):")
        simple_nodes = simple_graph.get('nodes', [])
        for i, node in enumerate(simple_nodes[:3]):
            node_id = node.get('id', 'N/A')
            node_name = node.get('name', 'N/A')
            print(f"  {i+1}. ID: {node_id[:20]}... → Name: {node_name}")
            
            if node_name.startswith('doc-') or (len(node_name) == 32 and all(c in '0123456789abcdef' for c in node_name.lower())):
                print(f"     ⚠️  Warning: Simple graph node name appears to be a hash")
            else:
                print(f"     ✅ Simple graph node name looks meaningful")
        
        print("\n" + "=" * 60)
        print("✅ Graph naming test completed")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_graph_naming())
    sys.exit(0 if success else 1)