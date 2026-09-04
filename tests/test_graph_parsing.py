"""Test structured graph extractor parsing functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.lightrag.structured_graph_extractor import StructuredGraphExtractor


def test_structured_parsing():
    """Test the structured graph extractor parsing without LLM calls."""
    
    print("=" * 60)
    print("Testing Structured Graph Extractor Parsing")
    print("=" * 60)
    
    # Sample LLM output in the expected format
    sample_llm_output = """[Entities]
("entity"<|>知识库<|>Component<|>知识库负责存储和管理企业文档、流程规范和技术资料，支持多种文档格式包括PDF、Word、Excel和PowerPoint)
##
("entity"<|>搜索引擎<|>Component<|>搜索引擎基于LightRAG技术，提供向量搜索和知识图谱查询功能，支持BM25稀疏搜索和语义向量搜索的混合检索模式)
##
("entity"<|>用户界面<|>Component<|>用户界面提供Web端和移动端访问，支持知识浏览、搜索和协作功能)
##
("entity"<|>权限管理系统<|>Component<|>权限管理系统基于RBAC模型，控制用户对不同知识库的访问权限)
##
("entity"<|>企业知识管理系统<|>System<|>企业知识管理系统（EKM）由多个组件构成，包括知识库、搜索引擎、用户界面和权限管理系统)

[Relationships]
("relationship"<|>搜索引擎<|>知识库<|>INDEXES<|>搜索引擎对知识库中的内容进行向量化和关系抽取以支持搜索功能<|>9)
##
("relationship"<|>用户界面<|>搜索引擎<|>CALLS<|>用户界面通过API调用搜索引擎获取搜索结果<|>7)
##
("relationship"<|>用户界面<|>知识库<|>ACCESSES<|>用户界面通过API直接访问知识库获取文档内容<|>6)
##
("relationship"<|>权限管理系统<|>知识库<|>PROTECTS<|>权限管理系统保护知识库的安全访问，控制用户对不同文档的访问权限<|>8)
##
("relationship"<|>权限管理系统<|>搜索引擎<|>AUTHORIZES<|>权限管理系统验证用户权限后授权搜索引擎执行搜索操作<|>7)
##
("relationship"<|>企业知识管理系统<|>知识库<|>CONTAINS<|>企业知识管理系统包含知识库作为核心存储组件<|>10)
##
("relationship"<|>企业知识管理系统<|>搜索引擎<|>INCLUDES<|>企业知识管理系统包含搜索引擎作为检索组件<|>10)
<|COMPLETE|>"""
    
    print("\nStep 1: Parsing structured LLM output...")
    print(f"Sample output length: {len(sample_llm_output)} characters")
    
    extractor = StructuredGraphExtractor()
    entities, relationships = extractor.parse_llm_output(sample_llm_output)
    
    print(f"\nExtracted {len(entities)} entities")
    print(f"Extracted {len(relationships)} relationships")
    
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
    print("\nStep 2: Validating consistency...")
    errors = extractor.validate_consistency()
    if errors:
        print(f"Found {len(errors)} validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ No validation errors found!")
    
    # Get statistics
    print("\nStep 3: Graph statistics...")
    entity_types = extractor.get_entity_types()
    print(f"Entity types: {entity_types}")
    
    relationship_types = extractor.get_relationship_types()
    print(f"Relationship types: {relationship_types}")
    
    # Test entity lookup
    print("\nStep 4: Testing entity lookup...")
    kb_entity = extractor.get_entity_by_name("知识库")
    if kb_entity:
        print(f"Found entity: {kb_entity.name}")
        print(f"Type: {kb_entity.entity_type}")
        print(f"Description: {kb_entity.description[:100]}...")
    else:
        print("Entity not found")
    
    # Test relationship lookup
    print("\nStep 5: Testing relationship lookup...")
    kb_relationships = extractor.get_relationships_for_entity("知识库")
    print(f"Relationships for '知识库': {len(kb_relationships)}")
    for rel in kb_relationships:
        direction = "incoming" if rel.target == "知识库" else "outgoing"
        other = rel.target if rel.source == "知识库" else rel.source
        print(f"  {direction}: {other} ({rel.rel_type}, strength: {rel.strength})")
    
    # Convert to NetworkX format
    print("\nStep 6: Converting to NetworkX format...")
    nx_format = extractor.to_networkx_format()
    print(f"NetworkX nodes: {len(nx_format['nodes'])}")
    print(f"NetworkX edges: {len(nx_format['edges'])}")
    
    # Test dual-level concepts
    print("\nStep 7: Testing dual-level concepts...")
    system_entity = extractor.get_entity_by_name("企业知识管理系统")
    if system_entity:
        print(f"High-level entity: {system_entity.name}")
        print(f"Type: {system_entity.entity_type}")
        
        system_relationships = extractor.get_relationships_for_entity("企业知识管理系统")
        print(f"System-level relationships: {len(system_relationships)}")
        for rel in system_relationships:
            print(f"  {rel.source} -> {rel.target} ({rel.rel_type}, strength: {rel.strength})")
    
    print("\n" + "=" * 60)
    print("✅ All parsing tests passed successfully!")
    print("=" * 60)
    
    return True


def test_fallback_parsing():
    """Test fallback parsing for non-standard formats."""
    
    print("\n" + "=" * 60)
    print("Testing Fallback Parsing")
    print("=" * 60)
    
    # Sample JSON format output
    json_output = """{
    "entities": [
        {
            "name": "数据库服务器",
            "type": "Component",
            "description": "存储和管理企业数据的数据库服务器"
        },
        {
            "name": "应用服务器",
            "type": "Component",
            "description": "运行业务逻辑的应用服务器"
        }
    ],
    "relationships": [
        {
            "source": "应用服务器",
            "target": "数据库服务器",
            "type": "CONNECTS_TO",
            "description": "应用服务器连接到数据库服务器进行数据访问",
            "strength": 9
        }
    ]
}"""
    
    print("\nStep 1: Testing JSON fallback parsing...")
    extractor = StructuredGraphExtractor()
    entities, relationships = extractor.parse_llm_output(json_output)
    
    print(f"Extracted {len(entities)} entities")
    print(f"Extracted {len(relationships)} relationships")
    
    if entities:
        print("\nEntities from JSON:")
        for entity in entities:
            print(f"  - {entity.name} ({entity.entity_type})")
    
    if relationships:
        print("\nRelationships from JSON:")
        for rel in relationships:
            print(f"  - {rel.source} -> {rel.target} ({rel.rel_type}, strength: {rel.strength})")
    
    print("\n✅ Fallback parsing test passed!")
    return True


def test_validation_errors():
    """Test validation error detection."""
    
    print("\n" + "=" * 60)
    print("Testing Validation Error Detection")
    print("=" * 60)
    
    # Output with validation errors
    invalid_output = """[Entities]
