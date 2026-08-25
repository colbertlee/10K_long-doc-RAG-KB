"""Utility modules for RAG KB system."""

# Try to import async context and deduplication (core utilities)
from rag_kb.utils.async_context import get_async_context, AsyncContextManager
from rag_kb.utils.deduplication import get_deduplicator, DocumentDeduplicator

# Try to import performance monitoring utilities (optional, requires psutil)
try:
    from .performance import PerformanceMonitor, PerformanceOptimizer, QueryOptimizer, CacheManager
    _performance_available = True
except ImportError:
    _performance_available = False
    PerformanceMonitor = None
    PerformanceOptimizer = None
    QueryOptimizer = None
    CacheManager = None

__all__ = [
    'get_async_context',
    'AsyncContextManager', 
    'get_deduplicator',
    'DocumentDeduplicator'
]

# Add performance utilities to __all__ if available
if _performance_available:
    __all__.extend([
        'PerformanceMonitor',
        'PerformanceOptimizer', 
        'QueryOptimizer',
        'CacheManager'
    ])