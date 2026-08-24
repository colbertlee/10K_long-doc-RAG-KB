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
        from rag_kb.chunkers import StructuredChunker
        from rag_kb.lightrag.adapter import LightRAGAdapter
        import json
        import time
        
        upload_path = settings.data_dir / 'uploads' / file.filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        upload_path.write_bytes(await file.read())
        
        # Step 1: Parse and clean document
        pipeline = IngestPipeline()
        doc = pipeline.run(upload_path, acl={'dept': [dept], 'level': [level]})
        
        # Step 2: Semantic chunking
        chunker = StructuredChunker()
        chunks = chunker.chunk(doc.content, doc.metadata)
        
        # Step 3: LightRAG indexing and knowledge graph generation
        try:
            rag = LightRAGAdapter()
            # Insert document into LightRAG for indexing and graph generation
            rag.ingest([{
                'doc_id': doc.doc_id,
                'content': doc.content,
                'metadata': doc.metadata
            }])
            
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
            
            return {
                'doc_id': doc.doc_id, 
                'title': doc.title, 
                'pages': doc.metadata.get('pages', 0),
                'chunks': len(chunks),
                'status': 'indexed',
                'graph_generated': True
            }
        except Exception as e:
            # LightRAG indexing failed, but document was parsed
            print(f"LightRAG indexing failed: {e}")
            return {
                'doc_id': doc.doc_id, 
                'title': doc.title, 
                'pages': doc.metadata.get('pages', 0),
                'chunks': len(chunks),
                'status': 'parsed_only',
                'graph_generated': False,
                'error': f'LightRAG indexing failed: {str(e)}'
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
        from rag_kb.chunkers import StructuredChunker
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
                
                # Step 2: Semantic chunking
                chunks = chunker.chunk(doc.content, doc.metadata)
                
                # Step 3: LightRAG indexing
                try:
                    rag.ingest([{
                        'doc_id': doc.doc_id,
                        'content': doc.content,
                        'metadata': doc.metadata
                    }])
                    indexed_documents.append(doc.doc_id)
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


@app.post('/api/v1/search')
async def search(q: str = Query(...), dept: str = '', level: str = 'Internal', top_k: int = 8, mode: str = 'hybrid', query_mode: str = 'hybrid'):
    """Search the RAG knowledge base with multiple modes.
    
    Args:
        q: Search query
        dept: Department filter
        level: Access level filter
        top_k: Number of results to return
        mode: Search mode ('lightrag', 'bm25', 'hybrid')
        
    Returns:
        Search results with answer and sources
    """
    try:
        from rag_kb.lightrag.adapter import LightRAGAdapter
        from rag_kb.retrieval import BM25Search, HybridSearch
        
        user_acl = {'dept': [dept], 'level': [level]}
        bm25_index_path = settings.data_dir / 'bm25_index.json'
        
        if mode == 'bm25':
            # BM25-only search
            bm25 = BM25Search()
            # Load BM25 index if available
            if bm25_index_path.exists():
                bm25.load_index(bm25_index_path)
            
            results = bm25.search(q, top_k=top_k)
            answer = f"Found {len(results)} relevant documents using BM25 search."
            return {'answer': answer, 'sources': results, 'mode': 'bm25'}
            
        elif mode == 'hybrid':
            # Hybrid search (BM25 + LightRAG)
            rag = LightRAGAdapter()
            bm25 = BM25Search()
            
            if bm25_index_path.exists():
                bm25.load_index(bm25_index_path)
            
            hybrid = HybridSearch(bm25_search=bm25, lightrag_adapter=rag)
            results = hybrid.search(q, top_k=top_k, use_bm25=True, use_lightrag=True)
            
            # Generate answer using LightRAG with specified query mode
            try:
                lightrag_answer = rag.query(q, mode=query_mode)
                if not lightrag_answer or lightrag_answer == "":
                    lightrag_answer = "抱歉，当前知识库中没有相关文档或LightRAG未正确配置。"
            except Exception as e:
                lightrag_answer = f"LightRAG查询失败: {str(e)}"
            
            return {'answer': lightrag_answer, 'sources': results, 'mode': 'hybrid', 'query_mode': query_mode}
            
        else:  # lightrag mode (default)
            rag = LightRAGAdapter()
            try:
                answer = rag.query(q, mode=query_mode)
                if not answer or answer == "":
                    answer = "抱歉，当前知识库中没有相关文档或LightRAG未正确配置。请先上传文档并确保LightRAG已正确设置。"
                return {'answer': answer, 'sources': [], 'mode': 'lightrag', 'query_mode': query_mode, 'status': 'no_documents'}
                return {'answer': answer, 'sources': [], 'mode': 'lightrag', 'query_mode': query_mode}
            except Exception as e:
                answer = f"搜索失败: {str(e)}。请确保LightRAG已正确配置且有文档已索引。"
                return {'answer': answer, 'sources': [], 'mode': 'lightrag', 'query_mode': query_mode, 'error': str(e)}
            
    except Exception as e:
        return {'error': str(e), 'message': 'Search failed', 'answer': f'搜索失败: {str(e)}', 'sources': [], 'mode': mode, 'query_mode': query_mode}


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
    
    # Add citations if requested
    if with_citations:
        try:
            sources = _get_search_sources(rag, prompt, mode)
            if sources:
                citations_text = "\n\n**参考来源：**\n"
                for i, source in enumerate(sources[:5], 1):
                    doc_id = source.get('doc_id', f"doc_{i}")
                    title = source.get('title', f"文档 {i}")
                    citations_text += f"{i}. [{title}](#doc-{doc_id})\n"
                
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