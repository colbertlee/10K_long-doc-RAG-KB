"""Hybrid search combining BM25 and LightRAG with RRF fusion."""

from typing import List, Dict, Any
from .bm25_search import BM25Search


class HybridSearch:
    """Hybrid search combining BM25 sparse search and LightRAG semantic search."""
    
    def __init__(self, bm25_search: BM25Search = None, lightrag_adapter=None):
        """
        Initialize hybrid search.
        
        Args:
            bm25_search: BM25 search instance
            lightrag_adapter: LightRAG adapter instance
        """
        self.bm25_search = bm25_search
        self.lightrag_adapter = lightrag_adapter
        self.rrf_k = 60  # RRF constant
        
    def search(self, query: str, top_k: int = 10, use_bm25: bool = True, use_lightrag: bool = True) -> List[Dict[str, Any]]:
        """
        Perform hybrid search using RRF fusion.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            use_bm25: Whether to use BM25 search
            use_lightrag: Whether to use LightRAG search
            
        Returns:
            List of fused search results
        """
        all_results = {}
        
        # BM25 search
        if use_bm25 and self.bm25_search:
            bm25_results = self.bm25_search.search(query, top_k=top_k * 2)
            for rank, result in enumerate(bm25_results):
                doc_id = result['id']
                if doc_id not in all_results:
                    all_results[doc_id] = {
                        'id': doc_id,
                        'text': result['text'],
                        'metadata': result.get('metadata', {}),
                        'bm25_score': result['score'],
                        'lightrag_score': 0.0,
                        'rrf_score': 0.0
                    }
                all_results[doc_id]['bm25_score'] = result['score']
        
        # LightRAG search
        if use_lightrag and self.lightrag_adapter:
            try:
                lightrag_answer = self.lightrag_adapter.query(query, mode='hybrid')
                # Parse LightRAG results (this is simplified - actual implementation depends on LightRAG output)
                # For now, we'll simulate some results
                lightrag_results = self._parse_lightrag_results(lightrag_answer)
                
                for rank, result in enumerate(lightrag_results):
                    doc_id = result['id']
                    if doc_id not in all_results:
                        all_results[doc_id] = {
                            'id': doc_id,
                            'text': result['text'],
                            'metadata': result.get('metadata', {}),
                            'bm25_score': 0.0,
                            'lightrag_score': result['score'],
                            'rrf_score': 0.0
                        }
                    all_results[doc_id]['lightrag_score'] = result['score']
            except Exception as e:
                print(f"LightRAG search failed: {e}")
        
        # Apply RRF fusion
        for doc_id, result in all_results.items():
            rrf_score = 0.0
            
            if use_bm25 and result['bm25_score'] > 0:
                # Convert BM25 score to rank (simplified)
                bm25_rank = self._score_to_rank(result['bm25_score'], all_results.values(), 'bm25_score')
                rrf_score += 1.0 / (self.rrf_k + bm25_rank)
            
            if use_lightrag and result['lightrag_score'] > 0:
                # Convert LightRAG score to rank (simplified)
                lightrag_rank = self._score_to_rank(result['lightrag_score'], all_results.values(), 'lightrag_score')
                rrf_score += 1.0 / (self.rrf_k + lightrag_rank)
            
            result['rrf_score'] = rrf_score
        
        # Sort by RRF score and return top_k
        sorted_results = sorted(all_results.values(), key=lambda x: x['rrf_score'], reverse=True)[:top_k]
        
        return sorted_results
    
    def _parse_lightrag_results(self, lightrag_answer: str) -> List[Dict[str, Any]]:
        """
        Parse LightRAG results (simplified implementation).
        
        Args:
            lightrag_answer: LightRAG query response
            
        Returns:
            List of parsed results
        """
        # This is a simplified implementation
        # In practice, you'd need to parse the actual LightRAG output format
        # For now, return empty list
        return []
    
    def _score_to_rank(self, score: float, all_results, score_field: str) -> int:
        """
        Convert score to rank for RRF calculation.
        
        Args:
            score: Score value
            all_results: All results
            score_field: Field name for score
            
        Returns:
            Rank (1-based)
        """
        sorted_scores = sorted([r[score_field] for r in all_results if r[score_field] > 0], reverse=True)
        try:
            return sorted_scores.index(score) + 1
        except ValueError:
            return len(sorted_scores) + 1