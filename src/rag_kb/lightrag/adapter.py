"""LightRAG adapter for RAG KB integration."""

import asyncio
import json
from pathlib import Path
from lightrag import LightRAG, QueryParam
from rag_kb.lightrag.llm_funcs import ollama_llm
from rag_kb.lightrag.embedding_funcs import ollama_embed
from rag_kb.config import settings

NL = chr(10)


class LightRAGAdapter:
    """Adapter for LightRAG integration with custom LLM and embedding functions."""
    
    def __init__(self, working_dir=None):
        """Initialize LightRAG adapter.
        
        Args:
            working_dir: Directory for LightRAG storage (uses default from settings if None)
        """
        self.working_dir = Path(working_dir or settings.lightrag_working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.rag = LightRAG(
            working_dir=str(self.working_dir),
            llm_model_func=ollama_llm,
            embedding_func=ollama_embed,
            chunk_token_size=settings.lightrag_chunk_token_size,
            max_token=settings.lightrag_max_token,
        )

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

    def query(self, question, mode=None):
        """Query LightRAG with a question.
        
        Args:
            question: Query string
            mode: Query mode (naive/local/global/hybrid)
            
        Returns:
            Query response text
        """
        mode = mode or settings.lightrag_query_mode
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