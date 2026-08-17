"""Data cleaning utilities for RAG KB."""

import re
from typing import List
from rag_kb.models import Document


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