"""Industrial-grade Cross-Encoder reranker for precision refinement."""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import torch
from sentence_transformers import CrossEncoder

from rag_kb.retrieval.hybrid_search import SearchResult


@dataclass
class RerankingConfig:
    """Configuration for reranking system."""
    model_name: str = "BAAI/bge-reranker-large"  # Top-tier reranker
    max_length: int = 512  # Context window size
    batch_size: int = 16  # Batch size for reranking
    device: str = "auto"  # Device selection
    enable_fallback: bool = True  # Enable rule-based fallback
    top_k: int = 10  # Default top-k results


@dataclass
class RerankingResult:
    """Result of reranking operation."""
    reranked_results: List[SearchResult]
    original_scores: List[float]
    reranked_scores: List[float]
    score_improvements: List[float]
    processing_time: float
    model_used: str
    fallback_used: bool


class IndustrialCrossEncoderReranker:
    """Industrial-grade Cross-Encoder reranker with advanced features."""
    
    # Recommended reranker models
    RECOMMENDED_MODELS = {
        'multilingual_large': 'BAAI/bge-reranker-large',  # Best overall performance
        'multilingual_base': 'BAAI/bge-reranker-base',   # Good performance, faster
        'multilingual_v2': 'BAAI/bge-reranker-v2-m3',  # Latest multilingual
        'chinese_large': 'BAAI/bge-reranker-large',  # Also excellent for Chinese
        'english_large': 'BAAI/bge-reranker-large',  # Optimized for English
    }
    
    def __init__(self, config: Optional[RerankingConfig] = None):
        """Initialize industrial Cross-Encoder reranker.
        
        Args:
            config: Reranking configuration
        """
        self.config = config or RerankingConfig()
        self.model = None
        self.device = self._determine_device()
        self._initialized = False
        
        # Performance tracking
        self.stats = {
            'total_rerankings': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'fallback_count': 0,
            'avg_score_improvement': 0.0
        }
    
    def _determine_device(self) -> str:
        """Determine the best available device."""
        if self.config.device != "auto":
            return self.config.device
        
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"  # Apple Silicon
        else:
            return "cpu"
    
    async def initialize(self):
        """Initialize the reranker model."""
        if self._initialized:
            return
        
        try:
            print(f"Loading Cross-Encoder reranker: {self.config.model_name}", flush=True)
            
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None,
                lambda: CrossEncoder(self.config.model_name, device=self.device)
            )
            
            self._initialized = True
            print(f"Cross-Encoder reranker loaded: {self.config.model_name} on {self.device}", flush=True)
            
        except Exception as e:
            print(f"Failed to load Cross-Encoder reranker: {e}", flush=True)
            if self.config.enable_fallback:
                print("Rule-based reranking will be used as fallback", flush=True)
            else:
                raise
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Rerank search results using Cross-Encoder with advanced features.
        
        Args:
            query: Original search query
            results: Search results to rerank
            top_k: Number of top results to return
            
        Returns:
            Reranked search results
        """
        start_time = asyncio.get_event_loop().time()
        
        if not results:
            return results
        
        # Use configured top_k if not provided
        if top_k is None:
            top_k = self.config.top_k
        
        # Store original scores
        original_scores = [result.score for result in results]
        
        # Try Cross-Encoder reranking
        if self._initialized and self.model:
            try:
                reranked_results = await self._cross_encoder_rerank(query, results, top_k)
                
                # Calculate score improvements
                reranked_scores = [result.score for result in reranked_results]
                score_improvements = [
                    reranked_scores[i] - original_scores[i] 
                    for i in range(min(len(reranked_scores), len(original_scores)))
                ]
                
                processing_time = asyncio.get_event_loop().time() - start_time
                
                # Update statistics
                self.stats['total_rerankings'] += 1
                self.stats['total_time'] += processing_time
                self.stats['avg_time'] = (
                    self.stats['total_time'] / self.stats['total_rerankings']
                    if self.stats['total_rerankings'] > 0 else 0.0
                )
                
                if score_improvements:
                    self.stats['avg_score_improvement'] = sum(score_improvements) / len(score_improvements)
                
                return reranked_results
                
            except Exception as e:
                print(f"Cross-Encoder reranking error: {e}", flush=True)
                if self.config.enable_fallback:
                    self.stats['fallback_count'] += 1
                    return await self._rule_based_rerank(query, results, top_k)
                else:
                    raise
        else:
            # Use rule-based reranking if model not initialized
            if self.config.enable_fallback:
                self.stats['fallback_count'] += 1
                return await self._rule_based_rerank(query, results, top_k)
            else:
                return results
    
    async def _cross_encoder_rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: int
    ) -> List[SearchResult]:
        """Perform Cross-Encoder reranking with batch processing.
        
        Args:
            query: Original search query
            results: Search results to rerank
            top_k: Number of results to return
            
        Returns:
            Reranked search results
        """
        # Prepare query-document pairs with intelligent truncation
        query_doc_pairs = []
        for result in results:
            # Smart truncation preserving query terms
            truncated_content = self._smart_truncate(result.content, query)
            query_doc_pairs.append([query, truncated_content])
        
        # Run reranking in batches
        loop = asyncio.get_event_loop()
        all_scores = []
        
        # Process in batches to handle large result sets
        for i in range(0, len(query_doc_pairs), self.config.batch_size):
            batch_pairs = query_doc_pairs[i:i + self.config.batch_size]
            batch_scores = await loop.run_in_executor(
                None,
                lambda: self.model.predict(batch_pairs)
            )
            all_scores.extend(batch_scores)
        
        # Update scores and sort
        for i, result in enumerate(results):
            if i < len(all_scores):
                result.score = float(all_scores[i])
                result.metadata = result.metadata or {}
                result.metadata['reranked'] = True
                result.metadata['reranker_model'] = self.config.model_name
                result.metadata['original_score'] = original_scores[i] if i < len(original_scores) else result.score
        
        # Sort by new scores
        reranked = sorted(results, key=lambda x: x.score, reverse=True)
        
        return reranked[:top_k]
    
    def _smart_truncate(self, content: str, query: str) -> str:
        """Intelligent content truncation preserving query-relevant parts.
        
        Args:
            content: Original content
            query: Query for relevance preservation
            
        Returns:
            Truncated content
        """
        # Extract query terms for relevance preservation
        query_terms = set(query.lower().split())
        
        # Calculate available tokens
        query_tokens = len(query.split())
        available_tokens = self.config.max_length - query_tokens - 30  # 30 token buffer
        
        if available_tokens <= 0:
            return content[:100]  # Minimal fallback
        
        # Conservative character estimate
        target_chars = available_tokens * 3  # 1 token ≈ 3 chars
        
        if len(content) <= target_chars:
            return content
        
        # Find query term positions for smart truncation
        term_positions = []
        for term in query_terms:
            term_lower = term.lower()
            start = 0
            while True:
                pos = content.lower().find(term_lower, start)
                if pos == -1:
                    break
                term_positions.append((pos, pos + len(term)))
                start = pos + len(term)
        
        if term_positions:
            # Try to include query terms in truncation
            # Find the range that includes most query terms
            min_pos = min(pos[0] for pos in term_positions)
            max_pos = max(pos[1] for pos in term_positions)
            
            # Extend range to include context around query terms
            context_size = (target_chars - (max_pos - min_pos)) // 2
            extended_min = max(0, min_pos - context_size)
            extended_max = min(len(content), max_pos + context_size)
            
            if extended_max - extended_min > target_chars:
                # If extended range is still too large, prioritize query terms
                return content[extended_min:extended_max]
            else:
                return content[extended_min:extended_max]
        
        # Fallback: truncate at sentence boundary
        truncated = content[:target_chars]
        sentence_endings = ['。', '！', '？', '.', '!', '?', '\n']
        
        for i in range(len(truncated) - 1, -1, -1):
            if truncated[i] in sentence_endings:
                return truncated[:i + 1]
        
        return truncated + "..."  # Add ellipsis if no sentence boundary found
    
    async def _rule_based_rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: int
    ) -> List[SearchResult]:
        """Enhanced rule-based reranking with multiple scoring factors.
        
        Args:
            query: Original search query
            results: Search results to rerank
            top_k: Number of results to return
            
        Returns:
            Reranked search results
        """
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
            
            # Term density score (terms close together is better)
            term_density = self._calculate_term_density(content_lower, query_terms)
            
            # Combined score with weighted factors
            result.score = (
                term_score * 0.4 +
                position_score * 0.2 +
                exact_match_bonus * 0.2 +
                term_density * 0.2
            )
            
            result.metadata = result.metadata or {}
            result.metadata['reranked'] = True
            result.metadata['reranker_method'] = 'rule_based'
        
        # Sort by score
        reranked = sorted(results, key=lambda x: x.score, reverse=True)
        
        return reranked[:top_k]
    
    def _calculate_term_density(self, content: str, query_terms: set) -> float:
        """Calculate term density (how close query terms are to each other).
        
        Args:
            content: Content to analyze
            query_terms: Query terms
            
        Returns:
            Term density score
        """
        if not query_terms:
            return 0.0
        
        # Find positions of all query terms
        term_positions = []
        for term in query_terms:
            start = 0
            while True:
                pos = content.find(term, start)
                if pos == -1:
                    break
                term_positions.append(pos)
                start = pos + len(term)
        
        if len(term_positions) < 2:
            return 0.0
        
        # Calculate average distance between consecutive terms
        distances = []
        for i in range(len(term_positions) - 1):
            distances.append(term_positions[i + 1] - term_positions[i])
        
        if not distances:
            return 0.0
        
        avg_distance = sum(distances) / len(distances)
        
        # Convert distance to density score (closer = higher density)
        max_distance = len(content)
        density_score = 1.0 - (avg_distance / max_distance)
        
        return density_score
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get reranking performance statistics.
        
        Returns:
            Performance statistics dictionary
        """
        return {
            'total_rerankings': self.stats['total_rerankings'],
            'total_time': self.stats['total_time'],
            'avg_time': self.stats['avg_time'],
            'fallback_count': self.stats['fallback_count'],
            'fallback_rate': (
                self.stats['fallback_count'] / self.stats['total_rerankings']
                if self.stats['total_rerankings'] > 0 else 0.0
            ),
            'avg_score_improvement': self.stats['avg_score_improvement'],
            'model_used': self.config.model_name if self._initialized else 'not_initialized',
            'device': self.device
        }


