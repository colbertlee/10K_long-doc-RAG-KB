"""Utility modules for RAG KB system."""

# Try to import async context and deduplication (core utilities)
from rag_kb.utils.async_context import AsyncContextManager, get_async_context
from rag_kb.utils.deduplication import DocumentDeduplicator, get_deduplicator

# Try to import index scheduler (optional)
try:
    from rag_kb.utils.index_scheduler import IndexScheduler
    _index_scheduler_available = True
except ImportError:
    _index_scheduler_available = False
    IndexScheduler = None

# Try to import performance monitoring utilities (optional, requires psutil)
try:
    from .performance import (
        CacheManager,
        PerformanceMonitor,
        PerformanceOptimizer,
        QueryOptimizer,
    )
    _performance_available = True
except ImportError:
    _performance_available = False
    PerformanceMonitor = None
    PerformanceOptimizer = None
    QueryOptimizer = None
    CacheManager = None

__all__ = [
    'AsyncContextManager',
    'DocumentDeduplicator',
    'get_async_context',
    'get_deduplicator'
]

# Add index scheduler to __all__ if available
if _index_scheduler_available:
    __all__.extend(['IndexScheduler'])

# Add performance utilities to __all__ if available
if _performance_available:
    __all__.extend([
        'CacheManager',
        'PerformanceMonitor',
        'PerformanceOptimizer',
        'QueryOptimizer'
    ])