"""Index performance monitoring and history tracking."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from rag_kb.config import settings


class IndexPerformanceMonitor:
    """Monitor and track index performance metrics."""
    
    def __init__(self):
        """Initialize index performance monitor."""
        self.data_dir = settings.data_dir
        self.history_file = self.data_dir / 'index_history.json'
        self.performance_file = self.data_dir / 'index_performance.json'
        
        self.history = self._load_history()
        self.performance_metrics = self._load_performance()
    
    def _load_history(self) -> List[Dict]:
        """Load index history from file.
        
        Returns:
            List of index history records
        """
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading index history: {e}")
                return []
        return []
    
    def _save_history(self):
        """Save index history to file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving index history: {e}")
    
    def _load_performance(self) -> Dict:
        """Load performance metrics from file.
        
        Returns:
            Dictionary of performance metrics
        """
        if self.performance_file.exists():
            try:
                with open(self.performance_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading performance metrics: {e}")
                return {}
        return {}
    
    def _save_performance(self):
        """Save performance metrics to file."""
        try:
            self.performance_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.performance_file, 'w', encoding='utf-8') as f:
                json.dump(self.performance_metrics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving performance metrics: {e}")
    
    def record_index_operation(self, operation_type: str, doc_id: str, success: bool, duration: float, metadata: Dict = None):
        """Record an index operation.
        
        Args:
            operation_type: Type of operation (e.g., 'index', 'delete', 'update')
            doc_id: Document ID
            success: Whether operation succeeded
            duration: Operation duration in seconds
            metadata: Additional metadata
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,
            'doc_id': doc_id,
            'success': success,
            'duration': duration,
            'metadata': metadata or {}
        }
        
        self.history.append(record)
        
        # Keep only last 1000 records
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        self._save_history()
        
        # Update performance metrics
        self._update_performance_metrics(operation_type, success, duration)
    
    def _update_performance_metrics(self, operation_type: str, success: bool, duration: float):
        """Update performance metrics.
        
        Args:
            operation_type: Type of operation
            success: Whether operation succeeded
            duration: Operation duration
        """
        if operation_type not in self.performance_metrics:
            self.performance_metrics[operation_type] = {
                'total_count': 0,
                'success_count': 0,
                'failure_count': 0,
                'total_duration': 0,
                'avg_duration': 0,
                'min_duration': float('inf'),
                'max_duration': 0
            }
        
        metrics = self.performance_metrics[operation_type]
        metrics['total_count'] += 1
        
        if success:
            metrics['success_count'] += 1
        else:
            metrics['failure_count'] += 1
        
        metrics['total_duration'] += duration
        metrics['avg_duration'] = metrics['total_duration'] / metrics['total_count']
        metrics['min_duration'] = min(metrics['min_duration'], duration)
        metrics['max_duration'] = max(metrics['max_duration'], duration)
        
        self._save_performance()
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary.
        
        Returns:
            Dictionary with performance summary
        """
        return {
            'total_operations': len(self.history),
            'performance_metrics': self.performance_metrics,
            'recent_history': self.history[-10:]
        }
    
    def get_index_history(self, limit: int = 50) -> List[Dict]:
        """Get index history.
        
        Args:
            limit: Number of recent records to return
            
        Returns:
            List of recent index history records
        """
        return self.history[-limit:]
    
    def get_slow_operations(self, threshold: float = 5.0) -> List[Dict]:
        """Get slow operations.
        
        Args:
            threshold: Threshold in seconds
            
        Returns:
            List of slow operations
        """
        slow_ops = [op for op in self.history if op['duration'] > threshold]
        slow_ops.sort(key=lambda x: x['duration'], reverse=True)
        return slow_ops[:100]
    
    def get_operation_stats(self, operation_type: str) -> Dict:
        """Get statistics for a specific operation type.
        
        Args:
            operation_type: Type of operation
            
        Returns:
            Dictionary with operation statistics
        """
        if operation_type not in self.performance_metrics:
            return {
                'operation_type': operation_type,
                'total_count': 0,
                'success_count': 0,
                'failure_count': 0,
                'avg_duration': 0
            }
        
        return self.performance_metrics[operation_type]


# Global performance monitor instance
_index_performance_monitor: Optional[IndexPerformanceMonitor] = None


def get_index_performance_monitor() -> IndexPerformanceMonitor:
    """Get or create global index performance monitor instance.
    
    Returns:
        IndexPerformanceMonitor instance
    """
    global _index_performance_monitor
    if _index_performance_monitor is None:
        _index_performance_monitor = IndexPerformanceMonitor()
    return _index_performance_monitor