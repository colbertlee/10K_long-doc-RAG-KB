"""Hashing utilities for file processing."""

import hashlib
from pathlib import Path


def compute_file_hash(path: Path) -> str:
    """Compute SHA256 hash of a file.
    
    Args:
        path: Path to the file
        
    Returns:
        SHA256 hash as hexadecimal string
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of text content.
    
    Args:
        content: Text content to hash
        
    Returns:
        SHA256 hash as hexadecimal string
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()