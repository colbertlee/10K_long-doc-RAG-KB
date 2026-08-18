"""Reranking module for improving search result precision using cross-encoder models."""

from typing import List, Dict, Optional, Tuple
from rag_kb.models import SearchResult
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np


class CrossEncoderReranker:
    """Cross-encoder reranker for improving search result precision."""
    
    def __init__(self, model_name: str = 'BAAI/bge-reranker-base', 
                 device: str = 'cpu', batch_size: int = 16):
        """Initialize cross-encoder reranker.
        
        Args:
            model_name: HuggingFace model name for reranking
            device: Device to run model on ('cpu' or 'cuda')
            batch_size: Batch size for inference
        """
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the cross-encoder model and tokenizer."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Warning: Failed to load reranker model {self.model_name}: {e}")
            print("Reranking will be disabled")
            self.model = None
    
    def rerank(self, query: str, results: List[SearchResult], 
               top_k: int = 10) -> List[SearchResult]:
        """Rerank search results using cross-encoder model.
        
        Args:
            query: Original search query
            results: Initial search results to rerank
            top_k: Number of top results to return
            
        Returns:
            Reranked list of SearchResult objects
        """
        if not results or not self.model:
            return results[:top_k]
        
        if len(results) <= top_k:
            return results
        
        # Prepare query-document pairs
        pairs = [(query, result.text) for result in results]
        
        # Compute reranking scores
        scores = self._compute_scores(pairs)
        
        # Update scores and rerank
        for i, result in enumerate(results):
            result.score = float(scores[i])
        
        # Sort by new scores
        reranked = sorted(results, key=lambda x: x.score, reverse=True)
        
        # Update ranks
        for i, result in enumerate(reranked):
            result.rank = i + 1
        
        return reranked[:top_k]
    
    def _compute_scores(self, pairs: List[Tuple[str, str]]) -> np.ndarray:
        """Compute relevance scores for query-document pairs.
        
        Args:
            pairs: List of (query, document) tuples
            
        Returns:
            Array of relevance scores
        """
        if not self.model or not self.tokenizer:
            return np.zeros(len(pairs))
        
        scores = []
        
        # Process in batches
        for i in range(0, len(pairs), self.batch_size):
            batch_pairs = pairs[i:i + self.batch_size]
            
            # Tokenize batch
            inputs = self.tokenizer(
                batch_pairs,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            ).to(self.device)
            
            # Compute scores
            with torch.no_grad():
                outputs = self.model(**inputs)
                batch_scores = outputs.logits.squeeze(-1).cpu().numpy()
                scores.extend(batch_scores.tolist())
        
        return np.array(scores)
    
    def rerank_with_metadata(self, query: str, results: List[SearchResult],
                            metadata_fields: List[str] = None,
                            top_k: int = 10) -> List[SearchResult]:
        """Rerank results considering both text and metadata.
        
        Args:
            query: Original search query
            results: Initial search results to rerank
            metadata_fields: List of metadata fields to consider
            top_k: Number of top results to return
            
        Returns:
            Reranked list of SearchResult objects
        """
        if not results:
            return results
        
        # First, do standard text-based reranking
        reranked = self.rerank(query, results, top_k=len(results))
        
        # If metadata fields specified, apply metadata-based boosting
        if metadata_fields:
            reranked = self._apply_metadata_boosting(reranked, metadata_fields, query)
        
        return reranked[:top_k]
    
    def _apply_metadata_boosting(self, results: List[SearchResult],
                                 metadata_fields: List[str],
                                 query: str) -> List[SearchResult]:
        """Apply metadata-based boosting to reranked results.
        
        Args:
            results: Reranked search results
            metadata_fields: Metadata fields to consider for boosting
            query: Original query for keyword matching
            
        Returns:
            Results with metadata-boosted scores
        """
        query_lower = query.lower()
        
        for result in results:
            boost = 1.0
            
            for field in metadata_fields:
                field_value = result.metadata.get(field, '')
                if field_value:
                    # Check if query terms appear in metadata
                    if isinstance(field_value, str):
                        if any(term in field_value.lower() for term in query_lower.split()):
                            boost *= 1.2  # 20% boost for metadata match
                    elif isinstance(field_value, list):
                        if any(term in str(v).lower() for term in query_lower.split() for v in field_value):
                            boost *= 1.2
            
            result.score *= boost
        
        # Re-sort after boosting
        reranked = sorted(results, key=lambda x: x.score, reverse=True)
        
        # Update ranks
        for i, result in enumerate(reranked):
            result.rank = i + 1
        
        return reranked


