"""Ollama embedding functions for LightRAG."""

import numpy as np
import ollama
from rag_kb.config import settings

# For newer LightRAG versions that expect EmbeddingFunc
try:
    from lightrag import EmbeddingFunc
except ImportError:
    EmbeddingFunc = None


def ollama_embed(texts: list):
    """Generate embeddings using Ollama.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        numpy array of embeddings
    """
    client = ollama.Client(host=settings.embedding_base_url)
    resp = client.embed(model=settings.embedding_model, input=texts)
    return np.array(resp['embeddings'], dtype=np.float32)


class OllamaEmbedWrapper:
    """Wrapper for Ollama embedding to support LightRAG's EmbeddingFunc interface."""
    
    def __call__(self, texts: list):
        return ollama_embed(texts)


# Create EmbeddingFunc instance if available
if EmbeddingFunc is not None:
    ollama_embed_func = EmbeddingFunc(callback=OllamaEmbedWrapper())
else:
    ollama_embed_func = ollama_embed