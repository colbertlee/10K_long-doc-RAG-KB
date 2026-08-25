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
        # Use a more balanced system prompt for better knowledge base recognition
        system_prompt = """你是一个基于知识库回答问题的助手。请遵循以下规则：

1. 优先基于提供的上下文信息回答问题
2. 如果上下文中有相关信息，请详细准确地回答
3. 如果上下文中信息不完整，请如实说明上下文中的已知部分
4. 如果上下文中确实没有相关信息，请回答"知识库中未找到相关信息"
5. 保持回答准确、客观，基于事实
6. 可以使用上下文中的具体内容来支持你的回答"""

        # Run synchronous Ollama call in thread pool
        loop = asyncio.get_event_loop()
        client = ollama.Client(host=settings.llm_base_url)
        
        def sync_chat():
            print(f"LLM Request: {prompt[:100]}...", flush=True)
            try:
                # Try chat API with stream=False (timeout not supported in ollama client)
                resp = client.chat(
                    model=settings.llm_model,
                    messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': prompt}
                    ],
                    options={
                        'temperature': 0.3,  # Moderate temperature for balanced responses
                        'top_p': 0.3,        # Moderate top_p for focused but creative responses
                        'num_predict': settings.llm_max_tokens,
                        'num_ctx': 4096,     # Increased context window
                    },
                    stream=False
                )
                result = resp['message']['content']
                print(f"LLM Response length: {len(result) if result else 0}", flush=True)
                print(f"LLM Response preview: {result[:100] if result else 'empty'}...", flush=True)
                
                # Basic validation only
                if not result or not result.strip():
                    return "知识库中未找到相关信息"
                
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