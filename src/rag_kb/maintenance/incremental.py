"""Incremental update mechanism for knowledge base maintenance."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from rag_kb.config import settings


class IncrementalUpdater:
    """Handle incremental updates for knowledge base."""
    
    def __init__(self):
        self.data_dir = settings.data_dir
        self.registry_file = self.data_dir / 'document_registry.json'
        self.hash_file = self.data_dir / 'file_hashes.json'
        self.change_log_file = self.data_dir / 'change_log.json'
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA256 hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def get_file_hashes(self) -> dict[str, str]:
        """Get stored file hashes.
        
        Returns:
            Dictionary mapping file paths to hashes
        """
        if self.hash_file.exists():
            with open(self.hash_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_file_hashes(self, hashes: dict[str, str]):
        """Save file hashes.
        
        Args:
            hashes: Dictionary mapping file paths to hashes
        """
        with open(self.hash_file, 'w', encoding='utf-8') as f:
            json.dump(hashes, f, indent=2, ensure_ascii=False)
    
    def detect_changes(self, file_paths: list[Path]) -> dict[str, Any]:
        """Detect changed files since last update.
        
        Args:
            file_paths: List of file paths to check
            
        Returns:
            Dictionary with change information
        """
        stored_hashes = self.get_file_hashes()
        changes = {
            'new': [],
            'modified': [],
            'unchanged': [],
            'deleted': []
        }
        
        current_files = set(str(p) for p in file_paths if p.exists())
        stored_files = set(stored_hashes.keys())
        
        # Detect new files
        for file_path in file_paths:
            if file_path.exists():
                file_str = str(file_path)
                if file_str not in stored_files:
                    changes['new'].append(file_str)
                else:
                    current_hash = self.calculate_file_hash(file_path)
                    if current_hash != stored_hashes[file_str]:
                        changes['modified'].append(file_str)
                    else:
                        changes['unchanged'].append(file_str)
        
        # Detect deleted files
        for file_str in stored_files:
            if file_str not in current_files:
                changes['deleted'].append(file_str)
        
        return changes
    
    def log_change(self, change_type: str, file_path: str, details: dict[str, Any]):
        """Log a change to the change log.
        
        Args:
            change_type: Type of change (new, modified, deleted)
            file_path: Path to the file
            details: Additional details about the change
        """
        change_log = []
        if self.change_log_file.exists():
            with open(self.change_log_file, 'r', encoding='utf-8') as f:
                change_log = json.load(f)
        
        change_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': change_type,
            'file_path': file_path,
            'details': details
        }
        
        change_log.append(change_entry)
        
        # Keep only last 1000 changes
        if len(change_log) > 1000:
            change_log = change_log[-1000:]
        
        with open(self.change_log_file, 'w', encoding='utf-8') as f:
            json.dump(change_log, f, indent=2, ensure_ascii=False)
    
    def get_change_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent change log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of change log entries
        """
        if self.change_log_file.exists():
            with open(self.change_log_file, 'r', encoding='utf-8') as f:
                change_log = json.load(f)
                return change_log[-limit:]
        return []
    
    def cleanup_deleted_documents(self, deleted_files: list[str]):
        """Clean up deleted documents from registry.
        
        Args:
            deleted_files: List of deleted file paths
        """
        if not self.registry_file.exists():
            return
        
        with open(self.registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Remove deleted documents from registry
        updated_registry = {}
        for doc_id, doc_data in registry.items():
            if doc_data.get('source') not in deleted_files:
                updated_registry[doc_id] = doc_data
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(updated_registry, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> dict[str, Any]:
        """Get knowledge base statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_documents': 0,
            'total_chunks': 0,
            'indexed_documents': 0,
            'last_update': None,
            'storage_size': 0
        }
        
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                stats['total_documents'] = len(registry)
                stats['total_chunks'] = sum(doc.get('chunks', 0) for doc in registry.values())
                stats['indexed_documents'] = sum(1 for doc in registry.values() if doc.get('indexed', False))
        
        if self.change_log_file.exists():
            with open(self.change_log_file, 'r', encoding='utf-8') as f:
                change_log = json.load(f)
                if change_log:
                    stats['last_update'] = change_log[-1]['timestamp']
        
        # Calculate storage size
        if self.data_dir.exists():
            stats['storage_size'] = sum(f.stat().st_size for f in self.data_dir.rglob('*') if f.is_file())
        
        return stats