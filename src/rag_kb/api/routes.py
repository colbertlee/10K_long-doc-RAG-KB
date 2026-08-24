"""API routes for RAG KB."""

import json
import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

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