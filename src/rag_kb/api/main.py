"""FastAPI main application for RAG KB."""

import json
import asyncio
import requests
from typing import AsyncIterator
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
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

# Custom search endpoint (before router includes to avoid conflicts)
@app.post('/api/v1/search')
async def search(body: dict):
    """Search the RAG knowledge base.
    
    Args:
        body: Request body with q, dept, level, top_k parameters
        
    Returns:
        Search results with answer and sources
    """
    try:
        q = body.get('q', '')
        dept = body.get('dept', '')
        level = body.get('level', 'Internal')
        top_k = body.get('top_k', 8)
        
        if not q:
            return {'error': 'Query parameter "q" is required', 'status': 'failed'}
        
        user_acl = {'dept': [dept] if dept else [], 'level': [level] if level else ['Internal']}
        rag = LightRAGAdapter()
        
        # Use async query to avoid event loop issues
        answer = await rag.aquery(q, mode='hybrid', user_roles=user_acl)
        
        if answer is None:
            return {'error': 'No results found', 'status': 'failed', 'results': []}
        
        # Parse the answer to extract results
        # LightRAG returns a string with the answer and sources
        results = []
        try:
            # Try to extract sources from the answer
            import re
            source_pattern = r'\[([^\]]+)\]'
            sources = re.findall(source_pattern, answer)
            for source in sources:
                results.append({'source': source, 'content': answer})
        except:
            results.append({'source': 'unknown', 'content': answer})
        
        return {
            'status': 'success',
            'answer': answer,
            'results': results[:top_k]
        }
    except Exception as e:
        return {'error': str(e), 'status': 'failed'}

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
        
        # Get system metrics
        from rag_kb.utils.logging import get_logger
        current_logger = get_logger()
        system_metrics = current_logger.get_system_metrics()
        
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
        from rag_kb.utils.logging import get_logger
        current_logger = get_logger()
        current_logger.error(f"Health check failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@app.get('/metrics')
def metrics():
    """Get performance metrics and statistics."""
    try:
        # Get logger instance if available
        from rag_kb.utils.logging import get_logger
        current_logger = get_logger()
        
        performance_summary = current_logger.get_performance_summary()
        system_metrics = current_logger.get_system_metrics()
        
        return {
            'performance': performance_summary,
            'system': system_metrics,
            'timestamp': system_metrics['timestamp']
        }
    except Exception as e:
        # Return basic metrics if logger not fully initialized
        return {
            'performance': {'message': 'No performance data available'},
            'system': {'message': 'System metrics not available'},
            'error': str(e)
        }


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


@app.get('/graph-ui')
async def graph_ui():
    """Knowledge graph visualization interface."""
    graph_ui_file = static_dir / "graph_ui.html"
    if graph_ui_file.exists():
        return HTMLResponse(content=graph_ui_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="""
        <html>
        <head><title>Graph UI</title></head>
        <body>
        <h1>Knowledge Graph Visualization</h1>
        <p>Graph interface not found. Please ensure static files are properly configured.</p>
        </body>
        </html>
        """)


@app.get('/chat-ui')
async def chat_ui():
    """Chat interface for conversational RAG."""
    chat_ui_file = static_dir / "chat_ui.html"
    if chat_ui_file.exists():
        return HTMLResponse(content=chat_ui_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="""
        <html>
        <head><title>Chat UI</title></head>
        <body>
        <h1>Chat Interface</h1>
        <p>Chat interface not found. Please ensure static files are properly configured.</p>
        </body>
        </html>
        """)


@app.get('/')
async def root():
    """Root endpoint - redirect to simple UI."""
    simple_ui_file = static_dir / "simple_ui.html"
    if simple_ui_file.exists():
        return HTMLResponse(content=simple_ui_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="""
        <html>
        <head><title>RAG KB</title></head>
        <body>
        <h1>RAG Knowledge Base</h1>
        <p>Welcome to RAG KB. Please visit:</p>
        <ul>
            <li><a href="/docs">API Documentation</a></li>
            <li><a href="/docs/docs-ui">Document Management UI</a></li>
            <li><a href="/health">Health Check</a></li>
        </ul>
        </body>
        </html>
        """)


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
    try:
        # Get logger instance
        from rag_kb.utils.logging import get_logger
        current_logger = get_logger()
        
        with PerformanceMonitor(current_logger, "document_ingestion", 
                               {"filename": file.filename, "dept": dept, "level": level}):
            upload_path = settings.data_dir / 'uploads' / file.filename
            upload_path.parent.mkdir(parents=True, exist_ok=True)
            upload_path.write_bytes(await file.read())
            
            pipeline = IngestPipeline()
            doc = pipeline.run(upload_path, acl={'dept': [dept], 'level': [level]})
            
            current_logger.info(f"Successfully ingested document: {doc.doc_id}")
            return {'doc_id': doc.doc_id, 'title': doc.title, 'pages': doc.metadata.get('pages', 0)}
    except Exception as e:
        return {'error': str(e), 'status': 'failed'}


@app.post('/api/v1/search')
async def search(body: dict):
    """Search the RAG knowledge base.
    
    Args:
        body: Request body with q, dept, level, top_k parameters
        
    Returns:
        Search results with answer and sources
    """
    try:
        q = body.get('q', '')
        dept = body.get('dept', '')
        level = body.get('level', 'Internal')
        top_k = body.get('top_k', 8)
        
        if not q:
            return {'error': 'Query parameter "q" is required', 'status': 'failed'}
        
        user_acl = {'dept': [dept] if dept else [], 'level': [level] if level else ['Internal']}
        rag = LightRAGAdapter()
        
        # Use async query to avoid event loop issues
        answer = await rag.aquery(q, mode='hybrid', user_roles=user_acl)
        
        # Handle None response (no data available)
        if answer is None:
            return {
                'answer': 'No relevant information found in the knowledge base.',
                'sources': [],
                'acl_filter': user_acl,
                'results': [],
                'status': 'success'
            }
        
        # Extract sources from the answer
        import re
        sources = re.findall(r'\[DATA:([^\]]+)\]', answer)
        
        return {
            'answer': answer, 
            'sources': sources, 
            'acl_filter': user_acl, 
            'results': sources[:top_k],
            'status': 'success'
        }
    except Exception as e:
        return {'error': str(e), 'status': 'failed'}


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