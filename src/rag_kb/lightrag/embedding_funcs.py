"""Ollama embedding functions for LightRAG."""

import asyncio
import numpy as np
import ollama
from rag_kb.config import settings
from dataclasses import dataclass


@dataclass
class EmbeddingFunc:
    """Embedding function wrapper for LightRAG compatibility.
    
    This matches the LightRAG EmbeddingFunc interface from lightrag.utils
    """
    embedding_dim: int = 768
    func: callable = None
    max_token_size: int = None
    send_dimensions: bool = False
    model_name: str = None
    supports_asymmetric: bool = False
    
    def __post_init__(self):
        """Initialize func attribute."""
        if self.func is None:
            self.func = self._ollama_embed
    
    async def _ollama_embed(self, texts: list, **kwargs) -> np.ndarray:
        """Generate embeddings using Ollama (async).
        
        Args:
            texts: List of text strings to embed
            **kwargs: Additional keyword arguments
            
        Returns:
            numpy array of embeddings
        """
        try:
            # Run synchronous Ollama call in thread pool
            loop = asyncio.get_event_loop()
            client = ollama.Client(host=settings.embedding_base_url)
            
            def sync_embed():
                print(f"Embedding {len(texts) if isinstance(texts, list) else 1} texts...", flush=True)
                resp = client.embed(model=settings.embedding_model, input=texts)
                embeddings = np.array(resp['embeddings'], dtype=np.float32)
                print(f"Embeddings shape: {embeddings.shape}", flush=True)
                return embeddings
            
            result = await loop.run_in_executor(None, sync_embed)
            return result
        except Exception as e:
            print(f"Ollama embedding error: {e}")
            # Return a zero array as fallback
            if isinstance(texts, list):
                return np.zeros((len(texts), self.embedding_dim), dtype=np.float32)
            else:
                return np.zeros((1, self.embedding_dim), dtype=np.float32)
    
    async def __call__(self, *args, **kwargs) -> np.ndarray:
        """Make the embedding function callable (async)."""
        return await self.func(*args, **kwargs)


# Create global embedding function instance
ollama_embed = EmbeddingFunc()