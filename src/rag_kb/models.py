"""Domain models for RAG KB."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Document(BaseModel):
    """Document model representing a single document in the knowledge base."""
    
    doc_id: str = Field(..., description='Unique document id, e.g. sha256 of normalized content or file hash')
    title: str = ''
    source: str = ''
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    file_hash: str = ''
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    acl: Dict[str, List[str]] = Field(default_factory=dict, description='RBAC/ACL tags, e.g. {"dept": ["Sales"], "level": ["Internal"]}')


class Chunk(BaseModel):
    """Chunk model representing a semantic chunk of a document."""
    
    chunk_id: str
    doc_id: str
    parent_id: Optional[str] = None
    text: str
    level: int = 0
    section_path: List[str] = Field(default_factory=list)
    token_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None


class SearchResult(BaseModel):
    """Search result model representing a retrieved chunk."""
    
    chunk_id: str
    doc_id: str
    text: str
    score: float
    rank: int
    source: str = ''
    metadata: Dict[str, Any] = Field(default_factory=dict)