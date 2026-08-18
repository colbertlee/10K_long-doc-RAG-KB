"""LightRAG adapter for RAG KB integration."""

import asyncio
import json
import os
import numpy as np
from pathlib import Path
from functools import partial
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.utils import EmbeddingFunc, wrap_embedding_func_with_attrs
    from lightrag.llm.ollama import ollama_embed
except ImportError:
    LightRAG = None
    QueryParam = None
    EmbeddingFunc = None
    wrap_embedding_func_with_attrs = None
    ollama_embed = None
from rag_kb.config import settings

NL = chr(10)


async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    """LLM function for LightRAG using Ollama."""
    import ollama
    client = ollama.Client(host=settings.llm_base_url)
    
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.extend(history_messages)
    messages.append({'role': 'user', 'content': prompt})
    
    resp = client.chat(
        model=settings.llm_model,
        messages=messages,
        options={
            'temperature': settings.llm_temperature,
            'top_p': settings.llm_top_p,
            'num_predict': settings.llm_max_tokens,
        },
    )
    return resp['message']['content']


@wrap_embedding_func_with_attrs(
    embedding_dim=1024,
    max_token_size=8192,
)
async def embedding_func(texts: list) -> np.ndarray:
    """Embedding function for LightRAG using Ollama."""
    import ollama
    client = ollama.Client(host=settings.embedding_base_url)
    resp = client.embed(model=settings.embedding_model, input=texts)
    return np.array(resp['embeddings'], dtype=np.float32)


class LightRAGAdapter:
    """Adapter for LightRAG integration with custom LLM and embedding functions."""
    
    def __init__(self, working_dir=None):
        """Initialize LightRAG adapter.
        
        Args:
            working_dir: Directory for LightRAG storage (uses default from settings if None)
        """
        if LightRAG is None:
            raise ImportError("LightRAG is not installed. Install it with: pip install lightrag-hku")
        
        self.working_dir = Path(working_dir or settings.lightrag_working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LightRAG with proper async functions
        try:
            self.rag = LightRAG(
                working_dir=str(self.working_dir),
                llm_model_func=llm_model_func,
                embedding_func=embedding_func,
                chunk_token_size=settings.lightrag_chunk_token_size,
            )
        except Exception as e:
            # Fallback with minimal configuration
            try:
                self.rag = LightRAG(
                    working_dir=str(self.working_dir),
                    llm_model_func=llm_model_func,
                    embedding_func=embedding_func,
                )
            except Exception as e2:
                raise ImportError(f"Failed to initialize LightRAG: {e}, {e2}")

    def insert_chunks(self, chunks):
        """Insert chunks into LightRAG index.
        
        Args:
            chunks: List of Chunk objects to index
        """
        parts = []
        for c in chunks:
            meta = getattr(c, 'metadata', {}) or {}
            header = (
                '[source=' + str(meta.get('source', '')) +
                ';category=' + str(meta.get('category', '')) +
                ';product_id=' + str(meta.get('product_id', '')) +
                ';doc_id=' + str(c.doc_id) + ']'
            )
            parts.append(header + NL + c.text)
        doc_text = (NL + NL).join(parts)
        self.rag.insert(doc_text)

    def query(self, question, mode=None, user_roles=None):
        """Query LightRAG with a question and optional ACL filtering.
        
        Args:
            question: Query string
            mode: Query mode (naive/local/global/hybrid)
            user_roles: Optional user roles for ACL filtering
            
        Returns:
            Query response text
        """
        mode = mode or settings.lightrag_query_mode
        
        # Apply ACL pre-filtering if user roles are provided
        if user_roles:
            from rag_kb.security.acl import apply_pre_filter_query
            question = apply_pre_filter_query(question, user_roles)
        
        return self.rag.query(
            question,
            param=QueryParam(mode=mode, only_need_context=False),
        )

    async def stream_query(self, question, mode=None):
        """Stream query response in SSE format.
        
        Args:
            question: Query string
            mode: Query mode (naive/local/global/hybrid)
            
        Yields:
            SSE-formatted response chunks
        """
        loop = asyncio.get_event_loop()
        mode = mode or settings.lightrag_query_mode
        answer = await loop.run_in_executor(
            None,
            self.rag.query,
            question,
            QueryParam(mode=mode, only_need_context=False),
        )
        SSE_END = NL * 2
        buf = ''
        for ch in answer:
            buf += ch
            if ch in ('。', '？', '！', '.', '?', '!', NL):
                payload = json.dumps({'choices': [{'delta': {'content': buf}}]})
                yield 'data: ' + payload + SSE_END
                buf = ''
        if buf:
            yield 'data: ' + json.dumps({'choices': [{'delta': {'content': buf}}]}) + SSE_END
        yield 'data: [DONE]' + SSE_END