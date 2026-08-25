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
        # Add strict anti-hallucination system prompt
        system_prompt = """你是一个严格基于提供的上下文信息回答问题的助手。请遵循以下严格规则：

1. 只能基于提供的上下文信息回答问题，不能使用任何外部知识
2. 如果提供的上下文中没有相关信息，必须直接回答"提供的上下文中没有相关信息"
3. 严禁编造、猜测或添加上下文之外的信息
4. 如果信息不完整，请如实说明上下文中的已知部分
5. 保持回答准确、客观，不添加主观臆测
6. 不要提供一般性的定义、概念解释或背景知识
7. 只回答与上下文直接相关的内容"""

        # Combine system prompt with user prompt
        enhanced_prompt = f"{system_prompt}\n\n上下文信息：\n{prompt}"
        
        # Run synchronous Ollama call in thread pool
        loop = asyncio.get_event_loop()
        client = ollama.Client(host=settings.llm_base_url)
        
        def sync_chat():
            print(f"LLM Request: {enhanced_prompt[:100]}...", flush=True)
            try:
                # Try chat API with stream=False
                resp = client.chat(
                    model=settings.llm_model,
                    messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': prompt}
                    ],
                    options={
                        'temperature': 0.1,  # Lower temperature for more deterministic responses
                        'top_p': 0.1,        # Lower top_p for more focused responses
                        'num_predict': settings.llm_max_tokens,
                    },
                    stream=False
                )
                result = resp['message']['content']
                print(f"LLM Response length: {len(result) if result else 0}", flush=True)
                print(f"LLM Response preview: {result[:100] if result else 'empty'}...", flush=True)
                
                # Post-process response for anti-hallucination
                if not result or not result.strip():
                    return "提供的上下文中没有相关信息"
                
                # Check for generic knowledge patterns
                generic_patterns = [
                    '简单来说', '一般来说', '通常情况下', '总的来说', 
                    '这是一个', '这是一个非常', '这是一个极具',
                    '根据不同的语境', '可以从多个角度', '在日常生活中',
                    '在现代物理学中', '在机器学习中', '在计算机科学中',
                    '量子力学', '监督学习', '深度学习', '人工智能'
                ]
                
                if any(pattern in result for pattern in generic_patterns):
                    # If response contains generic knowledge, check if it references context
                    context_indicators = ['根据上下文', '从文档中', '根据提供的信息', '上下文中提到']
                    if not any(indicator in result for indicator in context_indicators):
                        return "提供的上下文中没有相关信息"
                
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