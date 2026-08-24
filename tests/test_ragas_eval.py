"""RAGAS evaluation tests for RAG KB system."""

import pytest
from typing import List, Dict, Any
from rag_kb.models import SearchResult, Document, Chunk
from rag_kb.retrieval.bm25_search import BM25Search


class RAGASEvaluator:
    """RAGAS evaluation framework for RAG systems."""
    
    def __init__(self):
        """Initialize RAGAS evaluator."""
        self.evaluation_results = []
    
    def evaluate_retrieval(self, query: str, retrieved_results: List[SearchResult], 
                          ground_truth: List[str]) -> Dict[str, float]:
        """Evaluate retrieval performance using RAGAS metrics.
        
        Args:
            query: Search query
            retrieved_results: Retrieved search results
            ground_truth: List of relevant document IDs
            
        Returns:
            Dictionary with evaluation metrics
        """
        if not retrieved_results:
            return {
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0,
                'mrr': 0.0,
                'hit_rate': 0.0
            }
        
        # Calculate Precision@k
        retrieved_ids = [result.doc_id for result in retrieved_results]
        relevant_retrieved = [doc_id for doc_id in retrieved_ids if doc_id in ground_truth]
        
        precision = len(relevant_retrieved) / len(retrieved_ids) if retrieved_ids else 0.0
        
        # Calculate Recall@k
        recall = len(relevant_retrieved) / len(ground_truth) if ground_truth else 0.0
        
        # Calculate F1 score
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Calculate Mean Reciprocal Rank (MRR)
        mrr = 0.0
        for i, result in enumerate(retrieved_results):
            if result.doc_id in ground_truth:
                mrr = 1.0 / (i + 1)
                break
        
        # Calculate Hit Rate
        hit_rate = 1.0 if any(result.doc_id in ground_truth for result in retrieved_results) else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'mrr': mrr,
            'hit_rate': hit_rate
        }
    
    def evaluate_context_relevance(self, query: str, contexts: List[str], 
                                  answer: str) -> Dict[str, float]:
        """Evaluate context relevance (simplified version).
        
        Args:
            query: Original query
            contexts: Retrieved contexts
            answer: Generated answer
            
        Returns:
            Dictionary with context relevance metrics
        """
        if not contexts:
            return {'context_relevance': 0.0, 'context_utilization': 0.0}
        
        # Simplified context relevance: check if query terms appear in contexts
        query_terms = set(query.lower().split())
        context_relevance_scores = []
        
        for context in contexts:
            context_lower = context.lower()
            matched_terms = sum(1 for term in query_terms if term in context_lower)
            relevance = matched_terms / len(query_terms) if query_terms else 0.0
            context_relevance_scores.append(relevance)
        
        avg_context_relevance = sum(context_relevance_scores) / len(context_relevance_scores)
        
        # Context utilization: how much of the context is used in the answer
        answer_lower = answer.lower()
        context_utilization = 0.0
        for context in contexts:
            context_lower = context.lower()
            overlap = len(set(context_lower.split()) & set(answer_lower.split()))
            context_utilization = max(context_utilization, overlap / len(context_lower.split()) if context_lower.split() else 0.0)
        
        return {
            'context_relevance': avg_context_relevance,
            'context_utilization': context_utilization
        }
    
    def evaluate_answer_relevance(self, query: str, answer: str) -> Dict[str, float]:
        """Evaluate answer relevance (simplified version).
        
        Args:
            query: Original query
            answer: Generated answer
            
        Returns:
            Dictionary with answer relevance metrics
        """
        if not answer:
            return {'answer_relevance': 0.0, 'answer_completeness': 0.0}
        
        # Simplified answer relevance: check if query terms appear in answer
        query_terms = set(query.lower().split())
        answer_lower = answer.lower()
        
        matched_terms = sum(1 for term in query_terms if term in answer_lower)
        answer_relevance = matched_terms / len(query_terms) if query_terms else 0.0
        
        # Answer completeness: check if answer is substantial
        answer_completeness = min(len(answer.split()) / 20.0, 1.0)  # Assume 20 words is a complete answer
        
        return {
            'answer_relevance': answer_relevance,
            'answer_completeness': answer_completeness
        }
    
    def evaluate_faithfulness(self, contexts: List[str], answer: str) -> Dict[str, float]:
        """Evaluate faithfulness (answer groundedness in contexts).
        
        Args:
            contexts: Retrieved contexts
            answer: Generated answer
            
        Returns:
            Dictionary with faithfulness metrics
        """
        if not contexts or not answer:
            return {'faithfulness': 0.0, 'groundedness': 0.0}
        
        # Simplified faithfulness: check if answer statements are supported by contexts
        answer_sentences = answer.split('.')
        grounded_statements = 0
        
        for sentence in answer_sentences:
            sentence_lower = sentence.lower().strip()
            if not sentence_lower:
                continue
            
            # Check if key terms in the sentence appear in contexts
            sentence_terms = set(sentence_lower.split())
            for context in contexts:
                context_lower = context.lower()
                if len(sentence_terms & set(context_lower.split())) >= len(sentence_terms) * 0.5:
                    grounded_statements += 1
                    break
        
        faithfulness = grounded_statements / len(answer_sentences) if answer_sentences else 0.0
        
        # Groundedness: similar metric but more strict
        groundedness = faithfulness * 0.9  # Slightly more conservative
        
        return {
            'faithfulness': faithfulness,
            'groundedness': groundedness
        }
    
    def comprehensive_evaluation(self, query: str, retrieved_results: List[SearchResult],
                                 contexts: List[str], answer: str, 
                                 ground_truth: List[str] = None) -> Dict[str, Any]:
        """Perform comprehensive RAGAS evaluation.
        
        Args:
            query: Search query
            retrieved_results: Retrieved search results
            contexts: Retrieved contexts
            answer: Generated answer
            ground_truth: Optional ground truth document IDs
            
        Returns:
            Dictionary with all evaluation metrics
        """
        evaluation = {
            'query': query,
            'retrieval_metrics': {},
            'context_metrics': {},
            'answer_metrics': {},
            'faithfulness_metrics': {},
            'overall_score': 0.0
        }
        
        # Retrieval metrics
        if ground_truth:
            evaluation['retrieval_metrics'] = self.evaluate_retrieval(query, retrieved_results, ground_truth)
        
        # Context relevance
        evaluation['context_metrics'] = self.evaluate_context_relevance(query, contexts, answer)
        
        # Answer relevance
        evaluation['answer_metrics'] = self.evaluate_answer_relevance(query, answer)
        
        # Faithfulness
        evaluation['faithfulness_metrics'] = self.evaluate_faithfulness(contexts, answer)
        
        # Calculate overall score (weighted average)
        weights = {
            'precision': 0.2,
            'recall': 0.2,
            'context_relevance': 0.15,
            'answer_relevance': 0.2,
            'faithfulness': 0.25
        }
        
        overall_score = 0.0
        if ground_truth:
            overall_score += weights['precision'] * evaluation['retrieval_metrics']['precision']
            overall_score += weights['recall'] * evaluation['retrieval_metrics']['recall']
            overall_score += weights['context_relevance'] * evaluation['context_metrics']['context_relevance']
            overall_score += weights['answer_relevance'] * evaluation['answer_metrics']['answer_relevance']
            overall_score += weights['faithfulness'] * evaluation['faithfulness_metrics']['faithfulness']
        else:
            # If no ground truth, redistribute weights
            adjusted_weights = {k: v / (1 - weights['precision'] - weights['recall']) 
                              for k, v in weights.items() if k not in ['precision', 'recall']}
            for metric, weight in adjusted_weights.items():
                if metric == 'context_relevance':
                    overall_score += weight * evaluation['context_metrics']['context_relevance']
                elif metric == 'answer_relevance':
                    overall_score += weight * evaluation['answer_metrics']['answer_relevance']
                elif metric == 'faithfulness':
                    overall_score += weight * evaluation['faithfulness_metrics']['faithfulness']
        
        evaluation['overall_score'] = overall_score
        self.evaluation_results.append(evaluation)
        
        return evaluation
    
    def get_average_metrics(self) -> Dict[str, float]:
        """Get average metrics across all evaluations.
        
        Returns:
            Dictionary with average metrics
        """
        if not self.evaluation_results:
            return {}
        
        avg_metrics = {}
        
        # Collect all metric keys
        all_keys = set()
        for result in self.evaluation_results:
            for category in ['retrieval_metrics', 'context_metrics', 'answer_metrics', 'faithfulness_metrics']:
                all_keys.update(result[category].keys())
        
        # Calculate averages
        for key in all_keys:
            values = []
            for result in self.evaluation_results:
                for category in ['retrieval_metrics', 'context_metrics', 'answer_metrics', 'faithfulness_metrics']:
                    if key in result[category]:
                        values.append(result[category][key])
            
            if values:
                avg_metrics[key] = sum(values) / len(values)
        
        # Average overall score
        overall_scores = [result['overall_score'] for result in self.evaluation_results]
        avg_metrics['overall_score'] = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        
        return avg_metrics


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        Document(
            doc_id="doc1",
            title="Machine Learning Basics",
            content="Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.",
            metadata={"category": "AI", "source": "test1.pdf"}
        ),
        Document(
            doc_id="doc2", 
            title="Deep Learning Introduction",
            content="Deep learning is a subset of machine learning that uses neural networks with multiple layers.",
            metadata={"category": "AI", "source": "test2.pdf"}
        ),
        Document(
            doc_id="doc3",
            title="Natural Language Processing",
            content="NLP is a branch of AI that helps computers understand, interpret and manipulate human language.",
            metadata={"category": "NLP", "source": "test3.pdf"}
        )
    ]


