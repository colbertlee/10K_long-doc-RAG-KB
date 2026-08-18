"""API routes for RAG KB."""

import json
import re
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.ingest.user_manager import UserDataManager
from rag_kb.config import settings
from rag_kb.utils.validation import validate_user_id, validate_kb_name, get_current_user

router = APIRouter()
rag = LightRAGAdapter()
user_manager = UserDataManager(settings.data_dir / "users")


@router.get('/current-user')
async def get_current_user_endpoint():
    """Get current logged-in user ID.
    
    Returns:
        Current user information
    """
    current_user = get_current_user()
    return {
        "user_id": current_user,
        "authenticated": current_user != "default"
    }


def extract_sources(answer):
    """Extract source citations from LightRAG answer.
    
    Args:
        answer: Answer text from LightRAG
        
    Returns:
        List of source citations
    """
    # Simple example: match patterns like [DATA:...]
    return re.findall(r'\[DATA:([^\]]+)\]', answer)


@router.post('/chat/completions')
async def chat_completions(body: dict):
    """OpenAI-compatible chat completions endpoint.
    
    Args:
        body: Request body with messages and parameters
        
    Returns:
        Response with answer and sources
    """
    question = body['messages'][-1]['content']
    mode = body.get('mode', 'hybrid')
    
    # Extract user roles for ACL filtering
    user_roles = body.get('user_roles', {})
    if not user_roles:
        # Default to internal access if no roles specified
        user_roles = {'level': ['Internal']}
    
    answer = rag.query(question, mode=mode, user_roles=user_roles)
    sources = extract_sources(answer)
    
    return {'answer': answer, 'sources': sources}


