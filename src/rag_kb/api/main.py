"""FastAPI main application for RAG KB."""

import json
import asyncio
from typing import AsyncIterator
from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from rag_kb.config import settings

app = FastAPI(title=settings.app_name)

# Include API routes - using direct import to avoid importlib issues
try:
    from rag_kb.api.routes import router as api_router
    app.include_router(api_router, prefix="/api/v1")
except Exception as e:
    print(f"Warning: Could not import API routes: {e}")

# Static files directory
static_dir = Path(__file__).parent.parent / "static"

# Mount static files directory
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get('/')
def root():
    """Root endpoint with system information."""
    return {
        'message': 'RAG KB API Server',
        'version': '0.4.4',
        'endpoints': {
            'health': '/health',
            'api_docs': '/docs',
            'chat_ui': '/chat-ui',
            'graph_ui': '/graph-ui',
            'knowledge_manager': '/knowledge-manager'
        }
    }


@app.get('/health')
def health():
    """Health check endpoint."""
    return {'status': 'ok'}


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
    from rag_kb.ingest.pipeline import IngestPipeline
    
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
    from rag_kb.lightrag.adapter import LightRAGAdapter
    
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
    from rag_kb.lightrag.adapter import LightRAGAdapter
    
    question = body['messages'][-1]['content']
    rag = LightRAGAdapter()
    mode = settings.lightrag_query_mode or 'hybrid'
    
    return StreamingResponse(
        _stream_answer(rag, question, mode=mode),
        media_type='text/event-stream',
    )


@app.get('/chat-ui')
async def chat_ui():
    """Chat interface endpoint."""
    chat_file = static_dir / "chat_ui.html"
    if chat_file.exists():
        return HTMLResponse(content=chat_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="""
        <html>
        <head><title>RAG KB Chat Interface</title></head>
        <body>
        <h1>RAG KB Chat Interface</h1>
        <p>Chat interface not found. Please ensure static files are properly configured.</p>
        <p>Available endpoints: <a href="/docs">API Documentation</a></p>
        <p>Or use: <a href="/static/simple_ui.html">Simple UI</a></p>
        </body>
        </html>
        """)


@app.get('/graph-ui')
async def graph_ui():
    """Knowledge graph visualization interface."""
    graph_file = static_dir / "graph_ui.html"
    if graph_file.exists():
        return HTMLResponse(content=graph_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="""
        <html>
        <head><title>Knowledge Graph Visualization</title></head>
        <body>
        <h1>Knowledge Graph Visualization</h1>
        <p>Graph visualization interface not found. Please ensure static files are properly configured.</p>
        <p>Available endpoints: <a href="/docs">API Documentation</a></p>
        <p>Or use: <a href="/static/graph_ui.html">Direct Graph UI</a></p>
        </body>
        </html>
        """)


@app.get('/knowledge-manager')
async def knowledge_manager():
    """Unified knowledge management interface."""
    km_file = static_dir / "knowledge_manager.html"
    if km_file.exists():
        return HTMLResponse(content=km_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="""
        <html>
        <head><title>Knowledge Manager</title></head>
        <body>
        <h1>Knowledge Manager</h1>
        <p>Knowledge manager interface not found. Please ensure static files are properly configured.</p>
        <p>Available endpoints: <a href="/docs">API Documentation</a></p>
        </body>
        </html>
        """)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)