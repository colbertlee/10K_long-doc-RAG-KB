"""Ollama LLM functions for LightRAG."""

import ollama
from rag_kb.config import settings

# For newer LightRAG versions that expect EmbeddingFunc and LLMFunc
try:
    from lightrag import LLMFunc, EmbeddingFunc
except ImportError:
    LLMFunc = None
    EmbeddingFunc = None


def ollama_llm(prompt: str, **kwargs):
    """Generate LLM response using Ollama.
    
    Args:
        prompt: Input prompt for the LLM
        **kwargs: Additional parameters for generation
        
    Returns:
        Generated text response
    """
    client = ollama.Client(host=settings.llm_base_url)
    resp = client.chat(
        model=settings.llm_model,
        messages=[{'role': 'user', 'content': prompt}],
        options={
            'temperature': settings.llm_temperature,
            'top_p': settings.llm_top_p,
            'num_predict': settings.llm_max_tokens,
        },
    )
    return resp['message']['content']


class OllamaLLMWrapper:
    """Wrapper for Ollama LLM to support LightRAG's LLMFunc interface."""
    
    def __call__(self, prompt: str, **kwargs):
        return ollama_llm(prompt, **kwargs)


# Create LLMFunc instance if available
if LLMFunc is not None:
    ollama_llm_func = LLMFunc(callback=OllamaLLMWrapper())
else:
    ollama_llm_func = ollama_llm