@router.post('/users/{user_id}/kbs')
async def create_user_kb(user_id: str, kb_name: str = Form(...)):
    """Create a new knowledge base for a user.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        
    Returns:
        Knowledge base creation result
    """
    # Validate inputs
    is_valid_user, user_error = validate_user_id(user_id)
    if not is_valid_user:
        raise HTTPException(status_code=400, detail=f"Invalid user ID: {user_error}")
    
    is_valid_kb, kb_error = validate_kb_name(kb_name)
    if not is_valid_kb:
        raise HTTPException(status_code=400, detail=f"Invalid knowledge base name: {kb_error}")
    
    try:
        kb_path = user_manager.create_user_kb(user_id, kb_name)
        return {
            "success": True,
            "user_id": user_id,
            "kb_name": kb_name,
            "kb_path": str(kb_path)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/users/{user_id}/kbs')
async def list_user_kbs(user_id: str):
    """List all knowledge bases for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        List of knowledge base names
    """
    try:
        kbs = user_manager.get_user_kbs(user_id)
        return {
            "user_id": user_id,
            "knowledge_bases": kbs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/users/{user_id}/kbs/{kb_name}/upload')
async def upload_to_user_kb(user_id: str, kb_name: str, file: UploadFile = File(...)):
    """Upload a file to a user's knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        file: Uploaded file
        
    Returns:
        Upload result
    """
    try:
        kb_folder = user_manager.get_user_folder(user_id) / kb_name
        raw_folder = kb_folder / "raw"
        raw_folder.mkdir(parents=True, exist_ok=True)
        
        file_path = raw_folder / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "success": True,
            "user_id": user_id,
            "kb_name": kb_name,
            "filename": file.filename,
            "file_path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/users/{user_id}/kbs/{kb_name}/ingest')
async def ingest_user_kb(user_id: str, kb_name: str, acl: dict = None):
    """Ingest all documents from a user's knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        acl: Access control list metadata
        
    Returns:
        Ingestion result
    """
    try:
        documents = user_manager.ingest_user_folder(user_id, kb_name, acl)
        return {
            "success": True,
            "user_id": user_id,
            "kb_name": kb_name,
            "documents_processed": len(documents),
            "documents": [doc.metadata for doc in documents]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/users/{user_id}/kbs/{kb_name}/stats')
async def get_kb_stats(user_id: str, kb_name: str):
    """Get statistics for a user's knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        
    Returns:
        Knowledge base statistics
    """
    try:
        stats = user_manager.get_kb_stats(user_id, kb_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/users/{user_id}/kbs/{kb_name}')
async def delete_user_kb(user_id: str, kb_name: str):
    """Delete a user's knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        
    Returns:
        Deletion result
    """
    try:
        success = user_manager.delete_user_kb(user_id, kb_name)
        return {
            "success": success,
            "user_id": user_id,
            "kb_name": kb_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/users/{user_id}/kbs/{kb_name}/import-folder')
async def import_folder(user_id: str, kb_name: str, folder_path: str, acl: dict = None):
    """Import entire folder to knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        folder_path: Path to local folder to import
        acl: Access control list metadata
        
    Returns:
        Import result with statistics
    """
    try:
        from pathlib import Path
        import shutil
        
        folder = Path(folder_path)
        if not folder.exists():
            raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")
        
        if not folder.is_dir():
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {folder_path}")
        
        # Get user knowledge base folder
        kb_folder = user_manager.get_user_folder(user_id) / kb_name
        raw_folder = kb_folder / "raw"
        raw_folder.mkdir(parents=True, exist_ok=True)
        
        # Process files
        documents = []
        skipped_files = []
        failed_files = []
        
        for file_path in folder.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    # Check if file already exists
                    target_path = raw_folder / file_path.name
                    if target_path.exists():
                        skipped_files.append(file_path.name)
                        continue
                    
                    # Copy file to user knowledge base
                    shutil.copy2(file_path, target_path)
                    
                    # Process document
                    doc = user_manager.pipeline.run(target_path, acl=acl)
                    documents.append(doc)
                    
                except Exception as e:
                    failed_files.append({
                        "file": file_path.name,
                        "error": str(e)
                    })
        
        return {
            "success": True,
            "user_id": user_id,
            "kb_name": kb_name,
            "source_folder": str(folder),
            "total_files_found": len(list(folder.rglob('*'))),
            "files_processed": len(documents),
            "files_skipped": len(skipped_files),
            "files_failed": len(failed_files),
            "documents": [doc.metadata for doc in documents],
            "skipped_files": skipped_files,
            "failed_files": failed_files
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/import-local-folder')
async def import_local_folder_simple(folder_path: str, user_id: str = "default", kb_name: str = "default", acl: dict = None):
    """Simple endpoint to import local folder without requiring user/kb creation first.
    
    Args:
        folder_path: Path to local folder to import
        user_id: User identifier (default: "default")
        kb_name: Knowledge base name (default: "default")
        acl: Access control list metadata
        
    Returns:
        Import result
    """
    try:
        # Auto-create user and KB if they don't exist
        user_manager.create_user_kb(user_id, kb_name)
        
        # Import folder
        return await import_folder(user_id, kb_name, folder_path, acl)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/users/{user_id}/kbs/{kb_name}/graph')
async def get_knowledge_graph(user_id: str, kb_name: str):
    """Get knowledge graph data for visualization.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        
    Returns:
        Graph data with nodes and edges
    """
    try:
        # Get the knowledge base directory
        kb_folder = user_manager.get_user_folder(user_id) / kb_name
        graph_file = kb_folder / "graph_data.json"
        
        # Check if cached graph data exists
        if graph_file.exists():
            import json
            with open(graph_file, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            return graph_data
        else:
            # Try to extract from LightRAG using the new graph extractor
            try:
                from rag_kb.lightrag.graph_extractor import LightRAGGraphExtractor
                
                # Look for LightRAG working directory
                lightrag_dir = kb_folder / "index"
                if not lightrag_dir.exists():
                    lightrag_dir = kb_folder  # Fallback to KB folder
                
                if lightrag_dir.exists():
                    # Extract graph data using the new extractor
                    extractor = LightRAGGraphExtractor(lightrag_dir)
                    graph_data = extractor.get_graph_data()
                    
                    # Cache the extracted data
                    extractor.save_graph_data(graph_file)
                    
                    # Add statistics
                    stats = extractor.get_statistics()
                    graph_data['statistics'] = stats
                    
                    return graph_data
                
                # Return empty graph if no data found
                return {
                    "nodes": [],
                    "edges": [],
                    "statistics": {
                        "total_nodes": 0,
                        "total_edges": 0,
                        "node_types": {},
                        "relation_types": {},
                        "avg_degree": 0,
                        "connected_components": 0
                    },
                    "message": "没有找到知识图谱数据。请先导入文档以生成知识图谱。"
                }
            except ImportError:
                return {
                    "nodes": [],
                    "edges": [],
                    "statistics": {
                        "total_nodes": 0,
                        "total_edges": 0,
                        "node_types": {},
                        "relation_types": {},
                        "avg_degree": 0,
                        "connected_components": 0
                    },
                    "message": "知识图谱可视化需要NetworkX库。请安装: pip install networkx"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))