@pytest.fixture
def bm25_engine():
    """Create BM25 search engine for testing."""
    engine = BM25Search()
    return engine


@pytest.fixture
def ragas_evaluator():
    """Create RAGAS evaluator for testing."""
    return RAGASEvaluator()


@pytest.fixture
def sample_search_results():
    """Create sample search results for testing."""
    return [
        SearchResult(chunk_id="c1", doc_id="doc1", text="Machine learning content", score=0.9, rank=1),
        SearchResult(chunk_id="c2", doc_id="doc2", text="Deep learning content", score=0.8, rank=2),
        SearchResult(chunk_id="c3", doc_id="doc3", text="NLP content", score=0.7, rank=3)
    ]


def test_retrieval_evaluation(ragas_evaluator, sample_search_results):
    """Test retrieval evaluation metrics."""
    # Ground truth
    ground_truth = ["doc1", "doc2"]
    
    # Evaluate
    metrics = ragas_evaluator.evaluate_retrieval("machine learning", sample_search_results, ground_truth)
    
    # Assertions
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1' in metrics
    assert 'mrr' in metrics
    assert 'hit_rate' in metrics
    assert 0 <= metrics['precision'] <= 1
    assert 0 <= metrics['recall'] <= 1


def test_context_relevance_evaluation(ragas_evaluator):
    """Test context relevance evaluation."""
    query = "machine learning basics"
    contexts = [
        "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.",
        "Deep learning uses neural networks with multiple layers for learning."
    ]
    answer = "Machine learning is about building systems that learn from data using algorithms."
    
    metrics = ragas_evaluator.evaluate_context_relevance(query, contexts, answer)
    
    assert 'context_relevance' in metrics
    assert 'context_utilization' in metrics
    assert 0 <= metrics['context_relevance'] <= 1
    assert 0 <= metrics['context_utilization'] <= 1


