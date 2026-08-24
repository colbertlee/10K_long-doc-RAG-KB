"""Ollama embedding functions for LightRAG."""

import numpy as np
import ollama
from rag_kb.config import settings


class EmbeddingFunc:
    """Embedding function wrapper for LightRAG compatibility."""
    
    def __init__(self, **kwargs):
        """Initialize with any kwargs that LightRAG might pass."""
        self.embedding_dim = kwargs.get('embedding_dim', 768)
        self.func = self.__call__
    
    def __call__(self, texts: list) -> np.ndarray:
        """Generate embeddings using Ollama.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings
        """
        try:
            client = ollama.Client(host=settings.embedding_base_url)
            resp = client.embed(model=settings.embedding_model, input=texts)
            embeddings = np.array(resp['embeddings'], dtype=np.float32)
            return embeddings
        except Exception as e:
            print(f"Ollama embedding error: {e}")
            # Return a zero array as fallback
            if isinstance(texts, list):
                return np.zeros((len(texts), self.embedding_dim), dtype=np.float32)
            else:
                return np.zeros((1, self.embedding_dim), dtype=np.float32)


# Create global embedding function instance
ollama_embed = EmbeddingFunc()