"""Hybrid search engine combining BM25 and vector search."""

from typing import List, Dict, Tuple, Optional
from rag_kb.retrieval.bm25_search import BM25SearchEngine
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.models import SearchResult
from rag_kb.retrieval.reranker import RerankerPipeline
import re


class HybridSearchEngine:
    """Hybrid search engine combining BM25 sparse search with LightRAG vector search."""
    
    def __init__(self, bm25_engine: BM25SearchEngine = None, lightrag_adapter: LightRAGAdapter = None, 
                 enable_reranking: bool = True, reranker_device: str = 'cpu'):
        """Initialize hybrid search engine.
        
        Args:
            bm25_engine: BM25 search engine instance (creates new if None)
            lightrag_adapter: LightRAG adapter instance (creates new if None)
            enable_reranking: Whether to enable cross-encoder reranking
            reranker_device: Device for reranker model ('cpu' or 'cuda')
        """
        self.bm25 = bm25_engine or BM25SearchEngine()
        self.lightrag = lightrag_adapter
        
        # RRF (Reciprocal Rank Fusion) parameters
        self.rrf_k = 60  # RRF constant, typically 60
        
        # Initialize reranker
        self.enable_reranking = enable_reranking
        if enable_reranking:
            try:
                self.reranker = RerankerPipeline(
                    cross_encoder_model='BAAI/bge-reranker-base',
                    device=reranker_device,
                    enable_cross_encoder=True
                )
            except Exception as e:
                print(f"Failed to initialize reranker: {e}. Using simple reranking instead.")
                self.reranker = RerankerPipeline(enable_cross_encoder=False)
        else:
            self.reranker = None
    
    def add_document(self, doc_id: str, text: str, metadata: Dict = None):
        """Add document to both BM25 and LightRAG indexes.
        
        Args:
            doc_id: Document identifier
            text: Document text content
            metadata: Optional document metadata
        """
        # Add to BM25 index
        self.bm25.add_document(doc_id, text, metadata)
        
        # Add to LightRAG index (if adapter is provided)
        if self.lightrag:
            # LightRAG handles its own indexing through insert_chunks
            # This is a placeholder for LightRAG integration
            pass
    
    def build_indexes(self):
        """Build both BM25 and LightRAG indexes."""
        self.bm25.build_index()
        # LightRAG builds its index automatically during insert operations
    
    def search(self, query: str, top_k: int = 10, mode: str = 'hybrid', 
               bm25_weight: float = 0.3, vector_weight: float = 0.7,
               user_roles: Dict = None, enable_reranking: bool = None) -> List[SearchResult]:
        """Perform hybrid search combining BM25 and vector search.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            mode: Search mode ('hybrid', 'bm25_only', 'vector_only')
            bm25_weight: Weight for BM25 scores (default: 0.3)
            vector_weight: Weight for vector scores (default: 0.7)
            user_roles: Optional user roles for ACL filtering
            enable_reranking: Whether to apply reranking (overrides default)
            
        Returns:
            List of SearchResult objects sorted by combined score
        """
        # Get initial results
        if mode == 'bm25_only':
            results = self._bm25_search(query, top_k * 2, user_roles)  # Get more for reranking
        elif mode == 'vector_only':
            results = self._vector_search(query, top_k * 2, user_roles)
        else:  # hybrid mode
            results = self._hybrid_search(query, top_k * 2, bm25_weight, vector_weight, user_roles)
        
        # Apply reranking if enabled
        should_rerank = enable_reranking if enable_reranking is not None else self.enable_reranking
        if should_rerank and self.reranker and len(results) > top_k:
            results = self.reranker.rerank(query, results, top_k=top_k, use_metadata=True)
        
        return results[:top_k]
    
    def _bm25_search(self, query: str, top_k: int, user_roles: Dict = None) -> List[SearchResult]:
        """Perform BM25-only search.
        
        Args:
            query: Search query
            top_k: Number of results
            user_roles: Optional user roles for ACL filtering
            
        Returns:
            List of SearchResult objects
        """
        bm25_results = self.bm25.search(query, top_k=top_k * 2)  # Get more for filtering
        
        search_results = []
        for doc_id, score in bm25_results:
            doc = self.bm25.get_document(doc_id)
            if doc:
                # Apply ACL filtering if user roles are provided
                if user_roles and not self._check_acl(doc['metadata'], user_roles):
                    continue
                
                search_results.append(SearchResult(
                    chunk_id=doc_id,
                    doc_id=doc_id,
                    text=doc['text'][:500],  # Preview text
                    score=score,
                    rank=len(search_results) + 1,
                    source=doc['metadata'].get('source', ''),
                    metadata=doc['metadata']
                ))
        
        return search_results[:top_k]
    
    def _vector_search(self, query: str, top_k: int, user_roles: Dict = None) -> List[SearchResult]:
        """Perform vector-only search using LightRAG.
        
        Args:
            query: Search query
            top_k: Number of results
            user_roles: Optional user roles for ACL filtering
            
        Returns:
            List of SearchResult objects
        """
        if not self.lightrag:
            return []
        
        # Query LightRAG
        answer = self.lightrag.query(query, mode='hybrid', user_roles=user_roles)
        
        # Extract sources from LightRAG response
        sources = self._extract_lightrag_sources(answer)
        
        search_results = []
        for i, source in enumerate(sources[:top_k]):
            search_results.append(SearchResult(
                chunk_id=f"vector_{i}",
                doc_id=source.get('doc_id', 'unknown'),
                text=source.get('text', '')[:500],
                score=1.0 - (i * 0.1),  # Decreasing score based on rank
                rank=i + 1,
                source=source.get('source', ''),
                metadata=source.get('metadata', {})
            ))
        
        return search_results
    
    def _hybrid_search(self, query: str, top_k: int, bm25_weight: float, 
                      vector_weight: float, user_roles: Dict = None) -> List[SearchResult]:
        """Perform hybrid search using RRF (Reciprocal Rank Fusion).
        
        Args:
            query: Search query
            top_k: Number of results
            bm25_weight: Weight for BM25 scores
            vector_weight: Weight for vector scores
            user_roles: Optional user roles for ACL filtering
            
        Returns:
            List of SearchResult objects sorted by combined score
        """
        # Get results from both search engines
        bm25_results = self.bm25.search(query, top_k=top_k * 2)
        vector_results = []
        
        if self.lightrag:
            answer = self.lightrag.query(query, mode='hybrid', user_roles=user_roles)
            vector_sources = self._extract_lightrag_sources(answer)
            vector_results = [(s.get('doc_id', f"vector_{i}"), 1.0 - (i * 0.1)) 
                            for i, s in enumerate(vector_sources)]
        
        # Apply RRF fusion
        fused_scores = self._rrf_fusion(bm25_results, vector_results)
        
        # Convert to SearchResult objects
        search_results = []
        for doc_id, combined_score in sorted(fused_scores.items(), 
                                            key=lambda x: x[1], reverse=True):
            # Try to get document from BM25 first
            doc = self.bm25.get_document(doc_id)
            if doc:
                # Apply ACL filtering
                if user_roles and not self._check_acl(doc['metadata'], user_roles):
                    continue
                
                search_results.append(SearchResult(
                    chunk_id=doc_id,
                    doc_id=doc_id,
                    text=doc['text'][:500],
                    score=combined_score,
                    rank=len(search_results) + 1,
                    source=doc['metadata'].get('source', ''),
                    metadata=doc['metadata']
                ))
            else:
                # Fallback for vector-only results
                search_results.append(SearchResult(
                    chunk_id=doc_id,
                    doc_id=doc_id,
                    text="Vector search result",
                    score=combined_score,
                    rank=len(search_results) + 1,
                    source="vector_search",
                    metadata={}
                ))
        
        return search_results[:top_k]
    
    def _rrf_fusion(self, bm25_results: List[Tuple[str, float]], 
                   vector_results: List[Tuple[str, float]]) -> Dict[str, float]:
        """Apply Reciprocal Rank Fusion to combine results.
        
        Args:
            bm25_results: List of (doc_id, score) from BM25
            vector_results: List of (doc_id, score) from vector search
            
        Returns:
            Dictionary mapping doc_id to fused score
        """
        fused_scores = {}
        
        # Process BM25 results
        for rank, (doc_id, score) in enumerate(bm25_results, 1):
            rrf_score = 1.0 / (self.rrf_k + rank)
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + rrf_score * 0.3  # BM25 weight
        
        # Process vector results
        for rank, (doc_id, score) in enumerate(vector_results, 1):
            rrf_score = 1.0 / (self.rrf_k + rank)
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + rrf_score * 0.7  # Vector weight
        
        return fused_scores
    
    def _extract_lightrag_sources(self, answer: str) -> List[Dict]:
        """Extract source information from LightRAG answer.
        
        Args:
            answer: LightRAG response text
            
        Returns:
            List of source dictionaries
        """
        sources = []
        # Extract [DATA:...] patterns from LightRAG response
        data_matches = re.findall(r'\[DATA:([^\]]+)\]', answer)
        
        for match in data_matches:
            # Parse the data format (this depends on LightRAG's actual format)
            sources.append({
                'doc_id': match[:50],  # Simplified doc_id extraction
                'text': match,
                'source': 'lightrag',
                'metadata': {}
            })
        
        return sources
    
    def _check_acl(self, metadata: Dict, user_roles: Dict) -> bool:
        """Check if document passes ACL filter.
        
        Args:
            metadata: Document metadata
            user_roles: User roles for ACL checking
            
        Returns:
            True if document passes ACL check
        """
        if not user_roles:
            return True
        
        for key, required_roles in user_roles.items():
            if required_roles:  # Only check if there are requirements
                doc_roles = metadata.get(f'acl_{key}', [])
                if doc_roles and not any(role in doc_roles for role in required_roles):
                    return False
        
        return True
    
    def save_indexes(self, name: str = 'hybrid_index'):
        """Save both indexes to disk.
        
        Args:
            name: Base name for index files
        """
        self.bm25.save_index(f'{name}_bm25')
        # LightRAG manages its own index storage
    
    def load_indexes(self, name: str = 'hybrid_index'):
        """Load both indexes from disk.
        
        Args:
            name: Base name for index files
        """
        self.bm25.load_index(f'{name}_bm25')
        # LightRAG manages its own index loading
    
    def get_statistics(self) -> Dict:
        """Get statistics for both search engines.
        
        Returns:
            Dictionary with combined statistics
        """
        stats = {
            'bm25': self.bm25.get_statistics(),
            'lightrag': 'enabled' if self.lightrag else 'disabled',
            'rrf_k': self.rrf_k
        }
        return stats