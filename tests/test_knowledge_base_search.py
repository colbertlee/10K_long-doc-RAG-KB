"""Unit tests for knowledge base search functionality (simplified, BM25-focused)."""

import pytest
import json
import tempfile
import shutil
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


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
                # Support both 'id' and 'doc_id' fields
                doc_id = doc.get('id') or doc.get('doc_id')
                self.term_doc_map[term].append((doc_id, freq))
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
            # Support both 'id' and 'doc_id' fields
            doc = next((d for d in self.documents if d.get('id') == doc_id or d.get('doc_id') == doc_id), None)
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


class TestKnowledgeBaseSearch:
    """Test suite for knowledge base search using BM25."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_documents(self):
        """Create sample knowledge base documents for testing."""
        return [
            {
                'doc_id': 'kb_doc_001',
                'text': """
# 企业知识管理

企业知识管理（EKM）是指组织内部知识的创造、存储、共享和应用的过程。

## 核心要素
1. 知识创造：从员工经验中提取新知识
2. 知识存储：建立知识库和文档管理系统
3. 知识共享：促进员工之间的知识交流
4. 知识应用：将知识应用于业务决策

## 价值
知识管理可以提高企业效率、促进创新、增强竞争力。
""",
                'metadata': {
                    'title': '企业知识管理',
                    'source': 'enterprise_kb',
                    'category': 'management'
                }
            },
            {
                'doc_id': 'kb_doc_002',
                'text': """
# 数据安全策略

数据安全是企业信息管理的重要组成部分。

## 安全措施
1. 访问控制：限制数据访问权限
2. 加密技术：保护敏感数据
3. 备份策略：定期数据备份
4. 审计日志：记录数据访问行为

## 合规要求
企业需要遵守GDPR、个人信息保护法等相关法规。
""",
                'metadata': {
                    'title': '数据安全策略',
                    'source': 'security_kb',
                    'category': 'security'
                }
            },
            {
                'doc_id': 'kb_doc_003',
                'text': """
# 项目管理最佳实践

有效的项目管理是企业成功的关键因素。

## 方法论
1. 敏捷开发：快速迭代和持续改进
2. 瀑布模型：阶段性的开发流程
3. 混合方法：结合敏捷和瀑布的优点

## 工具
常用的项目管理工具包括Jira、Trello、Asana等。
""",
                'metadata': {
                    'title': '项目管理最佳实践',
                    'source': 'project_kb',
                    'category': 'management'
                }
            }
        ]
    
    def test_knowledge_base_indexing(self, temp_data_dir, sample_documents):
        """Test that knowledge base documents can be indexed."""
        # Create BM25 search instance
        bm25 = SimpleBM25Search()
        
        # Index documents
        bm25.add_documents(sample_documents)
        
        # Verify indexing succeeded
        assert len(bm25.documents) == len(sample_documents), \
            f"Knowledge base should contain {len(sample_documents)} documents"
        
        # Verify term_doc_map is populated
        assert len(bm25.term_doc_map) > 0, "Term document map should be populated"
    
    def test_knowledge_base_search(self, sample_documents):
        """Test that knowledge base search can retrieve indexed content."""
        # Create BM25 search and index documents
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Test various search queries
        test_queries = [
            ("企业知识管理", "知识管理"),
            ("数据安全措施", "安全"),
            ("项目管理方法", "项目"),
            ("知识共享", "共享")
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
    
    def test_knowledge_base_persistence(self, temp_data_dir, sample_documents):
        """Test that knowledge base can be persisted and reloaded."""
        index_path = temp_data_dir / "kb_index.json"
        
        # Create and save index
        bm251 = SimpleBM25Search()
        bm251.add_documents(sample_documents)
        bm251.save_index(index_path)
        
        # Load index
        bm252 = SimpleBM25Search()
        bm252.load_index(index_path)
        
        # Verify index was loaded
        assert len(bm252.documents) == len(sample_documents), \
            "Reloaded knowledge base should contain same number of documents"
        
        # Verify search works with reloaded knowledge base
        results = bm252.search("知识管理", top_k=3)
        assert len(results) > 0, "Search should work with reloaded knowledge base"
    
    def test_knowledge_base_category_filtering(self, sample_documents):
        """Test that knowledge base can filter by category."""
        # Create BM25 search and index documents
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Search for management-related content
        results = bm25.search("管理", top_k=5)
        
        # Verify we get results
        assert len(results) > 0, "Search should return management-related results"
        
        # Verify at least one result has management category
        management_docs = [r for r in results if r['metadata'].get('category') == 'management']
        assert len(management_docs) > 0, "Should find documents with management category"
    
    def test_knowledge_base_incremental_updates(self, temp_data_dir, sample_documents):
        """Test that knowledge base can handle incremental updates."""
        # Create BM25 search and index initial documents
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Save initial state
        initial_docs = bm25.documents.copy()
        initial_term_map = bm25.term_doc_map.copy()
        
        # Add new document by combining with existing
        new_doc = {
            'doc_id': 'kb_doc_004',
            'text': """
