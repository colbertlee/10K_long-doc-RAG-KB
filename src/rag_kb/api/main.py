"""FastAPI main application for RAG KB."""

import json
import asyncio
import requests
from typing import AsyncIterator
from pathlib import Path
from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from rag_kb.config import settings
from rag_kb.ingest.pipeline import IngestPipeline
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.security.acl import build_acl_filter
from rag_kb.api.docs_ui import router as docs_ui_router
from rag_kb.api.routes import router as api_router

app = FastAPI(title=settings.app_name)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(docs_ui_router, prefix="/docs")
app.include_router(api_router, prefix="/api/v1")

# Mount static files directory (after routers to avoid conflicts)
static_dir = Path(__file__).parent.parent.parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get('/health')
def health():
    """Health check endpoint with detailed status."""
    try:
        # Check if data directory exists
        data_dir_exists = settings.data_dir.exists()
        
        # Check if Ollama is accessible (simple check)
        ollama_status = "unknown"
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 11434))
            sock.close()
            ollama_status = "running" if result == 0 else "not_running"
        except:
            ollama_status = "not_running"
        
        return {
            'status': 'ok',
            'service': 'rag-kb',
            'version': '0.1.8',
            'data_dir_exists': data_dir_exists,
            'ollama_status': ollama_status,
            'endpoints': {
                'api_docs': '/docs',
                'docs_ui': '/docs/docs-ui',
                'current_user': '/api/v1/current-user',
                'openwebui_integration': '/openwebui-integration',
                'rag_kb_integration': '/rag-kb-integration'
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@app.post('/api/v1/ingest')
async def ingest(file: UploadFile = File(...), dept: str = '', level: str = 'Internal'):
    """Ingest a document into the RAG knowledge base.
    
    Args:
        file: Uploaded file to process
        dept: Department for ACL
        level: Access level for ACL
        
    Returns:
        Document metadata
    """
    upload_path = settings.data_dir / 'uploads' / file.filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(await file.read())
    
    pipeline = IngestPipeline()
    doc = pipeline.run(upload_path, acl={'dept': [dept], 'level': [level]})
    
    return {'doc_id': doc.doc_id, 'title': doc.title, 'pages': doc.metadata.get('pages', 0)}


@app.post('/api/v1/search')
async def search(q: str = Query(...), dept: str = '', level: str = 'Internal', top_k: int = 8):
    """Search the RAG knowledge base.
    
    Args:
        q: Search query
        dept: Department filter
        level: Access level filter
        top_k: Number of results to return
        
    Returns:
        Search results with answer and sources
    """
    user_acl = {'dept': [dept], 'level': [level]}
    rag = LightRAGAdapter()
    answer = rag.query(q, mode='hybrid')
    
    # Metadata filtering through post-filtering or sub-library implementation
    return {'answer': answer, 'sources': []}


async def _stream_answer(rag, prompt, mode='hybrid') -> AsyncIterator[str]:
    """Stream answer from LightRAG in SSE format.
    
    Args:
        rag: LightRAG adapter instance
        prompt: Query prompt
        mode: Query mode
        
    Yields:
        SSE-formatted response chunks
    """
    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, rag.query, prompt, mode)
    NL = chr(10)
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


@app.post('/api/v1/chat/completions')
async def chat_completions(body: dict):
    """OpenAI-compatible chat completions endpoint.
    
    Args:
        body: Request body with messages and parameters
        
    Returns:
        Streaming response with generated text
    """
    question = body['messages'][-1]['content']
    rag = LightRAGAdapter()
    mode = settings.lightrag_query_mode or 'hybrid'
    
    return StreamingResponse(
        _stream_answer(rag, question, mode=mode),
        media_type='text/event-stream',
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)