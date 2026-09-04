"""Document processing progress tracking and notification system."""

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ProcessingStatus(Enum):
    """Document processing status."""
    PENDING = "pending"
    PARSING = "parsing"
    CHUNKING = "chunking"
    INDEXING = "indexing"
    GRAPH_GENERATION = "graph_generation"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DocumentProcessingTask:
    """Document processing task."""
    task_id: str
    user_id: str
    kb_name: str
    file_path: str
    file_name: str
    status: ProcessingStatus
    progress: float = 0.0
    current_stage: str = ""
    error_message: str | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'user_id': self.user_id,
            'kb_name': self.kb_name,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'status': self.status.value,
            'progress': self.progress,
            'current_stage': self.current_stage,
            'error_message': self.error_message,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'metadata': self.metadata
        }


class ProcessingTracker:
    """Tracker for document processing progress."""
    
    def __init__(self):
        """Initialize processing tracker."""
        from rag_kb.config import settings
        self.tracker_file = settings.data_dir / 'processing_tracker.json'
        self.tasks: dict[str, DocumentProcessingTask] = {}
        self.lock = threading.Lock()
        self._load_tasks()
    
    def _load_tasks(self):
        """Load tasks from file."""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_id, task_data in data.get('tasks', {}).items():
                        self.tasks[task_id] = self._dict_to_task(task_data)
            except Exception as e:
                print(f"Error loading tasks: {e}")
    
    def _save_tasks(self):
        """Save tasks to file."""
        try:
            data = {
                'tasks': {
                    task_id: task.to_dict()
                    for task_id, task in self.tasks.items()
                }
            }
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def _dict_to_task(self, data: dict[str, Any]) -> DocumentProcessingTask:
        """Convert dictionary to task object."""
        return DocumentProcessingTask(
            task_id=data['task_id'],
            user_id=data['user_id'],
            kb_name=data['kb_name'],
            file_path=data['file_path'],
            file_name=data['file_name'],
            status=ProcessingStatus(data['status']),
            progress=data.get('progress', 0.0),
            current_stage=data.get('current_stage', ''),
            error_message=data.get('error_message'),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            metadata=data.get('metadata', {})
        )
    
    def create_task(self, user_id: str, kb_name: str, file_path: str, 
                   file_name: str, metadata: dict[str, Any] = None) -> str:
        """Create a new processing task.
        
        Args:
            user_id: User ID
            kb_name: Knowledge base name
            file_path: File path
            file_name: File name
            metadata: Additional metadata
            
        Returns:
            Task ID
        """
        import uuid
        
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        task = DocumentProcessingTask(
            task_id=task_id,
            user_id=user_id,
            kb_name=kb_name,
            file_path=file_path,
            file_name=file_name,
            status=ProcessingStatus.PENDING,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.tasks[task_id] = task
            self._save_tasks()
        
        return task_id
    
    def update_task(self, task_id: str, status: ProcessingStatus = None,
                   progress: float = None, current_stage: str = None,
                   error_message: str = None) -> bool:
        """Update task status.
        
        Args:
            task_id: Task ID
            status: New status
            progress: Progress percentage (0-100)
            current_stage: Current processing stage
            error_message: Error message if failed
            
        Returns:
            True if update successful
        """
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            
            if status:
                task.status = status
                if status == ProcessingStatus.COMPLETED:
                    task.end_time = datetime.now()
                    task.progress = 100.0
                elif status == ProcessingStatus.FAILED:
                    task.end_time = datetime.now()
            
            if progress is not None:
                task.progress = progress
            
            if current_stage:
                task.current_stage = current_stage
            
            if error_message:
                task.error_message = error_message
            
            self._save_tasks()
            return True
    
    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task data or None
        """
        with self.lock:
            if task_id in self.tasks:
                return self.tasks[task_id].to_dict()
        return None
    
    def get_user_tasks(self, user_id: str) -> list[dict[str, Any]]:
        """Get all tasks for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of task data
        """
        with self.lock:
            return [
                task.to_dict()
                for task in self.tasks.values()
                if task.user_id == user_id
            ]
    
    def get_kb_tasks(self, kb_name: str) -> list[dict[str, Any]]:
        """Get all tasks for a knowledge base.
        
        Args:
            kb_name: Knowledge base name
            
        Returns:
            List of task data
        """
        with self.lock:
            return [
                task.to_dict()
                for task in self.tasks.values()
                if task.kb_name == kb_name
            ]
    
    def get_active_tasks(self) -> list[dict[str, Any]]:
        """Get all active (not completed/failed) tasks.
        
        Returns:
            List of active task data
        """
        with self.lock:
            return [
                task.to_dict()
                for task in self.tasks.values()
                if task.status not in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]
            ]
    
    def get_processing_summary(self, kb_name: str) -> dict[str, Any]:
        """Get processing summary for a knowledge base.
        
        Args:
            kb_name: Knowledge base name
            
        Returns:
            Processing summary
        """
        with self.lock:
            kb_tasks = [
                task for task in self.tasks.values()
                if task.kb_name == kb_name
            ]
            
            total = len(kb_tasks)
            completed = sum(1 for t in kb_tasks if t.status == ProcessingStatus.COMPLETED)
            failed = sum(1 for t in kb_tasks if t.status == ProcessingStatus.FAILED)
            active = sum(1 for t in kb_tasks if t.status not in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED])
            
            return {
                'kb_name': kb_name,
                'total_tasks': total,
                'completed_tasks': completed,
                'failed_tasks': failed,
                'active_tasks': active,
                'progress_percentage': (completed / total * 100) if total > 0 else 0,
                'ready_for_query': active == 0 and completed > 0
            }
    
    def cleanup_old_tasks(self, days: int = 7):
        """Clean up tasks older than specified days.
        
        Args:
            days: Number of days to keep
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.lock:
            to_remove = [
                task_id for task_id, task in self.tasks.items()
                if task.start_time < cutoff_date
                and task.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]
            ]
            
            for task_id in to_remove:
                del self.tasks[task_id]
            
            if to_remove:
                self._save_tasks()


# Global instance
processing_tracker = ProcessingTracker()