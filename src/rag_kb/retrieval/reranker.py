"""BGE-Reranker integration for improved retrieval precision."""

import asyncio
from typing import List, Dict, Any, Optional
import torch
from sentence_transformers import CrossEncoder

from rag_kb.retrieval.hybrid_search import SearchResult


class BGEReranker:
    """BGE-Reranker for cross-encoder based reranking."""
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """Initialize BGE-Reranker.
        
        Args:
            model_name: Model name for BGE-Reranker
                       Options: 'BAAI/bge-reranker-base', 'BAAI/bge-reranker-large'
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialized = False
    
    async def initialize(self):
        """Initialize the reranker model."""
        if self._initialized:
            return
        
        try:
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None,
                lambda: CrossEncoder(self.model_name, device=self.device)
            )
            self._initialized = True
            print(f"BGE-Reranker loaded: {self.model_name} on {self.device}", flush=True)
        except Exception as e:
            print(f"Failed to load BGE-Reranker: {e}", flush=True)
            print("Falling back to rule-based reranking", flush=True)
    
    async def rerank(
        self, 
        query: str, 
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Rerank search results using BGE-Reranker.
        
        Args:
            query: Original search query
            results: Search results to rerank
            top_k: Number of top results to return
            
        Returns:
            Reranked search results
        """
        if not self._initialized or not self.model:
            # Fallback to rule-based reranking
            return self._rule_based_rerank(query, results, top_k)
        
        if not results:
            return results
        
        try:
            # Prepare query-document pairs
            query_doc_pairs = [
                (query, result.content)
                for result in results
            ]
            
            # Run reranking in thread pool
            loop = asyncio.get_event_loop()
            scores = await loop.run_in_executor(
                None,
                lambda: self.model.predict(query_doc_pairs)
            )
            
            # Update scores and sort
            for i, result in enumerate(results):
                result.score = float(scores[i])
            
            # Sort by new scores
            reranked = sorted(results, key=lambda x: x.score, reverse=True)
            
            if top_k:
                reranked = reranked[:top_k]
            
            return reranked
            
        except Exception as e:
            print(f"Reranking error: {e}", flush=True)
            return self._rule_based_rerank(query, results, top_k)
    
    def _rule_based_rerank(
        self, 
        query: str, 
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Fallback rule-based reranking."""
        # Simple keyword matching score
        query_terms = set(query.lower().split())
        
        for result in results:
            content_lower = result.content.lower()
            matched_terms = sum(1 for term in query_terms if term in content_lower)
            result.score = matched_terms / len(query_terms) if query_terms else 0
        
        # Sort by score
        reranked = sorted(results, key=lambda x: x.score, reverse=True)
        
        if top_k:
            reranked = reranked[:top_k]
        
        return reranked


class RuleBasedReranker:
    """Rule-based reranker as fallback when model is not available."""
    
    def __init__(self):
        """Initialize rule-based reranker."""
        self._initialized = True
    
    async def initialize(self):
        """No initialization needed."""
        pass
    
    async def rerank(
        self, 
        query: str, 
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Rule-based reranking using keyword matching and heuristics."""
        if not results:
            return results
        
        query_terms = set(query.lower().split())
        
        for result in results:
            content_lower = result.content.lower()
            
            # Exact phrase match bonus
            exact_match_bonus = 2.0 if query.lower() in content_lower else 0
            
            # Term frequency score
            matched_terms = sum(1 for term in query_terms if term in content_lower)
            term_score = matched_terms / len(query_terms) if query_terms else 0
            
            # Position score (earlier in document is better)
            first_occurrence = content_lower.find(query.lower())
            position_score = 1.0 if first_occurrence == 0 else 0.5 if first_occurrence < 100 else 0.2
            
            # Combined score
            result.score = (
                term_score * 0.5 + 
                position_score * 0.3 + 
                exact_match_bonus * 0.2
            )
        
        # Sort by score
        reranked = sorted(results, key=lambda x: x.score, reverse=True)
        
        if top_k:
            reranked = reranked[:top_k]
        
        return reranked


class RerankerFactory:
    """Factory for creating rerankers based on availability."""
    
    @staticmethod
    def create_reranker(use_bge: bool = True, model_name: str = "BAAI/bge-reranker-base"):
        """Create appropriate reranker based on configuration.
        
        Args:
            use_bge: Whether to use BGE-Reranker
            model_name: Model name for BGE-Reranker
            
        Returns:
            Reranker instance
        """
        if use_bge:
            try:
                return BGEReranker(model_name)
            except Exception as e:
                print(f"Could not create BGE-Reranker: {e}", flush=True)
                print("Using rule-based reranker instead", flush=True)
                return RuleBasedReranker()
        else:
            return RuleBasedReranker()