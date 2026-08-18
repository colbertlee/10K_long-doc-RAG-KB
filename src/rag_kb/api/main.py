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
from rag_kb.utils.logging import setup_logging, PerformanceMonitor

app = FastAPI(title=settings.app_name)

# Setup logging
logger = setup_logging(log_level=settings.log_level)
logger.info(f"Starting {settings.app_name} API server")

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


@app.get('/openwebui-integration')
async def openwebui_integration():
    """Open WebUI integration page."""
    integration_file = static_dir / "openwebui_integration.html"
    if integration_file.exists():
        return HTMLResponse(content=integration_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="""
        <html>
        <head><title>Open WebUI Integration</title></head>
        <body>
        <h1>Open WebUI Integration</h1>
        <p>Integration page not found. Please ensure static files are properly configured.</p>
        <p>Expected file: static/openwebui_integration.html</p>
        </body>
        </html>
        """)


@app.get('/rag-kb-integration')
async def rag_kb_integration():
    """RAG KB integration page."""
    integration_file = static_dir / "rag_kb_integration.html"
    if integration_file.exists():
        return HTMLResponse(content=integration_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="""
        <html>
        <head><title>RAG KB Integration</title></head>
        <body>
        <h1>RAG KB Integration</h1>
        <p>Integration page not found. Please ensure static files are properly configured.</p>
        <p>Expected file: static/rag_kb_integration.html</p>
        </body>
        </html>
        """)


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
        
        # Get system metrics
        system_metrics = logger.get_system_metrics()
        
        return {
            'status': 'ok',
            'service': 'rag-kb',
            'version': '0.3.0',
            'data_dir_exists': data_dir_exists,
            'ollama_status': ollama_status,
            'system_metrics': system_metrics,
            'endpoints': {
                'api_docs': '/docs',
                'docs_ui': '/docs/docs-ui',
                'current_user': '/api/v1/current-user',
                'openwebui_integration': '/openwebui-integration',
                'rag_kb_integration': '/rag-kb-integration',
                'metrics': '/metrics'
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@app.get('/metrics')
def metrics():
    """Get performance metrics and statistics."""
    try:
        performance_summary = logger.get_performance_summary()
        system_metrics = logger.get_system_metrics()
        
        return {
            'performance': performance_summary,
            'system': system_metrics,
            'timestamp': system_metrics['timestamp']
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return {
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
    with PerformanceMonitor(logger, "document_ingestion", 
                           {"filename": file.filename, "dept": dept, "level": level}):
        upload_path = settings.data_dir / 'uploads' / file.filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        upload_path.write_bytes(await file.read())
        
        pipeline = IngestPipeline()
        doc = pipeline.run(upload_path, acl={'dept': [dept], 'level': [level]})
        
        logger.info(f"Successfully ingested document: {doc.doc_id}")
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
    user_acl = {'dept': [dept] if dept else [], 'level': [level] if level else ['Internal']}
    rag = LightRAGAdapter()
    answer = rag.query(q, mode='hybrid', user_roles=user_acl)
    
    # Extract sources from the answer
    import re
    sources = re.findall(r'\[DATA:([^\]]+)\]', answer)
    
    return {'answer': answer, 'sources': sources, 'acl_filter': user_acl}


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