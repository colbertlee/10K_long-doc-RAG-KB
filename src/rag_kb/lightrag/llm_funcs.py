"""Ollama LLM functions for LightRAG."""

import asyncio
import ollama
from rag_kb.config import settings


async def ollama_llm(prompt: str, **kwargs):
    """Generate LLM response using Ollama (async).
    
    Args:
        prompt: Input prompt for the LLM
        **kwargs: Additional parameters for generation
        
    Returns:
        Generated text response
    """
    try:
        # Run synchronous Ollama call in thread pool
        loop = asyncio.get_event_loop()
        client = ollama.Client(host=settings.llm_base_url)
        
        def sync_chat():
            print(f"LLM Request: {prompt[:100]}...", flush=True)
            try:
                # Try chat API with stream=False
                resp = client.chat(
                    model=settings.llm_model,
                    messages=[{'role': 'user', 'content': prompt}],
                    options={
                        'temperature': settings.llm_temperature,
                        'top_p': settings.llm_top_p,
                        'num_predict': settings.llm_max_tokens,
                    },
                    stream=False
                )
                result = resp['message']['content']
                print(f"LLM Response length: {len(result) if result else 0}", flush=True)
                print(f"LLM Response preview: {result[:100] if result else 'empty'}...", flush=True)
                return result
            except Exception as e:
                print(f"Chat API failed: {e}", flush=True)
                # Return a simple JSON fallback
                return '[]'
        
        result = await loop.run_in_executor(None, sync_chat)
        
        if not result or not result.strip():
            print("LLM returned empty response, using fallback", flush=True)
            return '[]'
            
        return result
    except Exception as e:
        print(f"Ollama LLM error: {e}")
        # Return a fallback response
        return '[]'