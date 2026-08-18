"""Incremental update utilities for RAG KB."""

import hashlib
import json
import shutil
from pathlib import Path
from typing import List, Set, Tuple, Callable, Dict, Any
from datetime import datetime

CHUNK_MAP = Path('./data/chunk_map.json')
CATEGORY_DIR = Path('./data/category_dbs')
DOC_REGISTRY = Path('./data/doc_registry.json')


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


def load_doc_registry() -> Dict[str, Any]:
    """Load document registry with version tracking."""
    if DOC_REGISTRY.exists():
        return json.loads(DOC_REGISTRY.read_text(encoding='utf-8'))
    return {}


def save_doc_registry(registry: Dict[str, Any]):
    """Save document registry to disk."""
    DOC_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    DOC_REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding='utf-8')


def register_document(doc_id: str, file_hash: str, source: str, metadata: Dict[str, Any] = None):
    """Register a document in the registry with version tracking.
    
    Args:
        doc_id: Document ID
        file_hash: Current file hash
        source: Source file path
        metadata: Additional document metadata
    """
    registry = load_doc_registry()
    registry[doc_id] = {
        'hash': file_hash,
        'source': source,
        'registered_at': datetime.utcnow().isoformat(),
        'metadata': metadata or {}
    }
    save_doc_registry(registry)


def get_document_version(doc_id: str) -> Dict[str, Any]:
    """Get current version information for a document.
    
    Args:
        doc_id: Document ID
        
    Returns:
        Document version information or None if not found
    """
    registry = load_doc_registry()
    return registry.get(doc_id)


def is_document_changed(doc_id: str, current_hash: str) -> bool:
    """Check if a document has changed since last registration.
    
    Args:
        doc_id: Document ID
        current_hash: Current file hash
        
    Returns:
        True if document has changed or is new, False otherwise
    """
    version_info = get_document_version(doc_id)
    if not version_info:
        return True  # New document
    return version_info.get('hash') != current_hash


def cleanup_old_chunks(doc_id: str, chunk_ids: List[str], adapter):
    """Clean up old chunks for a document when it's updated or deleted.
    
    Args:
        doc_id: Document ID
        chunk_ids: List of chunk IDs to remove
        adapter: LightRAG adapter instance
    """
    # This is a placeholder - actual implementation depends on LightRAG's deletion API
    # LightRAG doesn't have a direct delete API, so we might need to rebuild the index
    # or implement a soft-deletion mechanism
    pass


def plan_incremental_update(docs_dir: Path) -> Tuple[List[Path], List[str], List[Tuple[str, str]]]:
    """Plan comprehensive incremental update.
    
    Args:
        docs_dir: Directory containing documents
        
    Returns:
        Tuple of (files_to_add, doc_ids_to_delete, files_to_update)
        where files_to_update is list of (doc_id, new_file_path) tuples
    """
    registry = load_doc_registry()
    current_files = {}
    
    # Scan current directory
    for p in docs_dir.rglob('*'):
        if p.is_file() and not p.name.startswith('.'):
            file_hash = compute_file_hash(p)
            current_files[file_hash] = p
    
    to_add = []
    to_update = []
    to_delete = []
    
    # Check for new and modified files
    for file_hash, file_path in current_files.items():
        # Find if this file was already registered
        doc_id = None
        for registered_id, info in registry.items():
            if info.get('hash') == file_hash:
                doc_id = registered_id
                break
        
        if doc_id is None:
            # New file - need to generate doc_id from content
            to_add.append(file_path)
        elif is_document_changed(doc_id, file_hash):
            # File has changed
            to_update.append((doc_id, file_path))
    
    # Check for deleted files
    registered_hashes = {info.get('hash') for info in registry.values()}
    current_hashes = set(current_files.keys())
    deleted_hashes = registered_hashes - current_hashes
    
    for doc_id, info in registry.items():
        if info.get('hash') in deleted_hashes:
            to_delete.append(doc_id)
    
    return to_add, to_delete, to_update