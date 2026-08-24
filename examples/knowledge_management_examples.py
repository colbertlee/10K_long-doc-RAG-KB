"""
Knowledge Management Features Usage Examples (v0.4.0)

This file demonstrates how to use the new knowledge management features
introduced in v0.4.0, including knowledge organization and batch operations.
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def example_knowledge_organization():
    """Example: Automatic document organization and classification."""
    print("=== Knowledge Organization Example ===\n")
    
    url = f"{BASE_URL}/api/v1/knowledge/organize"
    
    # Example 1: Technical document
    tech_content = """
    Python是一种高级编程语言，广泛应用于机器学习和人工智能领域。
    在技术架构设计中，我们使用Docker进行容器化部署，使用Kubernetes进行集群管理。
    该系统支持多种文档格式，包括PDF、Word、Excel等。
    """
    
    tech_data = {
        "content": tech_content,
        "filename": "technical_architecture.txt",
        "metadata": {"author": "John Doe", "date": "2024-08-24"}
    }
    
    response = requests.post(url, json=tech_data)
    result = response.json()
    
    print("Technical Document Organization:")
    print(f"Category: {result['organization']['category']}")
    print(f"Tags: {result['organization']['tags']}")
    print(f"Suggested Folder: {result['organization']['suggested_folder']}")
    print(f"Confidence: {result['organization']['confidence']}")
    print(f"Quality Score: {result['quality_analysis']['overall_score']}")
    print(f"Suggestions: {result['quality_analysis']['suggestions']}")
    
    # Example 2: Business document
    business_content = """
    本季度的市场销售策略重点关注客户增长和收入提升。
    我们计划通过数字营销和合作伙伴关系来扩大市场份额。
    目标是增长20%的用户基数和15%的收入。
    """
    
    business_data = {
        "content": business_content,
        "filename": "business_strategy.txt",
        "metadata": {"department": "Marketing", "quarter": "Q3"}
    }
    
    response = requests.post(url, json=business_data)
    result = response.json()
    
    print("\nBusiness Document Organization:")
    print(f"Category: {result['organization']['category']}")
    print(f"Tags: {result['organization']['tags']}")
    print(f"Suggested Folder: {result['organization']['suggested_folder']}")
    print(f"Confidence: {result['organization']['confidence']}")

def example_batch_operations():
    """Example: Batch operations on multiple documents."""
    print("\n=== Batch Operations Example ===\n")
    
    url = f"{BASE_URL}/api/v1/knowledge/batch-operation"
    
    # Example 1: Batch tagging
    tag_data = {
        "operation": "tag",
        "document_ids": ["doc1", "doc2", "doc3", "doc4", "doc5"],
        "parameters": {
            "tags": ["技术", "Python", "机器学习"]
        }
    }
    
    response = requests.post(url, json=tag_data)
    result = response.json()
    
    print("Batch Tagging Results:")
    print(f"Operation: {result['operation']}")
    print(f"Total Documents: {result['total']}")
    print(f"Successful: {result['successful']}")
    print(f"Failed: {result['failed']}")
    
    for item in result['results']:
        print(f"  - {item['doc_id']}: {item['status']}")
    
    # Example 2: Batch category movement
    move_data = {
        "operation": "move",
        "document_ids": ["doc1", "doc2"],
        "parameters": {
            "category": "technical"
        }
    }
    
    response = requests.post(url, json=move_data)
    result = response.json()
    
    print("\nBatch Category Movement Results:")
    print(f"Operation: {result['operation']}")
    print(f"Total Documents: {result['total']}")
    print(f"Successful: {result['successful']}")
    
    # Example 3: Batch reindexing
    reindex_data = {
        "operation": "reindex",
        "document_ids": ["doc1", "doc2", "doc3"],
        "parameters": {}
    }
    
    response = requests.post(url, json=reindex_data)
    result = response.json()
    
    print("\nBatch Reindexing Results:")
    print(f"Operation: {result['operation']}")
    print(f"Total Documents: {result['total']}")
    print(f"Successful: {result['successful']}")

def example_quality_improvement():
    """Example: Using quality analysis to improve documents."""
    print("\n=== Quality Improvement Example ===\n")
    
    url = f"{BASE_URL}/api/v1/knowledge/organize"
    
    # Poor quality document
    poor_content = "短内容"
    
    poor_data = {
        "content": poor_content,
        "filename": "poor_doc.txt",
        "metadata": {}
    }
    
    response = requests.post(url, json=poor_data)
    result = response.json()
    
    print("Poor Quality Document Analysis:")
    print(f"Overall Score: {result['quality_analysis']['overall_score']}")
    print(f"Completeness: {result['quality_analysis']['metrics']['completeness']}")
    print(f"Readability: {result['quality_analysis']['metrics']['readability']}")
    print(f"Structure: {result['quality_analysis']['metrics']['structure']}")
    print(f"Suggestions: {result['quality_analysis']['suggestions']}")
    
    # Improved document based on suggestions
    improved_content = """
    # Python编程语言概述

    Python是一种高级编程语言，具有以下特点：
    - 语法简洁易读
    - 广泛应用于机器学习和人工智能
    - 拥有丰富的第三方库
    
    在技术架构中，Python常用于：
    - 数据处理和分析
    - Web开发
    - 自动化脚本
    """
    
    improved_data = {
        "content": improved_content,
        "filename": "improved_doc.txt",
        "metadata": {"title": "Python编程语言概述", "category": "技术", "tags": ["Python", "编程"]}
    }
    
    response = requests.post(url, json=improved_data)
    result = response.json()
    
    print("\nImproved Document Analysis:")
    print(f"Overall Score: {result['quality_analysis']['overall_score']}")
    print(f"Completeness: {result['quality_analysis']['metrics']['completeness']}")
    print(f"Readability: {result['quality_analysis']['metrics']['readability']}")
    print(f"Structure: {result['quality_analysis']['metrics']['structure']}")
    print(f"Suggestions: {result['quality_analysis']['suggestions']}")

def example_entity_extraction():
    """Example: Entity extraction from documents."""
    print("\n=== Entity Extraction Example ===\n")
    
    url = f"{BASE_URL}/api/v1/knowledge/organize"
    
    # Document with various entities
    content = """
    在2024年8月24日，我们的技术团队完成了Python项目的部署。
    我们使用了Docker和Kubernetes进行容器化，数据库选择了PostgreSQL。
    项目负责人是John Smith，联系邮箱是john.smith@example.com。
    更多信息请访问 https://example.com/project。
    """
    
    data = {
        "content": content,
        "filename": "project_report.txt",
        "metadata": {}
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print("Extracted Entities:")
    entities = result['organization']['entities']
    print(f"Technologies: {entities['technologies']}")
    print(f"Dates: {entities['dates']}")
    print(f"Emails: {entities['emails']}")
    print(f"URLs: {entities['urls']}")

def example_workflow():
    """Example: Complete workflow using knowledge management features."""
    print("\n=== Complete Workflow Example ===\n")
    
    url_organize = f"{BASE_URL}/api/v1/knowledge/organize"
    url_batch = f"{BASE_URL}/api/v1/knowledge/batch-operation"
    
    # Step 1: Upload and organize multiple documents
    documents = [
        {
            "content": "Python是一种编程语言，用于AI和机器学习。",
            "filename": "doc1.txt",
            "metadata": {}
        },
        {
            "content": "Docker用于容器化部署，Kubernetes用于集群管理。",
            "filename": "doc2.txt",
            "metadata": {}
        },
        {
            "content": "PostgreSQL是一个开源的关系型数据库。",
            "filename": "doc3.txt",
            "metadata": {}
        }
    ]
    
    organized_docs = []
    for i, doc in enumerate(documents, 1):
        response = requests.post(url_organize, json=doc)
        result = response.json()
        organized_docs.append({
            "doc_id": f"doc{i}",
            "category": result['organization']['category'],
            "tags": result['organization']['tags']
        })
        print(f"Document {i}: {result['organization']['category']} - {result['organization']['tags']}")
    
    # Step 2: Batch tag all documents with common tags
    doc_ids = [doc['doc_id'] for doc in organized_docs]
    tag_data = {
        "operation": "tag",
        "document_ids": doc_ids,
        "parameters": {"tags": ["技术", "开发"]}
    }
    
    response = requests.post(url_batch, json=tag_data)
    result = response.json()
    print(f"\nBatch Tagging: {result['successful']}/{result['total']} successful")
    
    # Step 3: Analyze overall quality
    print("\nQuality Summary:")
    for i, doc in enumerate(organized_docs, 1):
        print(f"Document {i}: {doc['category']} - Tags: {doc['tags']}")

def main():
    """Run all examples."""
    print("Knowledge Management Features Usage Examples")
    print("=" * 50)
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("Error: Server is not running. Please start the server first.")
            return
        
        # Run examples
        example_knowledge_organization()
        example_batch_operations()
        example_quality_improvement()
        example_entity_extraction()
        example_workflow()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server. Please ensure the server is running.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()