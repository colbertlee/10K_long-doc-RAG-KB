"""Tests for RAG evaluation metrics."""

from typing import List
from rag_kb.models import SearchResult


def simple_faithfulness(answer: str, contexts: List[SearchResult]) -> float:
    """Calculate simplified faithfulness metric.
    
    Args:
        answer: Generated answer text
        contexts: List of search result contexts
        
    Returns:
        Faithfulness score (ratio of answer words present in contexts)
    """
    answer_words = set(answer.lower().split())
    context_words = set(' '.join(c.text.lower() for c in contexts).split())
    
    if not answer_words:
        return 0.0
    
    return len(answer_words & context_words) / len(answer_words)


def test_simple_faithfulness():
    """Test the simplified faithfulness metric."""
    answer = "The product has excellent features and good performance"
    contexts = [
        SearchResult(
            chunk_id="c1",
            doc_id="d1", 
            text="The product has excellent features",
            score=0.9,
            rank=1
        ),
        SearchResult(
            chunk_id="c2",
            doc_id="d1",
            text="It shows good performance in tests",
            score=0.8,
            rank=2
        )
    ]
    
    score = simple_faithfulness(answer, contexts)
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Should have decent overlap


def test_simple_faithfulness_empty_answer():
    """Test faithfulness with empty answer."""
    answer = ""
    contexts = [SearchResult(chunk_id="c1", doc_id="d1", text="Some context", score=0.9, rank=1)]
    
    score = simple_faithfulness(answer, contexts)
    assert score == 0.0


def test_simple_faithfulness_no_context():
    """Test faithfulness with no contexts."""
    answer = "Some answer"
    contexts = []
    
    score = simple_faithfulness(answer, contexts)
    assert score == 0.0