class SimpleReranker:
    """Simple rule-based reranker as fallback when cross-encoder is unavailable."""
    
    def __init__(self):
        """Initialize simple reranker."""
        pass
    
    def rerank(self, query: str, results: List[SearchResult], 
               top_k: int = 10) -> List[SearchResult]:
        """Rerank using simple keyword matching and length penalties.
        
        Args:
            query: Original search query
            results: Initial search results to rerank
            top_k: Number of top results to return
            
        Returns:
            Reranked list of SearchResult objects
        """
        if not results:
            return results[:top_k]
        
        query_terms = set(query.lower().split())
        
        for result in results:
            text_lower = result.text.lower()
            
            # Keyword matching score
            keyword_score = sum(1 for term in query_terms if term in text_lower)
            keyword_score = keyword_score / max(len(query_terms), 1)
            
            # Length penalty (prefer concise, relevant answers)
            length_penalty = 1.0 / (1.0 + len(result.text) / 1000.0)
            
            # Combine scores
            result.score = result.score * 0.7 + keyword_score * 0.2 + length_penalty * 0.1
        
        # Sort by new scores
        reranked = sorted(results, key=lambda x: x.score, reverse=True)
        
        # Update ranks
        for i, result in enumerate(reranked):
            result.rank = i + 1
        
        return reranked[:top_k]


class RerankerPipeline:
    """Pipeline for multi-stage reranking."""
    
    def __init__(self, cross_encoder_model: str = 'BAAI/bge-reranker-base',
                 device: str = 'cpu', enable_cross_encoder: bool = True):
        """Initialize reranker pipeline.
        
        Args:
            cross_encoder_model: Model name for cross-encoder
            device: Device to run models on
            enable_cross_encoder: Whether to use cross-encoder reranking
        """
        self.enable_cross_encoder = enable_cross_encoder
        
        if enable_cross_encoder:
            try:
                self.cross_encoder = CrossEncoderReranker(cross_encoder_model, device)
            except:
                print("Cross-encoder initialization failed, falling back to simple reranker")
                self.cross_encoder = None
                self.enable_cross_encoder = False
        
        self.simple_reranker = SimpleReranker()
    
    def rerank(self, query: str, results: List[SearchResult],
               top_k: int = 10, use_metadata: bool = False) -> List[SearchResult]:
        """Apply reranking pipeline to search results.
        
        Args:
            query: Original search query
            results: Initial search results
            top_k: Number of top results to return
            use_metadata: Whether to consider metadata in reranking
            
        Returns:
            Reranked search results
        """
        if not results:
            return results[:top_k]
        
        # Apply cross-encoder reranking if enabled
        if self.enable_cross_encoder and self.cross_encoder:
            if use_metadata:
                results = self.cross_encoder.rerank_with_metadata(
                    query, results, metadata_fields=['title', 'source'], top_k=len(results)
                )
            else:
                results = self.cross_encoder.rerank(query, results, top_k=len(results))
        else:
            # Fallback to simple reranking
            results = self.simple_reranker.rerank(query, results, top_k=len(results))
        
        return results[:top_k]
    
    def get_reranker_info(self) -> Dict:
        """Get information about the reranker configuration.
        
        Returns:
            Dictionary with reranker information
        """
        return {
            'cross_encoder_enabled': self.enable_cross_encoder,
            'cross_encoder_model': getattr(self.cross_encoder, 'model_name', None) if self.cross_encoder else None,
            'device': getattr(self.cross_encoder, 'device', None) if self.cross_encoder else 'cpu'
        }