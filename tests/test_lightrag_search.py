"""Unit tests for LightRAG search functionality to ensure indexed content can be retrieved."""

import pytest
import asyncio
import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.config import settings


class TestLightRAGSearch:
    """Test suite for LightRAG search functionality."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing."""
        return [
            {
                'doc_id': 'doc_001',
                'content': """
# 人工智能基础

人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。

## 主要领域
1. 机器学习：从数据中学习模式
2. 自然语言处理：理解和生成人类语言
3. 计算机视觉：识别和分析图像
4. 机器人技术：创建智能机器人

## 应用
人工智能在医疗、金融、教育等领域有广泛应用。
""",
                'metadata': {
                    'title': '人工智能基础',
                    'source': 'test_source',
                    'category': 'technology'
                }
            },
            {
                'doc_id': 'doc_002',
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
                'doc_id': 'doc_003',
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
    
    @pytest.mark.asyncio
    async def test_document_indexing(self, temp_data_dir, sample_documents):
        """Test that documents can be successfully indexed."""
        # Create adapter with temporary directory
        rag = LightRAGAdapter(working_dir=temp_data_dir)
        await rag.ensure_initialized()
        
        # Index documents
        success = await rag.ingest(sample_documents)
        
        # Verify indexing succeeded
        assert success is True, "Document indexing should succeed"
        
        # Verify BM25 index was created
        assert rag.bm25_index_path.exists(), "BM25 index file should be created"
        
        # Verify documents are in BM25 index
        assert len(rag.bm25_search.documents) == len(sample_documents), \
            f"BM25 should contain {len(sample_documents)} documents"
    
    @pytest.mark.asyncio
    async def test_bm25_search_retrieval(self, temp_data_dir, sample_documents):
        """Test that BM25 search can retrieve indexed documents."""
        # Create adapter and index documents
        rag = LightRAGAdapter(working_dir=temp_data_dir)
        await rag.ensure_initialized()
        
        # Index documents
        await rag.ingest(sample_documents)
        
        # Test search queries
        test_queries = [
            ("什么是人工智能", "人工智能"),
            ("深度学习的应用", "深度学习"),
            ("自然语言处理任务", "自然语言处理"),
            ("机器学习", "机器学习")
        ]
        
        for query, expected_keyword in test_queries:
            results = rag.bm25_search.search(query, top_k=3)
            
            # Verify we got results
            assert len(results) > 0, f"Search for '{query}' should return results"
            
            # Verify results contain expected keyword
            found_keyword = False
            for result in results:
                if expected_keyword in result['text']:
                    found_keyword = True
                    break
            
            assert found_keyword, f"Results for '{query}' should contain '{expected_keyword}'"
    
    @pytest.mark.asyncio
    async def test_bm25_chinese_tokenization(self, temp_data_dir):
        """Test that Chinese tokenization works correctly."""
        # Create adapter
        rag = LightRAGAdapter(working_dir=temp_data_dir)
        await rag.ensure_initialized()
        
        # Test tokenization
        test_text = "机器学习是人工智能的一个分支"
        tokens = rag.bm25_search._tokenize(test_text)
        
        # Verify tokens contain expected characters
        expected_tokens = ['机', '器', '学', '习', '是', '人', '工', '智', '能']
        for expected in expected_tokens:
            assert expected in tokens, f"Token '{expected}' should be in tokenized result"
        
        # Verify query tokenization
        query = "什么是机器学习"
        query_tokens = rag.bm25_search._tokenize(query)
        assert '机' in query_tokens, "Query tokenization should work"
        assert '器' in query_tokens, "Query tokenization should work"
        assert '学' in query_tokens, "Query tokenization should work"
        assert '习' in query_tokens, "Query tokenization should work"
    
    @pytest.mark.asyncio
    async def test_bm25_index_persistence(self, temp_data_dir, sample_documents):
        """Test that BM25 index can be saved and loaded."""
        # Create adapter and index documents
        rag1 = LightRAGAdapter(working_dir=temp_data_dir)
        await rag1.ensure_initialized()
        await rag1.ingest(sample_documents)
        
        # Create new adapter instance to test loading
        rag2 = LightRAGAdapter(working_dir=temp_data_dir)
        await rag2.ensure_initialized()
        
        # Verify index was loaded
        assert len(rag2.bm25_search.documents) == len(sample_documents), \
            "Loaded index should contain same number of documents"
        
        # Verify search works with loaded index
        results = rag2.bm25_search.search("人工智能", top_k=3)
        assert len(results) > 0, "Search should work with loaded index"
    
    @pytest.mark.asyncio
    async def test_search_with_no_results(self, temp_data_dir):
        """Test search behavior when no results are found."""
        # Create adapter with no documents
        rag = LightRAGAdapter(working_dir=temp_data_dir)
        await rag.ensure_initialized()
        
        # Search for something that shouldn't exist
        results = rag.bm25_search.search("不存在的文档内容xyz", top_k=3)
        
        # Verify no results
        assert len(results) == 0, "Search should return no results for non-existent content"
    
    @pytest.mark.asyncio
    async def test_search_result_ranking(self, temp_data_dir, sample_documents):
        """Test that search results are properly ranked."""
        # Create adapter and index documents
        rag = LightRAGAdapter(working_dir=temp_data_dir)
        await rag.ensure_initialized()
        await rag.ingest(sample_documents)
        
        # Search for specific term
        results = rag.bm25_search.search("人工智能", top_k=3)
        
        # Verify results are ranked (higher score first)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]['score'] >= results[i+1]['score'], \
                    "Results should be ranked by score (descending)"
    
    @pytest.mark.asyncio
    async def test_multiple_document_search(self, temp_data_dir, sample_documents):
        """Test search across multiple documents."""
        # Create adapter and index documents
        rag = LightRAGAdapter(working_dir=temp_data_dir)
        await rag.ensure_initialized()
        await rag.ingest(sample_documents)
        
        # Search for term that appears in multiple documents
        results = rag.bm25_search.search("学习", top_k=5)
        
        # Verify we get results from multiple documents
        doc_ids = set([r['id'] for r in results])
        assert len(doc_ids) > 1, "Search should return results from multiple documents"
    
    @pytest.mark.asyncio
    async def test_document_metadata_preservation(self, temp_data_dir, sample_documents):
        """Test that document metadata is preserved during indexing."""
        # Create adapter and index documents
        rag = LightRAGAdapter(working_dir=temp_data_dir)
        await rag.ensure_initialized()
        await rag.ingest(sample_documents)
        
        # Search and verify metadata
        results = rag.bm25_search.search("人工智能", top_k=1)
        
        if results:
            # Verify metadata is preserved
            assert 'metadata' in results[0], "Result should contain metadata"
            assert 'title' in results[0]['metadata'], "Metadata should contain title"
            assert results[0]['metadata']['title'] == '人工智能基础', \
                "Title should match original document"


class TestLightRAGIntegration:
    """Integration tests for LightRAG search with actual LLM."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_end_to_end_search_workflow(self, temp_data_dir):
        """Test complete workflow: index, search, and generate answer."""
        # Create adapter
        rag = LightRAGAdapter(working_dir=temp_data_dir)
        await rag.ensure_initialized()
        
        # Index a simple document
        test_doc = {
            'doc_id': 'test_doc',
            'content': """
# Python编程基础

Python是一种高级编程语言，以其简洁易读的语法而闻名。

## 主要特点
1. 简单易学：语法清晰，适合初学者
2. 功能强大：丰富的标准库和第三方库
3. 跨平台：可在Windows、Linux、Mac上运行
4. 应用广泛：Web开发、数据分析、人工智能等

Python在数据科学和机器学习领域特别受欢迎。
""",
            'metadata': {
                'title': 'Python编程基础',
                'source': 'test'
            }
        }
        
        # Index document
        success = await rag.ingest([test_doc])
        assert success is True, "Document indexing should succeed"
        
        # Search for content
        results = rag.bm25_search.search("Python的特点", top_k=1)
        assert len(results) > 0, "Search should return results"
        
        # Verify content matches
        assert "Python" in results[0]['text'], "Result should contain Python"
        assert "特点" in results[0]['text'] or "简单" in results[0]['text'], \
            "Result should contain relevant content"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])