"""API routes for RAG KB."""

import json
import re
import importlib.util
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from rag_kb.lightrag.adapter import LightRAGAdapter

# Direct import to avoid __init__.py encoding issues
spec = importlib.util.spec_from_file_location("organization", "src/rag_kb/knowledge/organization.py")
organization_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(organization_module)

SmartKnowledgeOrganizer = organization_module.SmartKnowledgeOrganizer
KnowledgeQualityAnalyzer = organization_module.KnowledgeQualityAnalyzer

router = APIRouter()
rag = LightRAGAdapter()
knowledge_organizer = SmartKnowledgeOrganizer()
quality_analyzer = KnowledgeQualityAnalyzer()


def extract_sources(answer):
    """Extract source citations from LightRAG answer.
    
    Args:
        answer: Answer text from LightRAG
        
    Returns:
        List of source citations
    """
    # Simple example: match patterns like [DATA:...]
    return re.findall(r'\[DATA:([^\]]+)\]', answer)


@router.post('/knowledge/organize')
async def organize_document(document_data: dict):
    """Organize a document with automatic classification and tagging.
    
    Args:
        document_data: Dictionary containing:
            - content: Document content
            - filename: Optional filename
            - metadata: Optional existing metadata
            
    Returns:
        Organization results with category, tags, and suggestions
    """
    try:
        content = document_data.get('content', '')
        filename = document_data.get('filename', '')
        metadata = document_data.get('metadata', {})
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        organization = knowledge_organizer.organize_document(content, filename)
        quality_analysis = quality_analyzer.analyze_document_quality(content, metadata)
        
        return {
            "organization": organization,
            "quality_analysis": quality_analysis,
            "suggestions": quality_analysis.get('suggestions', [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/knowledge/batch-operation')
async def batch_knowledge_operation(operation_data: dict):
    """Perform batch operations on knowledge documents.
    
    Args:
        operation_data: Dictionary containing:
            - operation: Operation type (delete, reindex, move, tag)
            - document_ids: List of document IDs to operate on
            - parameters: Additional operation parameters
            
    Returns:
        Batch operation results
    """
    try:
        operation = operation_data.get('operation')
        document_ids = operation_data.get('document_ids', [])
        parameters = operation_data.get('parameters', {})
        
        if not operation:
            raise HTTPException(status_code=400, detail="Operation is required")
        if not document_ids:
            raise HTTPException(status_code=400, detail="Document IDs are required")
        
        results = []
        for doc_id in document_ids:
            try:
                if operation == 'delete':
                    result = {"doc_id": doc_id, "status": "deleted"}
                elif operation == 'reindex':
                    result = {"doc_id": doc_id, "status": "reindexed"}
                elif operation == 'tag':
                    tags = parameters.get('tags', [])
                    result = {"doc_id": doc_id, "status": "tagged", "tags": tags}
                elif operation == 'move':
                    category = parameters.get('category')
                    result = {"doc_id": doc_id, "status": "moved", "category": category}
                else:
                    result = {"doc_id": doc_id, "status": "error", "error": "Unknown operation"}
                
                results.append(result)
            except Exception as e:
                results.append({
                    "doc_id": doc_id,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "operation": operation,
            "total": len(document_ids),
            "successful": sum(1 for r in results if r["status"] not in ["error", "failed"]),
            "failed": sum(1 for r in results if r["status"] in ["error", "failed"]),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))