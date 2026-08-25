"""FastAPI main application for RAG KB."""

import json
import asyncio
from typing import AsyncIterator, List, Dict, Any
from fastapi import FastAPI, File, Query, UploadFile, Body
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
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
    """Ingest a document into the RAG knowledge base with full processing.
    
    Args:
        file: Uploaded file to process
        dept: Department for ACL
        level: Access level for ACL
        
    Returns:
        Document metadata with processing status
    """
    try:
        from rag_kb.ingest.pipeline import IngestPipeline
        from rag_kb.lightrag.adapter import LightRAGAdapter
        import json
        import time
        
        upload_path = settings.data_dir / 'uploads' / file.filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        upload_path.write_bytes(await file.read())
        
        # Step 1: Parse and clean document
        pipeline = IngestPipeline()
        doc = pipeline.run(upload_path, acl={'dept': [dept], 'level': [level]})
        
        # Step 2: Semantic chunking (using simple chunking for reliability)
        chunks = []
        simple_chunk_size = 1000
        for i in range(0, len(doc.content), simple_chunk_size):
            chunk_text = doc.content[i:i+simple_chunk_size]
            from rag_kb.models import Chunk
            import uuid
            chunks.append(Chunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=doc.doc_id,
                text=chunk_text,
                metadata=doc.metadata
            ))
        
        # Step 3: LightRAG indexing and knowledge graph generation
        graph_generated = False
        indexing_error = None
        try:
            import sys
            print("Starting LightRAG indexing...", file=sys.stderr, flush=True)
            rag = LightRAGAdapter()
            print("LightRAG adapter created for indexing", file=sys.stderr, flush=True)
            
            # Insert document into LightRAG for indexing and graph generation
            print(f"Attempting to ingest document {doc.doc_id}", file=sys.stderr, flush=True)
            ingest_success = await rag.ingest([{
                'doc_id': doc.doc_id,
                'content': doc.content,
                'metadata': doc.metadata
            }])
            
            print(f"Ingest result: {ingest_success}", file=sys.stderr, flush=True)
            
            if not ingest_success:
                raise Exception("LightRAG ingestion returned False")
                
            graph_generated = True
            print("LightRAG indexing completed successfully", file=sys.stderr, flush=True)
        except Exception as e:
            # LightRAG indexing failed, but document was parsed
            print(f"LightRAG indexing failed: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            graph_generated = False
            indexing_error = str(e)
        
        # Save document to registry
        registry_file = settings.data_dir / 'document_registry.json'
        registry = {}
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        
        registry[doc.doc_id] = {
            'doc_id': doc.doc_id,
            'title': doc.title,
            'content': doc.content,
            'metadata': doc.metadata,
            'acl': doc.acl,
            'chunks_count': len(chunks),
            'import_type': 'upload',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        if graph_generated:
            return {
                'doc_id': doc.doc_id, 
                'title': doc.title, 
                'pages': doc.metadata.get('pages', 0),
                'chunks': len(chunks),
                'status': 'indexed',
                'graph_generated': True
            }
        else:
            return {
                'doc_id': doc.doc_id, 
                'title': doc.title, 
                'pages': doc.metadata.get('pages', 0),
                'chunks': len(chunks),
                'status': 'parsed_only',
                'graph_generated': False,
                'error': f'LightRAG indexing failed: {indexing_error}'
            }
        
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
        import json
        import uuid
        
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
        from rag_kb.lightrag.adapter import LightRAGAdapter
        import json
        
        pipeline = IngestPipeline()
        chunker = StructuredChunker()
        rag = LightRAGAdapter()
        
        processed = 0
        skipped = 0
        failed = 0
        failed_files = []
        documents = []
        indexed_documents = []
        
        for file_path in files:
            try:
                # Step 1: Parse and clean
                doc = pipeline.run(file_path, acl=acl or {'read': [user_id], 'write': [user_id]})
                processed += 1
                
                # Step 2: Semantic chunking (using simple chunking for reliability)
                chunks = []
                simple_chunk_size = 1000
                for i in range(0, len(doc.content), simple_chunk_size):
                    chunk_text = doc.content[i:i+simple_chunk_size]
                    from rag_kb.models import Chunk
                    import uuid
                    chunks.append(Chunk(
                        chunk_id=str(uuid.uuid4()),
                        doc_id=doc.doc_id,
                        text=chunk_text,
                        metadata=doc.metadata
                    ))
                
                # Step 3: LightRAG indexing
                try:
                    ingest_success = rag.ingest([{
                        'doc_id': doc.doc_id,
                        'content': doc.content,
                        'metadata': doc.metadata
                    }])
                    if ingest_success:
                        indexed_documents.append(doc.doc_id)
                    else:
                        print(f"LightRAG indexing failed for {file_path.name}: ingestion returned False")
                except Exception as e:
                    print(f"LightRAG indexing failed for {file_path.name}: {e}")
                
                documents.append({
                    'doc_id': doc.doc_id,
                    'title': doc.title,
                    'source': str(file_path),
                    'pages': doc.metadata.get('pages', 0),
                    'import_type': 'folder',
                    'folder_id': str(uuid.uuid4()),
                    'chunks': len(chunks),
                    'indexed': doc.doc_id in indexed_documents
                })
            except Exception as e:
                failed += 1
                failed_files.append({'file': str(file_path.name), 'error': str(e)})
        
        # Save folder record
        folder_id = str(uuid.uuid4())
        import time
        folder_record = {
            'folder_id': folder_id,
            'folder_name': folder.name,
            'folder_path': str(folder),
            'file_count': processed,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save to folder registry
        registry_file = settings.data_dir / 'folder_registry.json'
        folder_registry = {}
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                folder_registry = json.load(f)
        
        folder_registry[folder_id] = folder_record
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(folder_registry, f, indent=2, ensure_ascii=False)
        
        # Save documents to document registry
        doc_registry_file = settings.data_dir / 'document_registry.json'
        doc_registry = {}
        if doc_registry_file.exists():
            with open(doc_registry_file, 'r', encoding='utf-8') as f:
                doc_registry = json.load(f)
        
        for doc in documents:
            doc_registry[doc['doc_id']] = {
                'doc_id': doc['doc_id'],
                'title': doc['title'],
                'source': doc['source'],
                'pages': doc['pages'],
                'import_type': 'folder',
                'folder_id': folder_id,
                'chunks': doc.get('chunks', 0),
                'indexed': doc.get('indexed', False),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        with open(doc_registry_file, 'w', encoding='utf-8') as f:
            json.dump(doc_registry, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'source_folder': str(folder),
            'total_files_found': len(files),
            'files_processed': processed,
            'files_skipped': skipped,
            'files_failed': failed,
            'failed_files': failed_files,
            'documents': documents,
            'folder_id': folder_id,
            'folder_record': folder_record,
            'indexed_count': len(indexed_documents),
            'user_id': user_id,
            'kb_name': kb_name
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Folder import failed'}


@app.get('/api/v1/users/{user_id}/kbs/{kb_name}/entity-subgraph')
async def get_entity_subgraph(user_id: str, kb_name: str, entity: str):
    """Get subgraph centered around a specific entity.
    
    Args:
        user_id: User ID
        kb_name: Knowledge base name
        entity: Entity name to center subgraph around
        
    Returns:
        Subgraph data with entity and its neighbors
    """
    try:
        from rag_kb.lightrag.adapter import LightRAGAdapter
        import json
        from pathlib import Path
        
        rag = LightRAGAdapter()
        
        # Try to get entity-specific subgraph from LightRAG
        subgraph_data = {
            'nodes': [],
            'edges': []
        }
        
        # Check if LightRAG graph data exists
        lightrag_dir = settings.data_dir / 'lightrag_output'
        if lightrag_dir.exists():
            graph_file = lightrag_dir / 'graph_index.json'
            if graph_file.exists():
                try:
                    with open(graph_file, 'r', encoding='utf-8') as f:
                        lightrag_graph = json.load(f)
                        
                        # Find entity and its neighbors
                        entity_node = None
                        for node in lightrag_graph.get('nodes', []):
                            if entity.lower() in node.get('label', '').lower():
                                entity_node = node
                                break
                        
                        if entity_node:
                            subgraph_data['nodes'].append(entity_node)
                            
                            # Find connected nodes
                            node_id = entity_node.get('id', '')
                            for edge in lightrag_graph.get('edges', []):
                                if edge.get('source') == node_id or edge.get('target') == node_id:
                                    subgraph_data['edges'].append(edge)
                                    
                                    # Add connected nodes
                                    connected_id = edge.get('target') if edge.get('source') == node_id else edge.get('source')
                                    for node in lightrag_graph.get('nodes', []):
                                        if node.get('id') == connected_id:
                                            subgraph_data['nodes'].append(node)
                                            break
                except Exception as e:
                    print(f"Error reading LightRAG graph: {e}")
        
        # If no subgraph data, create a synthetic one
        if not subgraph_data['nodes']:
            subgraph_data['nodes'] = [
                {'id': f'entity_{entity}', 'label': entity, 'type': 'entity'}
            ]
            subgraph_data['edges'] = []
        
        return {
            'success': True,
            'entity': entity,
            'nodes': subgraph_data['nodes'],
            'edges': subgraph_data['edges'],
            'node_count': len(subgraph_data['nodes']),
            'edge_count': len(subgraph_data['edges'])
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get entity subgraph', 'nodes': [], 'edges': [], 'node_count': 0, 'edge_count': 0}


@app.get('/api/v1/users/{user_id}/kbs/{kb_name}/node-source')
async def get_node_source(user_id: str, kb_name: str, node_id: str):
    """Get source document for a specific graph node.
    
    Args:
        user_id: User ID
        kb_name: Knowledge base name
        node_id: Node ID in the graph
        
    Returns:
        Source document information
    """
    try:
        import json
        from pathlib import Path
        
        # Try to find source document from registry
        registry_file = settings.data_dir / 'document_registry.json'
        source_info = None
        
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                
                # Try to find document by node_id
                for doc_id, doc_data in registry.items():
                    if node_id in doc_id or node_id in doc_data.get('title', ''):
                        source_info = {
                            'doc_id': doc_id,
                            'title': doc_data.get('title', 'Unknown'),
                            'content': doc_data.get('content', ''),
                            'metadata': doc_data.get('metadata', {}),
                            'source': doc_data.get('source', '')
                        }
                        break
        
        if not source_info:
            # Create synthetic source info
            source_info = {
                'doc_id': node_id,
                'title': f'Document for {node_id}',
                'content': f'Content related to node {node_id}',
                'metadata': {},
                'source': 'synthetic'
            }
        
        return {
            'success': True,
            'node_id': node_id,
            'source': source_info
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get node source', 'source': None}


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
        from pathlib import Path
        
        rag = LightRAGAdapter()
        
        # Try to get actual graph data from LightRAG
        graph_data = {
            'nodes': [],
            'edges': []
        }
        
        # Check if LightRAG graph data exists
        lightrag_dir = settings.data_dir / 'lightrag_output'
        if lightrag_dir.exists():
            # Try to read LightRAG graph files
            graph_file = lightrag_dir / 'graph_index.json'
            if graph_file.exists():
                try:
                    with open(graph_file, 'r', encoding='utf-8') as f:
                        lightrag_graph = json.load(f)
                        # Convert LightRAG graph format to our format
                        if 'nodes' in lightrag_graph:
                            graph_data['nodes'] = lightrag_graph['nodes']
                        if 'edges' in lightrag_graph:
                            graph_data['edges'] = lightrag_graph['edges']
                except Exception as e:
                    print(f"Error reading LightRAG graph: {e}")
        
        # If no graph data exists, create nodes from documents
        if not graph_data['nodes']:
            registry_file = settings.data_dir / 'document_registry.json'
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                    # Create nodes from documents
                    for doc_id, doc_data in registry.items():
                        graph_data['nodes'].append({
                            'id': doc_id,
                            'label': doc_data.get('title', doc_id),
                            'type': 'document'
                        })
        
        # If still no nodes, create sample nodes
        if not graph_data['nodes']:
            graph_data['nodes'] = [
                {'id': 'node1', 'label': '文档节点示例', 'type': 'document'},
                {'id': 'node2', 'label': '实体节点示例', 'type': 'entity'}
            ]
            graph_data['edges'] = [
                {'source': 'node1', 'target': 'node2', 'label': '关联'}
            ]
        
        return {
            'success': True,
            'nodes': graph_data['nodes'],
            'edges': graph_data['edges'],
            'user_id': user_id,
            'kb_name': kb_name,
            'node_count': len(graph_data['nodes']),
            'edge_count': len(graph_data['edges'])
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get graph data', 'nodes': [], 'edges': [], 'node_count': 0, 'edge_count': 0}


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


@app.get('/api/v1/folders')
async def get_folder_records():
    """Get list of folder import records.
    
    Returns:
        List of folder import records
    """
    try:
        import json
        
        registry_file = settings.data_dir / 'folder_registry.json'
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                folder_registry = json.load(f)
                records = list(folder_registry.values())
        else:
            records = []
        
        return {
            'success': True,
            'folders': records,
            'total': len(records)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get folder records', 'folders': [], 'total': 0}


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


@app.get('/api/v1/search')
async def search_get(q: str = Query(''), dept: str = '', level: str = 'Internal', top_k: int = 8, mode: str = 'hybrid', query_mode: str = 'hybrid', category: str = 'all', auto_classify: bool = True):
    """Search the RAG knowledge base (GET method for backward compatibility)."""
    import sys
    print(f"=== MAIN.PY SEARCH GET CALLED ===", file=sys.stderr, flush=True)
    print(f"Query: {q}, mode: {mode}, query_mode: {query_mode}", file=sys.stderr, flush=True)
    
    # Call the POST search logic
    return await _search_impl(q, mode, query_mode, category, dept, level, top_k, auto_classify)


@app.post('/api/v1/search')
async def search_post(body: dict = Body(None), dept: str = '', level: str = 'Internal', top_k: int = 8, mode: str = 'hybrid', query_mode: str = 'hybrid', category: str = 'all', auto_classify: bool = True):
    """Search the RAG knowledge base with multi-knowledge base support and automatic intent classification.

    Args:
        body: Request body with 'q' parameter and other optional parameters
        dept: Department filter
        level: Access level filter
        top_k: Number of results to return
        mode: Search mode ('lightrag', 'bm25', 'hybrid')
        query_mode: LightRAG query mode ('naive', 'local', 'global', 'hybrid')
        category: Product category for multi-knowledge base routing
        auto_classify: Whether to automatically classify query intent

    Returns:
        Search results with answer and sources
    """
    import sys
    print(f"=== MAIN.PY SEARCH POST CALLED ===", file=sys.stderr, flush=True)
    
    # Extract query from request body
    if body:
        q = body.get('q', '')
        mode = body.get('mode', mode)
        query_mode = body.get('query_mode', query_mode)
        category = body.get('category', category)
    else:
        q = ''
    
    print(f"Query: {q}, mode: {mode}, query_mode: {query_mode}", file=sys.stderr, flush=True)
    
    return await _search_impl(q, mode, query_mode, category, dept, level, top_k, auto_classify)


async def _search_impl(q: str, mode: str, query_mode: str, category: str, dept: str, level: str, top_k: int, auto_classify: bool):
    """Internal search implementation shared by GET and POST methods."""
    
    try:
        from rag_kb.lightrag.adapter import LightRAGAdapter
        
        print("Attempting LightRAG search...", file=sys.stderr, flush=True)
        
        rag = LightRAGAdapter()
        print("LightRAG adapter created", file=sys.stderr, flush=True)
        
        await rag.ensure_initialized()
        print("LightRAG initialized", file=sys.stderr, flush=True)
        
        print("Performing query...", file=sys.stderr, flush=True)
        answer = await rag.query(q, mode=query_mode)
        print(f"LightRAG query result: {answer[:200] if answer else 'empty'}", file=sys.stderr, flush=True)
        
        if not answer or answer.strip() == "":
            raise Exception("LightRAG returned empty response")
        
        return {
            'answer': answer,
            'sources': [],
            'mode': 'lightrag',
            'query_mode': query_mode,
            'category': category,
            'intent_classification': None
        }
    except Exception as e:
        print(f"LightRAG search failed: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        print("Falling back to document registry search", file=sys.stderr, flush=True)
        
        # Fallback to document registry search
        import json
        from pathlib import Path
        registry_file = settings.data_dir / 'document_registry.json'
        
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Simple text search
            results = []
            for doc_id, doc_data in registry.items():
                content = doc_data.get('content', '')
                title = doc_data.get('title', '')
                if q.lower() in content.lower() or q.lower() in title.lower():
                    results.append({
                        'text': content[:500] + '...' if len(content) > 500 else content,
                        'metadata': {'title': title, 'doc_id': doc_id}
                    })
            
            return {
                'answer': f"LightRAG unavailable, using document search. Found {len(results)} documents matching '{q}'.",
                'sources': results[:top_k],
                'mode': 'basic',
                'query_mode': query_mode,
                'category': category,
                'intent_classification': None
            }
        else:
            return {
                'error': 'No documents found in knowledge base',
                'answer': '知识库中未找到相关信息。请先上传文档。',
                'sources': [],
                'mode': 'basic',
                'query_mode': query_mode,
                'category': category,
                'intent_classification': None
            }


async def _stream_answer(rag, prompt, mode='hybrid', with_citations=True) -> AsyncIterator[str]:
    """Stream answer from LightRAG in SSE format with citations.
    
    Args:
        rag: LightRAG adapter instance
        prompt: Query prompt
        mode: Query mode
        with_citations: Whether to include citations
        
    Yields:
        SSE-formatted response chunks
    """
    # Add system prompt to prevent hallucination
    system_prompt = """你是一个严格基于知识库回答问题的助手。请遵循以下规则：

1. 只能基于提供的知识库内容回答问题
2. 如果知识库中没有相关信息，必须直接回答"知识库中未找到相关信息"
3. 严禁编造、猜测或添加知识库之外的信息
4. 如果信息不完整，请如实说明知识库中的已知部分
5. 保持回答准确、客观，不添加主观臆测"""
    
    # Combine system prompt with user question
    enhanced_prompt = f"{system_prompt}\n\n用户问题：{prompt}"
    
    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, rag.query, enhanced_prompt, mode)
    NL = chr(10)
    SSE_END = NL * 2
    buf = ''
    
    # Check if answer indicates no information found
    if not answer or not answer.strip():
        answer = "知识库中未找到相关信息"
    
    # Check if the answer is trying to say it doesn't have information
    answer_lower = answer.lower()
    if any(phrase in answer_lower for phrase in ['不知道', '无法回答', '没有信息', '未找到', 'not found', 'don\'t know']):
        answer = "知识库中未找到相关信息"
    
    for ch in answer:
        buf += ch
        if ch in ('。', '？', '！', '.', '?', '!', NL):
            payload = json.dumps({'choices': [{'delta': {'content': buf}}]})
            yield 'data: ' + payload + SSE_END
            buf = ''
    
    if buf:
        yield 'data: ' + json.dumps({'choices': [{'delta': {'content': buf}}]}) + SSE_END
    
    # Add citations if requested
    if with_citations:
        try:
            sources = _get_search_sources(rag, prompt, mode)
            if sources:
                citations_text = "\n\n**参考来源：**\n"
                for i, source in enumerate(sources[:5], 1):
                    doc_id = source.get('doc_id', f"doc_{i}")
                    title = source.get('title', f"文档 {i}")
                    page_num = source.get('metadata', {}).get('page_number', 'N/A')
                    chunk_id = source.get('chunk_id', f"chunk_{i}")
                    
                    citations_text += f"{i}. [{title}](#doc-{doc_id}) "
                    if page_num != 'N/A':
                        citations_text += f"(页码: {page_num}) "
                    citations_text += f"[{chunk_id}]\n"
                
                payload = json.dumps({'choices': [{'delta': {'content': citations_text}}]})
                yield 'data: ' + payload + SSE_END
        except Exception as e:
            print(f"Error adding citations: {e}")
    
    yield 'data: [DONE]' + SSE_END


def _get_search_sources(rag, query, mode='hybrid') -> List[Dict[str, Any]]:
    """Get search sources for citations with entity extraction.
    
    Args:
        rag: LightRAG adapter instance
        query: Search query
        mode: Search mode
        
    Returns:
        List of source documents with entities
    """
    try:
        from rag_kb.retrieval import BM25Search, HybridSearch
        import re
        
        bm25_index_path = settings.data_dir / 'bm25_index.json'
        
        sources = []
        
        if mode == 'hybrid':
            bm25 = BM25Search()
            if bm25_index_path.exists():
                bm25.load_index(bm25_index_path)
            
            hybrid = HybridSearch(bm25_search=bm25, lightrag_adapter=rag)
            results = hybrid.search(query, top_k=5, use_bm25=True, use_lightrag=True)
            
            for result in results:
                # Extract entities from text
                entities = _extract_entities(result.get('text', ''))
                
                sources.append({
                    'doc_id': result.get('doc_id', ''),
                    'title': result.get('title', 'Unknown'),
                    'score': result.get('score', 0.0),
                    'text': result.get('text', '')[:200],
                    'entities': entities
                })
            return sources
        
        elif mode == 'bm25':
            bm25 = BM25Search()
            if bm25_index_path.exists():
                bm25.load_index(bm25_index_path)
            
            results = bm25.search(query, top_k=5)
            
            for result in results:
                entities = _extract_entities(result.get('text', ''))
                
                sources.append({
                    'doc_id': result.get('id', ''),
                    'title': result.get('title', 'Unknown'),
                    'score': result.get('score', 0.0),
                    'text': result.get('text', '')[:200],
                    'entities': entities
                })
            return sources
        
        else:  # lightrag mode
            return []
            
    except Exception as e:
        print(f"Error getting search sources: {e}")
        return []


def _extract_entities(text: str) -> List[str]:
    """Extract entities from text (simplified implementation).
    
    Args:
        text: Text to extract entities from
        
    Returns:
        List of extracted entities
    """
    # Simple entity extraction - in production, use NER models
    entities = []
    
    # Extract capitalized words (potential entities)
    words = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
    entities.extend(words)
    
    # Extract numbers and codes
    codes = re.findall(r'\b[A-Z0-9_]+\b', text)
    entities.extend(codes)
    
    # Remove duplicates and limit
    entities = list(set(entities))
    return entities[:10]  # Limit to top 10 entities


@app.post('/api/v1/evaluate')
async def evaluate_rag(test_case: dict):
    """Evaluate RAG performance using RAGAS metrics.
    
    Args:
        test_case: Test case with query, contexts, answer, ground_truth
        
    Returns:
        Evaluation results with metrics
    """
    try:
        from rag_kb.evaluation.ragas_eval import RAGASEvaluator
        
        evaluator = RAGASEvaluator()
        
        # Create sample search results for evaluation
        from rag_kb.models import SearchResult
        search_results = [
            SearchResult(
                chunk_id=f"chunk_{i}",
                doc_id=f"doc_{i}",
                text=context,
                score=0.9 - i * 0.1,
                rank=i + 1
            )
            for i, context in enumerate(test_case.get('retrieved_contexts', []))
        ]
        
        ground_truth = test_case.get('ground_truth', '').split(',') if test_case.get('ground_truth') else []
        
        evaluation = evaluator.comprehensive_evaluation(
            query=test_case.get('query', ''),
            retrieved_results=search_results,
            contexts=test_case.get('retrieved_contexts', []),
            answer=test_case.get('generated_answer', ''),
            ground_truth=ground_truth
        )
        
        return {
            'query': evaluation['query'],
            'metrics': {
                'retrieval_metrics': evaluation['retrieval_metrics'],
                'context_metrics': evaluation['context_metrics'],
                'answer_metrics': evaluation['answer_metrics'],
                'faithfulness_metrics': evaluation['faithfulness_metrics']
            },
            'overall_score': evaluation['overall_score'],
            'average_metrics': evaluator.get_average_metrics()
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Evaluation failed'}


@app.get('/api/v1/maintenance/statistics')
async def get_maintenance_statistics():
    """Get knowledge base maintenance statistics.
    
    Returns:
        Statistics about document counts, storage, and changes
    """
    try:
        from rag_kb.maintenance import IncrementalUpdater
        
        updater = IncrementalUpdater()
        stats = updater.get_statistics()
        
        # Get recent changes
        recent_changes = updater.get_change_log(limit=10)
        
        return {
            'success': True,
            'statistics': stats,
            'recent_changes': recent_changes
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get statistics'}


@app.get('/api/v1/maintenance/performance')
async def get_performance_metrics():
    """Get performance metrics and monitoring data.
    
    Returns:
        Performance metrics and quality trends
    """
    try:
        from rag_kb.maintenance import PerformanceMonitor, QualityMetrics
        
        perf_monitor = PerformanceMonitor()
        quality_metrics = QualityMetrics()
        
        performance_summary = perf_monitor.get_performance_summary()
        quality_score = quality_metrics.get_overall_quality_score()
        
        # Get quality trends
        quality_trends = {}
        for metric in ['precision', 'recall', 'relevance', 'faithfulness']:
            quality_trends[metric] = quality_metrics.get_quality_trends(metric, days=7)
        
        return {
            'success': True,
            'performance': performance_summary,
            'quality': {
                'overall_score': quality_score,
                'trends': quality_trends
            },
            'alerts': perf_monitor.get_alerts(hours=24)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get performance metrics'}


@app.post('/api/v1/maintenance/record-metric')
async def record_performance_metric(metric_data: dict):
    """Record a performance metric.
    
    Args:
        metric_data: Metric data with name, value, and metadata
        
    Returns:
        Success status
    """
    try:
        from rag_kb.maintenance import PerformanceMonitor
        
        perf_monitor = PerformanceMonitor()
        perf_monitor.record_metric(
            metric_name=metric_data.get('metric_name', ''),
            value=metric_data.get('value', 0.0),
            metadata=metric_data.get('metadata', {})
        )
        
        return {'success': True, 'message': 'Metric recorded'}
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to record metric'}


@app.post('/api/v1/maintenance/record-quality')
async def record_quality_metric(quality_data: dict):
    """Record quality metrics for a query.
    
    Args:
        quality_data: Quality data with query and metrics
        
    Returns:
        Success status
    """
    try:
        from rag_kb.maintenance import QualityMetrics
        
        quality_monitor = QualityMetrics()
        quality_monitor.record_quality(
            query=quality_data.get('query', ''),
            metrics=quality_data.get('metrics', {}),
            context=quality_data.get('context', {})
        )
        
        return {'success': True, 'message': 'Quality metrics recorded'}
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to record quality metrics'}


@app.post('/api/v1/maintenance/sync')
async def sync_documents(file_paths: List[str] = None):
    """Synchronize documents and detect changes.
    
    Args:
        file_paths: List of file paths to sync
        
    Returns:
        Sync results with change information
    """
    try:
        from rag_kb.maintenance import IncrementalUpdater
        from pathlib import Path
        
        updater = IncrementalUpdater()
        
        if file_paths:
            paths = [Path(fp) for fp in file_paths]
        else:
            # Default to uploads directory
            upload_dir = settings.data_dir / 'uploads'
            paths = list(upload_dir.glob('*')) if upload_dir.exists() else []
        
        changes = updater.detect_changes(paths)
        
        # Update hashes and log changes
        current_hashes = {}
        for file_path in paths:
            if file_path.exists():
                current_hashes[str(file_path)] = updater.calculate_file_hash(file_path)
        
        updater.save_file_hashes(current_hashes)
        
        # Log changes
        for new_file in changes['new']:
            updater.log_change('new', new_file, {'timestamp': datetime.now().isoformat()})
        
        for modified_file in changes['modified']:
            updater.log_change('modified', modified_file, {'timestamp': datetime.now().isoformat()})
        
        # Cleanup deleted documents
        if changes['deleted']:
            updater.cleanup_deleted_documents(changes['deleted'])
            for deleted_file in changes['deleted']:
                updater.log_change('deleted', deleted_file, {'timestamp': datetime.now().isoformat()})
        
        return {
            'success': True,
            'changes': changes,
            'total_files': len(paths),
            'new_files': len(changes['new']),
            'modified_files': len(changes['modified']),
            'deleted_files': len(changes['deleted'])
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Sync failed'}


@app.post('/api/v1/maintenance/cleanup')
async def cleanup_old_documents(days: int = 30):
    """Clean up documents older than specified days.
    
    Args:
        days: Number of days threshold
        
    Returns:
        Cleanup results
    """
    try:
        from rag_kb.maintenance import IncrementalUpdater
        from datetime import datetime, timedelta
        import json
        
        updater = IncrementalUpdater()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if not updater.registry_file.exists():
            return {'success': True, 'cleaned': 0, 'message': 'No registry file found'}
        
        with open(updater.registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        cleaned_count = 0
        updated_registry = {}
        
        for doc_id, doc_data in registry.items():
            doc_timestamp = doc_data.get('timestamp', '')
            if doc_timestamp:
                try:
                    doc_date = datetime.fromisoformat(doc_timestamp)
                    if doc_date < cutoff_date:
                        cleaned_count += 1
                        updater.log_change('cleanup', doc_data.get('source', doc_id), {
                            'reason': f'Older than {days} days',
                            'timestamp': datetime.now().isoformat()
                        })
                        continue
                except:
                    pass
            
            updated_registry[doc_id] = doc_data
        
        with open(updater.registry_file, 'w', encoding='utf-8') as f:
            json.dump(updated_registry, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'cleaned': cleaned_count,
            'message': f'Cleaned {cleaned_count} documents older than {days} days'
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Cleanup failed'}


@app.get('/api/v1/maintenance/strategies')
async def get_strategies():
    """Get current strategy configurations.
    
    Returns:
        Current strategies for chunking, retrieval, and reranking
    """
    try:
        from rag_kb.maintenance import StrategyManager
        
        strategy_manager = StrategyManager()
        current_strategies = strategy_manager.current_strategies
        
        return {
            'success': True,
            'strategies': current_strategies
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get strategies'}


@app.post('/api/v1/maintenance/strategies/update')
async def update_strategy(strategy_data: dict):
    """Update a specific strategy configuration.
    
    Args:
        strategy_data: Strategy update data
        
    Returns:
        Update results
    """
    try:
        from rag_kb.maintenance import StrategyManager
        
        strategy_manager = StrategyManager()
        strategy_manager.update_strategy(
            strategy_type=strategy_data.get('strategy_type', ''),
            strategy_name=strategy_data.get('strategy_name', ''),
            config=strategy_data.get('config', {})
        )
        
        return {
            'success': True,
            'message': 'Strategy updated successfully'
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to update strategy'}


@app.post('/api/v1/maintenance/strategies/optimize')
async def optimize_strategy(optimization_data: dict):
    """Automatically optimize a strategy based on target metrics.
    
    Args:
        optimization_data: Optimization parameters
        
    Returns:
        Optimization results
    """
    try:
        from rag_kb.maintenance import StrategyManager
        
        strategy_manager = StrategyManager()
        results = strategy_manager.auto_optimize_strategy(
            strategy_type=optimization_data.get('strategy_type', ''),
            target_metrics=optimization_data.get('target_metrics', {})
        )
        
        return {
            'success': True,
            'results': results
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to optimize strategy'}


@app.get('/api/v1/maintenance/strategies/compare')
async def compare_strategies(strategy_type: str = 'retrieval'):
    """Compare performance of different strategies.
    
    Args:
        strategy_type: Type of strategy to compare
        
    Returns:
        Comparison results
    """
    try:
        from rag_kb.maintenance import StrategyManager
        
        strategy_manager = StrategyManager()
        comparison = strategy_manager.get_strategy_comparison(strategy_type)
        
        return {
            'success': True,
            'comparison': comparison
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to compare strategies'}


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


@app.post('/api/v1/multi-kb/register')
async def register_product_kb(product_data: dict):
    """Register a new product knowledge base.
    
    Args:
        product_data: Product registration data
        
    Returns:
        Registration results
    """
    try:
        from rag_kb.multi_kb import multi_kb_manager
        
        result = multi_kb_manager.register_product_kb(
            product_id=product_data.get('product_id', ''),
            product_name=product_data.get('product_name', ''),
            source_folder=product_data.get('source_folder', ''),
            kb_name=product_data.get('kb_name', 'default')
        )
        
        return result
    except Exception as e:
        return {'error': str(e), 'message': 'Product KB registration failed'}


@app.get('/api/v1/multi-kb/products')
async def get_available_products():
    """Get list of available product knowledge bases.
    
    Returns:
        List of available products
    """
    try:
        from rag_kb.multi_kb import multi_kb_manager
        
        products = multi_kb_manager.get_available_products()
        
        return {
            'success': True,
            'products': products,
            'total': len(products)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get products', 'products': [], 'total': 0}


@app.post('/api/v1/multi-kb/update')
async def update_product_kb(product_id: str, source_folder: str = None):
    """Update a product knowledge base with new documents.
    
    Args:
        product_id: Product identifier
        source_folder: Path to new documentation folder
        
    Returns:
        Update results
    """
    try:
        from rag_kb.multi_kb import multi_kb_manager
        
        result = multi_kb_manager.update_product_kb(
            product_id=product_id,
            source_folder=source_folder
        )
        
        return result
    except Exception as e:
        return {'error': str(e), 'message': 'Product KB update failed'}


@app.delete('/api/v1/multi-kb/{product_id}')
async def delete_product_kb(product_id: str):
    """Delete a product knowledge base.
    
    Args:
        product_id: Product identifier
        
    Returns:
        Deletion results
    """
    try:
        from rag_kb.multi_kb import multi_kb_manager
        
        result = multi_kb_manager.delete_product_kb(product_id=product_id)
        
        return result
    except Exception as e:
        return {'error': str(e), 'message': 'Product KB deletion failed'}


@app.get('/multi-kb-selector')
async def multi_kb_selector_ui():
    """Multi-knowledge base selector interface."""
    return FileResponse('static/multi_kb_selector.html')


@app.post('/api/v1/workflow/execute')
async def execute_workflow(request: dict):
    """Execute complete RAG workflow with all stages.
    
    Args:
        request: Workflow execution request
        
    Returns:
        Complete workflow results
    """
    try:
        from rag_kb.workflow import workflow_manager, WorkflowContext, WorkflowStage
        
        context = WorkflowContext(
            query=request.get('query', ''),
            user_id=request.get('user_id', 'default'),
            kb_name=request.get('kb_name', 'default'),
            product_id=request.get('product_id', None),
            metadata=request.get('metadata', {})
        )
        
        # Determine which stages to execute
        stages = request.get('stages')
        if stages:
            stage_mapping = {
                'ingestion': WorkflowStage.INGESTION,
                'retrieval': WorkflowStage.RETRIEVAL,
                'generation': WorkflowStage.GENERATION,
                'citation': WorkflowStage.CITATION
            }
            stages = [stage_mapping.get(s) for s in stages if s in stage_mapping]
        
        results = await workflow_manager.execute_workflow(context, stages)
        
        return results
    except Exception as e:
        return {'error': str(e), 'message': 'Workflow execution failed'}


@app.get('/api/v1/workflow/status/{workflow_id}')
async def get_workflow_status(workflow_id: str):
    """Get workflow execution status.
    
    Args:
        workflow_id: Workflow ID
        
    Returns:
        Workflow status
    """
    try:
        # In a real implementation, you'd store workflow results in a database
        # For now, return a placeholder response
        return {
            'workflow_id': workflow_id,
            'status': 'completed',
            'message': 'Workflow status tracking not implemented yet'
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get workflow status'}


@app.post('/api/v1/workflow/ingestion')
async def execute_ingestion_stage(request: dict):
    """Execute ingestion stage only.
    
    Args:
        request: Ingestion request
        
    Returns:
        Ingestion stage results
    """
    try:
        from rag_kb.workflow import workflow_manager, WorkflowContext, WorkflowStage
        
        context = WorkflowContext(
            query='',  # Ingestion doesn't need query
            user_id=request.get('user_id', 'default'),
            kb_name=request.get('kb_name', 'default'),
            product_id=request.get('product_id', None),
            metadata=request.get('metadata', {})
        )
        
        result = await workflow_manager._execute_stage(WorkflowStage.INGESTION, context)
        
        return result.to_dict()
    except Exception as e:
        return {'error': str(e), 'message': 'Ingestion stage failed'}


@app.post('/api/v1/workflow/retrieval')
async def execute_retrieval_stage(request: dict):
    """Execute retrieval stage only.
    
    Args:
        request: Retrieval request
        
    Returns:
        Retrieval stage results
    """
    try:
        from rag_kb.workflow import workflow_manager, WorkflowContext, WorkflowStage
        
        context = WorkflowContext(
            query=request.get('query', ''),
            user_id=request.get('user_id', 'default'),
            kb_name=request.get('kb_name', 'default'),
            product_id=request.get('product_id', None),
            metadata=request.get('metadata', {})
        )
        
        result = await workflow_manager._execute_stage(WorkflowStage.RETRIEVAL, context)
        
        return result.to_dict()
    except Exception as e:
        return {'error': str(e), 'message': 'Retrieval stage failed'}


@app.post('/api/v1/workflow/generation')
async def execute_generation_stage(request: dict):
    """Execute generation stage only.
    
    Args:
        request: Generation request
        
    Returns:
        Generation stage results
    """
    try:
        from rag_kb.workflow import workflow_manager, WorkflowContext, WorkflowStage
        
        context = WorkflowContext(
            query=request.get('query', ''),
            user_id=request.get('user_id', 'default'),
            kb_name=request.get('kb_name', 'default'),
            product_id=request.get('product_id', None),
            metadata=request.get('metadata', {})
        )
        
        # First execute retrieval stage
        retrieval_result = await workflow_manager._execute_stage(WorkflowStage.RETRIEVAL, context)
        context.set_stage_result(retrieval_result)
        
        # Then execute generation stage
        result = await workflow_manager._execute_stage(WorkflowStage.GENERATION, context)
        
        return result.to_dict()
    except Exception as e:
        return {'error': str(e), 'message': 'Generation stage failed'}


@app.post('/api/v1/workflow/citation')
async def execute_citation_stage(request: dict):
    """Execute citation stage only.
    
    Args:
        request: Citation request
        
    Returns:
        Citation stage results
    """
    try:
        from rag_kb.workflow import workflow_manager, WorkflowContext, WorkflowStage
        
        context = WorkflowContext(
            query=request.get('query', ''),
            user_id=request.get('user_id', 'default'),
            kb_name=request.get('kb_name', 'default'),
            product_id=request.get('product_id', None),
            metadata=request.get('metadata', {})
        )
        
        # First execute retrieval and generation stages
        retrieval_result = await workflow_manager._execute_stage(WorkflowStage.RETRIEVAL, context)
        context.set_stage_result(retrieval_result)
        
        generation_result = await workflow_manager._execute_stage(WorkflowStage.GENERATION, context)
        context.set_stage_result(generation_result)
        
        # Then execute citation stage
        result = await workflow_manager._execute_stage(WorkflowStage.CITATION, context)
        
        return result.to_dict()
    except Exception as e:
        return {'error': str(e), 'message': 'Citation stage failed'}


@app.post('/api/v1/feedback')
async def add_user_feedback(feedback_data: dict):
    """Add user feedback for RAG quality improvement.
    
    Args:
        feedback_data: Feedback data
        
    Returns:
        Feedback addition result
    """
    try:
        from rag_kb.feedback import feedback_manager, UserFeedback, FeedbackType, FeedbackReason
        from datetime import datetime
        import uuid
        
        feedback = UserFeedback(
            feedback_id=str(uuid.uuid4()),
            user_id=feedback_data.get('user_id', 'anonymous'),
            query=feedback_data.get('query', ''),
            answer=feedback_data.get('answer', ''),
            feedback_type=FeedbackType(feedback_data.get('feedback_type', 'thumbs_up')),
            feedback_reason=FeedbackReason(feedback_data['feedback_reason']) if feedback_data.get('feedback_reason') else None,
            feedback_comment=feedback_data.get('feedback_comment', ''),
            metadata=feedback_data.get('metadata', {})
        )
        
        result = feedback_manager.add_feedback(feedback)
        
        return result
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to add feedback'}


@app.get('/api/v1/feedback/statistics')
async def get_feedback_statistics():
    """Get feedback statistics.
    
    Returns:
        Feedback statistics
    """
    try:
        from rag_kb.feedback import feedback_manager
        
        stats = feedback_manager.get_feedback_statistics()
        satisfaction_rate = feedback_manager.calculate_satisfaction_rate()
        negative_reasons = feedback_manager.get_negative_feedback_reasons()
        
        return {
            'success': True,
            'statistics': stats,
            'satisfaction_rate': satisfaction_rate,
            'negative_feedback_reasons': negative_reasons
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get feedback statistics'}


@app.get('/api/v1/feedback/recent')
async def get_recent_feedback(limit: int = 10):
    """Get recent feedback.
    
    Args:
        limit: Number of recent feedback items
        
    Returns:
        Recent feedback items
    """
    try:
        from rag_kb.feedback import feedback_manager
        
        recent = feedback_manager.get_recent_feedback(limit)
        
        return {
            'success': True,
            'feedbacks': recent,
            'count': len(recent)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get recent feedback'}


@app.get('/api/v1/suggestions')
async def get_search_suggestions(category: str = None, limit: int = 10):
    """Get search suggestions and quick questions.
    
    Args:
        category: Filter by category (optional)
        limit: Maximum number of suggestions
        
    Returns:
        Search suggestions
    """
    try:
        from rag_kb.suggestions import suggestion_manager
        
        suggestions = suggestion_manager.get_suggestions(category, limit)
        
        return {
            'success': True,
            'suggestions': suggestions,
            'count': len(suggestions)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get suggestions', 'suggestions': [], 'count': 0}


@app.get('/api/v1/suggestions/autocomplete')
async def get_autocomplete_suggestions(prefix: str, limit: int = 5):
    """Get autocomplete suggestions based on text prefix.
    
    Args:
        prefix: Text prefix to match
        limit: Maximum number of suggestions
        
    Returns:
        Autocomplete suggestions
    """
    try:
        from rag_kb.suggestions import suggestion_manager
        
        suggestions = suggestion_manager.get_suggestions_by_prefix(prefix, limit)
        
        return {
            'success': True,
            'suggestions': suggestions,
            'count': len(suggestions)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get autocomplete suggestions', 'suggestions': [], 'count': 0}


@app.get('/api/v1/suggestions/quick-questions')
async def get_quick_questions(product_id: str = None, limit: int = 5):
    """Get quick questions for a specific product.
    
    Args:
        product_id: Product ID (optional)
        limit: Maximum number of questions
        
    Returns:
        Quick questions
    """
    try:
        from rag_kb.suggestions import suggestion_manager
        
        questions = suggestion_manager.get_quick_questions(product_id, limit)
        
        return {
            'success': True,
            'questions': questions,
            'count': len(questions)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get quick questions', 'questions': [], 'count': 0}


@app.post('/api/v1/suggestions/use')
async def record_suggestion_use(suggestion_id: str):
    """Record that a suggestion was used.
    
    Args:
        suggestion_id: Suggestion ID
        
    Returns:
        Update result
    """
    try:
        from rag_kb.suggestions import suggestion_manager
        
        result = suggestion_manager.record_suggestion_use(suggestion_id)
        
        return result
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to record suggestion use'}


@app.get('/api/v1/suggestions/categories')
async def get_suggestion_categories():
    """Get available suggestion categories.
    
    Returns:
        Suggestion categories
    """
    try:
        from rag_kb.suggestions import suggestion_manager
        
        categories = suggestion_manager.get_categories()
        
        return {
            'success': True,
            'categories': categories
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get categories', 'categories': {}}


@app.get('/api/v1/processing/task/{task_id}')
async def get_processing_task(task_id: str):
    """Get processing task status by ID.
    
    Args:
        task_id: Task ID
        
    Returns:
        Task status
    """
    try:
        from rag_kb.processing import processing_tracker
        
        task = processing_tracker.get_task(task_id)
        
        if task:
            return {
                'success': True,
                'task': task
            }
        else:
            return {
                'success': False,
                'message': 'Task not found'
            }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get task status'}


@app.get('/api/v1/processing/user/{user_id}')
async def get_user_processing_tasks(user_id: str):
    """Get all processing tasks for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        List of user's tasks
    """
    try:
        from rag_kb.processing import processing_tracker
        
        tasks = processing_tracker.get_user_tasks(user_id)
        
        return {
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get user tasks', 'tasks': [], 'count': 0}


@app.get('/api/v1/processing/kb/{kb_name}/summary')
async def get_kb_processing_summary(kb_name: str):
    """Get processing summary for a knowledge base.
    
    Args:
        kb_name: Knowledge base name
        
    Returns:
        Processing summary
    """
    try:
        from rag_kb.processing import processing_tracker
        
        summary = processing_tracker.get_processing_summary(kb_name)
        
        return {
            'success': True,
            'summary': summary
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get processing summary'}


@app.get('/api/v1/processing/active')
async def get_active_processing_tasks():
    """Get all active processing tasks.
    
    Returns:
        List of active tasks
    """
    try:
        from rag_kb.processing import processing_tracker
        
        tasks = processing_tracker.get_active_tasks()
        
        return {
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get active tasks', 'tasks': [], 'count': 0}


@app.post('/api/v1/processing/cleanup')
async def cleanup_old_processing_tasks(days: int = 7):
    """Clean up old processing tasks.
    
    Args:
        days: Number of days to keep
        
    Returns:
        Cleanup result
    """
    try:
        from rag_kb.processing import processing_tracker
        
        processing_tracker.cleanup_old_tasks(days)
        
        return {
            'success': True,
            'message': f'Cleaned up tasks older than {days} days'
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to cleanup tasks'}


@app.post('/api/v1/perspective/analyze')
async def analyze_fragment_perspective(request: dict):
    """Analyze similar fragments with enhanced perspective.
    
    Args:
        request: Analysis request with query and retrieval results
        
    Returns:
        Fragment perspective analysis
    """
    try:
        from rag_kb.perspective import fragment_perspective
        
        query = request.get('query', '')
        retrieval_results = request.get('retrieval_results', [])
        top_k = request.get('top_k', 10)
        
        perspective = fragment_perspective.get_fragment_perspective_view(
            query, retrieval_results
        )
        
        return {
            'success': True,
            'perspective': perspective
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to analyze fragment perspective'}


@app.post('/api/v1/perspective/compare')
async def compare_fragments(request: dict):
    """Compare two similar fragments.
    
    Args:
        request: Comparison request with two fragment IDs
        
    Returns:
        Comparison result
    """
    try:
        from rag_kb.perspective import fragment_perspective, SimilarFragment, MatchType
        
        # In a real implementation, you'd fetch actual fragments
        # For now, return a placeholder
        return {
            'success': True,
            'message': 'Fragment comparison requires actual fragment data'
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to compare fragments'}


@app.post('/api/v1/routing/register-directory')
async def register_working_directory(request: dict):
    """Register a new working directory for optimized routing.
    
    Args:
        request: Directory registration data
        
    Returns:
        Registration result
    """
    try:
        from rag_kb.routing import optimized_router
        
        result = optimized_router.register_working_directory(
            dir_id=request.get('dir_id', ''),
            dir_path=request.get('dir_path', ''),
            product_id=request.get('product_id'),
            category=request.get('category'),
            user_id=request.get('user_id'),
            capacity=request.get('capacity', 1000)
        )
        
        return result
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to register directory'}


@app.get('/api/v1/routing/route')
async def route_query(query: str, product_id: str = None, 
                      category: str = None, user_id: str = None):
    """Route query to optimal working directory.
    
    Args:
        query: Search query
        product_id: Product ID (optional)
        category: Category (optional)
        user_id: User ID (optional)
        
    Returns:
        Routing result
    """
    try:
        from rag_kb.routing import optimized_router
        
        dir_id = optimized_router.route_query(query, product_id, category, user_id)
        
        if dir_id:
            dir_status = optimized_router.get_directory_status(dir_id)
            return {
                'success': True,
                'routed_to': dir_id,
                'directory': dir_status
            }
        else:
            return {
                'success': False,
                'message': 'No suitable directory found'
            }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to route query'}


@app.get('/api/v1/routing/directories')
async def get_working_directories():
    """Get all working directories.
    
    Returns:
        List of working directories
    """
    try:
        from rag_kb.routing import optimized_router
        
        directories = optimized_router.get_all_directories()
        
        return {
            'success': True,
            'directories': directories,
            'count': len(directories)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get directories', 'directories': [], 'count': 0}


@app.post('/api/v1/rlhf/training-example')
async def add_rlhf_training_example(request: dict):
    """Add a training example from user feedback.
    
    Args:
        request: Training example data
        
    Returns:
        Addition result
    """
    try:
        from rag_kb.rlhf import rlhf_manager, FeedbackLabel
        
        label = FeedbackLabel(request.get('label', 'neutral'))
        
        result = rlhf_manager.add_training_example(
            query=request.get('query', ''),
            response=request.get('response', ''),
            label=label,
            feedback_reason=request.get('feedback_reason'),
            user_id=request.get('user_id', 'anonymous')
        )
        
        return result
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to add training example'}


@app.get('/api/v1/rlhf/statistics')
async def get_rlhf_statistics():
    """Get RLHF dataset statistics.
    
    Returns:
        Dataset statistics
    """
    try:
        from rag_kb.rlhf import rlhf_manager
        
        stats = rlhf_manager.get_dataset_statistics()
        
        return {
            'success': True,
            'statistics': stats
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get RLHF statistics'}


@app.get('/api/v1/rlhf/reward')
async def calculate_response_reward(query: str, response: str):
    """Calculate reward score for a response.
    
    Args:
        query: User query
        response: Model response
        
    Returns:
        Reward score
    """
    try:
        from rag_kb.rlhf import rlhf_manager
        
        reward = rlhf_manager.calculate_response_reward(query, response)
        
        return {
            'success': True,
            'reward_score': reward
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to calculate reward'}


@app.get('/api/v1/rlhf/training-batch')
async def get_rlhf_training_batch(batch_size: int = 10):
    """Get a batch of training examples.
    
    Args:
        batch_size: Number of examples
        
    Returns:
        Training batch
    """
    try:
        from rag_kb.rlhf import rlhf_manager
        
        batch = rlhf_manager.get_training_batch(batch_size)
        
        return {
            'success': True,
            'batch': batch,
            'batch_size': len(batch)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get training batch', 'batch': [], 'batch_size': 0}


@app.get('/api/v1/graph/neighborhood')
async def get_graph_neighborhood(node_id: str, degree: int = 2):
    """Get neighborhood of a graph node.
    
    Args:
        node_id: Node ID
        degree: Neighborhood degree
        
    Returns:
        Neighborhood analysis
    """
    try:
        from rag_kb.graph_analysis import graph_analyzer
        
        neighborhood = graph_analyzer.get_neighborhood(node_id, degree)
        
        return {
            'success': True,
            'neighborhood': neighborhood
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get neighborhood'}


@app.get('/api/v1/graph/entity-relationships')
async def analyze_entity_relationships(entity_id: str, max_degree: int = 3):
    """Analyze relationships for an entity.
    
    Args:
        entity_id: Entity ID
        max_degree: Maximum degree
        
    Returns:
        Relationship analysis
    """
    try:
        from rag_kb.graph_analysis import graph_analyzer
        
        relationships = graph_analyzer.analyze_entity_relationships(entity_id, max_degree)
        
        return {
            'success': True,
            'relationships': relationships
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to analyze relationships'}


@app.get('/api/v1/graph/paths')
async def find_graph_paths(entity1: str, entity2: str, max_paths: int = 5):
    """Find paths between two entities.
    
    Args:
        entity1: First entity ID
        entity2: Second entity ID
        max_paths: Maximum number of paths
        
    Returns:
        Paths between entities
    """
    try:
        from rag_kb.graph_analysis import graph_analyzer
        
        paths = graph_analyzer.find_paths_between_entities(entity1, entity2, max_paths)
        
        return {
            'success': True,
            'paths': paths,
            'path_count': len(paths)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to find paths', 'paths': [], 'path_count': 0}


@app.get('/api/v1/graph/centrality')
async def get_graph_centrality():
    """Get centrality measures for all nodes.
    
    Returns:
        Centrality measures
    """
    try:
        from rag_kb.graph_analysis import graph_analyzer
        
        centrality = graph_analyzer.get_centrality_measures()
        
        return {
            'success': True,
            'centrality': centrality
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get centrality measures'}


@app.get('/api/v1/graph/communities')
async def detect_graph_communities():
    """Detect communities in the graph.
    
    Returns:
        Community detection results
    """
    try:
        from rag_kb.graph_analysis import graph_analyzer
        
        communities = graph_analyzer.detect_communities()
        
        return {
            'success': True,
            'communities': communities
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to detect communities'}


@app.post('/api/v1/multimodal/process')
async def process_multimodal_file(request: dict):
    """Process a multimodal file (image or table).
    
    Args:
        request: File processing request
        
    Returns:
        Processing result
    """
    try:
        from rag_kb.multimodal import multimodal_manager
        
        result = multimodal_manager.process_multimodal_file(
            file_path=request.get('file_path', ''),
            doc_id=request.get('doc_id')
        )
        
        return result
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to process multimodal file'}


@app.get('/api/v1/multimodal/search')
async def search_multimodal_content(query: str, modality_type: str = None):
    """Search multimodal content by description.
    
    Args:
        query: Search query
        modality_type: Filter by modality type
        
    Returns:
        Matching content
    """
    try:
        from rag_kb.multimodal import multimodal_manager
        
        results = multimodal_manager.search_multimodal_content(query, modality_type)
        
        return {
            'success': True,
            'results': results,
            'count': len(results)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to search multimodal content', 'results': [], 'count': 0}


@app.get('/api/v1/multimodal/content')
async def get_multimodal_content_by_type(modality_type: str):
    """Get all content of a specific type.
    
    Args:
        modality_type: Modality type
        
    Returns:
        Content items
    """
    try:
        from rag_kb.multimodal import multimodal_manager
        
        content = multimodal_manager.get_content_by_type(modality_type)
        
        return {
            'success': True,
            'content': content,
            'count': len(content)
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to get multimodal content', 'content': [], 'count': 0}


@app.post('/api/v1/routing/strategy')
async def set_routing_strategy(strategy: str):
    """Change routing strategy.
    
    Args:
        strategy: New routing strategy
        
    Returns:
        Strategy change result
    """
    try:
        from rag_kb.routing import optimized_router, RoutingStrategy
        
        strategy_enum = RoutingStrategy(strategy)
        optimized_router.set_routing_strategy(strategy_enum)
        
        return {
            'success': True,
            'strategy': strategy,
            'message': 'Routing strategy updated successfully'
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to set routing strategy'}


@app.get('/api/v1/intent/classify')
async def classify_query_intent(query: str):
    """Classify query intent for automatic mode selection.
    
    Args:
        query: User query
        
    Returns:
        Intent classification result
    """
    try:
        from rag_kb.intent import intent_classifier
        
        classification = intent_classifier.classify(query)
        
        return {
            'success': True,
            'classification': {
                'intent': classification.intent.value,
                'confidence': classification.confidence,
                'recommended_mode': classification.recommended_mode,
                'reasoning': classification.reasoning
            }
        }
    except Exception as e:
        return {'error': str(e), 'message': 'Failed to classify intent'}


@app.get('/pdf-preview')
async def pdf_preview_ui():
    """PDF preview interface with paragraph highlighting."""
    return FileResponse('static/pdf_preview.html')


@app.get('/interactive-graph')
async def interactive_graph_ui():
    """Interactive graph interface with entity linking and source tracing."""
    return FileResponse('static/interactive_graph.html')


@app.get('/enhanced-search')
async def enhanced_search_ui():
    """Enhanced search interface with hybrid retrieval and multi-modal interaction."""
    return FileResponse('static/enhanced_search.html')


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