"""LightRAG adapter for RAG KB integration."""

import sys
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
            # Try to initialize pipeline status but don't fail if it doesn't work
            try:
                from lightrag.kg.shared_storage import initialize_pipeline_status
                await initialize_pipeline_status()
                print("Pipeline status initialized successfully", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"Warning: Could not initialize pipeline status: {e}", file=sys.stderr, flush=True)
                # Try alternative initialization
                try:
                    from lightrag.kg.shared_storage import initialize_chunk_entity_relation_graph
                    await initialize_chunk_entity_relation_graph()
                    print("Alternative graph initialization successful", file=sys.stderr, flush=True)
                except Exception as e2:
                    print(f"Alternative initialization also failed: {e2}", file=sys.stderr, flush=True)
                    # Try manual initialization
                    try:
                        from lightrag.kg.shared_storage import namespace_data
                        await namespace_data("pipeline_status", {"status": "initialized"})
                        print("Manual pipeline status initialization successful", file=sys.stderr, flush=True)
                    except Exception as e3:
                        print(f"Manual initialization also failed: {e3}", file=sys.stderr, flush=True)
                        # Continue anyway - basic functionality should still work
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
            
            import sys
            print(f"Starting ingestion of {len(documents)} documents", file=sys.stderr, flush=True)
            
            # Use async insert method directly on the same event loop
            for doc in documents:
                content = doc.get('content', '')
                doc_id = doc.get('doc_id', '')
                metadata = doc.get('metadata', {})
                
                if not content.strip():
                    print(f"Skipping empty document: {doc_id}", file=sys.stderr, flush=True)
                    continue
                
                # Format document with metadata for better indexing
                formatted_content = self._format_document(content, doc_id, metadata)
                
                # Use async insert method directly on the same event loop
                try:
                    print(f"Ingesting document: {doc_id} (content length: {len(formatted_content)})", file=sys.stderr, flush=True)
                    await self.rag.ainsert(formatted_content)
                    print(f"Successfully ingested document: {doc_id}", file=sys.stderr, flush=True)
                except Exception as e:
                    print(f"Error ingesting document {doc_id}: {e}", file=sys.stderr, flush=True)
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    # Continue with other documents even if one fails
            
            print(f"Document ingestion completed", file=sys.stderr, flush=True)
            return True
        except Exception as e:
            print(f"LightRAG ingestion error: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return False
    
    def _format_document(self, content, doc_id, metadata):
        """Format document content with metadata for better indexing.
        
        Args:
            content: Document content
            doc_id: Document ID
            metadata: Document metadata
            
        Returns:
            Formatted document string
        """
        # Add document metadata as header
        header = f"[doc_id={doc_id}"
        if metadata:
            if 'title' in metadata:
                header += f";title={metadata['title']}"
            if 'pages' in metadata:
                header += f";pages={metadata['pages']}"
            if 'source' in metadata:
                header += f";source={metadata['source']}"
        header += "]"
        
        # Combine header with content
        return f"{header}\n\n{content}"

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
            print(f"LightRAG query: question='{question}', mode='{mode}'", file=sys.stderr, flush=True)
            
            # Try naive mode first (simpler, no graph dependencies)
            result = await self.rag.aquery(
                question,
                param=QueryParam(mode="naive", only_need_context=False, enable_rerank=False),
            )
            print(f"LightRAG result length: {len(result) if result else 0}", file=sys.stderr, flush=True)
            print(f"LightRAG result preview: {result[:500] if result else 'empty'}...", file=sys.stderr, flush=True)
            
            # Check if we got any meaningful result
            if not result or not result.strip():
                print("Empty result from LightRAG, trying hybrid mode", file=sys.stderr, flush=True)
                # Try hybrid mode as fallback
                result = await self.rag.aquery(
                    question,
                    param=QueryParam(mode="hybrid", only_need_context=False, enable_rerank=False),
                )
                print(f"Hybrid mode result length: {len(result) if result else 0}", file=sys.stderr, flush=True)
            
            # If still no result, return informative message
            if not result or not result.strip():
                return "知识库中未找到相关信息。请确保文档已正确上传和索引。"
            
            # Only filter obviously empty or error responses
            if "提供的上下文中没有相关信息" in result or "知识库中未找到相关信息" in result:
                return result  # Let LLM's own judgment stand
            
            return result
        except Exception as e:
            print(f"LightRAG query error: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Return a more informative error message
            return f"查询出错: {str(e)}。请检查文档是否已正确索引。"

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