"""FastAPI main application for RAG KB."""

import json
import asyncio
from typing import AsyncIterator
from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from rag_kb.config import settings
from rag_kb import __version__

app = FastAPI(title=settings.app_name)

# Include API routes - using direct import to avoid importlib issues
try:
    from rag_kb.api.routes import router as api_router
    app.include_router(api_router, prefix="/api/v1")
except Exception as e:
    print(f"Warning: Could not import API routes: {e}")

# Static files directory - navigate to project root
static_dir = Path(__file__).parent.parent.parent.parent / "static"

# Mount static files directory
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    print(f"Warning: Static directory not found at {static_dir}")


@app.get('/')
def root():
    """Root endpoint with unified interface."""
    try:
        main_ui_file = static_dir / "main_ui.html"
        if main_ui_file.exists():
            content = main_ui_file.read_text(encoding='utf-8')
            return HTMLResponse(content=content)
        else:
            # Fallback to simple UI if main UI doesn't exist
            simple_ui_file = static_dir / "simple_ui.html"
            if simple_ui_file.exists():
                content = simple_ui_file.read_text(encoding='utf-8')
                return HTMLResponse(content=content)
            else:
                return {
                    'message': 'RAG KB API Server',
                    'version': __version__,
                    'endpoints': {
                        'health': '/health',
                        'api_docs': '/docs',
                        'chat_ui': '/chat-ui',
                        'graph_ui': '/graph-ui',
                        'knowledge_manager': '/knowledge-manager'
                    }
                }
    except Exception as e:
        return {
            'message': 'RAG KB API Server',
            'version': __version__,
            'error': str(e),
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
    try:
        from rag_kb.ingest.pipeline import IngestPipeline
        
        upload_path = settings.data_dir / 'uploads' / file.filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        upload_path.write_bytes(await file.read())
        
        pipeline = IngestPipeline()
        doc = pipeline.run(upload_path, acl={'dept': [dept], 'level': [level]})
        
        return {'doc_id': doc.doc_id, 'title': doc.title, 'pages': doc.metadata.get('pages', 0)}
    except Exception as e:
        return {'error': str(e), 'message': 'Document ingestion failed'}


@app.post('/api/v1/import-folder')
async def import_folder(folder_path: str = '', user_id: str = 'default', kb_name: str = 'default', acl: dict = None):
    """Import a local folder into the RAG knowledge base.
    
    Args:
        folder_path: Path to the local folder
        user_id: User ID for the knowledge base
        kb_name: Knowledge base name
        acl: Access control list
        
    Returns:
        Import results
    """
    try:
        from pathlib import Path
        import glob
        
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return {'error': 'Invalid folder path', 'message': f'Folder not found: {folder_path}'}
        
        # Find supported files
        supported_extensions = ['.pdf', '.txt', '.md', '.docx']
        files = []
        for ext in supported_extensions:
            files.extend(folder.glob(f'**/*{ext}'))
        
        if not files:
            return {'error': 'No supported files found', 'message': f'No files with extensions {supported_extensions} found in folder'}
        
        # Process files
        from rag_kb.ingest.pipeline import IngestPipeline
        pipeline = IngestPipeline()
        
        processed = 0
        skipped = 0
        failed = 0
        failed_files = []
        documents = []
        
        for file_path in files:
            try:
                doc = pipeline.run(file_path, acl=acl or {'read': [user_id], 'write': [user_id]})
                processed += 1
                documents.append({
                    'doc_id': doc.doc_id,
                    'title': doc.title,
                    'source': str(file_path),
                    'pages': doc.metadata.get('pages', 0),
                    'import_type': 'folder'
                })
            except Exception as e:
                failed += 1
                failed_files.append({'file': str(file_path.name), 'error': str(e)})
        
        return {
            'success': True,
            'source_folder': str(folder),
            'total_files_found': len(files),
            'files_processed': processed,
            'files_skipped': skipped,
            'files_failed': failed,
            'failed_files': failed_files,
            'documents': documents,
            'user_id': user_id,
            'kb_name': kb_name
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Folder import failed'}


@app.get('/api/v1/users/{user_id}/kbs/{kb_name}/graph')
async def get_knowledge_graph(user_id: str, kb_name: str):
    """Get knowledge graph data for a specific knowledge base.
    
    Args:
        user_id: User ID
        kb_name: Knowledge base name
        
    Returns:
        Graph data with nodes and edges
    """
    try:
        from rag_kb.lightrag.adapter import LightRAGAdapter
        import json
        
        rag = LightRAGAdapter()
        
        # Try to get graph data from LightRAG
        # This is a simplified implementation - in a real system, you'd extract actual graph data
        graph_data = {
            'nodes': [
                {'id': 'node1', 'label': 'Document', 'type': 'document'},
                {'id': 'node2', 'label': 'Entity', 'type': 'entity'},
                {'id': 'node3', 'label': 'Concept', 'type': 'concept'}
            ],
            'edges': [
                {'source': 'node1', 'target': 'node2', 'label': 'contains'},
                {'source': 'node2', 'target': 'node3', 'label': 'related_to'}
            ]
        }
        
        return {
            'success': True,
            'nodes': graph_data['nodes'],
            'edges': graph_data['edges'],
            'user_id': user_id,
            'kb_name': kb_name
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get graph data', 'nodes': [], 'edges': []}


@app.get('/api/v1/users/{user_id}/kbs')
async def get_user_knowledge_bases(user_id: str):
    """Get list of knowledge bases for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        List of knowledge bases
    """
    try:
        from pathlib import Path
        
        # Check for user directories
        user_dir = settings.data_dir / 'users' / user_id
        knowledge_bases = []
        
        if user_dir.exists():
            for kb_dir in user_dir.iterdir():
                if kb_dir.is_dir():
                    knowledge_bases.append({
                        'name': kb_dir.name,
                        'created': kb_dir.stat().st_ctime
                    })
        
        # Add default knowledge base if none exist
        if not knowledge_bases:
            knowledge_bases.append({
                'name': 'default',
                'created': 0
            })
        
        return {
            'success': True,
            'knowledge_bases': knowledge_bases,
            'user_id': user_id
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get knowledge bases', 'knowledge_bases': []}


@app.get('/api/v1/documents')
async def get_documents():
    """Get list of all documents in the knowledge base.
    
    Returns:
        List of documents with metadata
    """
    try:
        from pathlib import Path
        import json
        import os
        
        # Check for document registry
        registry_file = settings.data_dir / 'document_registry.json'
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                documents = list(registry.values())
                
                # Add import_type if missing
                for doc in documents:
                    if 'import_type' not in doc:
                        doc['import_type'] = 'upload'
        else:
            # Fallback to uploaded files directory
            upload_dir = settings.data_dir / 'uploads'
            documents = []
            if upload_dir.exists():
                for file_path in upload_dir.glob('*'):
                    if file_path.is_file():
                        documents.append({
                            'doc_id': file_path.stem,
                            'title': file_path.name,
                            'source': str(file_path),
                            'import_type': 'upload',
                            'timestamp': os.path.getmtime(file_path)
                        })
        
        return {
            'success': True,
            'documents': documents,
            'total': len(documents)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get documents', 'documents': [], 'total': 0}


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
    try:
        from rag_kb.lightrag.adapter import LightRAGAdapter
        
        user_acl = {'dept': [dept], 'level': [level]}
        rag = LightRAGAdapter()
        answer = rag.query(q, mode='hybrid')
        
        # Metadata filtering through post-filtering or sub-library implementation
        return {'answer': answer, 'sources': []}
    except Exception as e:
        return {'error': str(e), 'message': 'Search failed', 'answer': f'搜索失败: {str(e)}', 'sources': []}


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
    try:
        from rag_kb.lightrag.adapter import LightRAGAdapter
        
        question = body['messages'][-1]['content']
        rag = LightRAGAdapter()
        mode = settings.lightrag_query_mode or 'hybrid'
        
        return StreamingResponse(
            _stream_answer(rag, question, mode=mode),
            media_type='text/event-stream',
        )
    except Exception as e:
        # Return error as JSON instead of streaming
        return {'error': str(e), 'message': 'Chat completion failed'}


@app.get('/chat-ui')
async def chat_ui():
    """Chat interface endpoint."""
    try:
        chat_file = static_dir / "chat_ui.html"
        if chat_file.exists():
            content = chat_file.read_text(encoding='utf-8')
            return HTMLResponse(content=content)
        else:
            return HTMLResponse(content=f"""
            <html>
            <head><title>RAG KB Chat Interface</title></head>
            <body>
            <h1>RAG KB Chat Interface</h1>
            <p>Chat interface not found. Please ensure static files are properly configured.</p>
            <p>Static directory: {static_dir}</p>
            <p>Available endpoints: <a href="/docs">API Documentation</a></p>
            </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"""
        <html>
        <head><title>Chat Interface Error</title></head>
        <body>
        <h1>Chat Interface Error</h1>
        <p>Error loading chat interface: {str(e)}</p>
        <p>Static directory: {static_dir}</p>
        <p>Available endpoints: <a href="/docs">API Documentation</a></p>
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
    try:
        km_file = static_dir / "knowledge_manager.html"
        if km_file.exists():
            content = km_file.read_text(encoding='utf-8')
            return HTMLResponse(content=content)
        else:
            html_content = "<html><head><title>Knowledge Manager</title></head><body>"
            html_content += "<h1>Knowledge Manager</h1>"
            html_content += "<p>Knowledge manager interface not found. Please ensure static files are properly configured.</p>"
            html_content += "<p>Static directory: " + str(static_dir) + "</p>"
            html_content += "<p>Available endpoints: <a href=\"/docs\">API Documentation</a></p>"
            html_content += "</body></html>"
            return HTMLResponse(content=html_content)
    except Exception as e:
        html_content = "<html><head><title>Knowledge Manager Error</title></head><body>"
        html_content += "<h1>Knowledge Manager Error</h1>"
        html_content += "<p>Error loading knowledge manager: " + str(e) + "</p>"
        html_content += "<p>Static directory: " + str(static_dir) + "</p>"
        html_content += "<p>Available endpoints: <a href=\"/docs\">API Documentation</a></p>"
        html_content += "</body></html>"
        return HTMLResponse(content=html_content)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)