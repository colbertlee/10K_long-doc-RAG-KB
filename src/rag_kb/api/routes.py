"""API routes for RAG KB."""

import json
import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any

router = APIRouter()

# Lazy initialization to avoid blocking on import
def get_rag():
    """Get LightRAG adapter instance (lazy initialization)."""
    from rag_kb.lightrag.adapter import LightRAGAdapter
    return LightRAGAdapter()


def extract_sources(answer):
    """Extract source citations from LightRAG answer.
    
    Args:
        answer: Answer text from LightRAG
        
    Returns:
        List of source citations
    """
    # Simple example: match patterns like [DATA:...]
    return re.findall(r'\[DATA:([^\]]+)\]', answer)


@router.post("/search")
async def search_endpoint(q: str, mode: str = "hybrid", top_k: int = 8):
    """Search endpoint for RAG knowledge base.
    
    Args:
        q: Search query
        mode: Search mode ('lightrag', 'bm25', 'hybrid')
        top_k: Number of results to return
        
    Returns:
        Search results with answer and sources
    """
    try:
        # Simple document search from registry
        import json
        from pathlib import Path
        registry_file = Path("C:/Users/liz8/OneDrive - Dell Technologies/Documents/BaiduSyncdisk/Works/Vibe_Coding/10K_long-doc-RAG-KB/data/document_registry.json")
        
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
                        'content': content[:500] + '...' if len(content) > 500 else content,
                        'metadata': {'title': title, 'doc_id': doc_id}
                    })
            
            return {
                "answer": f"Found {len(results)} documents matching '{q}'. Note: Advanced search features are temporarily disabled due to dependency compatibility issues.",
                "sources": results[:top_k],
                "mode": "basic",
                "source_count": len(results[:top_k])
            }
        else:
            return {
                "error": "No documents found in knowledge base",
                "answer": "知识库中未找到任何文档。请先上传文档。",
                "sources": [],
                "mode": "basic",
                "source_count": 0
            }
    except Exception as e:
        return {
            "error": str(e),
            "answer": f"搜索失败: {str(e)}",
            "sources": [],
            "mode": "basic",
            "source_count": 0
        }


@router.post("/chat/completions")
async def chat_completions_endpoint(body: dict):
    """OpenAI-compatible chat completions endpoint.
    
    Args:
        body: Request body with messages and other parameters
        
    Returns:
        Streaming response with chat completions
    """
    try:
        messages = body.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Extract the last user message as the query
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        rag = get_rag()
        
        # Generate response using LightRAG
        answer = rag.query(user_message, mode="hybrid")
        
        # Return in OpenAI-compatible format
        return {
            "id": "chat-" + str(hash(user_message)),
            "object": "chat.completion",
            "created": int(__import__("time").time()),
            "model": "lightrag",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(user_message),
                "completion_tokens": len(answer),
                "total_tokens": len(user_message) + len(answer)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current-user")
async def get_current_user():
    """Get current user information.
    
    Returns:
        Current user information
    """
    import os
    return {
        "user_id": os.environ.get('RAGKB_CURRENT_USER', 'default'),
        "authenticated": True
    }