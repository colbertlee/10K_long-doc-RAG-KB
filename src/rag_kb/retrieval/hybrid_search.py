"""Hybrid search combining BM25 and LightRAG with enhanced reranking."""

from typing import List, Dict, Any, Optional
from .bm25_search import BM25Search
from .reranker import RerankerPipeline


class HybridSearch:
    """Enhanced hybrid search with BM25, LightRAG, and intelligent reranking."""
    
    def __init__(self, bm25_search: BM25Search = None, lightrag_adapter=None,
                 enable_reranking: bool = True, reranker_device: str = 'cpu'):
        """
        Initialize enhanced hybrid search.
        
        Args:
            bm25_search: BM25 search instance
            lightrag_adapter: LightRAG adapter instance
            enable_reranking: Whether to enable reranking
            reranker_device: Device for reranker ('cpu' or 'cuda')
        """
        self.bm25_search = bm25_search
        self.lightrag_adapter = lightrag_adapter
        self.rrf_k = 60  # RRF constant
        self.enable_reranking = enable_reranking
        
        # Initialize reranker pipeline
        if enable_reranking:
            try:
                self.reranker = RerankerPipeline(
                    cross_encoder_model='BAAI/bge-reranker-base',
                    device=reranker_device,
                    enable_cross_encoder=True
                )
            except Exception as e:
                print(f"Reranker initialization failed: {e}")
                self.reranker = None
                self.enable_reranking = False
        else:
            self.reranker = None
        
    def search(self, query: str, top_k: int = 10, use_bm25: bool = True, use_lightrag: bool = True,
              bm25_weight: float = 0.3, lightrag_weight: float = 0.7, apply_reranking: bool = True) -> Dict[str, Any]:
        """
        Perform enhanced hybrid search with RRF fusion and optional reranking.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            use_bm25: Whether to use BM25 search
            use_lightrag: Whether to use LightRAG search
            bm25_weight: Weight for BM25 results in fusion
            lightrag_weight: Weight for LightRAG results in fusion
            apply_reranking: Whether to apply reranking
            
        Returns:
            Dictionary with answer and sources
        """
        all_results = {}
        lightrag_answer = ""
        
        # LightRAG dense retrieval (get answer first)
        if use_lightrag and self.lightrag_adapter:
            try:
                lightrag_answer = self.lightrag_adapter.query(query, mode='hybrid')
                # Parse LightRAG results (simplified implementation)
                lightrag_results = self._parse_lightrag_results(lightrag_answer)
                
                for rank, result in enumerate(lightrag_results):
                    doc_id = result['id']
                    if doc_id not in all_results:
                        all_results[doc_id] = {
                            'id': doc_id,
                            'text': result['text'],
                            'title': result.get('title', ''),
                            'metadata': result.get('metadata', {}),
                            'bm25_score': 0.0,
                            'lightrag_score': result['score'],
                            'rrf_score': 0.0,
                            'source': 'lightrag'
                        }
                    all_results[doc_id]['lightrag_score'] = result['score']
            except Exception as e:
                print(f"LightRAG search failed: {e}")
                lightrag_answer = f"LightRAG search failed: {str(e)}"
        
        # BM25 sparse retrieval
        if use_bm25 and self.bm25_search:
            try:
                bm25_results = self.bm25_search.search(query, top_k=top_k * 2)
                for rank, result in enumerate(bm25_results):
                    doc_id = result['id']
                    if doc_id not in all_results:
                        all_results[doc_id] = {
                            'id': doc_id,
                            'text': result['text'],
                            'title': result.get('title', ''),
                            'metadata': result.get('metadata', {}),
                            'bm25_score': result['score'],
                            'lightrag_score': 0.0,
                            'rrf_score': 0.0,
                            'source': 'bm25'
                        }
                    all_results[doc_id]['bm25_score'] = result['score']
            except Exception as e:
                print(f"BM25 search failed: {e}")
        
        # Apply weighted RRF fusion
        for doc_id, result in all_results.items():
            rrf_score = 0.0
            
            if use_bm25 and result['bm25_score'] > 0:
                bm25_rank = self._score_to_rank(result['bm25_score'], all_results.values(), 'bm25_score')
                rrf_score += (1.0 / (self.rrf_k + bm25_rank)) * bm25_weight
            
            if use_lightrag and result['lightrag_score'] > 0:
                lightrag_rank = self._score_to_rank(result['lightrag_score'], all_results.values(), 'lightrag_score')
                rrf_score += (1.0 / (self.rrf_k + lightrag_rank)) * lightrag_weight
            
            result['rrf_score'] = rrf_score
            result['score'] = rrf_score  # Use RRF score as main score
        
        # Convert to list and sort
        sorted_results = sorted(all_results.values(), key=lambda x: x['score'], reverse=True)
        
        # Apply reranking if enabled and we have enough results
        if apply_reranking and self.enable_reranking and self.reranker and len(sorted_results) > 1:
            sorted_results = self._apply_reranking(query, sorted_results, top_k)
        
        # Return answer and sources
        return {
            'answer': lightrag_answer or "No answer generated from search results",
            'sources': sorted_results[:top_k],
            'mode': 'hybrid',
            'source_count': len(sorted_results[:top_k])
        }
    
    def _parse_lightrag_results(self, lightrag_answer: str) -> List[Dict[str, Any]]:
        """
        Parse LightRAG results (simplified implementation).
        
        Args:
            lightrag_answer: LightRAG query response
            
        Returns:
            List of parsed results
        """
        # Parse LightRAG answer to extract relevant content
        # LightRAG returns a direct answer, so we create a synthetic result
        if not lightrag_answer or lightrag_answer.strip() == "":
            return []
        
        # Create a result from the LightRAG answer
        return [{
            'id': f"lightrag_{hash(lightrag_answer)}",
            'text': lightrag_answer,
            'title': 'LightRAG Answer',
            'metadata': {'source': 'lightrag', 'mode': 'hybrid'},
            'score': 1.0  # Give LightRAG answer high score
        }]
    
    def _apply_reranking(self, query: str, results: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """
        Apply reranking to search results.
        
        Args:
            query: Search query
            results: Search results to rerank
            top_k: Number of results to return
            
        Returns:
            Reranked results
        """
        from rag_kb.models import SearchResult
        
        # Convert to SearchResult format
        search_results = []
        for result in results:
            search_result = SearchResult(
                chunk_id=result['id'],
                doc_id=result['id'],
                text=result['text'],
                score=result['score'],
                rank=0,
                metadata=result.get('metadata', {})
            )
            search_results.append(search_result)
        
        # Apply reranking
        reranked = self.reranker.rerank(query, search_results, top_k=len(search_results))
        
        # Convert back to dict format
        reranked_dicts = []
        for i, result in enumerate(reranked):
            original_result = next((r for r in results if r['id'] == result.doc_id), results[i])
            reranked_dict = original_result.copy()
            reranked_dict['score'] = result.score
            reranked_dict['rank'] = result.rank
            reranked_dicts.append(reranked_dict)
        
        return reranked_dicts
    
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