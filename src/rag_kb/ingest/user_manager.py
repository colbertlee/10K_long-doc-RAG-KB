"""User data management for multi-user support."""

from pathlib import Path
from typing import Dict, List, Optional
from rag_kb.models import Document
from rag_kb.ingest.pipeline import IngestPipeline


class UserDataManager:
    """Manager for user-specific data folders and knowledge bases."""
    
    def __init__(self, base_data_dir: Path = None):
        """Initialize user data manager.
        
        Args:
            base_data_dir: Base directory for user data (default: ./data/users)
        """
        self.base_data_dir = Path(base_data_dir or "./data/users")
        self.base_data_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline = IngestPipeline()
    
    def get_user_folder(self, user_id: str) -> Path:
        """Get user-specific data folder.
        
        Args:
            user_id: User identifier (username, email, or user ID)
            
        Returns:
            Path to user's data folder
        """
        user_folder = self.base_data_dir / user_id
        user_folder.mkdir(parents=True, exist_ok=True)
        return user_folder
    
    def create_user_kb(self, user_id: str, kb_name: str) -> Path:
        """Create a new knowledge base for a user.
        
        Args:
            user_id: User identifier
            kb_name: Knowledge base name
            
        Returns:
            Path to the knowledge base folder
        """
        user_folder = self.get_user_folder(user_id)
        kb_folder = user_folder / kb_name
        kb_folder.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (kb_folder / "raw").mkdir(exist_ok=True)
        (kb_folder / "processed").mkdir(exist_ok=True)
        (kb_folder / "index").mkdir(exist_ok=True)
        
        return kb_folder
    
    def ingest_user_folder(self, user_id: str, kb_name: str, 
                          acl: Optional[Dict] = None) -> List[Document]:
        """Ingest all documents from a user's knowledge base folder.
        
        Args:
            user_id: User identifier
            kb_name: Knowledge base name
            acl: Access control list metadata
            
        Returns:
            List of processed documents
        """
        kb_folder = self.get_user_folder(user_id) / kb_name
        raw_folder = kb_folder / "raw"
        
        if not raw_folder.exists():
            raise ValueError(f"Raw folder not found: {raw_folder}")
        
        documents = []
        for file_path in raw_folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    doc = self.pipeline.run(file_path, acl=acl)
                    documents.append(doc)
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")
        
        return documents
    
    def get_user_kbs(self, user_id: str) -> List[str]:
        """Get list of knowledge bases for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of knowledge base names
        """
        user_folder = self.get_user_folder(user_id)
        if not user_folder.exists():
            return []
        
        return [d.name for d in user_folder.iterdir() if d.is_dir()]
    
    def delete_user_kb(self, user_id: str, kb_name: str) -> bool:
        """Delete a user's knowledge base.
        
        Args:
            user_id: User identifier
            kb_name: Knowledge base name
            
        Returns:
            True if deleted successfully
        """
        kb_folder = self.get_user_folder(user_id) / kb_name
        if kb_folder.exists():
            import shutil
            shutil.rmtree(kb_folder)
            return True
        return False
    
    def get_kb_stats(self, user_id: str, kb_name: str) -> Dict:
        """Get statistics for a knowledge base.
        
        Args:
            user_id: User identifier
            kb_name: Knowledge base name
            
        Returns:
            Dictionary with statistics
        """
        kb_folder = self.get_user_folder(user_id) / kb_name
        raw_folder = kb_folder / "raw"
        
        if not raw_folder.exists():
            return {"error": "Knowledge base not found"}
        
        file_count = sum(1 for f in raw_folder.iterdir() if f.is_file())
        total_size = sum(f.stat().st_size for f in raw_folder.iterdir() if f.is_file())
        
        return {
            "user_id": user_id,
            "kb_name": kb_name,
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "folder_path": str(kb_folder)
        }