"""LightRAG adapter for RAG KB integration."""

import asyncio
import json
from pathlib import Path
from lightrag import LightRAG, QueryParam
from rag_kb.lightrag.llm_funcs import ollama_llm
from rag_kb.lightrag.embedding_funcs import EmbeddingFunc
from rag_kb.config import settings

NL = chr(10)


class LightRAGAdapter:
    """Adapter for LightRAG integration with custom LLM and embedding functions."""
    
    def __init__(self, working_dir=None):
        """Initialize LightRAG adapter.
        
        Args:
            working_dir: Directory for LightRAG storage (uses default from settings if None)
        """
        self.working_dir = str(Path(working_dir or settings.lightrag_working_dir))
        Path(self.working_dir).mkdir(parents=True, exist_ok=True)
        
        # Use the embedding function from embedding_funcs.py
        from rag_kb.lightrag.embedding_funcs import EmbeddingFunc
        
        # Create a new instance for this adapter
        embedding_func = EmbeddingFunc()
        
        self.rag = LightRAG(
            working_dir=self.working_dir,
            llm_model_func=ollama_llm,
            embedding_func=embedding_func,
            chunk_token_size=settings.lightrag_chunk_token_size,
        )
        
        self._initialized = False
    
    async def ensure_initialized(self):
        """Ensure LightRAG storages are initialized."""
        if not self._initialized:
            await self.rag.initialize_storages()
            self._initialized = True

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

    async def ingest(self, documents):
        """Ingest documents into LightRAG for indexing and knowledge graph generation.
        
        Args:
            documents: List of document dictionaries with 'doc_id', 'content', and 'metadata'
        """
        try:
            # Ensure storages are initialized
            await self.ensure_initialized()
            
            for doc in documents:
                content = doc.get('content', '')
                doc_id = doc.get('doc_id', '')
                
                # Don't add prefix - use original content
                # unique_content = f"[DOC_ID:{doc_id}]\n{content}"
                
                # Use async insert method
                await self.rag.ainsert(content)
                
            return True
        except Exception as e:
            print(f"LightRAG ingestion error: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def query(self, question, mode=None):
        """Query LightRAG with a question (async).
        
        Args:
            question: Query string
            mode: Query mode (naive/local/global/hybrid)
            
        Returns:
            Query response text
        """
        try:
            # Ensure storages are initialized
            await self.ensure_initialized()
            
            mode = mode or settings.lightrag_query_mode
            print(f"LightRAG query: question='{question}', mode='{mode}'")
            
            # Add system prompt to prevent hallucination
            system_prompt = """你是一个严格基于知识库回答问题的助手。请遵循以下规则：

1. 只能基于提供的知识库内容回答问题
2. 如果知识库中没有相关信息，必须直接回答"知识库中未找到相关信息"
3. 严禁编造、猜测或添加知识库之外的信息
4. 如果信息不完整，请如实说明知识库中的已知部分
5. 保持回答准确、客观，不添加主观臆测"""
            
            # Combine system prompt with user question
            enhanced_question = f"{system_prompt}\n\n用户问题：{question}"
            
            # Try naive mode first (simpler, no graph dependencies)
            result = await self.rag.aquery(
                enhanced_question,
                param=QueryParam(mode="naive", only_need_context=False, enable_rerank=False),
            )
            print(f"LightRAG result length: {len(result) if result else 0}")
            print(f"LightRAG result preview: {result[:500] if result else 'empty'}...")
            
            # Check if result indicates no information found
            if not result or not result.strip():
                return "知识库中未找到相关信息"
            
            # Check if the result is trying to say it doesn't have information
            result_lower = result.lower()
            if any(phrase in result_lower for phrase in ['不知道', '无法回答', '没有信息', '未找到', 'not found', 'don\'t know']):
                return "知识库中未找到相关信息"
            
            return result
        except Exception as e:
            print(f"LightRAG query error: {e}")
            import traceback
            traceback.print_exc()
            # Return a more informative error message
            return "知识库中未找到相关信息"

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