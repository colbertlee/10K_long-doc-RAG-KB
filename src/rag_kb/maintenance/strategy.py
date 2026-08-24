"""Strategy management for closed-loop iteration and optimization."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from rag_kb.config import settings


class StrategyManager:
    """Manage retrieval and chunking strategies with closed-loop iteration."""
    
    def __init__(self):
        self.data_dir = settings.data_dir
        self.strategy_file = self.data_dir / 'strategy_config.json'
        self.performance_history_file = self.data_dir / 'strategy_performance.json'
        
        # Default strategies
        self.default_strategies = {
            'chunking': {
                'structured': {
                    'chunk_size': 512,
                    'chunk_overlap': 50,
                    'preserve_structure': True
                },
                'parent_child': {
                    'parent_size': 1024,
                    'child_size': 256,
                    'child_overlap': 50
                }
            },
            'retrieval': {
                'bm25': {
                    'k1': 1.5,
                    'b': 0.75,
                    'top_k': 10
                },
                'hybrid': {
                    'bm25_weight': 0.3,
                    'lightrag_weight': 0.7,
                    'rrf_k': 60
                }
            },
            'reranking': {
                'enabled': True,
                'model': 'cross-encoder',
                'top_k': 5
            }
        }
        
        self.current_strategies = self._load_strategies()
        self.performance_history = self._load_performance_history()
    
    def _load_strategies(self) -> Dict[str, Any]:
        """Load current strategies from file."""
        if self.strategy_file.exists():
            with open(self.strategy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.default_strategies.copy()
    
    def _save_strategies(self):
        """Save current strategies to file."""
        with open(self.strategy_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_strategies, f, indent=2, ensure_ascii=False)
    
    def _load_performance_history(self) -> List[Dict[str, Any]]:
        """Load performance history from file."""
        if self.performance_history_file.exists():
            with open(self.performance_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_performance_history(self):
        """Save performance history to file."""
        with open(self.performance_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.performance_history, f, indent=2, ensure_ascii=False)
    
    def get_current_strategy(self, strategy_type: str) -> Dict[str, Any]:
        """Get current strategy for a specific type.
        
        Args:
            strategy_type: Type of strategy (chunking, retrieval, reranking)
            
        Returns:
            Current strategy configuration
        """
        return self.current_strategies.get(strategy_type, {})
    
    def update_strategy(self, strategy_type: str, strategy_name: str, config: Dict[str, Any]):
        """Update a specific strategy.
        
        Args:
            strategy_type: Type of strategy
            strategy_name: Name of the strategy
            config: New configuration
        """
        if strategy_type not in self.current_strategies:
            self.current_strategies[strategy_type] = {}
        
        self.current_strategies[strategy_type][strategy_name] = config
        self._save_strategies()
    
    def record_performance(self, strategy_type: str, strategy_name: str, 
                         metrics: Dict[str, float], context: Optional[Dict[str, Any]] = None):
        """Record performance metrics for a strategy.
        
        Args:
            strategy_type: Type of strategy
            strategy_name: Name of the strategy
            metrics: Performance metrics
            context: Additional context
        """
        performance_entry = {
            'timestamp': datetime.now().isoformat(),
            'strategy_type': strategy_type,
            'strategy_name': strategy_name,
            'metrics': metrics,
            'context': context or {}
        }
        
        self.performance_history.append(performance_entry)
        
        # Keep only last 1000 performance entries
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
        
        self._save_performance_history()
    
    def analyze_performance_trend(self, strategy_type: str, strategy_name: str, 
                                  metric: str, days: int = 7) -> Dict[str, Any]:
        """Analyze performance trend for a specific strategy.
        
        Args:
            strategy_type: Type of strategy
            strategy_name: Name of the strategy
            metric: Metric to analyze
            days: Number of days to analyze
            
        Returns:
            Trend analysis results
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        relevant_entries = [
            entry for entry in self.performance_history
            if (entry['strategy_type'] == strategy_type and 
                entry['strategy_name'] == strategy_name and
                metric in entry['metrics'] and
                datetime.fromisoformat(entry['timestamp']) >= cutoff_date)
        ]
        
        if not relevant_entries:
            return {'trend': 'no_data', 'average': None, 'count': 0}
        
        values = [entry['metrics'][metric] for entry in relevant_entries]
        
        # Calculate trend
        if len(values) >= 2:
            recent_avg = sum(values[-5:]) / min(5, len(values))
            older_avg = sum(values[:-5]) / max(1, len(values) - 5)
            
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
    
    def suggest_strategy_adjustment(self, strategy_type: str, metric: str, 
                                   current_value: float, target_value: float) -> Dict[str, Any]:
        """Suggest strategy adjustments based on performance.
        
        Args:
            strategy_type: Type of strategy
            metric: Performance metric
            current_value: Current metric value
            target_value: Target metric value
            
        Returns:
            Suggested adjustments
        """
        suggestions = []
        
        if strategy_type == 'chunking':
            if current_value < target_value * 0.8:
                # Performance is significantly below target
                suggestions.append({
                    'type': 'increase_chunk_size',
                    'reason': 'Current chunk size may be too small, causing context fragmentation',
                    'action': 'Increase chunk_size by 20-30%'
                })
                suggestions.append({
                    'type': 'increase_overlap',
                    'reason': 'Low overlap may miss important context',
                    'action': 'Increase chunk_overlap to 100-150 tokens'
                })
            elif current_value > target_value * 1.2:
                # Performance is above target but may be inefficient
                suggestions.append({
                    'type': 'optimize_chunk_size',
                    'reason': 'Current chunk size may be larger than necessary',
                    'action': 'Consider reducing chunk_size to improve efficiency'
                })
        
        elif strategy_type == 'retrieval':
            if current_value < target_value * 0.8:
                suggestions.append({
                    'type': 'adjust_bm25_params',
                    'reason': 'BM25 parameters may need tuning',
                    'action': 'Try adjusting k1 (1.2-2.0) and b (0.6-0.9)'
                })
                suggestions.append({
                    'type': 'adjust_hybrid_weights',
                    'reason': 'Hybrid search weights may need rebalancing',
                    'action': 'Try different BM25/LightRAG weight combinations'
                })
                suggestions.append({
                    'type': 'enable_reranking',
                    'reason': 'Reranking may improve precision',
                    'action': 'Enable cross-encoder reranking'
                })
        
        elif strategy_type == 'reranking':
            if current_value < target_value * 0.8:
                suggestions.append({
                    'type': 'change_rerank_model',
                    'reason': 'Current reranking model may not be optimal',
                    'action': 'Try different cross-encoder models'
                })
                suggestions.append({
                    'type': 'adjust_top_k',
                    'reason': 'Top-k value may need adjustment',
                    'action': 'Try different top_k values (3-10)'
                })
        
        return {
            'current_value': current_value,
            'target_value': target_value,
            'gap': target_value - current_value,
            'gap_percentage': ((target_value - current_value) / target_value) * 100 if target_value > 0 else 0,
            'suggestions': suggestions
        }
    
    def auto_optimize_strategy(self, strategy_type: str, target_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Automatically optimize strategy based on target metrics.
        
        Args:
            strategy_type: Type of strategy to optimize
            target_metrics: Target performance metrics
            
        Returns:
            Optimization results
        """
        current_strategy = self.get_current_strategy(strategy_type)
        optimization_results = {
            'strategy_type': strategy_type,
            'original_config': current_strategy.copy(),
            'optimizations_applied': [],
            'new_config': current_strategy.copy()
        }
        
        for metric, target_value in target_metrics.items():
            # Get current performance
            trend_analysis = self.analyze_performance_trend(
                strategy_type, 'current', metric, days=7
            )
            
            if trend_analysis['trend'] == 'declining' or trend_analysis['average'] < target_value * 0.8:
                # Performance is declining or below target
                suggestions = self.suggest_strategy_adjustment(
                    strategy_type, metric, 
                    trend_analysis['average'] or 0, 
                    target_value
                )
                
                # Apply automatic optimizations
                for suggestion in suggestions['suggestions']:
                    if suggestion['type'] == 'increase_chunk_size':
                        if 'chunk_size' in optimization_results['new_config']:
                            old_size = optimization_results['new_config']['chunk_size']
                            new_size = int(old_size * 1.25)
                            optimization_results['new_config']['chunk_size'] = new_size
                            optimization_results['optimizations_applied'].append({
                                'type': 'increase_chunk_size',
                                'old_value': old_size,
                                'new_value': new_size,
                                'reason': suggestion['reason']
                            })
                    
                    elif suggestion['type'] == 'increase_overlap':
                        if 'chunk_overlap' in optimization_results['new_config']:
                            old_overlap = optimization_results['new_config']['chunk_overlap']
                            new_overlap = int(old_overlap * 1.5)
                            optimization_results['new_config']['chunk_overlap'] = new_overlap
                            optimization_results['optimizations_applied'].append({
                                'type': 'increase_overlap',
                                'old_value': old_overlap,
                                'new_value': new_overlap,
                                'reason': suggestion['reason']
                            })
        
        # Save optimized strategy
        if optimization_results['optimizations_applied']:
            for strategy_name, config in optimization_results['new_config'].items():
                self.update_strategy(strategy_type, strategy_name, config)
        
        return optimization_results
    
    def get_strategy_comparison(self, strategy_type: str) -> Dict[str, Any]:
        """Compare performance of different strategies.
        
        Args:
            strategy_type: Type of strategy to compare
            
        Returns:
            Comparison results
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=30)
        
        strategy_performance = {}
        
        for entry in self.performance_history:
            if (entry['strategy_type'] == strategy_type and 
                datetime.fromisoformat(entry['timestamp']) >= cutoff_date):
                
                strategy_name = entry['strategy_name']
                if strategy_name not in strategy_performance:
                    strategy_performance[strategy_name] = []
                
                strategy_performance[strategy_name].append(entry['metrics'])
        
        # Calculate averages for each strategy
        comparison = {}
        for strategy_name, metrics_list in strategy_performance.items():
            if not metrics_list:
                continue
            
            avg_metrics = {}
            for metric in metrics_list[0].keys():
                values = [m[metric] for m in metrics_list if metric in m]
                if values:
                    avg_metrics[metric] = sum(values) / len(values)
            
            comparison[strategy_name] = {
                'average_metrics': avg_metrics,
                'sample_count': len(metrics_list)
            }
        
        return comparison