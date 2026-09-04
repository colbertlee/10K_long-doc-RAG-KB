"""RAGAS evaluation tests for RAG KB system."""

import pytest
import pytest_asyncio
import asyncio
import numpy as np
import json
from typing import List, Dict, Any
from rag_kb.models import SearchResult, Document, Chunk
from rag_kb.retrieval.bm25_search import BM25Search
from rag_kb.lightrag.embedding_funcs import ollama_embed
from src.rag_kb.evaluation.rag_judge import RAGExpertJudge, evaluate_rag_quality


class RAGASEvaluator:
    """RAGAS evaluation framework for RAG systems with enhanced semantic evaluation."""
    
    def __init__(self, use_semantic: bool = True):
        """Initialize RAGAS evaluator.
        
        Args:
            use_semantic: Whether to use semantic similarity evaluation (requires embeddings)
        """
        self.evaluation_results = []
        self.use_semantic = use_semantic
        self._embedding_cache = {}
    
    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text with caching.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        try:
            embedding = await ollama_embed.func([text])
            self._embedding_cache[text] = embedding[0]
            return embedding[0]
        except Exception as e:
            print(f"Embedding error: {e}")
            # Return zero vector as fallback
            return np.zeros(ollama_embed.embedding_dim, dtype=np.float32)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
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
    
    async def evaluate_context_relevance(self, query: str, contexts: List[str], 
                                  answer: str) -> Dict[str, float]:
        """Evaluate context relevance with semantic matching and consistency.
        
        Args:
            query: Original query
            contexts: Retrieved contexts
            answer: Generated answer
            
        Returns:
            Dictionary with context relevance metrics
        """
        if not contexts:
            return {'context_relevance': 0.0, 'context_utilization': 0.0, 'semantic_matching': 0.0, 'context_consistency': 0.0}
        
        # Traditional keyword-based context relevance
        query_terms = set(query.lower().split())
        context_relevance_scores = []
        
        for context in contexts:
            context_lower = context.lower()
            matched_terms = sum(1 for term in query_terms if term in context_lower)
            relevance = matched_terms / len(query_terms) if query_terms else 0.0
            context_relevance_scores.append(relevance)
        
        avg_context_relevance = sum(context_relevance_scores) / len(context_relevance_scores)
        
        # Enhanced semantic matching
        semantic_matching = 0.0
        if self.use_semantic:
            try:
                query_embedding = await self._get_embedding(query)
                semantic_similarities = []
                
                for context in contexts:
                    context_embedding = await self._get_embedding(context)
                    similarity = self._cosine_similarity(query_embedding, context_embedding)
                    semantic_similarities.append(similarity)
                
                semantic_matching = sum(semantic_similarities) / len(semantic_similarities) if semantic_similarities else 0.0
            except Exception as e:
                print(f"Semantic matching error: {e}")
                semantic_matching = 0.0
        
        # Context consistency: ensure contexts can answer the query
        context_consistency = self._evaluate_context_consistency(query, contexts)
        
        # Context utilization: how much of the context is used in the answer
        answer_lower = answer.lower()
        context_utilization = 0.0
        for context in contexts:
            context_lower = context.lower()
            overlap = len(set(context_lower.split()) & set(answer_lower.split()))
            context_utilization = max(context_utilization, overlap / len(context_lower.split()) if context_lower.split() else 0.0)
        
        # Combined context relevance score
        combined_relevance = 0.4 * avg_context_relevance + 0.3 * semantic_matching + 0.3 * context_consistency
        
        return {
            'context_relevance': combined_relevance,
            'context_utilization': context_utilization,
            'semantic_matching': semantic_matching,
            'context_consistency': context_consistency,
            'keyword_relevance': avg_context_relevance
        }
    
    def _evaluate_context_consistency(self, query: str, contexts: List[str]) -> float:
        """Evaluate if contexts can consistently answer the query.
        
        Args:
            query: Original query
            contexts: Retrieved contexts
            
        Returns:
            Context consistency score
        """
        if not contexts:
            return 0.0
        
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        consistency_scores = []
        for context in contexts:
            context_lower = context.lower()
            context_terms = set(context_lower.split())
            
            # Check if context contains substantial information related to query
            overlap = len(query_terms & context_terms)
            coverage = overlap / len(query_terms) if query_terms else 0.0
            
            # Check if context is substantial enough (not just matching keywords)
            if len(context_terms) > 5:  # Ensure context has meaningful content
                consistency_scores.append(coverage)
            else:
                consistency_scores.append(0.0)
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
    
    async def evaluate_business_adaptability(self, query: str, contexts: List[str], 
                                           answer: str, business_keywords: List[str] = None) -> Dict[str, float]:
        """Evaluate business adaptability of retrieved documents and answers.
        
        Args:
            query: Original query
            contexts: Retrieved contexts
            answer: Generated answer
            business_keywords: Optional list of business-specific keywords for domain relevance
            
        Returns:
            Dictionary with business adaptability metrics
        """
        if not contexts and not answer:
            return {'business_relevance': 0.0, 'domain_alignment': 0.0, 'practical_applicability': 0.0}
        
        # Default business keywords if none provided
        if business_keywords is None:
            business_keywords = ['business', 'enterprise', 'company', 'organization', 
                               'process', 'workflow', 'system', 'solution', 
                               'implementation', 'deployment', 'strategy']
        
        business_keywords_set = set(keyword.lower() for keyword in business_keywords)
        
        # Business relevance: presence of business-related terms
        business_relevance = 0.0
        
        # Check contexts for business relevance
        context_business_scores = []
        for context in contexts:
            context_lower = context.lower()
            context_terms = set(context_lower.split())
            business_overlap = len(context_terms & business_keywords_set)
            business_score = business_overlap / len(context_terms) if context_terms else 0.0
            context_business_scores.append(business_score)
        
        if context_business_scores:
            business_relevance = sum(context_business_scores) / len(context_business_scores)
        
        # Check answer for business relevance
        if answer:
            answer_lower = answer.lower()
            answer_terms = set(answer_lower.split())
            answer_business_overlap = len(answer_terms & business_keywords_set)
            answer_business_score = answer_business_overlap / len(answer_terms) if answer_terms else 0.0
            business_relevance = max(business_relevance, answer_business_score)
        
        # Domain alignment: semantic similarity with business domain
        domain_alignment = 0.0
        if self.use_semantic and contexts:
            try:
                # Create a business domain description
                business_domain_text = " ".join(business_keywords)
                domain_embedding = await self._get_embedding(business_domain_text)
                
                # Calculate average similarity with business domain
                domain_similarities = []
                for context in contexts:
                    context_embedding = await self._get_embedding(context)
                    similarity = self._cosine_similarity(domain_embedding, context_embedding)
                    domain_similarities.append(similarity)
                
                if domain_similarities:
                    domain_alignment = sum(domain_similarities) / len(domain_similarities)
            except Exception as e:
                print(f"Domain alignment error: {e}")
                domain_alignment = 0.0
        
        # Practical applicability: assess if content is actionable
        practical_applicability = self._evaluate_practical_applicability(query, contexts, answer)
        
        # Combined business adaptability score
        combined_score = 0.4 * business_relevance + 0.3 * domain_alignment + 0.3 * practical_applicability
        
        return {
            'business_relevance': combined_score,
            'domain_alignment': domain_alignment,
            'practical_applicability': practical_applicability,
            'keyword_business_relevance': business_relevance
        }
    
    def _evaluate_practical_applicability(self, query: str, contexts: List[str], answer: str) -> float:
        """Evaluate if the content is practically applicable to business scenarios.
        
        Args:
            query: Original query
            contexts: Retrieved contexts
            answer: Generated answer
            
        Returns:
            Practical applicability score
        """
        if not contexts and not answer:
            return 0.0
        
        # Keywords that indicate practical applicability
        practical_keywords = [
            'how', 'step', 'process', 'implement', 'deploy', 'use', 'apply',
            'method', 'approach', 'solution', 'guide', 'tutorial', 'example',
            'best practice', 'recommendation', 'action', 'execute'
        ]
        
        practical_keywords_set = set(keyword.lower() for keyword in practical_keywords)
        
        applicability_scores = []
        
        # Check contexts for practical content
        for context in contexts:
            context_lower = context.lower()
            context_terms = set(context_lower.split())
            practical_overlap = len(context_terms & practical_keywords_set)
            practical_score = min(practical_overlap / 5.0, 1.0)  # Normalize to max 1.0
            applicability_scores.append(practical_score)
        
        # Check answer for practical content
        if answer:
            answer_lower = answer.lower()
            answer_terms = set(answer_lower.split())
            answer_practical_overlap = len(answer_terms & practical_keywords_set)
            answer_practical_score = min(answer_practical_overlap / 3.0, 1.0)  # Lower threshold for answers
            applicability_scores.append(answer_practical_score)
        
        return sum(applicability_scores) / len(applicability_scores) if applicability_scores else 0.0
    
    async def evaluate_answer_relevance(self, query: str, answer: str) -> Dict[str, float]:
        """Evaluate answer relevance with semantic similarity.
        
        Args:
            query: Original query
            answer: Generated answer
            
        Returns:
            Dictionary with answer relevance metrics
        """
        if not answer:
            return {'answer_relevance': 0.0, 'answer_completeness': 0.0, 'semantic_relevance': 0.0}
        
        # Traditional keyword-based relevance
        query_terms = set(query.lower().split())
        answer_lower = answer.lower()
        
        matched_terms = sum(1 for term in query_terms if term in answer_lower)
        keyword_relevance = matched_terms / len(query_terms) if query_terms else 0.0
        
        # Answer completeness: check if answer is substantial
        answer_completeness = min(len(answer.split()) / 20.0, 1.0)  # Assume 20 words is a complete answer
        
        # Enhanced semantic relevance using embeddings
        semantic_relevance = 0.0
        if self.use_semantic:
            try:
                query_embedding = await self._get_embedding(query)
                answer_embedding = await self._get_embedding(answer)
                semantic_relevance = self._cosine_similarity(query_embedding, answer_embedding)
            except Exception as e:
                print(f"Semantic evaluation error: {e}")
                semantic_relevance = 0.0
        
        # Combined relevance score (weighted average)
        combined_relevance = 0.6 * keyword_relevance + 0.4 * semantic_relevance
        
        return {
            'answer_relevance': combined_relevance,
            'answer_completeness': answer_completeness,
            'semantic_relevance': semantic_relevance,
            'keyword_relevance': keyword_relevance
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
    
    async def comprehensive_evaluation(self, query: str, retrieved_results: List[SearchResult],
                                 contexts: List[str], answer: str, 
                                 ground_truth: List[str] = None,
                                 business_keywords: List[str] = None,
                                 use_expert_judge: bool = True) -> Dict[str, Any]:
        """Perform comprehensive RAGAS evaluation with enhanced metrics and expert judge.
        
        Args:
            query: Search query
            retrieved_results: Retrieved search results
            contexts: Retrieved contexts
            answer: Generated answer
            ground_truth: Optional ground truth document IDs
            business_keywords: Optional business-specific keywords for domain evaluation
            use_expert_judge: Whether to include expert judge evaluation
            
        Returns:
            Dictionary with all evaluation metrics
        """
        evaluation = {
            'query': query,
            'retrieval_metrics': {},
            'context_metrics': {},
            'answer_metrics': {},
            'faithfulness_metrics': {},
            'business_metrics': {},
            'expert_judge_metrics': {},
            'overall_score': 0.0
        }
        
        # Retrieval metrics (synchronous)
        if ground_truth:
            evaluation['retrieval_metrics'] = self.evaluate_retrieval(query, retrieved_results, ground_truth)
        
        # Enhanced context relevance (async)
        evaluation['context_metrics'] = await self.evaluate_context_relevance(query, contexts, answer)
        
        # Enhanced answer relevance (async)
        evaluation['answer_metrics'] = await self.evaluate_answer_relevance(query, answer)
        
        # Faithfulness (synchronous)
        evaluation['faithfulness_metrics'] = self.evaluate_faithfulness(contexts, answer)
        
        # Business adaptability (async)
        evaluation['business_metrics'] = await self.evaluate_business_adaptability(
            query, contexts, answer, business_keywords
        )
        
        # Expert judge evaluation (optional)
        if use_expert_judge:
            from src.rag_kb.evaluation.rag_judge import RAGExpertJudge
            judge = RAGExpertJudge(use_semantic=self.use_semantic)
            judge_evaluation = judge.evaluate(query, contexts, answer)
            
            evaluation['expert_judge_metrics'] = {
                'faithfulness_score': judge_evaluation.scores['faithfulness'],
                'answer_relevance_score': judge_evaluation.scores['answer_relevance'],
                'context_precision_score': judge_evaluation.scores['context_precision'],
                'judge_overall_score': judge_evaluation.scores['overall_score'],
                'faithfulness_reason': judge_evaluation.verdict['faithfulness_reason'],
                'relevance_reason': judge_evaluation.verdict['relevance_reason'],
                'context_reason': judge_evaluation.verdict['context_reason'],
                'optimization_suggestions': judge_evaluation.optimization_suggestions
            }
        
        # Calculate overall score (weighted average with enhanced metrics)
        weights = {
            'precision': 0.12,
            'recall': 0.12,
            'context_relevance': 0.18,
            'answer_relevance': 0.18,
            'faithfulness': 0.15,
            'business_relevance': 0.10,
            'expert_judge': 0.15
        }
        
        overall_score = 0.0
        if ground_truth:
            overall_score += weights['precision'] * evaluation['retrieval_metrics']['precision']
            overall_score += weights['recall'] * evaluation['retrieval_metrics']['recall']
            overall_score += weights['context_relevance'] * evaluation['context_metrics']['context_relevance']
            overall_score += weights['answer_relevance'] * evaluation['answer_metrics']['answer_relevance']
            overall_score += weights['faithfulness'] * evaluation['faithfulness_metrics']['faithfulness']
            overall_score += weights['business_relevance'] * evaluation['business_metrics']['business_relevance']
            
            if use_expert_judge and evaluation['expert_judge_metrics']:
                # Normalize expert judge score from 0-5 to 0-1
                judge_score_normalized = evaluation['expert_judge_metrics']['judge_overall_score'] / 5.0
                overall_score += weights['expert_judge'] * judge_score_normalized
        else:
            # If no ground truth, redistribute weights
            total_retrieval_weight = weights['precision'] + weights['recall']
            adjusted_weights = {k: v / (1 - total_retrieval_weight) 
                              for k, v in weights.items() if k not in ['precision', 'recall']}
            for metric, weight in adjusted_weights.items():
                if metric == 'context_relevance':
                    overall_score += weight * evaluation['context_metrics']['context_relevance']
                elif metric == 'answer_relevance':
                    overall_score += weight * evaluation['answer_metrics']['answer_relevance']
                elif metric == 'faithfulness':
                    overall_score += weight * evaluation['faithfulness_metrics']['faithfulness']
                elif metric == 'business_relevance':
                    overall_score += weight * evaluation['business_metrics']['business_relevance']
                elif metric == 'expert_judge' and use_expert_judge and evaluation['expert_judge_metrics']:
                    judge_score_normalized = evaluation['expert_judge_metrics']['judge_overall_score'] / 5.0
                    overall_score += weight * judge_score_normalized
        
        evaluation['overall_score'] = overall_score
        self.evaluation_results.append(evaluation)
        
        return evaluation
    
    def get_average_metrics(self) -> Dict[str, float]:
        """Get average metrics across all evaluations including enhanced and expert judge metrics.
        
        Returns:
            Dictionary with average metrics
        """
        if not self.evaluation_results:
            return {}
        
        avg_metrics = {}
        
        # Collect all metric keys from all categories including business_metrics and expert_judge_metrics
        all_keys = set()
        for result in self.evaluation_results:
            for category in ['retrieval_metrics', 'context_metrics', 'answer_metrics', 'faithfulness_metrics', 'business_metrics', 'expert_judge_metrics']:
                if category in result:
                    # For expert_judge_metrics, only include numeric scores
                    if category == 'expert_judge_metrics':
                        numeric_keys = [k for k in result[category].keys() if 'score' in k]
                        all_keys.update(numeric_keys)
                    else:
                        all_keys.update(result[category].keys())
        
        # Calculate averages
        for key in all_keys:
            values = []
            for result in self.evaluation_results:
                for category in ['retrieval_metrics', 'context_metrics', 'answer_metrics', 'faithfulness_metrics', 'business_metrics', 'expert_judge_metrics']:
                    if category in result and key in result[category]:
                        # Only include numeric values
                        if isinstance(result[category][key], (int, float)):
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
    """Create RAGAS evaluator for testing with semantic evaluation disabled by default for sync tests."""
    return RAGASEvaluator(use_semantic=False)

@pytest.fixture
def semantic_evaluator():
    """Create RAGAS evaluator with semantic evaluation enabled for async tests."""
    return RAGASEvaluator(use_semantic=True)


@pytest.fixture
def sample_search_results():
    """Create sample search results for testing."""
    return [
        SearchResult(chunk_id="c1", doc_id="doc1", text="Machine learning content", score=0.9, rank=1),
        SearchResult(chunk_id="c2", doc_id="doc2", text="Deep learning content", score=0.8, rank=2),
        SearchResult(chunk_id="c3", doc_id="doc3", text="NLP content", score=0.7, rank=3)
    ]


def test_retrieval_evaluation(ragas_evaluator, sample_search_results):
    """Test retrieval evaluation metrics (synchronous)."""
    # Ground truth
    ground_truth = ["doc1", "doc2"]
    
    # Evaluate (retrieval is still synchronous)
    metrics = ragas_evaluator.evaluate_retrieval("machine learning", sample_search_results, ground_truth)
    
    # Assertions
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1' in metrics
    assert 'mrr' in metrics
    assert 'hit_rate' in metrics
    assert 0 <= metrics['precision'] <= 1
    assert 0 <= metrics['recall'] <= 1


@pytest.mark.asyncio
async def test_context_relevance_evaluation(semantic_evaluator):
    """Test context relevance evaluation with enhanced metrics."""
    query = "machine learning basics"
    contexts = [
        "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.",
        "Deep learning uses neural networks with multiple layers for learning."
    ]
    answer = "Machine learning is about building systems that learn from data using algorithms."
    
    metrics = await semantic_evaluator.evaluate_context_relevance(query, contexts, answer)
    
    assert 'context_relevance' in metrics
    assert 'context_utilization' in metrics
    assert 'semantic_matching' in metrics
    assert 'context_consistency' in metrics
    assert 0 <= metrics['context_relevance'] <= 1
    assert 0 <= metrics['context_utilization'] <= 1
    assert 0 <= metrics['semantic_matching'] <= 1
    assert 0 <= metrics['context_consistency'] <= 1


@pytest.mark.asyncio
async def test_answer_relevance_evaluation(semantic_evaluator):
    """Test answer relevance evaluation with semantic similarity."""
    query = "What is machine learning?"
    answer = "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data."
    
    metrics = await semantic_evaluator.evaluate_answer_relevance(query, answer)
    
    assert 'answer_relevance' in metrics
    assert 'answer_completeness' in metrics
    assert 'semantic_relevance' in metrics
    assert 'keyword_relevance' in metrics
    assert 0 <= metrics['answer_relevance'] <= 1
    assert 0 <= metrics['answer_completeness'] <= 1
    assert 0 <= metrics['semantic_relevance'] <= 1


def test_faithfulness_evaluation(ragas_evaluator):
    """Test faithfulness evaluation (synchronous)."""
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


@pytest.mark.asyncio
async def test_comprehensive_evaluation(semantic_evaluator, sample_search_results):
    """Test comprehensive RAGAS evaluation with enhanced metrics and expert judge."""
    query = "What is machine learning?"
    contexts = ["Machine learning is about systems that learn from data."]
    answer = "Machine learning focuses on building systems that learn from data."
    ground_truth = ["doc1"]
    
    evaluation = await semantic_evaluator.comprehensive_evaluation(
        query, sample_search_results[:2], contexts, answer, ground_truth, use_expert_judge=True
    )
    
    assert 'query' in evaluation
    assert 'retrieval_metrics' in evaluation
    assert 'context_metrics' in evaluation
    assert 'answer_metrics' in evaluation
    assert 'faithfulness_metrics' in evaluation
    assert 'business_metrics' in evaluation
    assert 'expert_judge_metrics' in evaluation
    assert 'overall_score' in evaluation
    assert 0 <= evaluation['overall_score'] <= 1
    
    # Check that enhanced metrics are present
    assert 'semantic_matching' in evaluation['context_metrics']
    assert 'semantic_relevance' in evaluation['answer_metrics']
    assert 'business_relevance' in evaluation['business_metrics']
    
    # Check expert judge metrics
    assert 'faithfulness_score' in evaluation['expert_judge_metrics']
    assert 'answer_relevance_score' in evaluation['expert_judge_metrics']
    assert 'context_precision_score' in evaluation['expert_judge_metrics']
    assert 'judge_overall_score' in evaluation['expert_judge_metrics']
    assert 'faithfulness_reason' in evaluation['expert_judge_metrics']
    assert 'relevance_reason' in evaluation['expert_judge_metrics']
    assert 'context_reason' in evaluation['expert_judge_metrics']
    assert 'optimization_suggestions' in evaluation['expert_judge_metrics']


@pytest.mark.asyncio
async def test_business_adaptability_evaluation(semantic_evaluator):
    """Test business adaptability evaluation."""
    query = "How to implement machine learning in business?"
    contexts = [
        "Machine learning implementation requires a systematic approach with proper data governance and business process integration.",
        "Enterprise deployment needs careful consideration of scalability and business requirements."
    ]
    answer = "To implement machine learning in business, you need a systematic approach that integrates with existing business processes."
    business_keywords = ["business", "enterprise", "implementation", "deployment", "process"]
    
    metrics = await semantic_evaluator.evaluate_business_adaptability(
        query, contexts, answer, business_keywords
    )
    
    assert 'business_relevance' in metrics
    assert 'domain_alignment' in metrics
    assert 'practical_applicability' in metrics
    assert 0 <= metrics['business_relevance'] <= 1
    assert 0 <= metrics['domain_alignment'] <= 1
    assert 0 <= metrics['practical_applicability'] <= 1

@pytest.mark.asyncio
async def test_average_metrics(semantic_evaluator):
    """Test average metrics calculation with enhanced evaluation."""
    # Run multiple evaluations
    for i in range(3):
        query = f"Test query {i}"
        search_results = [
            SearchResult(chunk_id=f"c{i}", doc_id=f"doc{i}", text="content", score=0.9, rank=1)
        ]
        contexts = ["Test context"]
        answer = "Test answer"
        ground_truth = [f"doc{i}"]
        
        await semantic_evaluator.comprehensive_evaluation(
            query, search_results, contexts, answer, ground_truth
        )
    
    avg_metrics = semantic_evaluator.get_average_metrics()
    
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
    
    # Test with evaluation (synchronous retrieval metrics still work)
    search_results = [
        SearchResult(chunk_id=result['id'], doc_id=result['id'], text=result['text'], 
                   score=result['score'], rank=i+1)
        for i, result in enumerate(results)
    ]
    
    ground_truth = ["doc1", "doc2"]
    evaluator = RAGASEvaluator(use_semantic=False)  # Disable semantic for sync test
    metrics = evaluator.evaluate_retrieval("machine learning", search_results, ground_truth)
    
    assert 'precision' in metrics
    assert 'recall' in metrics

@pytest.mark.asyncio
async def test_semantic_similarity_evaluation(semantic_evaluator):
    """Test semantic similarity evaluation functionality."""
    query = "artificial intelligence and machine learning"
    similar_text = "AI and ML are related fields in computer science"
    different_text = "The weather is nice today"
    
    # Get semantic similarity for similar text
    query_embedding = await semantic_evaluator._get_embedding(query)
    similar_embedding = await semantic_evaluator._get_embedding(similar_text)
    different_embedding = await semantic_evaluator._get_embedding(different_text)
    
    similar_score = semantic_evaluator._cosine_similarity(query_embedding, similar_embedding)
    different_score = semantic_evaluator._cosine_similarity(query_embedding, different_embedding)
    
    # Similar text should have higher similarity
    assert similar_score > different_score
    assert 0 <= similar_score <= 1
    assert 0 <= different_score <= 1

def test_rag_expert_judge_initialization():
    """Test RAG expert judge initialization."""
    judge = RAGExpertJudge(use_semantic=False)
    assert judge is not None
    assert judge.use_semantic == False

def test_rag_expert_judge_faithfulness():
    """Test faithfulness evaluation."""
    judge = RAGExpertJudge(use_semantic=False)
    
    # Test case with good faithfulness - exact match
    contexts = ["机器学习是人工智能的一个分支。"]
    answer = "机器学习是人工智能的一个分支。"
    
    score, reason = judge._evaluate_faithfulness(contexts, answer)
    assert 0 <= score <= 5
    assert isinstance(reason, str)
    assert score >= 4  # Should be high faithfulness for exact match
    
    # Test case with partial faithfulness - similar but with extra words
    contexts = ["机器学习是人工智能的一个分支。"]
    answer = "机器学习确实是人工智能的一个分支。"
    
    score, reason = judge._evaluate_faithfulness(contexts, answer)
    assert 0 <= score <= 5
    # Should detect some partial grounding
    assert score >= 2  # Should have some faithfulness due to overlap
    
    # Test case with clear hallucination - completely different content
    contexts = ["机器学习是人工智能的一个分支。"]
    answer = "量子计算是利用量子力学原理进行计算的新型计算模式，可以解决传统计算机无法处理的问题。"
    
    score, reason = judge._evaluate_faithfulness(contexts, answer)
    assert 0 <= score <= 5
    # Should detect the hallucination since answer is completely different from context
    assert score <= 2  # Should be low faithfulness due to completely different content

def test_rag_expert_judge_answer_relevance():
    """Test answer relevance evaluation."""
    judge = RAGExpertJudge(use_semantic=False)
    
    # Test case with good relevance
    question = "什么是机器学习？"
    answer = "机器学习是人工智能的一个分支，让计算机能够从数据中学习。"
    
    score, reason = judge._evaluate_answer_relevance(question, answer)
    assert 0 <= score <= 5
    assert isinstance(reason, str)
    
    # Test case with poor relevance
    question = "什么是机器学习？"
    answer = "今天天气很好，适合出去散步。"
    
    score, reason = judge._evaluate_answer_relevance(question, answer)
    assert score <= 3
    assert "答非所问" in reason or "未解决" in reason

def test_rag_expert_judge_context_precision():
    """Test context precision evaluation."""
    judge = RAGExpertJudge(use_semantic=False)
    
    # Test case with good context precision
    question = "什么是机器学习？"
    contexts = ["机器学习是人工智能的一个分支，让计算机能够从数据中学习。"]
    
    score, reason = judge._evaluate_context_precision(question, contexts)
    assert 0 <= score <= 5
    assert isinstance(reason, str)
    
    # Test case with poor context precision
    question = "什么是机器学习？"
    contexts = ["今天天气很好，适合出去散步。", "我喜欢吃苹果。"]
    
    score, reason = judge._evaluate_context_precision(question, contexts)
    assert score <= 2
    assert "无关" in reason or "噪音" in reason

def test_rag_expert_judge_comprehensive():
    """Test comprehensive expert judge evaluation."""
    judge = RAGExpertJudge(use_semantic=False)
    
    question = "什么是机器学习？"
    contexts = ["机器学习是人工智能的一个分支，让计算机能够从数据中学习。"]
    answer = "机器学习是人工智能的一个分支，让计算机能够从数据中学习。"
    
    evaluation = judge.evaluate(question, contexts, answer)
    
    assert evaluation.scores["faithfulness"] >= 4  # Should be high faithfulness
    assert evaluation.scores["answer_relevance"] >= 4  # Should be high relevance
    assert evaluation.scores["context_precision"] >= 3  # Should be decent context precision
    assert 0 <= evaluation.scores["overall_score"] <= 5
    
    assert "faithfulness_reason" in evaluation.verdict
    assert "relevance_reason" in evaluation.verdict
    assert "context_reason" in evaluation.verdict
    
    assert isinstance(evaluation.optimization_suggestions, list)

def test_rag_expert_judge_json_output():
    """Test JSON output format."""
    question = "什么是机器学习？"
    contexts = ["机器学习是人工智能的一个分支。"]
    answer = "机器学习是人工智能的一个分支。"
    
    json_result = evaluate_rag_quality(question, contexts, answer, use_semantic=False)
    
    # Parse and validate JSON structure
    result_dict = json.loads(json_result)
    
    assert "scores" in result_dict
    assert "verdict" in result_dict
    assert "optimization_suggestions" in result_dict
    
    assert "faithfulness" in result_dict["scores"]
    assert "answer_relevance" in result_dict["scores"]
    assert "context_precision" in result_dict["scores"]
    assert "overall_score" in result_dict["scores"]
    
    assert "faithfulness_reason" in result_dict["verdict"]
    assert "relevance_reason" in result_dict["verdict"]
    assert "context_reason" in result_dict["verdict"]
    
    assert isinstance(result_dict["optimization_suggestions"], list)

def test_rag_expert_judge_edge_cases():
    """Test edge cases for expert judge evaluation."""
    judge = RAGExpertJudge(use_semantic=False)
    
    # Empty answer
    evaluation = judge.evaluate("测试问题", ["测试上下文"], "")
    assert evaluation.scores["faithfulness"] == 1.0  # Should handle gracefully
    
    # Empty contexts
    evaluation = judge.evaluate("测试问题", [], "测试回答")
    assert evaluation.scores["context_precision"] == 1.0  # Should handle gracefully
    
    # Empty question
    evaluation = judge.evaluate("", ["测试上下文"], "测试回答")
    assert evaluation.scores["answer_relevance"] == 1.0  # Should handle gracefully

def test_rag_expert_judge_optimization_suggestions():
    """Test optimization suggestions generation."""
    judge = RAGExpertJudge(use_semantic=False)
    
    # Poor performance case
    question = "什么是机器学习？"
    contexts = ["今天天气很好。"]
    answer = "我不太清楚，可能是关于计算机的。"
    
    evaluation = judge.evaluate(question, contexts, answer)
    
    # Should have suggestions for improvement
    assert len(evaluation.optimization_suggestions) > 0
    assert any("检索" in suggestion or "生成" in suggestion 
               for suggestion in evaluation.optimization_suggestions)
    
    # Excellent performance case
    question = "什么是机器学习？"
    contexts = ["机器学习是人工智能的一个分支。"]
    answer = "机器学习是人工智能的一个分支。"
    
    evaluation = judge.evaluate(question, contexts, answer)
    
    # Should have positive feedback
    assert len(evaluation.optimization_suggestions) > 0