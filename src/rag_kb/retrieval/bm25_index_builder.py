"""BM25 index builder for hybrid search functionality."""

import json
import sys
from pathlib import Path
from typing import Any

from rag_kb.config import settings
from rag_kb.retrieval.bm25_search import BM25Search


class BM25IndexBuilder:
    """Build and manage BM25 index for hybrid search."""
    
    def __init__(self, working_dir: str = None):
        """Initialize BM25 index builder.
        
        Args:
            working_dir: Directory for BM25 index storage
        """
        self.working_dir = Path(working_dir or settings.data_dir / 'bm25_cache')
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.bm25_search = BM25Search()
        self.index_file = self.working_dir / 'bm25_index.json'
    
    async def build_index_from_documents(self, documents: list[dict[str, Any]]) -> dict[str, Any]:
        """Build BM25 index from documents.
        
        Args:
            documents: List of documents with 'doc_id', 'content', and 'metadata'
            
        Returns:
            Index building results
        """
        try:
            import sys
            print(f"Building BM25 index from {len(documents)} documents", file=sys.stderr, flush=True)
            
            # Prepare documents for BM25
            bm25_documents = []
            for doc in documents:
                doc_id = doc.get('doc_id', '')
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                # Combine title and content for better indexing
                title = metadata.get('title', metadata.get('filename', ''))
                text = f"{title}\n\n{content}" if title else content
                
                bm25_documents.append({
                    'id': doc_id,
                    'text': text,
                    'metadata': metadata
                })
            
            # Build BM25 index
            self.bm25_search.add_documents(bm25_documents)
            
            # Save index to disk
            self.bm25_search.save_index(self.index_file)
            
            print(f"BM25 index built successfully: {len(bm25_documents)} documents", file=sys.stderr, flush=True)
            
            return {
                'success': True,
                'documents_indexed': len(bm25_documents),
                'index_file': str(self.index_file),
                'message': f'BM25 index built from {len(bm25_documents)} documents'
            }
            
        except Exception as e:
            import traceback
            print(f"BM25 index building failed: {e}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            return {
                'success': False,
                'error': str(e),
                'documents_indexed': 0,
                'message': f'BM25 index building failed: {e!s}'
            }
    
    async def build_index_from_registry(self) -> dict[str, Any]:
        """Build BM25 index from document registry.
        
        Returns:
            Index building results
        """
        try:
            registry_file = Path(settings.data_dir) / 'document_registry.json'
            
            if not registry_file.exists():
                return {
                    'success': False,
                    'error': 'Document registry not found',
                    'documents_indexed': 0,
                    'message': 'Document registry not found'
                }
            
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Convert registry to document format
            documents = []
            for doc_id, doc_data in registry.items():
                documents.append({
                    'doc_id': doc_id,
                    'content': doc_data.get('content', ''),
                    'metadata': doc_data.get('metadata', {})
                })
            
            return await self.build_index_from_documents(documents)
            
        except Exception as e:
            import traceback
            print(f"BM25 index building from registry failed: {e}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            return {
                'success': False,
                'error': str(e),
                'documents_indexed': 0,
                'message': f'BM25 index building from registry failed: {e!s}'
            }
    
    async def load_index(self) -> bool:
        """Load BM25 index from disk.
        
        Returns:
            True if index loaded successfully
        """
        try:
            if self.index_file.exists():
                self.bm25_search.load_index(self.index_file)
                print(f"BM25 index loaded from {self.index_file}", file=sys.stderr, flush=True)
                return True
            else:
                print("BM25 index file not found", file=sys.stderr, flush=True)
                return False
        except Exception as e:
            print(f"Failed to load BM25 index: {e}", file=sys.stderr, flush=True)
            return False
    
    async def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search using BM25 index.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            Search results
        """
        try:
            # Ensure index is loaded
            if not self.bm25_search.total_docs:
                await self.load_index()
            
            results = self.bm25_search.search(query, top_k=top_k)
            return results
        except Exception as e:
            print(f"BM25 search failed: {e}", file=sys.stderr, flush=True)
            return []
    
    def get_index_stats(self) -> dict[str, Any]:
        """Get BM25 index statistics.
        
        Returns:
            Index statistics
        """
        return {
            'total_documents': self.bm25_search.total_docs,
            'avg_doc_length': self.bm25_search.avg_doc_length,
            'index_file_exists': self.index_file.exists(),
            'index_file_size': self.index_file.stat().st_size if self.index_file.exists() else 0
        }


# Global instance
bm25_index_builder = BM25IndexBuilder()