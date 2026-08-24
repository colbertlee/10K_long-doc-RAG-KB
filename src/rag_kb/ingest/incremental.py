"""Incremental update utilities for RAG KB."""

import hashlib
import json
import shutil
from pathlib import Path
from typing import List, Set, Tuple, Callable

CHUNK_MAP = Path('./data/chunk_map.json')
CATEGORY_DIR = Path('./data/category_dbs')


def load_doc_chunk_map() -> dict:
    """Load document-to-chunk mapping from disk."""
    if CHUNK_MAP.exists():
        return json.loads(CHUNK_MAP.read_text(encoding='utf-8'))
    return {}


def save_doc_chunk_map(m: dict):
    """Save document-to-chunk mapping to disk."""
    CHUNK_MAP.parent.mkdir(parents=True, exist_ok=True)
    CHUNK_MAP.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding='utf-8')


def compute_file_hash(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan_update(docs_dir: Path, known: dict) -> Tuple[List[Path], Set[str]]:
    """Plan incremental update by comparing current files with known hashes.
    
    Args:
        docs_dir: Directory containing documents
        known: Dictionary of known file hashes
        
    Returns:
        Tuple of (files_to_add, doc_ids_to_delete)
    """
    current = {}
    for p in docs_dir.rglob('*'):
        if p.is_file():
            current[compute_file_hash(p)] = p
    
    to_add = [v for h, v in current.items() if h not in known]
    to_delete = {doc_id for doc_id, info in known.items() if info.get('hash') not in current}
    return to_add, to_delete


def update_doc_chunk_map(doc_id: str, file_hash: str, source: str, category: str, m: dict):
    """Update document-to-chunk mapping with new document info.
    
    Args:
        doc_id: Document ID
        file_hash: File hash
        source: Source identifier
        category: Document category
        m: Mapping dictionary to update
    """
    m[doc_id] = {'hash': file_hash, 'source': source, 'category': category}


def rebuild_category(category: str, docs: list, adapter_factory: Callable) -> object:
    """Rebuild LightRAG index for a specific category.
    
    Args:
        category: Category name
        docs: List of documents to index
        adapter_factory: Function to create LightRAG adapter
        
    Returns:
        LightRAG adapter instance
    """
    cat_dir = CATEGORY_DIR / category
    if cat_dir.exists():
        shutil.rmtree(cat_dir)
    cat_dir.parent.mkdir(parents=True, exist_ok=True)
    
    adapter = adapter_factory(cat_dir)
    for doc in docs:
        adapter.insert_chunks(doc.chunks)
    
    return adapter