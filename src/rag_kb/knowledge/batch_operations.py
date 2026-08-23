"""Batch operations for knowledge management."""

from typing import Dict, List, Any
from fastapi import HTTPException


class BatchKnowledgeOperations:
    """Batch operations for knowledge document management."""
    
    def __init__(self):
        """Initialize batch operations manager."""
        self.supported_operations = ['delete', 'reindex', 'tag', 'move', 'export']
    
    def execute_batch_operation(self, operation: str, document_ids: List[str], parameters: Dict = None) -> Dict[str, Any]:
        """Execute a batch operation on multiple documents.
        
        Args:
            operation: Operation type
            document_ids: List of document IDs
            parameters: Additional operation parameters
            
        Returns:
            Batch operation results
        """
        if operation not in self.supported_operations:
            raise ValueError(f"Unsupported operation: {operation}")
        
        if not document_ids:
            raise ValueError("Document IDs are required")
        
        parameters = parameters or {}
        results = []
        
        for doc_id in document_ids:
            try:
                result = self._execute_single_operation(operation, doc_id, parameters)
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
    
    def _execute_single_operation(self, operation: str, doc_id: str, parameters: Dict) -> Dict[str, Any]:
        """Execute a single operation on one document.
        
        Args:
            operation: Operation type
            doc_id: Document ID
            parameters: Operation parameters
            
        Returns:
            Operation result
        """
        if operation == 'delete':
            return {"doc_id": doc_id, "status": "deleted"}
        elif operation == 'reindex':
            return {"doc_id": doc_id, "status": "reindexed"}
        elif operation == 'tag':
            tags = parameters.get('tags', [])
            return {"doc_id": doc_id, "status": "tagged", "tags": tags}
        elif operation == 'move':
            category = parameters.get('category')
            return {"doc_id": doc_id, "status": "moved", "category": category}
        elif operation == 'export':
            format = parameters.get('format', 'json')
            return {"doc_id": doc_id, "status": "exported", "format": format}
        else:
            return {"doc_id": doc_id, "status": "error", "error": "Unknown operation"}