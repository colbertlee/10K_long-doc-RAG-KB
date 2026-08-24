"""Monitoring and metrics collection for knowledge base performance."""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from rag_kb.config import settings


class PerformanceMonitor:
    """Monitor and track knowledge base performance metrics."""
    
    def __init__(self):
        self.data_dir = settings.data_dir
        self.metrics_file = self.data_dir / 'performance_metrics.json'
        self.alerts_file = self.data_dir / 'performance_alerts.json'
        self.metrics_history = []
        self.alerts = []
        
    def record_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Record a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            metadata: Additional metadata
        """
        metric_entry = {
            'timestamp': datetime.now().isoformat(),
            'metric': metric_name,
            'value': value,
            'metadata': metadata or {}
        }
        
        self.metrics_history.append(metric_entry)
        
        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        self._save_metrics()
    
    def _save_metrics(self):
        """Save metrics to file."""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics_history, f, indent=2, ensure_ascii=False)
    
    def get_metrics(self, metric_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics for a specific name within time range.
        
        Args:
            metric_name: Name of the metric
            hours: Number of hours to look back
            
        Returns:
            List of metric entries
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metric for metric in self.metrics_history
            if metric['metric'] == metric_name and 
            datetime.fromisoformat(metric['timestamp']) >= cutoff_time
        ]
    
    def calculate_average(self, metric_name: str, hours: int = 24) -> Optional[float]:
        """Calculate average value for a metric.
        
        Args:
            metric_name: Name of the metric
            hours: Number of hours to look back
            
        Returns:
            Average value or None if no data
        """
        metrics = self.get_metrics(metric_name, hours)
        if not metrics:
            return None
        
        return sum(m['value'] for m in metrics) / len(metrics)
    
    def check_thresholds(self, thresholds: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Check if metrics exceed thresholds and generate alerts.
        
        Args:
            thresholds: Dictionary mapping metric names to threshold configs
                {metric_name: {'min': value, 'max': value}}
                
        Returns:
            List of alerts
        """
        new_alerts = []
        
        for metric_name, threshold_config in thresholds.items():
            current_value = self.calculate_average(metric_name, hours=1)
            
            if current_value is None:
                continue
            
            if 'min' in threshold_config and current_value < threshold_config['min']:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'metric': metric_name,
                    'type': 'below_threshold',
                    'value': current_value,
                    'threshold': threshold_config['min'],
                    'severity': 'warning'
                }
                new_alerts.append(alert)
            
            if 'max' in threshold_config and current_value > threshold_config['max']:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'metric': metric_name,
                    'type': 'above_threshold',
                    'value': current_value,
                    'threshold': threshold_config['max'],
                    'severity': 'warning'
                }
                new_alerts.append(alert)
        
        if new_alerts:
            self.alerts.extend(new_alerts)
            self._save_alerts()
        
        return new_alerts
    
    def _save_alerts(self):
        """Save alerts to file."""
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, indent=2, ensure_ascii=False)
    
    def get_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of alerts
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) >= cutoff_time
        ]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary.
        
        Returns:
            Dictionary with performance summary
        """
        summary = {
            'search_latency': self.calculate_average('search_latency', hours=24),
            'ingestion_latency': self.calculate_average('ingestion_latency', hours=24),
            'retrieval_precision': self.calculate_average('retrieval_precision', hours=24),
            'retrieval_recall': self.calculate_average('retrieval_recall', hours=24),
            'answer_relevance': self.calculate_average('answer_relevance', hours=24),
            'faithfulness': self.calculate_average('faithfulness', hours=24),
            'total_metrics': len(self.metrics_history),
            'active_alerts': len(self.get_alerts(hours=24))
        }
        
        return summary


class QualityMetrics:
    """Track RAG quality metrics for continuous improvement."""
    
    def __init__(self):
        self.data_dir = settings.data_dir
        self.quality_file = self.data_dir / 'quality_metrics.json'
        self.quality_history = []
        
    def record_quality(self, query: str, metrics: Dict[str, float], context: Optional[Dict[str, Any]] = None):
        """Record quality metrics for a query.
        
        Args:
            query: Search query
            metrics: Quality metrics (precision, recall, relevance, etc.)
            context: Additional context
        """
        quality_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'metrics': metrics,
            'context': context or {}
        }
        
        self.quality_history.append(quality_entry)
        
        # Keep only last 500 quality entries
        if len(self.quality_history) > 500:
            self.quality_history = self.quality_history[-500:]
        
        self._save_quality()
    
    def _save_quality(self):
        """Save quality metrics to file."""
        with open(self.quality_file, 'w', encoding='utf-8') as f:
            json.dump(self.quality_history, f, indent=2, ensure_ascii=False)
    
    def get_quality_trends(self, metric_name: str, days: int = 7) -> Dict[str, Any]:
        """Get quality trends for a specific metric.
        
        Args:
            metric_name: Name of the quality metric
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend information
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        
        relevant_entries = [
            entry for entry in self.quality_history
            if datetime.fromisoformat(entry['timestamp']) >= cutoff_time and
            metric_name in entry['metrics']
        ]
        
        if not relevant_entries:
            return {'trend': 'no_data', 'average': None, 'min': None, 'max': None}
        
        values = [entry['metrics'][metric_name] for entry in relevant_entries]
        
        # Calculate trend
        if len(values) >= 2:
            recent_avg = sum(values[-10:]) / min(10, len(values))
            older_avg = sum(values[:-10]) / max(1, len(values) - 10)
            
            if recent_avg > older_avg * 1.05:
                trend = 'improving'
            elif recent_avg < older_avg * 0.95:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'trend': trend,
            'average': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'count': len(values)
        }
    
    def get_overall_quality_score(self) -> Dict[str, Any]:
        """Get overall quality score across all metrics.
        
        Returns:
            Dictionary with overall quality assessment
        """
        if not self.quality_history:
            return {'overall_score': None, 'breakdown': {}}
        
        # Get latest quality metrics
        latest_metrics = self.quality_history[-1]['metrics']
        
        # Calculate weighted overall score
        weights = {
            'precision': 0.25,
            'recall': 0.25,
            'relevance': 0.25,
            'faithfulness': 0.25
        }
        
        overall_score = 0.0
        breakdown = {}
        
        for metric, weight in weights.items():
            if metric in latest_metrics:
                breakdown[metric] = latest_metrics[metric]
                overall_score += latest_metrics[metric] * weight
        
        return {
            'overall_score': overall_score,
            'breakdown': breakdown,
            'timestamp': self.quality_history[-1]['timestamp']
        }