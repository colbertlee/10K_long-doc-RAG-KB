"""API routes for RAG KB."""

import json
import re
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.ingest.user_manager import UserDataManager
from rag_kb.config import settings

router = APIRouter()
rag = LightRAGAdapter()
user_manager = UserDataManager(settings.data_dir / "users")


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
    answer = rag.query(question, mode=mode)
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
    try:
        kb_path = user_manager.create_user_kb(user_id, kb_name)
        return {
            "success": True,
            "user_id": user_id,
            "kb_name": kb_name,
            "kb_path": str(kb_path)
        }
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