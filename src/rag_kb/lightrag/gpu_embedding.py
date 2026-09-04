"""GPU-accelerated embedding functions with device detection."""

import torch
from typing import List, Union
import numpy as np

from rag_kb.config import settings


class GPUEmbedding:
    """GPU-accelerated embedding with automatic device detection."""
    
    def __init__(self):
        """Initialize GPU embedding with device detection."""
        self.device = self._detect_device()
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _detect_device(self) -> str:
        """Detect available device for computation.
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if settings.embedding_device == 'cuda' and torch.cuda.is_available():
            device = 'cuda'
            print(f"GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            device = 'cpu'
            print("Using CPU for embedding (GPU not available or not configured)")
        
        return device
    
    def _load_model(self):
        """Load embedding model on detected device."""
        try:
            from sentence_transformers import SentenceTransformer
            
            print(f"Loading embedding model: {settings.embedding_model}")
            print(f"Device: {self.device}")
            
            # Load model on detected device
            self.model = SentenceTransformer(
                settings.embedding_model,
                device=self.device
            )
            
            print("Embedding model loaded successfully")
            
        except ImportError:
            print("sentence-transformers not available, falling back to Ollama")
            self.device = 'cpu'
            self.model = None
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            self.device = 'cpu'
            self.model = None
    
    def embed(self, texts: Union[str, List[str]], batch_size: int = None) -> np.ndarray:
        """Generate embeddings for texts.
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing
            
        Returns:
            Embedding vectors as numpy array
        """
        if self.model is None:
            # Fallback to Ollama
            return self._ollama_embed(texts)
        
        # Use sentence-transformers with GPU
        if isinstance(texts, str):
            texts = [texts]
        
        batch_size = batch_size or settings.embedding_batch_size
        
        with torch.no_grad():
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
        
        return embeddings
    
    def _ollama_embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Fallback to Ollama for embedding.
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            Embedding vectors as numpy array
        """
        import ollama
        
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        for text in texts:
            response = ollama.embeddings(
                model=settings.embedding_model,
                prompt=text
            )
            embeddings.append(response['embedding'])
        
        return np.array(embeddings)
    
    def get_embedding_dim(self) -> int:
        """Get embedding dimension.
        
        Returns:
            Embedding dimension
        """
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        else:
            # Default for nomic-embed-text
            return 768


# Global embedding instance
_gpu_embedding = None


def get_gpu_embedding() -> GPUEmbedding:
    """Get or create global GPU embedding instance.
    
    Returns:
        GPUEmbedding instance
    """
    global _gpu_embedding
    if _gpu_embedding is None:
        _gpu_embedding = GPUEmbedding()
    return _gpu_embedding


def embedding_func(texts: Union[str, List[str]]) -> np.ndarray:
    """Embedding function compatible with LightRAG.
    
    Args:
        texts: Single text or list of texts
        
    Returns:
        Embedding vectors as numpy array
    """
    embedding = get_gpu_embedding()
    return embedding.embed(texts)