"""Ollama embedding functions for LightRAG."""

import asyncio
from dataclasses import dataclass

import numpy as np
import ollama

from rag_kb.config.core_config import settings


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
        """Generate embeddings using Ollama (async) with caching support.

        Args:
            texts: List of text strings to embed
            **kwargs: Additional keyword arguments

        Returns:
            numpy array of embeddings
        """
        try:
            # Check if caching is enabled from config
            cache_enabled = getattr(settings, 'lightrag_enable_embedding_cache', True)
            
            # Simple in-memory cache for embeddings
            if not hasattr(self, '_embedding_cache'):
                self._embedding_cache = {}
            
            # Generate cache keys for texts
            cache_keys = [hash(text) for text in texts] if isinstance(texts, list) else [hash(texts)]
            
            # Check cache first
            if cache_enabled:
                cached_embeddings = []
                missing_indices = []
                for i, key in enumerate(cache_keys):
                    if key in self._embedding_cache:
                        cached_embeddings.append((i, self._embedding_cache[key]))
                    else:
                        missing_indices.append(i)
                
                # If all cached, return immediately
                if len(cached_embeddings) == len(cache_keys):
                    cached_embeddings.sort(key=lambda x: x[0])
                    return np.array([emb for _, emb in cached_embeddings], dtype=np.float32)
            
            # Run synchronous Ollama call in thread pool for missing texts
            loop = asyncio.get_event_loop()
            client = ollama.Client(host=settings.embedding_base_url, timeout=60)  # Reduced timeout to 60s

            def sync_embed():
                texts_to_embed = [texts[i] for i in missing_indices] if missing_indices else texts
                print(f"Embedding {len(texts_to_embed) if isinstance(texts_to_embed, list) else 1} texts...", flush=True)
                resp = client.embed(model=settings.embedding_model, input=texts_to_embed)
                new_embeddings = np.array(resp['embeddings'], dtype=np.float32)
                print(f"Embeddings shape: {new_embeddings.shape}", flush=True)
                return new_embeddings

            new_embeddings = await loop.run_in_executor(None, sync_embed)
            
            # Cache new embeddings
            if cache_enabled and missing_indices:
                for i, key_idx in enumerate(missing_indices):
                    self._embedding_cache[cache_keys[key_idx]] = new_embeddings[i]
                
                # Combine cached and new embeddings
                final_embeddings = np.zeros((len(cache_keys), new_embeddings.shape[1]), dtype=np.float32)
                for i, emb in cached_embeddings:
                    final_embeddings[i] = emb
                for i, key_idx in enumerate(missing_indices):
                    final_embeddings[key_idx] = new_embeddings[i]
                
                return final_embeddings
            
            return new_embeddings
        except Exception as e:
            error_msg = f"Ollama embedding error: {e}. Please ensure Ollama is running and the model '{settings.embedding_model}' is available."
            print(error_msg, flush=True)
            # Raise the error instead of returning zero array to make the issue visible
            raise ConnectionError(error_msg)
    
    async def __call__(self, *args, **kwargs) -> np.ndarray:
        """Make the embedding function callable (async)."""
        return await self.func(*args, **kwargs)


# Create global embedding function instance
ollama_embed = EmbeddingFunc()