# Legacy BGEReranker class for backward compatibility
class BGEReranker(IndustrialCrossEncoderReranker):
    """Legacy BGE-Reranker class for backward compatibility."""
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-base", max_length: int = 512):
        """Initialize legacy BGE-Reranker."""
        config = RerankingConfig(
            model_name=model_name,
            max_length=max_length
        )
        super().__init__(config)


def get_industrial_reranker(
    model_name: str = "BAAI/bge-reranker-large",
    device: str = "auto"
) -> IndustrialCrossEncoderReranker:
    """Get industrial Cross-Encoder reranker instance.
    
    Args:
        model_name: Model name to use
        device: Device to use
        
    Returns:
        IndustrialCrossEncoderReranker instance
    """
    config = RerankingConfig(model_name=model_name, device=device)
    return IndustrialCrossEncoderReranker(config)


class RuleBasedReranker:
    """Rule-based reranker as fallback when model is not available."""
    
    def __init__(self):
        """Initialize rule-based reranker."""
        self._initialized = True
    
    async def initialize(self):
        """No initialization needed."""
    
    async def rerank(
        self, 
        query: str, 
        results: list[SearchResult],
        top_k: int | None = None
    ) -> list[SearchResult]:
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


def get_reranker_factory():
    """Get the reranker factory instance."""
    return RerankerFactory()