"""Test BM25 indexing directly without LightRAG entity extraction."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.lightrag.adapter import SimpleBM25Search


def test_bm25_indexing():
    """Test BM25 indexing directly."""
    
    print("=" * 60)
    print("Testing BM25 Indexing (Direct)")
    print("=" * 60)
    
    # Sample documents to index
    sample_documents = [
        {
            'id': 'test_doc_001',
            'text': """
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
            'id': 'test_doc_002',
            'text': """
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
            'id': 'test_doc_003',
            'text': """
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
        # Create BM25 search instance
        bm25 = SimpleBM25Search()
        
        # Index documents
        print("\nStep 2: Indexing documents...")
        bm25.add_documents(sample_documents)
        
        print(f"✅ Documents indexed successfully")
        print(f"   Total documents: {len(bm25.documents)}")
        print(f"   Total terms: {len(bm25.term_doc_map)}")
        
        # Save index
        print("\nStep 3: Saving BM25 index...")
        index_path = Path("lightrag_db/bm25_index.json")
        bm25.save_index(index_path)
        print(f"✅ BM25 index saved to {index_path}")
        
        # Load index to verify persistence
        print("\nStep 4: Loading BM25 index to verify persistence...")
        bm25_loaded = SimpleBM25Search()
        bm25_loaded.load_index(index_path)
        print(f"✅ BM25 index loaded successfully")
        print(f"   Documents loaded: {len(bm25_loaded.documents)}")
        
        # Test search
        print("\nStep 5: Testing search functionality...")
        test_queries = [
            "什么是机器学习",
            "深度学习的应用",
            "自然语言处理任务"
        ]
        
        for query in test_queries:
            results = bm25_loaded.search(query, top_k=2)
            print(f"\nQuery: '{query}'")
            print(f"Results: {len(results)}")
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['id']} (score: {result['score']})")
                    print(f"     {result['text'][:100]}...")
            else:
                print("  No results found")
        
        print("\n" + "=" * 60)
        print("✅ BM25 indexing test completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error during BM25 indexing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = test_bm25_indexing()
    sys.exit(0 if result else 1)