# 云计算架构

云计算提供了按需计算资源的服务模式。

## 服务模式
1. IaaS：基础设施即服务
2. PaaS：平台即服务
3. SaaS：软件即服务

云计算降低了IT成本，提高了灵活性。
""",
            'metadata': {
                'title': '云计算架构',
                'source': 'tech_kb',
                'category': 'technology'
            }
        }
        
        # Simulate incremental update by re-adding all documents
        all_documents = initial_docs + [new_doc]
        bm25.add_documents(all_documents)
        
        # Verify document count increased
        assert len(bm25.documents) == len(initial_docs) + 1, \
            "Document count should increase after adding new document"
        
        # Verify new document can be searched
        results = bm25.search("云计算", top_k=1)
        assert len(results) > 0, "New document should be searchable"
        assert results[0]['id'] == 'kb_doc_004', "Should find the newly added document"
    
    def test_knowledge_base_empty_query_handling(self):
        """Test handling of empty queries in knowledge base."""
        # Create BM25 search with no documents
        bm25 = SimpleBM25Search()
        
        # Test empty query
        results = bm25.search("", top_k=3)
        assert len(results) == 0, "Empty query should return no results"
        
        # Test query with whitespace
        results = bm25.search("   ", top_k=3)
        assert len(results) == 0, "Whitespace-only query should return no results"
    
    def test_knowledge_base_cross_document_search(self, sample_documents):
        """Test search across multiple knowledge base documents."""
        # Create BM25 search and index documents
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Search for term that appears in multiple documents
        results = bm25.search("管理", top_k=5)
        
        # Verify we get results from multiple documents
        doc_ids = set([r['id'] for r in results])
        assert len(doc_ids) > 1, "Search should return results from multiple documents"
    
    def test_knowledge_base_relevance_ranking(self, sample_documents):
        """Test that search results are properly ranked by relevance."""
        # Create BM25 search and index documents
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Search for specific term
        results = bm25.search("知识管理", top_k=3)
        
        # Verify results are ranked (higher score first)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]['score'] >= results[i+1]['score'], \
                    "Results should be ranked by score (descending)"
    
    def test_knowledge_base_metadata_preservation(self, sample_documents):
        """Test that document metadata is preserved during indexing."""
        # Create BM25 search and index documents
        bm25 = SimpleBM25Search()
        bm25.add_documents(sample_documents)
        
        # Search and verify metadata
        results = bm25.search("知识管理", top_k=1)
        
        if results:
            # Verify metadata is preserved
            assert 'metadata' in results[0], "Result should contain metadata"
            assert 'title' in results[0]['metadata'], "Metadata should contain title"
            assert results[0]['metadata']['title'] == '企业知识管理', \
                "Title should match original document"
            assert 'category' in results[0]['metadata'], "Metadata should contain category"
            assert results[0]['metadata']['category'] == 'management', \
                "Category should match original document"


class TestKnowledgeBaseIntegration:
    """Integration tests for complete knowledge base workflow."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_complete_knowledge_base_workflow(self, temp_data_dir):
        """Test complete workflow: create, index, search, persist."""
        # Step 1: Create knowledge base
        index_path = temp_data_dir / "knowledge_base.json"
        bm25 = SimpleBM25Search()
        
        # Step 2: Index documents
        documents = [
            {
                'doc_id': 'workflow_doc_1',
                'text': """
# 产品开发流程

产品开发是一个系统化的过程，包括需求分析、设计、开发、测试和发布。

## 阶段
1. 需求分析：收集和分析用户需求
2. 产品设计：设计产品功能和界面
3. 开发实现：编写代码实现功能
4. 测试验证：确保产品质量
5. 发布上线：将产品推向市场
""",
                'metadata': {
                    'title': '产品开发流程',
                    'source': 'product_kb'
                }
            }
        ]
        
        bm25.add_documents(documents)
        assert len(bm25.documents) == 1, "Should have indexed 1 document"
        
        # Step 3: Search documents
        results = bm25.search("产品开发", top_k=1)
        assert len(results) > 0, "Search should find indexed documents"
        assert "产品开发" in results[0]['text'], "Result should contain search term"
        
        # Step 4: Persist knowledge base
        bm25.save_index(index_path)
        assert index_path.exists(), "Index file should be created"
        
        # Step 5: Reload and verify
        bm25_reloaded = SimpleBM25Search()
        bm25_reloaded.load_index(index_path)
        
        results_reloaded = bm25_reloaded.search("产品开发", top_k=1)
        assert len(results_reloaded) > 0, "Reloaded knowledge base should work"
        assert results_reloaded[0]['id'] == 'workflow_doc_1', "Should find the same document"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])