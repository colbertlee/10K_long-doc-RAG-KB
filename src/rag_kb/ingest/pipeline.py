"""Ingestion pipeline for processing documents with knowledge-aware processing."""

from pathlib import Path
from typing import Optional

from rag_kb.ingest.cleaner import mask_pii_placeholder
from rag_kb.ingest.knowledge_cleaner import TechnicalDocumentCleaner, KnowledgePoint
from rag_kb.models import Document
from rag_kb.parsers.registry import PARSER_REGISTRY
from rag_kb.utils.deduplication import get_deduplicator
from rag_kb.config.core_config import settings


class IngestPipeline:
    """Pipeline for ingesting and processing documents with knowledge extraction."""
    
    def __init__(self, enable_deduplication: bool = True, enable_knowledge_processing: bool = True):
        """Initialize ingestion pipeline.
        
        Args:
            enable_deduplication: Whether to enable document deduplication
            enable_knowledge_processing: Whether to enable knowledge-aware processing
        """
        self.enable_deduplication = enable_deduplication
        self.deduplicator = get_deduplicator() if enable_deduplication else None
        self.enable_knowledge_processing = enable_knowledge_processing
        
        # Initialize knowledge processing components
        if self.enable_knowledge_processing:
            self.technical_cleaner = TechnicalDocumentCleaner()
        else:
            self.technical_cleaner = None
    
    def run(self, file: Path, acl: dict | None = None) -> Document:
        """Process a file through the ingestion pipeline.
        
        Args:
            file: Path to the file to process
            acl: Optional access control list metadata
            
        Returns:
            Processed Document with cleaned content and metadata
        """
        parser = next((p for p in PARSER_REGISTRY if p.can_parse(file)), None)
        if parser is None:
            raise ValueError(f'No parser registered for {file.suffix}')
        
        doc = parser.parse(file)
        
        # Check for duplicates using multi-dimensional analysis
        if self.enable_deduplication and self.deduplicator:
            is_duplicate, reason = self.deduplicator.is_duplicate(
                doc.doc_id, 
                doc.content, 
                doc.metadata
            )
            if is_duplicate:
                print(f"Skipping duplicate document {file.name}: {reason}", flush=True)
                return doc  # Return the document but marked as skipped
        
        if acl:
            doc.acl = acl
            for k, v in acl.items():
                # Keep source/category/ACL metadata scalar for downstream filtering and text header injection
                doc.metadata[f'acl_{k}'] = v[0] if isinstance(v, list) and v else str(v)
        
        # Apply knowledge-aware processing if enabled
        if self.enable_knowledge_processing and self.technical_cleaner:
            doc.content, knowledge_points = self.technical_cleaner.clean_document(doc.content)
            
            # Store knowledge points in metadata
            doc.metadata['knowledge_points'] = [
                {
                    'text': kp.text,
                    'type': kp.type,
                    'confidence': kp.confidence,
                    'location': kp.location,
                    'related_terms': kp.related_terms
                }
                for kp in knowledge_points
            ]
            
            # Add knowledge summary
            knowledge_summary = self.technical_cleaner.get_knowledge_summary(knowledge_points)
            doc.metadata['knowledge_summary'] = knowledge_summary
            
            print(f"Extracted {len(knowledge_points)} knowledge points from {file.name}", flush=True)
        else:
            # Apply basic PII masking
            doc.content = mask_pii_placeholder(doc.content)
        
        return doc
    
    def get_knowledge_points(self, doc: Document) -> list[KnowledgePoint]:
        """Extract knowledge points from a document.
        
        Args:
            doc: Document to extract knowledge points from
            
        Returns:
            List of knowledge points
        """
        if not self.technical_cleaner:
            return []
        
        _, knowledge_points = self.technical_cleaner.clean_document(doc.content)
        return knowledge_points