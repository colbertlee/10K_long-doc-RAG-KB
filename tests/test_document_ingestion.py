"""Test document ingestion and indexing to ensure knowledge base is properly indexed."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.lightrag.adapter import LightRAGAdapter


async def test_document_ingestion():
    """Test document ingestion to ensure knowledge base is properly indexed."""
    
    print("=" * 60)
    print("Testing Document Ingestion and Indexing")
    print("=" * 60)
    
    # Sample documents to index
    sample_documents = [
        {
            'doc_id': 'test_doc_001',
            'content': """
# 机器学习基础

机器学习是人工智能的一个分支，它专注于构建能够从数据中学习的系统。机器学习使计算机能够通过经验在特定任务上提高性能。

## 主要概念
1. 监督学习：算法在标记数据上训练
2. 无监督学习：算法在未标记数据中寻找模式
3. 深度学习：使用多层神经网络建模复杂模式

## 应用领域
- 医疗保健：疾病诊断
- 金融：欺诈检测
- 技术：图像识别
""",
            'metadata': {
                'title': '机器学习基础',
                'source': 'test_source',
                'category': 'technology'
            }
        },
        {
            'doc_id': 'test_doc_002',
            'content': """
# 深度学习概述

深度学习是机器学习的一个子集，使用多层神经网络来学习数据的复杂模式。

## 核心概念
- 神经网络：模拟人脑结构
- 反向传播：训练神经网络的关键算法
- 卷积神经网络：用于图像处理
- 循环神经网络：用于序列数据

深度学习在图像识别、语音识别、自然语言处理等领域取得了重大突破。
""",
            'metadata': {
                'title': '深度学习概述',
                'source': 'test_source',
                'category': 'technology'
            }
        },
        {
            'doc_id': 'test_doc_003',
            'content': """
# 自然语言处理

自然语言处理（NLP）是人工智能的一个分支，专注于计算机与人类语言之间的交互。

## 主要任务
1. 文本分类：将文本分类到预定义类别
2. 命名实体识别：识别文本中的实体
3. 情感分析：分析文本的情感倾向
4. 机器翻译：将文本从一种语言翻译到另一种语言

NLP技术广泛应用于聊天机器人、搜索引擎、翻译软件等。
""",
            'metadata': {
                'title': '自然语言处理',
                'source': 'test_source',
                'category': 'technology'
            }
        }
    ]
    
    print(f"\nStep 1: Preparing to index {len(sample_documents)} documents...")
    
    try:
        # Create adapter
        rag = LightRAGAdapter()
        await rag.ensure_initialized()
        
        print(f"LightRAG working directory: {rag.working_dir}")
        print(f"BM25 index path: {rag.bm25_index_path}")
        print(f"BM25 index exists: {rag.bm25_index_path.exists()}")
        
        # Index documents
        print("\nStep 2: Indexing documents...")
        success = await rag.ingest(sample_documents)
        
        if success:
            print("✅ Documents indexed successfully")
        else:
            print("❌ Document indexing failed")
            return False
        
        # Verify BM25 index
        print("\nStep 3: Verifying BM25 index...")
        if rag.bm25_index_path.exists():
            print(f"✅ BM25 index file exists")
            print(f"   Documents in index: {len(rag.bm25_search.documents)}")
        else:
            print("❌ BM25 index file not found")
            return False
        
        # Test search
        print("\nStep 4: Testing search functionality...")
        test_queries = [
            "什么是机器学习",
            "深度学习的应用",
            "自然语言处理任务"
        ]
        
        for query in test_queries:
            results = rag.bm25_search.search(query, top_k=2)
            print(f"\nQuery: '{query}'")
            print(f"Results: {len(results)}")
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['id']} (score: {result['score']})")
                    print(f"     {result['text'][:100]}...")
        
        # Test LightRAG query
        print("\nStep 5: Testing LightRAG query...")
        try:
            answer = await rag.query("什么是机器学习", mode="naive")
            print(f"LightRAG answer length: {len(answer) if answer else 0}")
            print(f"LightRAG answer preview: {answer[:200] if answer else 'empty'}...")
            
            if answer and "机器学习" in answer:
                print("✅ LightRAG query successful")
            else:
                print("⚠️ LightRAG query returned unexpected result")
        except Exception as e:
            print(f"❌ LightRAG query failed: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Document ingestion test completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error during document ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_document_ingestion())
    sys.exit(0 if result else 1)