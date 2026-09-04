"""Index recovery mechanism for corrupted or damaged indexes."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

from rag_kb.config import settings


class IndexRecoveryManager:
    """Manager for index recovery and repair."""
    
    def __init__(self):
        """Initialize index recovery manager."""
        self.lightrag_working_dir = settings.lightrag_working_dir
        self.backup_dir = self.lightrag_working_dir / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> Dict:
        """Create a backup of the current index.
        
        Returns:
            Dictionary with backup information
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_dir / f'index_backup_{timestamp}'
            
            print(f"Creating backup at: {backup_path}", flush=True)
            
            # Copy index files to backup
            if self.lightrag_working_dir.exists():
                shutil.copytree(self.lightrag_working_dir, backup_path, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
            
            return {
                'success': True,
                'backup_path': str(backup_path),
                'timestamp': timestamp,
                'message': 'Backup created successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Backup creation failed'
            }
    
    def list_backups(self) -> List[Dict]:
        """List available backups.
        
        Returns:
            List of backup information
        """
        backups = []
        
        if self.backup_dir.exists():
            for backup_path in self.backup_dir.iterdir():
                if backup_path.is_dir() and backup_path.name.startswith('index_backup_'):
                    backups.append({
                        'name': backup_path.name,
                        'path': str(backup_path),
                        'timestamp': backup_path.name.replace('index_backup_', '')
                    })
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def restore_backup(self, backup_name: str) -> Dict:
        """Restore index from backup.
        
        Args:
            backup_name: Name of the backup to restore
            
        Returns:
            Dictionary with restore result
        """
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                return {
                    'success': False,
                    'error': f"Backup {backup_name} not found",
                    'message': 'Backup not found'
                }
            
            print(f"Restoring from backup: {backup_path}", flush=True)
            
            # Create backup of current state before restore
            current_backup = self.create_backup()
            
            # Remove current index files (except backups)
            for item in self.lightrag_working_dir.iterdir():
                if item.name != 'backups':
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            
            # Restore from backup
            for item in backup_path.iterdir():
                dest = self.lightrag_working_dir / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                elif item.is_dir():
                    shutil.copytree(item, dest)
            
            return {
                'success': True,
                'backup_name': backup_name,
                'message': 'Index restored successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Index restore failed'
            }
    
    def repair_index(self) -> Dict:
        """Attempt to repair corrupted index.
        
        Returns:
            Dictionary with repair result
        """
        try:
            print("Attempting to repair index...", flush=True)
            
            # Check if index files exist and are valid
            issues = []
            
            # Check vector database files
            vdb_files = [
                self.lightrag_working_dir / 'vdb_entities.json',
                self.lightrag_working_dir / 'vdb_relationships.json',
                self.lightrag_working_dir / 'vdb_chunks.json'
            ]
            
            for vdb_file in vdb_files:
                if vdb_file.exists():
                    try:
                        import json
                        with open(vdb_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        print(f"✅ {vdb_file.name} is valid", flush=True)
                    except Exception as e:
                        issues.append(f"{vdb_file.name} is corrupted: {e}")
                        print(f"❌ {vdb_file.name} is corrupted: {e}", flush=True)
                else:
                    issues.append(f"{vdb_file.name} is missing")
                    print(f"⚠️ {vdb_file.name} is missing", flush=True)
            
            # Check graph file
            graph_file = self.lightrag_working_dir / 'graph_chunk_entity_relation.graphml'
            if graph_file.exists():
                try:
                    # Try to parse graph file
                    import xml.etree.ElementTree as ET
                    ET.parse(graph_file)
                    print(f"✅ {graph_file.name} is valid", flush=True)
                except Exception as e:
                    issues.append(f"{graph_file.name} is corrupted: {e}")
                    print(f"❌ {graph_file.name} is corrupted: {e}", flush=True)
            else:
                issues.append(f"{graph_file.name} is missing")
                print(f"⚠️ {graph_file.name} is missing", flush=True)
            
            if issues:
                return {
                    'success': False,
                    'issues': issues,
                    'message': f"Found {len(issues)} issues",
                    'suggestion': 'Consider restoring from backup or reindexing documents'
                }
            else:
                return {
                    'success': True,
                    'message': 'Index is healthy, no repair needed'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Index repair failed'
            }
    
    async def rebuild_index(self) -> Dict:
        """Rebuild index from document registry.
        
        Returns:
            Dictionary with rebuild result
        """
        try:
            print("Rebuilding index from document registry...", flush=True)
            
            # Load document registry
            registry_file = settings.data_dir / 'document_registry.json'
            if not registry_file.exists():
                return {
                    'success': False,
                    'error': 'Document registry not found',
                    'message': 'Cannot rebuild without document registry'
                }
            
            import json
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Create backup before rebuild
            backup_result = self.create_backup()
            
            # Remove current index files
            for item in self.lightrag_working_dir.iterdir():
                if item.name != 'backups':
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            
            # Reindex all documents
            from rag_kb.lightrag.adapter import LightRAGAdapter
            
            # Use embedding_only mode to build vector database without LLM dependency
            rag = LightRAGAdapter(embedding_only=True)
            # Reinitialize with clean state
            await rag.ensure_initialized()
            
            reindexed_count = 0
            failed_count = 0
            
            for doc_id, doc_info in registry.items():
                try:
                    content = doc_info.get('content', '')
                    if content and content.strip():
                        ingest_success = await rag.ingest([{
                            'doc_id': doc_id,
                            'content': content,
                            'metadata': doc_info.get('metadata', {})
                        }])
                        
                        if ingest_success:
                            reindexed_count += 1
                        else:
                            failed_count += 1
                except Exception as e:
                    print(f"Error reindexing {doc_id}: {e}", flush=True)
                    failed_count += 1
            
            return {
                'success': True,
                'reindexed_count': reindexed_count,
                'failed_count': failed_count,
                'total_count': len(registry),
                'backup_used': backup_result['success'],
                'message': f"Index rebuilt: {reindexed_count}/{len(registry)} successful"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Index rebuild failed'
            }
    
    def get_recovery_status(self) -> Dict:
        """Get index recovery status.
        
        Returns:
            Dictionary with recovery status
        """
        repair_result = self.repair_index()
        backups = self.list_backups()
        
        return {
            'index_health': 'healthy' if repair_result['success'] else 'corrupted',
            'repair_result': repair_result,
            'available_backups': backups,
            'backup_count': len(backups),
            'suggestion': self._get_recovery_suggestion(repair_result, backups)
        }
    
    def _get_recovery_suggestion(self, repair_result: Dict, backups: List[Dict]) -> str:
        """Get recovery suggestion based on status.
        
        Args:
            repair_result: Repair result
            backups: Available backups
            
        Returns:
            Suggestion message
        """
        if repair_result['success']:
            return "Index is healthy, no recovery needed"
        elif backups:
            return f"Index is corrupted. Consider restoring from backup (latest: {backups[0]['name']})"
        else:
            return "Index is corrupted and no backups available. Consider rebuilding index from document registry"


# Global recovery manager instance
_index_recovery_manager: Optional[IndexRecoveryManager] = None


def get_index_recovery_manager() -> IndexRecoveryManager:
    """Get or create global index recovery manager instance.
    
    Returns:
        IndexRecoveryManager instance
    """
    global _index_recovery_manager
    if _index_recovery_manager is None:
        _index_recovery_manager = IndexRecoveryManager()
    return _index_recovery_manager