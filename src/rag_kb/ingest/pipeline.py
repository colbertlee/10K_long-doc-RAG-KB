"""Ingestion pipeline for processing documents."""

from pathlib import Path
from typing import Optional
from rag_kb.models import Document
from rag_kb.ingest.cleaner import mask_pii_placeholder
from rag_kb.parsers.registry import PARSER_REGISTRY


class IngestPipeline:
    """Pipeline for ingesting and processing documents."""
    
    def run(self, file: Path, acl: Optional[dict] = None) -> Document:
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
        
        if acl:
            doc.acl = acl
            for k, v in acl.items():
                # Keep source/category/ACL metadata scalar for downstream filtering and text header injection
                doc.metadata[f'acl_{k}'] = v[0] if isinstance(v, list) and v else str(v)
        
        doc.content = mask_pii_placeholder(doc.content)
        return doc