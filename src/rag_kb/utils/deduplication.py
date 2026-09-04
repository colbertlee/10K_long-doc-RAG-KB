"""Document deduplication utility with multi-dimensional fingerprinting."""

import hashlib
import json
from datetime import datetime
from pathlib import Path


class DocumentDeduplicator:
    """Multi-dimensional document deduplication system."""
    
    def __init__(self, cache_file: Path | None = None):
        """Initialize document deduplicator.
        
        Args:
            cache_file: Optional file to persist deduplication cache
        """
        self.content_cache: dict[str, str] = {}  # content_hash -> doc_id
        self.metadata_cache: dict[str, str] = {}  # metadata_fingerprint -> doc_id
        self.filename_cache: dict[str, str] = {}  # filename -> doc_id
        self.cache_file = cache_file
        
        # Load existing cache if available
        if cache_file and cache_file.exists():
            self._load_cache()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate SHA256 hash of document content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _generate_metadata_fingerprint(self, metadata: dict) -> str:
        """Generate fingerprint from metadata."""
        # Normalize metadata for consistent fingerprinting
        normalized = {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'created': metadata.get('created', ''),
            'pages': metadata.get('pages', 0),
            'file_size': metadata.get('file_size', 0),
        }
        return hashlib.sha256(json.dumps(normalized, sort_keys=True).encode()).hexdigest()
    
    def _generate_filename_key(self, filename: str) -> str:
        """Generate normalized filename key."""
        return filename.lower().strip()
    
    def is_duplicate(self, doc_id: str, content: str, metadata: dict) -> tuple[bool, str]:
        """Check if document is a duplicate using multi-dimensional analysis.
        
        Args:
            doc_id: Document ID
            content: Document content
            metadata: Document metadata
            
        Returns:
            Tuple of (is_duplicate, reason)
        """
        # Check content hash (exact duplicate)
        content_hash = self._generate_content_hash(content)
        if content_hash in self.content_cache:
            existing_doc_id = self.content_cache[content_hash]
            return True, f"Content hash match with document {existing_doc_id}"
        
        # Check metadata fingerprint (likely duplicate)
        metadata_fingerprint = self._generate_metadata_fingerprint(metadata)
        if metadata_fingerprint in self.metadata_cache:
            existing_doc_id = self.metadata_cache[metadata_fingerprint]
            return True, f"Metadata fingerprint match with document {existing_doc_id}"
        
        # Check filename (possible duplicate)
        filename = metadata.get('filename', '')
        if filename:
            filename_key = self._generate_filename_key(filename)
            if filename_key in self.filename_cache:
                existing_doc_id = self.filename_cache[filename_key]
                # Only flag as duplicate if content is similar (90%+)
                existing_content_hash = self.content_cache.get(existing_doc_id)
                if existing_content_hash and self._is_content_similar(content_hash, existing_content_hash):
                    return True, f"Filename and content similarity match with document {existing_doc_id}"
        
        # Not a duplicate, register it
        self.content_cache[content_hash] = doc_id
        self.metadata_cache[metadata_fingerprint] = doc_id
        if filename:
            self.filename_cache[filename_key] = doc_id
        
        # Save cache if file is configured
        if self.cache_file:
            self._save_cache()
        
        return False, "New unique document"
    
    def _is_content_similar(self, hash1: str, hash2: str, threshold: float = 0.9) -> bool:
        """Check if two content hashes are similar (placeholder for future implementation).
        
        Note: This is a simplified check. For true content similarity,
        you would need to store the actual content and use similarity algorithms.
        """
        # For now, exact hash match only
        return hash1 == hash2
    
    def _save_cache(self):
        """Save deduplication cache to file."""
        if not self.cache_file:
            return
        
        try:
            cache_data = {
                'content_cache': self.content_cache,
                'metadata_cache': self.metadata_cache,
                'filename_cache': self.filename_cache,
                'timestamp': datetime.now().isoformat()
            }
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save deduplication cache: {e}", flush=True)
    
    def _load_cache(self):
        """Load deduplication cache from file."""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                self.content_cache = cache_data.get('content_cache', {})
                self.metadata_cache = cache_data.get('metadata_cache', {})
                self.filename_cache = cache_data.get('filename_cache', {})
            print(f"Loaded deduplication cache with {len(self.content_cache)} entries", flush=True)
        except Exception as e:
            print(f"Warning: Could not load deduplication cache: {e}", flush=True)
    
    def get_duplicate_stats(self) -> dict:
        """Get deduplication statistics."""
        return {
            'total_documents': len(self.content_cache),
            'content_hashes': len(self.content_cache),
            'metadata_fingerprints': len(self.metadata_cache),
            'filename_entries': len(self.filename_cache)
        }
    
    def clear_cache(self):
        """Clear all deduplication cache."""
        self.content_cache.clear()
        self.metadata_cache.clear()
        self.filename_cache.clear()
        if self.cache_file and self.cache_file.exists():
            self.cache_file.unlink()
        print("Deduplication cache cleared", flush=True)


# Global deduplicator instance
_global_deduplicator: DocumentDeduplicator | None = None


def get_deduplicator(cache_file: Path | None = None) -> DocumentDeduplicator:
    """Get the global document deduplicator instance."""
    global _global_deduplicator
    if _global_deduplicator is None:
        cache_path = cache_file or Path('./data/deduplication_cache.json')
        _global_deduplicator = DocumentDeduplicator(cache_file=cache_path)
    return _global_deduplicator