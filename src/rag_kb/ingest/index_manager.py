"""Index manager for automatic indexing and integrity checking."""

import json
import asyncio
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

from rag_kb.config import settings


class IndexManager:
    """Manage document indexing with automatic scanning and integrity checking."""
    
    def __init__(self):
        """Initialize index manager."""
        self.data_dir = settings.data_dir
        self.upload_dir = self.data_dir / 'uploads'
        self.registry_file = self.data_dir / 'document_registry.json'
        self.lightrag_working_dir = settings.lightrag_working_dir
    
    def get_unindexed_documents(self) -> List[Dict]:
        """Get list of documents that are uploaded but not indexed.
        
        Returns:
            List of unindexed document dictionaries
        """
        unindexed = []
        
        # Load document registry
        registry = {}
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        
        # Check each document in registry
        for doc_id, doc_info in registry.items():
            # Check if document is indexed
            if not self._is_document_indexed(doc_id):
                unindexed.append({
                    'doc_id': doc_id,
                    'title': doc_info.get('title', doc_id),
                    'timestamp': doc_info.get('timestamp', ''),
                    'import_type': doc_info.get('import_type', 'upload')
                })
        
        return unindexed
    
    def _is_document_indexed(self, doc_id: str) -> bool:
        """Check if a document is indexed in LightRAG.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if indexed, False otherwise
        """
        try:
            # First check if document is marked as indexed in registry
            registry = {}
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            
            if doc_id in registry:
                doc_info = registry[doc_id]
                # If explicitly marked as indexed, consider it indexed
                if doc_info.get('indexed') == True:
                    return True
            
            # Check LightRAG working directory for document chunks
            lightrag_dir = Path(self.lightrag_working_dir)
            if lightrag_dir.exists():
                # Check for various LightRAG index files that might contain the document
                # LightRAG stores indexed content in multiple files
                vdb_file = lightrag_dir / 'vdb_chunks.json'
                if vdb_file.exists():
                    try:
                        with open(vdb_file, 'r', encoding='utf-8') as f:
                            vdb_data = json.load(f)
                            # Check if document ID appears in the vector database
                            vdb_str = json.dumps(vdb_data)
                            if doc_id in vdb_str:
                                return True
                    except:
                        pass
                
                # Check for graph database files
                graph_files = [
                    lightrag_dir / 'graph_chunk_entity_relation.json',
                    lightrag_dir / 'kv_store_full_docs.json'
                ]
                for graph_file in graph_files:
                    if graph_file.exists():
                        try:
                            with open(graph_file, 'r', encoding='utf-8') as f:
                                graph_data = json.load(f)
                                graph_str = json.dumps(graph_data)
                                if doc_id in graph_str:
                                    return True
                        except:
                            pass
            
            # Check BM25 index as fallback
            from rag_kb.lightrag.adapter import LightRAGAdapter
            rag = LightRAGAdapter()
            
            if rag.bm25_index_path.exists():
                try:
                    rag.bm25_search.load_index(rag.bm25_index_path)
                    indexed_ids = {doc['id'] for doc in rag.bm25_search.documents}
                    return doc_id in indexed_ids
                except:
                    pass
            
            return False
        except Exception as e:
            print(f"Error checking indexed status for {doc_id}: {e}")
            return False
    
    def get_index_integrity_report(self) -> Dict:
        """Generate index integrity report.
        
        Returns:
            Dictionary with integrity information
        """
        report = {
            'total_uploaded': 0,
            'total_indexed': 0,
            'unindexed_count': 0,
            'orphan_files': 0,
            'unindexed_documents': [],
            'orphan_documents': [],
            'index_health': 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        # Get actual files on disk
        actual_files = set()
        if self.upload_dir.exists():
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    actual_files.add(file_path.name)
        
        report['total_uploaded'] = len(actual_files)
        
        # Load document registry
        registry = {}
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        
        # Check each document in registry
        registry_files = set(registry.keys())
        orphan_files = registry_files - actual_files
        
        report['orphan_files'] = len(orphan_files)
        report['orphan_documents'] = list(orphan_files)
        
        # Check each actual file
        for filename in actual_files:
            if filename in registry:
                if self._is_document_indexed(filename):
                    report['total_indexed'] += 1
                else:
                    report['unindexed_count'] += 1
                    doc_info = registry[filename]
                    report['unindexed_documents'].append({
                        'doc_id': filename,
                        'title': doc_info.get('title', filename),
                        'timestamp': doc_info.get('timestamp', ''),
                        'import_type': doc_info.get('import_type', 'upload')
                    })
        
        # Calculate index health
        if report['total_uploaded'] == 0:
            report['index_health'] = 'no_documents'
        elif report['total_indexed'] == report['total_uploaded']:
            report['index_health'] = 'healthy'
        elif report['total_indexed'] > 0:
            report['index_health'] = 'partial'
        else:
            report['index_health'] = 'unhealthy'
        
        # Ensure all required fields are present
        if 'unindexed_count' not in report:
            report['unindexed_count'] = len(report.get('unindexed_documents', []))
        
        return report
    
    async def index_document(self, doc_id: str) -> Tuple[bool, str]:
        """Index a specific document.
        
        Args:
            doc_id: Document ID to index
            
        Returns:
            Tuple of (success, message)
        """
        import time
        start_time = time.time()
        
        try:
            # Load document from registry
            registry = {}
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            
            if doc_id not in registry:
                return False, f"Document {doc_id} not found in registry"
            
            doc_info = registry[doc_id]
            content = doc_info.get('content', '')
            
            if not content or not content.strip():
                return False, f"Document {doc_id} has empty content"
            
            # Index using LightRAG
            from rag_kb.lightrag.adapter import LightRAGAdapter
            from rag_kb.utils.index_performance_monitor import get_index_performance_monitor
            
            rag = LightRAGAdapter()
            await rag.ensure_initialized()
            
            print(f"Attempting to index document {doc_id} (content length: {len(content)})", flush=True)
            
            ingest_success = await rag.ingest([{
                'doc_id': doc_id,
                'content': content,
                'metadata': doc_info.get('metadata', {})
            }])
            
            duration = time.time() - start_time
            
            # Record performance
            perf_monitor = get_index_performance_monitor()
            perf_monitor.record_index_operation(
                'index',
                doc_id,
                ingest_success,
                duration,
                {'content_length': len(content)}
            )
            
            if ingest_success:
                # Update registry to mark as indexed
                registry[doc_id]['indexed'] = True
                registry[doc_id]['indexing_error'] = None
                
                with open(self.registry_file, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2, ensure_ascii=False)
                
                return True, f"Document {doc_id} indexed successfully (duration: {duration:.2f}s)"
            else:
                return False, f"Document {doc_id} indexing failed (LightRAG returned False)"
                
        except Exception as e:
            duration = time.time() - start_time
            
            # Record performance for failed operation
            perf_monitor = get_index_performance_monitor()
            perf_monitor.record_index_operation(
                'index',
                doc_id,
                False,
                duration,
                {'error': str(e)}
            )
            
            return False, f"Document {doc_id} indexing failed with error: {str(e)}"
    
    def scan_upload_directory(self) -> List[Dict]:
        """Scan upload directory for files not in registry.
        
        Returns:
            List of files found in upload directory but not in registry
        """
        unregistered_files = []
        
        # Load existing registry
        registry = {}
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        
        # Scan upload directory
        if self.upload_dir.exists():
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    # Generate doc_id from filename (include extension to avoid duplicates)
                    doc_id = file_path.name  # Use full filename instead of stem
                    
                    # Check if file is already in registry
                    if doc_id not in registry:
                        # Skip binary files
                        if file_path.suffix.lower() in ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xls', '.xlsx']:
                            print(f"Skipping binary file: {file_path.name}", flush=True)
                            continue
                        
                        # Try to read file content with different encodings
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                        except UnicodeDecodeError:
                            # Try latin-1 encoding for text files
                            try:
                                with open(file_path, 'r', encoding='latin-1') as f:
                                    content = f.read()
                            except Exception as e:
                                print(f"Error reading file {file_path}: {e}")
                                continue
                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}")
                            continue
                        
                        unregistered_files.append({
                            'doc_id': doc_id,
                            'title': file_path.name,
                            'file_path': str(file_path),
                            'content': content,
                            'file_size': file_path.stat().st_size,
                            'timestamp': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
        
        return unregistered_files
    
    def register_scanned_files(self, files: List[Dict]) -> Tuple[int, str]:
        """Register scanned files in document registry.
        
        Args:
            files: List of file dictionaries from scan_upload_directory
            
        Returns:
            Tuple of (count, message)
        """
        if not files:
            return 0, "No files to register"
        
        # Load existing registry
        registry = {}
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        
        # Add files to registry
        registered_count = 0
        for file_info in files:
            doc_id = file_info['doc_id']
            
            if doc_id not in registry:
                registry[doc_id] = {
                    'title': file_info['title'],
                    'source': file_info['file_path'],
                    'content': file_info['content'],
                    'timestamp': file_info['timestamp'],
                    'import_type': 'directory_scan',
                    'indexed': False,
                    'file_size': file_info['file_size'],
                    'metadata': {
                        'source_file': file_info['file_path'],
                        'file_size': file_info['file_size']
                    }
                }
                registered_count += 1
        
        # Save updated registry
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        return registered_count, f"Registered {registered_count} files"
    
    async def auto_scan_and_index(self) -> Dict:
        """Automatically scan upload directory and index unregistered files.
        
        Returns:
            Dictionary with scan and indexing results
        """
        results = {
            'scanned_files': 0,
            'registered_files': 0,
            'indexed_files': 0,
            'failed_files': 0,
            'errors': []
        }
        
        try:
            # Step 1: Scan upload directory
            unregistered_files = self.scan_upload_directory()
            results['scanned_files'] = len(unregistered_files)
            
            if not unregistered_files:
                return {**results, 'message': 'No new files found in upload directory'}
            
            # Step 2: Register files
            registered_count, message = self.register_scanned_files(unregistered_files)
            results['registered_files'] = registered_count
            
            # Step 3: Index registered files
            for file_info in unregistered_files:
                doc_id = file_info['doc_id']
                try:
                    success, msg = await self.index_document(doc_id)
                    if success:
                        results['indexed_files'] += 1
                    else:
                        results['failed_files'] += 1
                        results['errors'].append(f"{doc_id}: {msg}")
                except Exception as e:
                    results['failed_files'] += 1
                    results['errors'].append(f"{doc_id}: {str(e)}")
            
            return {**results, 'message': f'Scan complete: {results["indexed_files"]} indexed, {results["failed_files"]} failed'}
            
        except Exception as e:
            results['errors'].append(f"Scan failed: {str(e)}")
            return results
    
    async def index_all_unindexed(self) -> Dict:
        """Index all unindexed documents.
        
        Returns:
            Dictionary with indexing results
        """
        results = {
            'total_unindexed': 0,
            'success_count': 0,
            'failure_count': 0,
            'results': []
        }
        
        unindexed = self.get_unindexed_documents()
        results['total_unindexed'] = len(unindexed)
        
        for doc in unindexed:
            doc_id = doc['doc_id']
            success, message = await self.index_document(doc_id)
            
            results['results'].append({
                'doc_id': doc_id,
                'success': success,
                'message': message
            })
            
            if success:
                results['success_count'] += 1
            else:
                results['failure_count'] += 1
        
        return results
    
    def get_file_indexing_status(self, file_path: Path) -> Dict:
        """Get indexing status for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with indexing status
        """
        doc_id = file_path.stem
        
        return {
            'file_path': str(file_path),
            'doc_id': doc_id,
            'indexed': self._is_document_indexed(doc_id),
            'in_registry': self._is_document_in_registry(doc_id)
        }
    
    def _is_document_in_registry(self, doc_id: str) -> bool:
        """Check if document is in registry.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if in registry, False otherwise
        """
        if not self.registry_file.exists():
            return False
        
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            return doc_id in registry
        except Exception:
            return False


# Global index manager instance
_index_manager = None


def get_index_manager() -> IndexManager:
    """Get or create global index manager instance.
    
    Returns:
        IndexManager instance
    """
    global _index_manager
    if _index_manager is None:
        _index_manager = IndexManager()
    return _index_manager