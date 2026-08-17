"""Ollama LLM functions for LightRAG."""

import ollama
from rag_kb.config import settings


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