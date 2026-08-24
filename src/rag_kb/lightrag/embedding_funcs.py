"""Ollama embedding functions for LightRAG."""

import numpy as np
import ollama
from rag_kb.config import settings


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