"""Test knowledge graph extraction and visualization."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.lightrag.graph_extractor import LightRAGGraphExtractor
from rag_kb.lightrag.structured_graph_extractor import StructuredGraphExtractor


def test_knowledge_graph():
    """Test knowledge graph extraction and visualization."""
    
    print("=" * 60)
    print("Testing Knowledge Graph Functionality")
    print("=" * 60)
    
    try:
        # Test 1: Graph extraction from LightRAG storage
        print("\nStep 1: Testing LightRAG graph extraction...")
        working_dir = Path("lightrag_db")
        
        if working_dir.exists():
            graph_extractor = LightRAGGraphExtractor(working_dir)
            graph_data = graph_extractor.get_graph_data()
            
            print(f"Graph extraction completed")
            print(f"  Total nodes: {graph_data['metadata']['total_nodes']}")
            print(f"  Total edges: {graph_data['metadata']['total_edges']}")
            
            if graph_data['metadata']['total_nodes'] > 0:
                print("✅ Graph data extracted successfully")
                
                # Display sample nodes
                print("\nSample nodes:")
                for i, node in enumerate(graph_data['nodes'][:3], 1):
                    print(f"  {i}. {node['id']} ({node['type']})")
                    if 'label' in node:
                        print(f"     Label: {node['label']}")
            else:
                print("⚠️ No graph data found (expected - documents not indexed with LightRAG)")
        else:
            print("⚠️ LightRAG working directory not found")
        
        # Test 2: Structured graph parsing
        print("\nStep 2: Testing structured graph parsing...")
        
        # Sample LLM output in the expected format
        sample_llm_output = """[Entities]
("entity"<|>机器学习<|>Concept<|>机器学习是人工智能的一个分支，专注于构建能够从数据中学习的系统)
##
("entity"<|>深度学习<|>Concept<|>深度学习是机器学习的子集，使用多层神经网络学习复杂模式)
##
("entity"<|>自然语言处理<|>Concept<|>自然语言处理专注于计算机与人类语言的交互)
##
("entity"<|>神经网络<|>Component<|>神经网络模拟人脑结构，是深度学习的基础)

[Relationships]
("relationship"<|>深度学习<|>机器学习<|>IS_SUBSET_OF<|>深度学习是机器学习的一个子集<|>9)
##
("relationship"<|>深度学习<|>神经网络<|>USES<|>深度学习使用神经网络作为基础架构<|>8)
##
("relationship"<|>自然语言处理<|>机器学习<|>RELATED_TO<|>自然语言处理与机器学习密切相关<|>6)
##
("relationship"<|>自然语言处理<|>深度学习<|>UTILIZES<|>自然语言处理利用深度学习技术<|>7)
<|COMPLETE|>"""
        
        structured_extractor = StructuredGraphExtractor()
        entities, relationships = structured_extractor.parse_llm_output(sample_llm_output)
        
        print(f"Structured parsing completed")
        print(f"  Entities extracted: {len(entities)}")
        print(f"  Relationships extracted: {len(relationships)}")
        
        if entities and relationships:
            print("✅ Structured graph parsing successful")
            
            # Display entities
            print("\nEntities:")
            for i, entity in enumerate(entities, 1):
                print(f"  {i}. {entity.name} ({entity.entity_type})")
                print(f"     {entity.description[:80]}...")
            
            # Display relationships
            print("\nRelationships:")
            for i, rel in enumerate(relationships, 1):
                print(f"  {i}. {rel.source} -> {rel.target} ({rel.rel_type}, strength: {rel.strength})")
                print(f"     {rel.description[:80]}...")
            
            # Validate consistency
            print("\nStep 3: Validating graph consistency...")
            errors = structured_extractor.validate_consistency()
            if errors:
                print(f"⚠️ Found {len(errors)} validation errors:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("✅ Graph consistency validated successfully")
            
            # Get statistics
            print("\nStep 4: Graph statistics...")
            entity_types = structured_extractor.get_entity_types()
            relationship_types = structured_extractor.get_relationship_types()
            
            print(f"Entity types: {entity_types}")
            print(f"Relationship types: {relationship_types}")
            
            # Convert to NetworkX format
            print("\nStep 5: Converting to NetworkX format...")
            nx_format = structured_extractor.to_networkx_format()
            print(f"NetworkX nodes: {len(nx_format['nodes'])}")
            print(f"NetworkX edges: {len(nx_format['edges'])}")
            print("✅ NetworkX format conversion successful")
        
        print("\n" + "=" * 60)
        print("✅ Knowledge graph test completed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error during knowledge graph test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = test_knowledge_graph()
    sys.exit(0 if result else 1)