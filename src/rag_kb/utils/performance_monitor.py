"""Performance monitoring system for RAG KB."""

import time
import psutil
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from pathlib import Path

from rag_kb.config import settings


class PerformanceMonitor:
    """Monitor system and application performance."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = defaultdict(list)
        self.operation_times = defaultdict(list)
        self.system_metrics = []
        self.start_time = time.time
        self.alerts = []
        self.alert_thresholds = {
            'slow_operation': 5.0,  # seconds
            'high_cpu': 80.0,  # percent
            'high_memory': 85.0,  # percent
            'high_disk': 90.0  # percent
        }
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """Set alert threshold for a metric.
        
        Args:
            metric: Metric name (slow_operation, high_cpu, high_memory, high_disk)
            threshold: Threshold value
        """
        self.alert_thresholds[metric] = threshold
        print(f"Alert threshold set: {metric} = {threshold}")
    
    def record_operation(self, operation_name: str, duration: float, metadata: Dict = None):
        """Record an operation's performance.
        
        Args:
            operation_name: Name of the operation
            duration: Duration in seconds
            metadata: Additional metadata about the operation
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation_name,
            'duration': duration,
            'metadata': metadata or {}
        }
        self.operation_times[operation_name].append(record)
        
        # Check for slow operation alert
        if duration > self.alert_thresholds['slow_operation']:
            self._create_alert('slow_operation', f"Slow operation: {operation_name} took {duration:.2f}s", record)
        
        # Keep only last 1000 records per operation
        if len(self.operation_times[operation_name]) > 1000:
            self.operation_times[operation_name] = self.operation_times[operation_name][-1000:]
    
    def _create_alert(self, alert_type: str, message: str, data: Dict = None):
        """Create an alert.
        
        Args:
            alert_type: Type of alert
            message: Alert message
            data: Additional data
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'message': message,
            'data': data or {}
        }
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        print(f"⚠️ ALERT: {message}", flush=True)
    
    def record_system_metrics(self):
        """Record current system metrics."""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used': psutil.virtual_memory().used / 1024**3,  # GB
                'memory_total': psutil.virtual_memory().total / 1024**3,  # GB
                'disk_usage': psutil.disk_usage('/').percent if Path('/').exists() else 0,
                'process_memory': psutil.Process().memory_info().rss / 1024**3  # GB
            }
            self.system_metrics.append(metrics)
            
            # Check for resource alerts
            if metrics['cpu_percent'] > self.alert_thresholds['high_cpu']:
                self._create_alert('high_cpu', f"High CPU usage: {metrics['cpu_percent']:.1f}%", metrics)
            
            if metrics['memory_percent'] > self.alert_thresholds['high_memory']:
                self._create_alert('high_memory', f"High memory usage: {metrics['memory_percent']:.1f}%", metrics)
            
            if metrics['disk_usage'] > self.alert_thresholds['high_disk']:
                self._create_alert('high_disk', f"High disk usage: {metrics['disk_usage']:.1f}%", metrics)
            
            # Keep only last 1000 system metrics
            if len(self.system_metrics) > 1000:
                self.system_metrics = self.system_metrics[-1000:]
        except Exception as e:
            print(f"Error recording system metrics: {e}")
    
    def get_operation_stats(self, operation_name: str) -> Dict:
        """Get statistics for a specific operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Dictionary with operation statistics
        """
        if operation_name not in self.operation_times:
            return {
                'operation': operation_name,
                'count': 0,
                'avg_duration': 0,
                'min_duration': 0,
                'max_duration': 0,
                'total_duration': 0
            }
        
        records = self.operation_times[operation_name]
        durations = [r['duration'] for r in records]
        
        return {
            'operation': operation_name,
            'count': len(durations),
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'total_duration': sum(durations),
            'last_duration': durations[-1] if durations else 0
        }
    
    def get_all_operation_stats(self) -> Dict:
        """Get statistics for all operations.
        
        Returns:
            Dictionary with all operation statistics
        """
        stats = {}
        for operation_name in self.operation_times:
            stats[operation_name] = self.get_operation_stats(operation_name)
        return stats
    
    def get_system_stats(self) -> Dict:
        """Get current system statistics.
        
        Returns:
            Dictionary with system statistics
        """
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_gb': psutil.virtual_memory().used / 1024**3,
                'memory_total_gb': psutil.virtual_memory().total / 1024**3,
                'disk_usage_percent': psutil.disk_usage('/').percent if Path('/').exists() else 0,
                'process_memory_gb': psutil.Process().memory_info().rss / 1024**3,
                'uptime_seconds': time.time() - self.start_time
            }
        except Exception as e:
            return {
                'error': str(e),
                'cpu_percent': 0,
                'memory_percent': 0,
                'memory_used_gb': 0,
                'memory_total_gb': 0,
                'disk_usage_percent': 0,
                'process_memory_gb': 0,
                'uptime_seconds': 0
            }
    
    def get_slow_operations(self, threshold: float = None) -> List[Dict]:
        """Get operations that exceed threshold.
        
        Args:
            threshold: Threshold in seconds (uses configured threshold if None)
            
        Returns:
            List of slow operation records
        """
        if threshold is None:
            threshold = self.alert_thresholds['slow_operation']
        
        slow_ops = []
        for operation_name, records in self.operation_times.items():
            for record in records:
                if record['duration'] > threshold:
                    slow_ops.append({
                        'operation': operation_name,
                        'duration': record['duration'],
                        'timestamp': record['timestamp'],
                        'metadata': record['metadata']
                    })
        
        # Sort by duration (descending)
        slow_ops.sort(key=lambda x: x['duration'], reverse=True)
        return slow_ops[:100]  # Return top 100 slow operations
    
    def get_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts.
        
        Args:
            limit: Number of recent alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.alerts[-limit:]
    
    def get_performance_summary(self) -> Dict:
        """Get overall performance summary.
        
        Returns:
            Dictionary with performance summary
        """
        stats = self.get_all_operation_stats()
        system_stats = self.get_system_stats()
        
        total_operations = sum(s['count'] for s in stats.values())
        total_duration = sum(s['total_duration'] for s in stats.values())
        
        slow_ops = self.get_slow_operations()
        
        return {
            'uptime_seconds': time.time() - self.start_time,
            'total_operations': total_operations,
            'total_duration': total_duration,
            'avg_operation_time': total_duration / total_operations if total_operations > 0 else 0,
            'slow_operations_count': len(slow_ops),
            'recent_alerts_count': len(self.alerts),
            'system_stats': system_stats,
            'operation_stats': stats,
            'alert_thresholds': self.alert_thresholds
        }


class OperationTimer:
    """Context manager for timing operations."""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str, metadata: Dict = None):
        """Initialize operation timer.
        
        Args:
            monitor: Performance monitor instance
            operation_name: Name of the operation
            metadata: Additional metadata
        """
        self.monitor = monitor
        self.operation_name = operation_name
        self.metadata = metadata or {}
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record."""
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.monitor.record_operation(self.operation_name, duration, self.metadata)
        return False


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor instance.
    
    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def time_operation(operation_name: str, metadata: Dict = None):
    """Decorator for timing operations.
    
    Args:
        operation_name: Name of the operation
        metadata: Additional metadata
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            with OperationTimer(monitor, operation_name, metadata):
                return func(*args, **kwargs)
        return wrapper
    return decorator


async def record_periodic_metrics(interval: int = 60):
    """Record system metrics periodically.
    
    Args:
        interval: Interval in seconds
    """
    monitor = get_performance_monitor()
    while True:
        monitor.record_system_metrics()
        await asyncio.sleep(interval)