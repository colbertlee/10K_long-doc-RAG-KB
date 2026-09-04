"""Logging and monitoring utilities for RAG KB."""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil


class RAGKBLogger:
    """Custom logger for RAG KB with structured logging and performance monitoring."""
    
    def __init__(self, name: str = "rag-kb", log_level: str = "INFO", log_dir: Path | None = None):
        """Initialize RAG KB logger.
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files (defaults to ./logs)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create log directory
        self.log_dir = log_dir or Path("./logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()
        self._setup_performance_handler()
        
        # Performance tracking
        self.performance_data = []
        self.start_time = time.time()
    
    def _setup_console_handler(self):
        """Setup console logging handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Simple format for console
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup file logging handler."""
        log_file = self.log_dir / f"rag_kb_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Detailed format for file
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_performance_handler(self):
        """Setup performance monitoring handler."""
        perf_file = self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.performance_file = perf_file
    
    def log_performance(self, operation: str, duration: float, metadata: dict[str, Any] = None):
        """Log performance metrics.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            metadata: Additional performance metadata
        """
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration_seconds': duration,
            'metadata': metadata or {}
        }
        
        self.performance_data.append(perf_data)
        
        # Write to performance log
        with open(self.performance_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(perf_data) + '\n')
        
        # Log slow operations
        if duration > 5.0:  # Log operations taking > 5 seconds
            self.logger.warning(f"Slow operation: {operation} took {duration:.2f}s")
    
    def get_system_metrics(self) -> dict[str, Any]:
        """Get current system metrics.
        
        Returns:
            Dictionary with system performance metrics
        """
        process = psutil.Process()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_mb': psutil.virtual_memory().used / (1024 * 1024),
            'memory_available_mb': psutil.virtual_memory().available / (1024 * 1024),
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'process_memory_mb': process.memory_info().rss / (1024 * 1024),
            'process_cpu_percent': process.cpu_percent(),
            'uptime_seconds': time.time() - self.start_time
        }
    
    def log_system_metrics(self):
        """Log current system metrics."""
        metrics = self.get_system_metrics()
        self.logger.info(f"System metrics: CPU={metrics['cpu_percent']}%, "
                        f"Memory={metrics['memory_percent']}%, "
                        f"Process Memory={metrics['process_memory_mb']:.1f}MB")
    
    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary statistics.
        
        Returns:
            Dictionary with performance summary
        """
        if not self.performance_data:
            return {'message': 'No performance data available'}
        
        # Group by operation
        operations = {}
        for perf in self.performance_data:
            op = perf['operation']
            if op not in operations:
                operations[op] = []
            operations[op].append(perf['duration_seconds'])
        
        # Calculate statistics
        summary = {}
        for op, durations in operations.items():
            summary[op] = {
                'count': len(durations),
                'total_time': sum(durations),
                'avg_time': sum(durations) / len(durations),
                'min_time': min(durations),
                'max_time': max(durations)
            }
        
        return {
            'total_operations': len(self.performance_data),
            'operations_summary': summary,
            'uptime_seconds': time.time() - self.start_time
        }
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)


class PerformanceMonitor:
    """Context manager for monitoring operation performance."""
    
    def __init__(self, logger: RAGKBLogger, operation: str, metadata: dict[str, Any] = None):
        """Initialize performance monitor.
        
        Args:
            logger: RAG KB logger instance
            operation: Operation name
            metadata: Additional metadata
        """
        self.logger = logger
        self.operation = operation
        self.metadata = metadata or {}
        self.start_time = None
    
    def __enter__(self):
        """Enter context manager."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        duration = time.time() - self.start_time
        
        # Add exception info if occurred
        if exc_type is not None:
            self.metadata['exception'] = str(exc_type)
            self.metadata['exception_type'] = exc_type.__name__
        
        self.logger.log_performance(self.operation, duration, self.metadata)
        return False  # Don't suppress exceptions


def setup_logging(log_level: str = "INFO", log_dir: Path | None = None) -> RAGKBLogger:
    """Setup logging for RAG KB application.
    
    Args:
        log_level: Logging level
        log_dir: Directory for log files
        
    Returns:
        Configured RAG KB logger
    """
    logger = RAGKBLogger(log_level=log_level, log_dir=log_dir)
    return logger


# Global logger instance
_global_logger = None

def get_logger() -> RAGKBLogger:
    """Get global logger instance.
    
    Returns:
        Global RAG KB logger
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging()
    return _global_logger