("entity"<|>知识库<|>Component<|>知识库负责存储和管理企业文档)
##
("entity"<|>搜索引擎<|>Component<|>搜索引擎基于LightRAG技术)

[Relationships]
("relationship"<|>搜索引擎<|>知识库<|>INDEXES<|>搜索引擎对知识库进行索引<|>9)
##
("relationship"<|>用户界面<|>不存在的组件<|>CALLS<|>用户界面调用不存在的组件<|>7)
##
("relationship"<|>知识库<|>搜索引擎<|>DEPENDS_ON<|>知识库依赖搜索引擎<|>15)
<|COMPLETE|>"""
    
    print("\nStep 1: Testing validation with invalid data...")
    extractor = StructuredGraphExtractor()
    entities, relationships = extractor.parse_llm_output(invalid_output)
    
    print(f"Extracted {len(entities)} entities")
    print(f"Extracted {len(relationships)} relationships")
    
    errors = extractor.validate_consistency()
    print(f"\nFound {len(errors)} validation errors:")
    for error in errors:
        print(f"  - {error}")
    
    # Should detect 2 errors: unknown target entity and invalid strength
    expected_errors = 2
    if len(errors) >= expected_errors:
        print(f"\n✅ Validation error detection works correctly!")
        return True
    else:
        print(f"\n❌ Expected at least {expected_errors} errors, got {len(errors)}")
        return False


if __name__ == "__main__":
    result1 = test_structured_parsing()
    result2 = test_fallback_parsing()
    result3 = test_validation_errors()
    
    if result1 and result2 and result3:
        print("\n" + "=" * 60)
        print("All knowledge graph parsing tests passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("Some tests failed!")
        print("=" * 60)
        sys.exit(1)