"""GPU-accelerated reranking with cross-encoder models."""

import torch
from typing import List, Tuple
import numpy as np

from rag_kb.config import settings


class GPUReranker:
    """GPU-accelerated reranking with cross-encoder models."""
    
    def __init__(self):
        """Initialize GPU reranker with device detection."""
        self.device = self._detect_device()
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _detect_device(self) -> str:
        """Detect available device for computation.
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if settings.reranking_device == 'cuda' and torch.cuda.is_available():
            device = 'cuda'
            print(f"GPU detected for reranking: {torch.cuda.get_device_name(0)}")
        else:
            device = 'cpu'
            print("Using CPU for reranking (GPU not available or not configured)")
        
        return device
    
    def _load_model(self):
        """Load reranking model on detected device."""
        if not settings.enable_reranking:
            print("Reranking is disabled in configuration")
            return
        
        try:
            from sentence_transformers import CrossEncoder
            
            print(f"Loading reranking model: {settings.reranking_model}")
            print(f"Device: {self.device}")
            
            # Load model on detected device
            self.model = CrossEncoder(
                settings.reranking_model,
                device=self.device
            )
            
            print("Reranking model loaded successfully")
            
        except ImportError:
            print("sentence-transformers not available, reranking disabled")
            self.model = None
        except Exception as e:
            print(f"Error loading reranking model: {e}")
            self.model = None
    
    def rerank(self, query: str, documents: List[str], top_k: int = None) -> List[Tuple[int, float]]:
        """Rerank documents based on query relevance.
        
        Args:
            query: Query string
            documents: List of document texts
            top_k: Number of top results to return
            
        Returns:
            List of (index, score) tuples sorted by relevance
        """
        if self.model is None:
            # Return original order with neutral scores
            return [(i, 0.5) for i in range(len(documents))]
        
        # Prepare query-document pairs
        pairs = [[query, doc] for doc in documents]
        
        # Compute scores
        with torch.no_grad():
            scores = self.model.predict(
                pairs,
                batch_size=settings.reranking_batch_size,
                show_progress_bar=False
            )
        
        # Sort by score (descending)
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        if top_k:
            indexed_scores = indexed_scores[:top_k]
        
        return indexed_scores
    
    def rerank_with_metadata(
        self, 
        query: str, 
        documents: List[dict], 
        top_k: int = None
    ) -> List[dict]:
        """Rerank documents with metadata.
        
        Args:
            query: Query string
            documents: List of document dictionaries with 'text' field
            top_k: Number of top results to return
            
        Returns:
            List of reranked document dictionaries
        """
        if not documents:
            return []
        
        # Extract texts
        texts = [doc.get('text', '') for doc in documents]
        
        # Rerank
        reranked_indices = self.rerank(query, texts, top_k)
        
        # Reorder documents
        reranked_docs = []
        for idx, score in reranked_indices:
            doc = documents[idx].copy()
            doc['rerank_score'] = float(score)
            reranked_docs.append(doc)
        
        return reranked_docs


# Global reranker instance
_gpu_reranker = None


def get_gpu_reranker() -> GPUReranker:
    """Get or create global GPU reranker instance.
    
    Returns:
        GPUReranker instance
    """
    global _gpu_reranker
    if _gpu_reranker is None:
        _gpu_reranker = GPUReranker()
    return _gpu_reranker


def rerank_results(query: str, results: List[dict], top_k: int = None) -> List[dict]:
    """Rerank search results.
    
    Args:
        query: Query string
        results: List of search result dictionaries
        top_k: Number of top results to return
        
    Returns:
        Reranked results
    """
    if not settings.enable_reranking:
        return results
    
    reranker = get_gpu_reranker()
    return reranker.rerank_with_metadata(query, results, top_k)