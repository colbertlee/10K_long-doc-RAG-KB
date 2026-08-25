"""Hybrid search combining BM25 sparse search and LightRAG vector search with RRF fusion."""

import sys
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.retrieval.bm25_search import BM25Search
from rag_kb.retrieval.bm25_index_builder import BM25IndexBuilder
from rag_kb.utils.performance_tuning import performance_tuner


@dataclass
class SearchResult:
    """Unified search result from hybrid retrieval."""
    doc_id: str
    content: str
    score: float
    source: str  # 'bm25', 'vector', or 'hybrid'
    metadata: Optional[Dict[str, Any]] = None


class HybridSearchEngine:
    """Hybrid search engine combining BM25 and vector search with RRF fusion."""
    
    def __init__(self, working_dir: Optional[str] = None, use_performance_tuning: bool = True):
        """Initialize hybrid search engine.
        
        Args:
            working_dir: Working directory for LightRAG storage
            use_performance_tuning: Whether to use performance tuning settings
        """
        self.lightrag_adapter = LightRAGAdapter(working_dir)
        self.bm25_index_builder = BM25IndexBuilder(working_dir)
        self.use_performance_tuning = use_performance_tuning
        
        # Load performance tuning settings
        if use_performance_tuning:
            rrf_config = performance_tuner.get_rrf_config()
            self.rrf_k = rrf_config['k']
            self.rrf_weight_bm25 = rrf_config['weight_bm25']
            self.rrf_weight_vector = rrf_config['weight_vector']
        else:
            self.rrf_k = 60  # Default RRF constant
            self.rrf_weight_bm25 = 0.4
            self.rrf_weight_vector = 0.6
        
    async def initialize(self):
        """Initialize both search engines."""
        await self.lightrag_adapter.ensure_initialized()
        # Try to load existing BM25 index
        await self.bm25_index_builder.load_index()
    
    async def search(
        self, 
        query: str, 
        top_k: int = 10,
        mode: str = "hybrid",
        use_reranking: bool = False
    ) -> List[SearchResult]:
        """Perform hybrid search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            mode: Search mode - 'bm25', 'vector', or 'hybrid'
            use_reranking: Whether to apply reranking
            
        Returns:
            List of search results
        """
        if mode == "bm25":
            return await self._bm25_search(query, top_k)
        elif mode == "vector":
            return await self._vector_search(query, top_k)
        elif mode == "hybrid":
            return await self._hybrid_search(query, top_k)
        else:
            raise ValueError(f"Unknown search mode: {mode}")
    
    async def _bm25_search(self, query: str, top_k: int) -> List[SearchResult]:
        """BM25 sparse search."""
        try:
            # Use BM25IndexBuilder for search
            bm25_results = await self.bm25_index_builder.search(query, top_k=top_k)
            
            return [
                SearchResult(
                    doc_id=result.get('id', ''),
                    content=result.get('text', ''),
                    score=result.get('score', 0.0),
                    source='bm25',
                    metadata=result.get('metadata', {})
                )
                for result in bm25_results
            ]
        except Exception as e:
            print(f"BM25 search error: {e}", flush=True)
            return []
    
    async def _vector_search(self, query: str, top_k: int) -> List[SearchResult]:
        """LightRAG vector search."""
        try:
            # Use LightRAG naive mode for pure vector search
            vector_results = await self.lightrag_adapter.query(
                query, 
                mode="naive"
            )
            
            # Parse LightRAG results
            results = []
            if vector_results and isinstance(vector_results, str):
                # LightRAG returns context as string, need to parse
                chunks = vector_results.split('\n\n')
                for i, chunk in enumerate(chunks[:top_k]):
                    results.append(SearchResult(
                        doc_id=f"vector_{i}",
                        content=chunk,
                        score=1.0 - (i / top_k),  # Simple scoring
                        source='vector',
                        metadata={}
                    ))
            
            return results[:top_k]
        except Exception as e:
            print(f"Vector search error: {e}", flush=True)
            return []
    
    async def _hybrid_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Hybrid search with RRF fusion."""
        # Run both searches in parallel
        bm25_task = asyncio.create_task(self._bm25_search(query, top_k * 2))
        vector_task = asyncio.create_task(self._vector_search(query, top_k * 2))
        
        bm25_results, vector_results = await asyncio.gather(bm25_task, vector_task)
        
        # Apply RRF fusion
        fused_results = self._rrf_fusion(bm25_results, vector_results, top_k)
        
        return fused_results
    
    def _rrf_fusion(
        self, 
        bm25_results: List[SearchResult], 
        vector_results: List[SearchResult],
        top_k: int
    ) -> List[SearchResult]:
        """Reciprocal Rank Fusion for combining results with weighted scoring."""
        # Create score maps
        bm25_scores = {result.doc_id: (1.0 / (self.rrf_k + i + 1)) * self.rrf_weight_bm25 
                      for i, result in enumerate(bm25_results)}
        vector_scores = {result.doc_id: (1.0 / (self.rrf_k + i + 1)) * self.rrf_weight_vector 
                        for i, result in enumerate(vector_results)}
        
        # Combine scores
        combined_scores = {}
        all_doc_ids = set(bm25_scores.keys()) | set(vector_scores.keys())
        
        for doc_id in all_doc_ids:
            combined_scores[doc_id] = (
                bm25_scores.get(doc_id, 0) + 
                vector_scores.get(doc_id, 0)
            )
        
        # Sort by combined score
        sorted_doc_ids = sorted(combined_scores.keys(), 
                               key=lambda x: combined_scores[x], 
                               reverse=True)
        
        # Build final results
        final_results = []
        for doc_id in sorted_doc_ids[:top_k]:
            # Prefer BM25 result if available
            bm25_result = next((r for r in bm25_results if r.doc_id == doc_id), None)
            vector_result = next((r for r in vector_results if r.doc_id == doc_id), None)
            
            base_result = bm25_result or vector_result
            if base_result:
                final_results.append(SearchResult(
                    doc_id=doc_id,
                    content=base_result.content,
                    score=combined_scores[doc_id],
                    source='hybrid',
                    metadata=base_result.metadata
                ))
        
        return final_results
    
    async def search_with_reranking(
        self,
        query: str,
        top_k: int = 10,
        reranker: Optional[Any] = None
    ) -> List[SearchResult]:
        """Search with reranking for improved precision."""
        # First get hybrid results
        hybrid_results = await self._hybrid_search(query, top_k * 2)
        
        if not reranker:
            return hybrid_results[:top_k]
        
        # Apply reranking
        reranked_results = await reranker.rerank(query, hybrid_results)
        
        return reranked_results[:top_k]
    
    async def build_bm25_index(self, documents: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Build BM25 index for hybrid search.
        
        Args:
            documents: Optional list of documents (will load from registry if not provided)
            
        Returns:
            Index building results
        """
        if documents:
            return await self.bm25_index_builder.build_index_from_documents(documents)
        else:
            return await self.bm25_index_builder.build_index_from_registry()
    
    def get_bm25_stats(self) -> Dict[str, Any]:
        """Get BM25 index statistics."""
        return self.bm25_index_builder.get_index_stats()


class QueryParam:
    """Query parameters for LightRAG."""
    def __init__(self, mode: str = "hybrid", only_need_context: bool = False):
        self.mode = mode
        self.only_need_context = only_need_context