def test_answer_relevance_evaluation(ragas_evaluator):
    """Test answer relevance evaluation."""
    query = "What is machine learning?"
    answer = "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data."
    
    metrics = ragas_evaluator.evaluate_answer_relevance(query, answer)
    
    assert 'answer_relevance' in metrics
    assert 'answer_completeness' in metrics
    assert 0 <= metrics['answer_relevance'] <= 1
    assert 0 <= metrics['answer_completeness'] <= 1


def test_faithfulness_evaluation(ragas_evaluator):
    """Test faithfulness evaluation."""
    contexts = [
        "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.",
        "Deep learning uses neural networks with multiple layers."
    ]
    answer = "Machine learning focuses on building systems that learn from data using algorithms and neural networks."
    
    metrics = ragas_evaluator.evaluate_faithfulness(contexts, answer)
    
    assert 'faithfulness' in metrics
    assert 'groundedness' in metrics
    assert 0 <= metrics['faithfulness'] <= 1
    assert 0 <= metrics['groundedness'] <= 1


def test_comprehensive_evaluation(ragas_evaluator, sample_search_results):
    """Test comprehensive RAGAS evaluation."""
    query = "What is machine learning?"
    contexts = ["Machine learning is about systems that learn from data."]
    answer = "Machine learning focuses on building systems that learn from data."
    ground_truth = ["doc1"]
    
    evaluation = ragas_evaluator.comprehensive_evaluation(
        query, sample_search_results[:2], contexts, answer, ground_truth
    )
    
    assert 'query' in evaluation
    assert 'retrieval_metrics' in evaluation
    assert 'context_metrics' in evaluation
    assert 'answer_metrics' in evaluation
    assert 'faithfulness_metrics' in evaluation
    assert 'overall_score' in evaluation
    assert 0 <= evaluation['overall_score'] <= 1


def test_average_metrics(ragas_evaluator):
    """Test average metrics calculation."""
    # Run multiple evaluations
    for i in range(3):
        query = f"Test query {i}"
        search_results = [
            SearchResult(chunk_id=f"c{i}", doc_id=f"doc{i}", text="content", score=0.9, rank=1)
        ]
        contexts = ["Test context"]
        answer = "Test answer"
        ground_truth = [f"doc{i}"]
        
        ragas_evaluator.comprehensive_evaluation(
            query, search_results, contexts, answer, ground_truth
        )
    
    avg_metrics = ragas_evaluator.get_average_metrics()
    
    assert isinstance(avg_metrics, dict)
    assert 'overall_score' in avg_metrics


def test_bm25_integration(bm25_engine, sample_documents):
    """Test BM25 integration with evaluation."""
    # Convert documents to BM25 format
    bm25_docs = [
        {'id': doc.doc_id, 'text': doc.content, 'metadata': doc.metadata}
        for doc in sample_documents
    ]
    
    # Add documents to BM25 index
    bm25_engine.add_documents(bm25_docs)
    
    # Search
    results = bm25_engine.search("machine learning", top_k=2)
    
    assert len(results) > 0
    assert all('score' in result for result in results)
    
    # Test with evaluation
    search_results = [
        SearchResult(chunk_id=result['id'], doc_id=result['id'], text=result['text'], 
                   score=result['score'], rank=i+1)
        for i, result in enumerate(results)
    ]
    
    ground_truth = ["doc1", "doc2"]
    evaluator = RAGASEvaluator()
    metrics = evaluator.evaluate_retrieval("machine learning", search_results, ground_truth)
    
    assert 'precision' in metrics
    assert 'recall' in metrics