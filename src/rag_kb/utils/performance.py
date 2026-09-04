"""Performance monitoring and optimization utilities."""

import threading
import time
from collections import defaultdict
from functools import wraps
from typing import Any

import psutil


class PerformanceMonitor:
    """Monitor system and application performance metrics."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = defaultdict(list)
        self.lock = threading.Lock()
        self.enabled = True
    
    def record_metric(self, name: str, value: float, metadata: dict = None):
        """Record a performance metric.
        
        Args:
            name: Metric name
            value: Metric value
            metadata: Optional metadata
        """
        if not self.enabled:
            return
        
        with self.lock:
            self.metrics[name].append({
                'value': value,
                'timestamp': time.time(),
                'metadata': metadata or {}
            })
    
    def get_system_metrics(self) -> dict[str, Any]:
        """Get current system metrics.
        
        Returns:
            System metrics including CPU, memory, disk usage
        """
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available': psutil.virtual_memory().available,
            'memory_used': psutil.virtual_memory().used,
            'disk_usage': psutil.disk_usage('.').percent,
            'process_memory': psutil.Process().memory_info().rss,
            'process_cpu': psutil.Process().cpu_percent()
        }
    
    def get_metric_statistics(self, name: str) -> dict[str, float]:
        """Get statistics for a specific metric.
        
        Args:
            name: Metric name
            
        Returns:
            Statistics including min, max, avg, count
        """
        with self.lock:
            values = [m['value'] for m in self.metrics[name]]
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'sum': sum(values)
        }
    
    def get_all_metrics(self) -> dict[str, Any]:
        """Get all recorded metrics.
        
        Returns:
            All metrics with statistics
        """
        with self.lock:
            return {
                name: self.get_metric_statistics(name)
                for name in self.metrics.keys()
            }
    
    def clear_metrics(self):
        """Clear all recorded metrics."""
        with self.lock:
            self.metrics.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(metric_name: str):
    """Decorator to monitor function performance.
    
    Args:
        metric_name: Name for the performance metric
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                performance_monitor.record_metric(metric_name, elapsed)
                return result
            except Exception:
                elapsed = time.time() - start_time
                performance_monitor.record_metric(f"{metric_name}_error", elapsed)
                raise
        return wrapper
    return decorator


class PerformanceOptimizer:
    """Performance optimization utilities."""
    
    @staticmethod
    def optimize_chunk_size(content_length: int, max_chunk_size: int = 1000) -> int:
        """Optimize chunk size based on content length.
        
        Args:
            content_length: Length of content
            max_chunk_size: Maximum chunk size
            
        Returns:
            Optimized chunk size
        """
        if content_length < max_chunk_size:
            return content_length
        
        # Calculate optimal chunk size
        optimal_size = int(content_length ** 0.5)  # Square root for balance
        return min(optimal_size, max_chunk_size)
    
    @staticmethod
    def should_cache_result(query: str, cache_size: int = 1000) -> bool:
        """Determine if a query result should be cached.
        
        Args:
            query: Search query
            cache_size: Current cache size
            
        Returns:
            Whether to cache the result
        """
        # Cache short queries
        if len(query) < 50:
            return True
        
        # Don't cache if cache is too large
        if cache_size > 1000:
            return False
        
        return False
    
    @staticmethod
    def optimize_batch_size(total_items: int, max_batch_size: int = 32) -> int:
        """Optimize batch size for processing.
        
        Args:
            total_items: Total number of items
            max_batch_size: Maximum batch size
            
        Returns:
            Optimized batch size
        """
        if total_items <= max_batch_size:
            return total_items
        
        # Use power of 2 for better performance
        batch_size = 1
        while batch_size * 2 <= max_batch_size and batch_size * 2 <= total_items:
            batch_size *= 2
        
        return batch_size


class QueryOptimizer:
    """Optimize search queries for better performance."""
    
    @staticmethod
    def optimize_query(query: str) -> str:
        """Optimize search query for better performance.
        
        Args:
            query: Original query
            
        Returns:
            Optimized query
        """
        # Remove excessive whitespace
        optimized = ' '.join(query.split())
        
        # Remove special characters that don't add value
        optimized = re.sub(r'[^\w\s]', '', optimized)
        
        return optimized.strip()
    
    @staticmethod
    def extract_key_terms(query: str, max_terms: int = 5) -> list:
        """Extract key terms from query.
        
        Args:
            query: Search query
            max_terms: Maximum number of terms
            
        Returns:
            List of key terms
        """
        # Simple term extraction
        words = query.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'must', '的', '是', '在', '和'}
        
        key_terms = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        return key_terms[:max_terms]


class CacheManager:
    """Simple cache manager for performance optimization."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize cache manager.
        
        Args:
            max_size: Maximum cache size
        """
        self.cache = {}
        self.max_size = max_size
        self.access_count = defaultdict(int)
    
    def get(self, key: str) -> Any | None:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if key in self.cache:
            self.access_count[key] += 1
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if len(self.cache) >= self.max_size:
            self._evict()
        
        self.cache[key] = value
        self.access_count[key] = 0
    
    def _evict(self):
        """Evict least recently used item."""
        if not self.cache:
            return
        
        # Find least recently used item
        lru_key = min(self.access_count, key=self.access_count.get)
        del self.cache[lru_key]
        del self.access_count[lru_key]
    
    def clear(self):
        """Clear cache."""
        self.cache.clear()
        self.access_count.clear()
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Cache statistics
        """
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': sum(1 for count in self.access_count.values() if count > 0) / max(len(self.cache), 1)
        }