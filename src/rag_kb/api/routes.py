"""API routes for RAG KB."""

import json
import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any

router = APIRouter()


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