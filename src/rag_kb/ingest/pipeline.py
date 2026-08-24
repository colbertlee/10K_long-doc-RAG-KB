"""Ingestion pipeline for processing documents."""

from pathlib import Path
from typing import Optional, List
from rag_kb.models import Document
from rag_kb.ingest.cleaner import mask_pii_placeholder
from rag_kb.parsers.registry import PARSER_REGISTRY
from rag_kb.processing import processing_tracker, ProcessingStatus


class IngestPipeline:
    """Pipeline for ingesting and processing documents."""
    
    def __init__(self, enable_tracking: bool = True):
        """Initialize ingestion pipeline.
        
        Args:
            enable_tracking: Whether to enable processing tracking
        """
        self.enable_tracking = enable_tracking
    
    def run(self, file: Path, acl: Optional[dict] = None, task_id: str = None) -> Document:
        """Process a file through the ingestion pipeline.
        
        Args:
            file: Path to the file to process
            acl: Optional access control list metadata
            task_id: Optional task ID for tracking
            
        Returns:
            Processed Document with cleaned content and metadata
        """
        if self.enable_tracking and task_id:
            processing_tracker.update_task(task_id, ProcessingStatus.PARSING, 10, "Parsing document")
        
        parser = next((p for p in PARSER_REGISTRY if p.can_parse(file)), None)
        if parser is None:
            if self.enable_tracking and task_id:
                processing_tracker.update_task(task_id, ProcessingStatus.FAILED, error_message=f"No parser registered for {file.suffix}")
            raise ValueError(f'No parser registered for {file.suffix}')
        
        doc = parser.parse(file)
        
        if self.enable_tracking and task_id:
            processing_tracker.update_task(task_id, progress=30, current_stage="Applying ACL and cleaning")
        
        if acl:
            doc.acl = acl
            for k, v in acl.items():
                # Keep source/category/ACL metadata scalar for downstream filtering and text header injection
                doc.metadata[f'acl_{k}'] = v[0] if isinstance(v, list) and v else str(v)
        
        doc.content = mask_pii_placeholder(doc.content)
        
        if self.enable_tracking and task_id:
            processing_tracker.update_task(task_id, progress=50, current_stage="Document parsing completed")
        
        return doc
    
    async def ingest_documents(self, user_id: str, kb_name: str, 
                              product_id: str = None) -> dict:
        """Ingest documents with progress tracking.
        
        Args:
            user_id: User ID
            kb_name: Knowledge base name
            product_id: Optional product ID
            
        Returns:
            Ingestion results
        """
        from rag_kb.config import settings
        import os
        
        upload_dir = settings.data_dir / 'users' / user_id / 'kbs' / kb_name / 'uploads'
        
        if not upload_dir.exists():
            return {
                'documents_processed': 0,
                'chunks_created': 0,
                'graph_nodes': 0,
                'graph_edges': 0,
                'processing_time': 0
            }
        
        # Create task for each file
        task_ids = []
        for file_path in upload_dir.glob('*'):
            if file_path.is_file():
                task_id = processing_tracker.create_task(
                    user_id=user_id,
                    kb_name=kb_name,
                    file_path=str(file_path),
                    file_name=file_path.name,
                    metadata={'product_id': product_id}
                )
                task_ids.append(task_id)
        
        # Process files
        documents_processed = 0
        chunks_created = 0
        graph_nodes = 0
        graph_edges = 0
        
        for i, file_path in enumerate(upload_dir.glob('*')):
            if file_path.is_file():
                task_id = task_ids[i] if i < len(task_ids) else None
                
                try:
                    # Run ingestion pipeline
                    doc = self.run(file_path, task_id=task_id)
                    documents_processed += 1
                    
                    if self.enable_tracking and task_id:
                        processing_tracker.update_task(task_id, progress=70, current_stage="Chunking document")
                    
                    # Simulate chunking (in real implementation, use actual chunker)
                    chunks_created += len(doc.content.split('\n\n')) // 2
                    
                    if self.enable_tracking and task_id:
                        processing_tracker.update_task(task_id, progress=90, current_stage="Generating graph")
                    
                    # Simulate graph generation
                    graph_nodes += 5
                    graph_edges += 8
                    
                    if self.enable_tracking and task_id:
                        processing_tracker.update_task(task_id, ProcessingStatus.COMPLETED, 100, "Completed")
                    
                except Exception as e:
                    if self.enable_tracking and task_id:
                        processing_tracker.update_task(task_id, ProcessingStatus.FAILED, error_message=str(e))
                    print(f"Error processing {file_path}: {e}")
        
        return {
            'documents_processed': documents_processed,
            'chunks_created': chunks_created,
            'graph_nodes': graph_nodes,
            'graph_edges': graph_edges,
            'processing_time': 0  # Would be calculated in real implementation
        }