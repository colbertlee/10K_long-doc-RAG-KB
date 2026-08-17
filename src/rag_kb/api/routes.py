"""API routes for RAG KB."""

import json
import re
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from rag_kb.lightrag.adapter import LightRAGAdapter

router = APIRouter()
rag = LightRAGAdapter()


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