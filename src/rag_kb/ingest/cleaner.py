"""Data cleaning utilities for RAG KB."""

import re
import hashlib
from typing import List, Dict, Any
from dataclasses import dataclass
from rag_kb.models import Document


@dataclass
class PIIEntity:
    """PII entity information."""
    text: str
    start: int
    end: int
    type: str


class PIIMasker:
    """Enhanced PII (Personally Identifiable Information) masking for data privacy."""
    
    def __init__(self):
        # Enhanced PII patterns
        self.patterns = {
            'phone': r'(?:(?:\+?86)?1[3-9]\d{9})',
            'id_card': r'(?:[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|10|11|12)(?:0[1-9]|[1-2]\d|30|31)\d{3}[\dXx])',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'credit_card': r'(?:\d{4}[-\s]?){3}\d{4}',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'url': r'https?://[^\s<>"{}|\\^`\[\]]+'
        }
        
    def mask_text(self, text: str, mask_char: str = '*') -> str:
        """Mask PII in text.
        
        Args:
            text: Input text
            mask_char: Character to use for masking
            
        Returns:
            Text with PII masked
        """
        masked_text = text
        entities = self.detect_pii(text)
        
        # Sort entities by position in reverse order to avoid index shifting
        entities_sorted = sorted(entities, key=lambda x: x.start, reverse=True)
        
        for entity in entities_sorted:
            masked_text = masked_text[:entity.start] + mask_char * (entity.end - entity.start) + masked_text[entity.end:]
        
        return masked_text
    
    def detect_pii(self, text: str) -> List[PIIEntity]:
        """Detect PII entities in text.
        
        Args:
            text: Input text
            
        Returns:
            List of PII entities
        """
        entities = []
        
        for pii_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                entities.append(PIIEntity(
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    type=pii_type
                ))
        
        return entities


class TextCleaner:
    """Enhanced text cleaning utilities."""
    
    def __init__(self):
        self.pii_masker = PIIMasker()
    
    def clean_text(self, text: str, mask_pii: bool = True) -> str:
        """Clean text by removing noise and optionally masking PII.
        
        Args:
            text: Input text
            mask_pii: Whether to mask PII
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page headers/footers (common patterns)
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'第\d+页', '', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Mask PII if requested
        if mask_pii:
            text = self.pii_masker.mask_text(text)
        
        return text.strip()
    
    def deduplicate_chunks(self, chunks: List[str], threshold: float = 0.9) -> List[str]:
        """Simple deduplication based on similarity.
        
        Args:
            chunks: List of text chunks
            threshold: Similarity threshold (0-1)
            
        Returns:
            Deduplicated chunks
        """
        if not chunks:
            return []
        
        unique_chunks = []
        seen_hashes = set()
        
        for chunk in chunks:
            # Use hash for exact deduplication
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
            
            if chunk_hash not in seen_hashes:
                seen_hashes.add(chunk_hash)
                unique_chunks.append(chunk)
        
        return unique_chunks


def dedupe_by_hash(documents: List[Document]) -> List[Document]:
    """Remove duplicate documents based on file hash."""
    seen = set()
    unique = []
    for doc in documents:
        if doc.file_hash in seen:
            continue
        seen.add(doc.file_hash)
        unique.append(doc)
    return unique


def mask_pii_placeholder(text: str) -> str:
    """Placeholder PII de-identification using regex patterns.
    
    Replace with a dedicated NER/PII library in production.
    """
    # Chinese ID card (18 digits)
    text = re.sub(r'\d{18}', '[ID]', text)
    # Chinese mobile number
    text = re.sub(r'1[3-9]\d{9}', '[MOBILE]', text)
    # Credit card number
    text = re.sub(r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}', '[CARD]', text)
    return text