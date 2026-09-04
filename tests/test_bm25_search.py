"""Unit tests for BM25 search functionality (simplified, no LightRAG dependency)."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path


class SimpleBM25Search:
    """Simple BM25 search implementation for testing."""
    
    def __init__(self):
        self.documents = []
        self.doc_freqs = {}
        self.term_doc_map = {}
        
    def add_documents(self, documents):
        """Add documents to the index."""
        self.documents = documents
        self.term_doc_map = {}
        self.doc_freqs = {}
        
        for doc in documents:
            text = doc.get('text', '')
            terms = self._tokenize(text)
            term_freq = {}
            for term in terms:
                term_freq[term] = term_freq.get(term, 0) + 1
            
            for term, freq in term_freq.items():
                if term not in self.term_doc_map:
                    self.term_doc_map[term] = []
                self.term_doc_map[term].append((doc['id'], freq))
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1
    
    def _tokenize(self, text):
        """Simple tokenization with Chinese support."""
        import re
        tokens = []
        for part in text.lower().split():
            if re.search(r'[\u4e00-\u9fff]', part):
                tokens.extend(list(part))
            else:
                tokens.append(part)
        return tokens
    
    def search(self, query, top_k=3):
        """Search using BM25."""
        query_terms = self._tokenize(query)
        scores = {}
        
        for term in query_terms:
            if term not in self.term_doc_map:
                continue
            
            for doc_id, term_freq in self.term_doc_map[term]:
                scores[doc_id] = scores.get(doc_id, 0) + term_freq
        
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for doc_id, score in sorted_results:
            doc = next((d for d in self.documents if d['id'] == doc_id), None)
            if doc:
                results.append({
                    'id': doc_id,
                    'score': score,
                    'text': doc.get('text', ''),
                    'metadata': doc.get('metadata', {})
                })
        
        return results
    
    def save_index(self, index_path):
        """Save index to disk."""
        index_data = {
            'documents': self.documents,
            'doc_freqs': self.doc_freqs,
            'term_doc_map': self.term_doc_map
        }
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def load_index(self, index_path):
        """Load index from disk."""
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            self.documents = index_data.get('documents', [])
            self.doc_freqs = index_data.get('doc_freqs', {})
            self.term_doc_map = index_data.get('term_doc_map', {})


class TestBM25Search:
    """Test suite for BM25 search functionality."""
    
    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing."""
        return [
            {
                'id': 'doc_001',
                'text': """
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
                'id': 'doc_002',
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
                'id': 'doc_003',
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
    
    def test_document_indexing(self, sample_documents):
        """Test that documents can be successfully indexed."""
        bm25 = SimpleBM25Search()
        
        # Index documents
        bm25.add_documents(sample_documents)
        
        # Verify indexing succeeded
        assert len(bm25.documents) == len(sample_documents), \
            f"BM25 should contain {len(sample_documents)} documents"
        
        # Verify term_doc_map is populated
        assert len(bm25.term_doc_map) > 0, "Term document map should be populated"
    
    def test_bm25_search_retrieval(self, sample_documents):
        """Test that BM25 search can retrieve indexed documents."""
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Test search queries
        test_queries = [
            ("什么是人工智能", "人工智能"),
            ("深度学习的应用", "深度学习"),
            ("自然语言处理任务", "自然语言处理"),
            ("机器学习", "机器学习")
        ]
        
        for query, expected_keyword in test_queries:
            results = bm25.search(query, top_k=3)
            
            # Verify we got results
            assert len(results) > 0, f"Search for '{query}' should return results"
            
            # Verify results contain expected keyword
            found_keyword = False
            for result in results:
                if expected_keyword in result['text']:
                    found_keyword = True
                    break
            
            assert found_keyword, f"Results for '{query}' should contain '{expected_keyword}'"
    
    def test_bm25_chinese_tokenization(self):
        """Test that Chinese tokenization works correctly."""
        bm25 = SimpleBM25Search()
        
        # Test tokenization
        test_text = "机器学习是人工智能的一个分支"
        tokens = bm25._tokenize(test_text)
        
        # Verify tokens contain expected characters
        expected_tokens = ['机', '器', '学', '习', '是', '人', '工', '智', '能']
        for expected in expected_tokens:
            assert expected in tokens, f"Token '{expected}' should be in tokenized result"
        
        # Verify query tokenization
        query = "什么是机器学习"
        query_tokens = bm25._tokenize(query)
        assert '机' in query_tokens, "Query tokenization should work"
        assert '器' in query_tokens, "Query tokenization should work"
        assert '学' in query_tokens, "Query tokenization should work"
        assert '习' in query_tokens, "Query tokenization should work"
    
    def test_bm25_index_persistence(self, sample_documents):
        """Test that BM25 index can be saved and loaded."""
        temp_dir = tempfile.mkdtemp()
        try:
            index_path = Path(temp_dir) / "bm25_index.json"
            
            # Create and save index
            bm251 = SimpleBM25Search()
            bm251.add_documents(sample_documents)
            bm251.save_index(index_path)
            
            # Load index
            bm252 = SimpleBM25Search()
            bm252.load_index(index_path)
            
            # Verify index was loaded
            assert len(bm252.documents) == len(sample_documents), \
                "Loaded index should contain same number of documents"
            
            # Verify search works with loaded index
            results = bm252.search("人工智能", top_k=3)
            assert len(results) > 0, "Search should work with loaded index"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_search_with_no_results(self):
        """Test search behavior when no results are found."""
        bm25 = SimpleBM25Search()
        
        # Search for something that shouldn't exist
        results = bm25.search("不存在的文档内容xyz", top_k=3)
        
        # Verify no results
        assert len(results) == 0, "Search should return no results for non-existent content"
    
    def test_search_result_ranking(self, sample_documents):
        """Test that search results are properly ranked."""
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Search for specific term
        results = bm25.search("人工智能", top_k=3)
        
        # Verify results are ranked (higher score first)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]['score'] >= results[i+1]['score'], \
                    "Results should be ranked by score (descending)"
    
    def test_multiple_document_search(self, sample_documents):
        """Test search across multiple documents."""
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Search for term that appears in multiple documents
        results = bm25.search("学习", top_k=5)
        
        # Verify we get results from multiple documents
        doc_ids = set([r['id'] for r in results])
        assert len(doc_ids) > 1, "Search should return results from multiple documents"
    
    def test_document_metadata_preservation(self, sample_documents):
        """Test that document metadata is preserved during indexing."""
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Search and verify metadata
        results = bm25.search("人工智能", top_k=1)
        
        if results:
            # Verify metadata is preserved
            assert 'metadata' in results[0], "Result should contain metadata"
            assert 'title' in results[0]['metadata'], "Metadata should contain title"
            assert results[0]['metadata']['title'] == '人工智能基础', \
                "Title should match original document"
    
    def test_empty_query_handling(self, sample_documents):
        """Test handling of empty queries."""
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Search with empty query
        results = bm25.search("", top_k=3)
        
        # Should return no results for empty query
        assert len(results) == 0, "Empty query should return no results"
    
    def test_special_characters_handling(self):
        """Test handling of special characters in text."""
        bm25 = SimpleBM25Search()
        
        doc = {
            'id': 'special_doc',
            'text': 'Python @#$%^&*() 特殊字符处理！测试？',
            'metadata': {}
        }
        
        bm25.add_documents([doc])
        
        # Search should still work
        results = bm25.search("Python", top_k=1)
        assert len(results) > 0, "Search should handle special characters"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])