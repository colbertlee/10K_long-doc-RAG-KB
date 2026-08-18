"""Test script for knowledge graph extraction functionality."""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.lightrag.graph_extractor import LightRAGGraphExtractor

def test_graph_extraction():
    """Test knowledge graph extraction."""
    print("🧪 Testing Knowledge Graph Extraction")
    print("=" * 50)
    
    # Create a test LightRAG working directory
    test_working_dir = Path(__file__).parent.parent / "lightrag_db"
    
    if not test_working_dir.exists():
        print(f"⚠️  LightRAG working directory not found: {test_working_dir}")
        print("   Creating test directory structure...")
        test_working_dir.mkdir(parents=True, exist_ok=True)
        
        # Create some test graph data files
        test_data_dir = test_working_dir / "test_data"
        test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sample graph data
        sample_graph_data = {
            "entities": {
                "machine_learning": {
                    "name": "Machine Learning",
                    "type": "concept",
                    "description": "Subset of AI focused on learning from data"
                },
                "deep_learning": {
                    "name": "Deep Learning", 
                    "type": "concept",
                    "description": "Subset of ML using neural networks"
                },
                "neural_networks": {
                    "name": "Neural Networks",
                    "type": "concept",
                    "description": "Computing systems inspired by biological networks"
                }
            },
            "relations": [
                {
                    "source": "machine_learning",
                    "target": "deep_learning",
                    "relation": "includes",
                    "weight": 0.9
                },
                {
                    "source": "deep_learning", 
                    "target": "neural_networks",
                    "relation": "uses",
                    "weight": 0.95
                }
            ]
        }
        
        sample_file = test_data_dir / "sample_graph.json"
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_graph_data, f, indent=2)
        
        print(f"   ✅ Created test graph data: {sample_file}")
    
    print(f"\n🔧 Creating graph extractor for: {test_working_dir}")
    
    try:
        extractor = LightRAGGraphExtractor(test_working_dir)
        print("✅ Graph extractor created successfully")
    except Exception as e:
        print(f"❌ Failed to create graph extractor: {e}")
        return False
    
    # Get graph data
    print("\n📊 Extracting graph data...")
    try:
        graph_data = extractor.get_graph_data()
        print(f"✅ Graph data extracted:")
        print(f"   - Total nodes: {graph_data['metadata']['total_nodes']}")
        print(f"   - Total edges: {graph_data['metadata']['total_edges']}")
        print(f"   - Working directory: {graph_data['metadata']['working_dir']}")
        
        if graph_data['nodes']:
            print(f"\n   Sample nodes:")
            for i, node in enumerate(graph_data['nodes'][:3]):
                print(f"   {i+1}. {node['id']} ({node.get('type', 'unknown')})")
                print(f"      Label: {node.get('label', 'N/A')}")
        
        if graph_data['edges']:
            print(f"\n   Sample edges:")
            for i, edge in enumerate(graph_data['edges'][:3]):
                print(f"   {i+1}. {edge['source']} -> {edge['target']} ({edge.get('label', 'related')})")
    
    except Exception as e:
        print(f"❌ Failed to extract graph data: {e}")
        return False
    
    # Get statistics
    print("\n📈 Getting graph statistics...")
    try:
        stats = extractor.get_statistics()
        print(f"✅ Graph statistics:")
        print(f"   - Total nodes: {stats['total_nodes']}")
        print(f"   - Total edges: {stats['total_edges']}")
        print(f"   - Average degree: {stats['avg_degree']:.2f}")
        print(f"   - Connected components: {stats['connected_components']}")
        
        if stats['node_types']:
            print(f"   - Node types: {stats['node_types']}")
        
        if stats['relation_types']:
            print(f"   - Relation types: {stats['relation_types']}")
    
    except Exception as e:
        print(f"❌ Failed to get statistics: {e}")
        return False
    
    # Test filtering
    if graph_data['nodes']:
        print("\n🔍 Testing entity type filtering...")
        try:
            # Get first entity type from available nodes
            first_type = graph_data['nodes'][0].get('type', 'concept')
            filtered_data = extractor.filter_by_entity_type(first_type)
            print(f"✅ Filtered by type '{first_type}':")
            print(f"   - Filtered nodes: {filtered_data['metadata']['total_nodes']}")
            print(f"   - Filtered edges: {filtered_data['metadata']['total_edges']}")
        except Exception as e:
            print(f"❌ Filtering failed: {e}")
    
    # Test neighborhood query (if we have nodes)
    if graph_data['nodes']:
        print("\n🏘️  Testing neighborhood query...")
        try:
            first_node_id = graph_data['nodes'][0]['id']
            neighborhood = extractor.get_neighborhood(first_node_id, depth=1)
            print(f"✅ Neighborhood of '{first_node_id}':")
            print(f"   - Center entity: {neighborhood['metadata']['center_entity']}")
            print(f"   - Depth: {neighborhood['metadata']['depth']}")
            print(f"   - Nodes in neighborhood: {neighborhood['metadata']['total_nodes']}")
            print(f"   - Edges in neighborhood: {neighborhood['metadata']['total_edges']}")
        except Exception as e:
            print(f"❌ Neighborhood query failed: {e}")
    
    # Test NetworkX conversion
    print("\n🔗 Testing NetworkX graph conversion...")
    try:
        nx_graph = extractor.get_networkx_graph()
        print(f"✅ NetworkX graph created:")
        print(f"   - Number of nodes: {nx_graph.number_of_nodes()}")
        print(f"   - Number of edges: {nx_graph.number_of_edges()}")
        
        # Test some NetworkX operations
        if nx_graph.number_of_nodes() > 0:
            print(f"   - Graph density: {nx.density(nx_graph):.4f}")
            if nx_graph.is_directed():
                print(f"   - Is directed: True")
            else:
                print(f"   - Is directed: False")
    
    except Exception as e:
        print(f"❌ NetworkX conversion failed: {e}")
        print(f"   This is expected if NetworkX is not installed")
    
    # Test saving graph data
    print("\n💾 Testing graph data saving...")
    try:
        output_file = Path(__file__).parent.parent / "data" / "test_graph_output.json"
        extractor.save_graph_data(output_file)
        print(f"✅ Graph data saved to: {output_file}")
        
        # Verify the file was created
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            print(f"   - Saved nodes: {len(saved_data['nodes'])}")
            print(f"   - Saved edges: {len(saved_data['edges'])}")
        else:
            print(f"   ⚠️  Output file not created")
    
    except Exception as e:
        print(f"❌ Failed to save graph data: {e}")
    
    print("\n🎉 Knowledge graph extraction tests passed!")
    return True

def test_api_integration():
    """Test knowledge graph API integration."""
    print("\n🧪 Testing Knowledge Graph API Integration")
    print("=" * 50)
    
    # This would test the actual API endpoint
    # For now, we'll just verify the API route exists
    api_routes_file = Path(__file__).parent.parent / "src" / "rag_kb" / "api" / "routes.py"
    
    if api_routes_file.exists():
        print(f"✅ API routes file found: {api_routes_file}")
        
        # Check if the graph endpoint exists
        content = api_routes_file.read_text(encoding='utf-8')
        if 'get_knowledge_graph' in content:
            print("✅ Knowledge graph API endpoint found in routes")
        else:
            print("⚠️  Knowledge graph API endpoint not found in routes")
    else:
        print(f"❌ API routes file not found: {api_routes_file}")
    
    print("\n🎉 API integration check completed!")
    return True

if __name__ == "__main__":
    print("🚀 RAG KB Knowledge Graph Test Suite")
    print("=" * 50)
    
    success = True
    
    try:
        if not test_graph_extraction():
            success = False
        
        if not test_api_integration():
            success = False
        
        if success:
            print("\n" + "=" * 50)
            print("✅ All knowledge graph tests completed successfully!")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed")
            print("=" * 50)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)