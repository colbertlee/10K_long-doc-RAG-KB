"""Domain models for RAG KB."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Document model representing a single document in the knowledge base."""
    
    doc_id: str = Field(..., description='Unique document id, e.g. sha256 of normalized content or file hash')
    title: str = ''
    source: str = ''
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    file_hash: str = ''
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    acl: dict[str, list[str]] = Field(default_factory=dict, description='RBAC/ACL tags, e.g. {"dept": ["Sales"], "level": ["Internal"]}')


class Chunk(BaseModel):
    """Chunk model representing a semantic chunk of a document."""
    
    chunk_id: str
    doc_id: str
    parent_id: str | None = None
    text: str
    level: int = 0
    section_path: list[str] = Field(default_factory=list)
    token_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] | None = None
    
    # Enhanced metadata for internal document retrieval
    source_file: str = Field(default="", description="Original source file name")
    page_num: int | None = Field(default=None, description="Page number in source document")
    section_title: str = Field(default="", description="Title of the section this chunk belongs to")
    chunk_type: str = Field(default="text", description="Type of chunk: text, table, heading, list, code")
    offset: int = Field(default=0, description="Character offset in original document")
    length: int = Field(default=0, description="Length of chunk in characters")
    table_id: str | None = Field(default=None, description="ID if this chunk is from a table")
    list_index: int | None = Field(default=None, description="Index if this chunk is from a list")


class SearchResult(BaseModel):
    """Search result model representing a retrieved chunk."""
    
    chunk_id: str
    doc_id: str
    text: str
    score: float
    rank: int
    source: str = ''
    metadata: dict[str, Any] = Field(default_factory=dict)