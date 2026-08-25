"""Performance tuning configuration for RAG system."""

import sys
from pathlib import Path
from typing import Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PerformanceSettings(BaseSettings):
    """Performance tuning settings for RAG system."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        env_prefix='RAGKB_PERF_',
    )
    
    # RRF (Reciprocal Rank Fusion) parameters
    rrf_k: int = Field(default=60, description="RRF constant for fusion (higher = more weight to lower ranks)")
    rrf_weight_bm25: float = Field(default=0.4, description="Weight for BM25 results in RRF fusion")
    rrf_weight_vector: float = Field(default=0.6, description="Weight for vector results in RRF fusion")
    
    # BM25 parameters
    bm25_k1: float = Field(default=1.5, description="BM25 term frequency saturation parameter")
    bm25_b: float = Field(default=0.75, description="BM25 length normalization parameter")
    
    # Reranking parameters
    rerank_enabled: bool = Field(default=True, description="Enable reranking")
    rerank_top_k: int = Field(default=20, description="Number of results to rerank")
    rerank_model: str = Field(default="BAAI/bge-reranker-base", description="Reranker model name")
    rerank_device: str = Field(default="cuda", description="Reranker device (cuda/cpu)")
    
    # Search parameters
    search_top_k: int = Field(default=10, description="Number of results to return")
    search_mode: str = Field(default="hybrid", description="Search mode (bm25/vector/hybrid)")
    
    # Performance optimization
    enable_cache: bool = Field(default=True, description="Enable result caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    parallel_search: bool = Field(default=True, description="Enable parallel search execution")
    
    # Quality thresholds
    quality_threshold_faithfulness: float = Field(default=0.8, description="Faithfulness quality threshold")
    quality_threshold_relevancy: float = Field(default=0.8, description="Answer relevancy quality threshold")
    quality_threshold_precision: float = Field(default=0.7, description="Context precision quality threshold")


# Global performance settings instance
performance_settings = PerformanceSettings()


class PerformanceTuner:
    """Performance tuner for RAG system optimization."""
    
    def __init__(self):
        self.settings = performance_settings
    
    def get_rrf_config(self) -> Dict[str, Any]:
        """Get RRF fusion configuration."""
        return {
            'k': self.settings.rrf_k,
            'weight_bm25': self.settings.rrf_weight_bm25,
            'weight_vector': self.settings.rrf_weight_vector
        }
    
    def get_bm25_config(self) -> Dict[str, Any]:
        """Get BM25 search configuration."""
        return {
            'k1': self.settings.bm25_k1,
            'b': self.settings.bm25_b
        }
    
    def get_rerank_config(self) -> Dict[str, Any]:
        """Get reranking configuration."""
        return {
            'enabled': self.settings.rerank_enabled,
            'top_k': self.settings.rerank_top_k,
            'model': self.settings.rerank_model,
            'device': self.settings.rerank_device
        }
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search configuration."""
        return {
            'top_k': self.settings.search_top_k,
            'mode': self.settings.search_mode,
            'enable_cache': self.settings.enable_cache,
            'parallel': self.settings.parallel_search
        }
    
    def get_quality_thresholds(self) -> Dict[str, float]:
        """Get quality monitoring thresholds."""
        return {
            'faithfulness': self.settings.quality_threshold_faithfulness,
            'answer_relevancy': self.settings.quality_threshold_relevancy,
            'context_precision': self.settings.quality_threshold_precision
        }
    
    def optimize_for_speed(self) -> Dict[str, Any]:
        """Get performance-optimized configuration (speed over accuracy)."""
        return {
            'rrf': {
                'k': 40,  # Lower k for faster ranking
                'weight_bm25': 0.6,  # More weight to faster BM25
                'weight_vector': 0.4
            },
            'rerank': {
                'enabled': False,  # Disable reranking for speed
                'top_k': 10
            },
            'search': {
                'top_k': 5,  # Fewer results
                'mode': 'bm25'  # Use faster BM25 only
            }
        }
    
    def optimize_for_accuracy(self) -> Dict[str, Any]:
        """Get accuracy-optimized configuration (accuracy over speed)."""
        return {
            'rrf': {
                'k': 100,  # Higher k for better ranking
                'weight_bm25': 0.3,  # More weight to vector search
                'weight_vector': 0.7
            },
            'rerank': {
                'enabled': True,
                'top_k': 30,  # Rerank more results
                'model': 'BAAI/bge-reranker-large'  # Use larger model
            },
            'search': {
                'top_k': 20,  # More results
                'mode': 'hybrid'
            }
        }
    
    def optimize_for_balance(self) -> Dict[str, Any]:
        """Get balanced configuration (speed and accuracy)."""
        return {
            'rrf': {
                'k': 60,  # Balanced k
                'weight_bm25': 0.4,
                'weight_vector': 0.6
            },
            'rerank': {
                'enabled': True,
                'top_k': 15,  # Moderate reranking
                'model': 'BAAI/bge-reranker-base'
            },
            'search': {
                'top_k': 10,
                'mode': 'hybrid'
            }
        }
    
    def update_rrf_k(self, k: int):
        """Update RRF k parameter."""
        self.settings.rrf_k = k
    
    def update_rrf_weights(self, bm25_weight: float, vector_weight: float):
        """Update RRF fusion weights."""
        total = bm25_weight + vector_weight
        if total > 0:
            self.settings.rrf_weight_bm25 = bm25_weight / total
            self.settings.rrf_weight_vector = vector_weight / total
    
    def update_rerank_config(self, enabled: bool, top_k: int = None):
        """Update reranking configuration."""
        self.settings.rerank_enabled = enabled
        if top_k is not None:
            self.settings.rerank_top_k = top_k
    
    def save_config(self, config_path: Path = None):
        """Save current configuration to file."""
        if config_path is None:
            config_path = Path('configs/performance_tuning.yaml')
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = {
            'rrf': self.get_rrf_config(),
            'bm25': self.get_bm25_config(),
            'rerank': self.get_rerank_config(),
            'search': self.get_search_config(),
            'quality': self.get_quality_thresholds()
        }
        
        import yaml
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
        
        print(f"Performance configuration saved to {config_path}", flush=True)
    
    def load_config(self, config_path: Path = None):
        """Load configuration from file."""
        if config_path is None:
            config_path = Path('configs/performance_tuning.yaml')
        
        if not config_path.exists():
            print(f"Configuration file not found: {config_path}", flush=True)
            return
        
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        # Update settings from loaded config
        if 'rrf' in config_dict:
            self.settings.rrf_k = config_dict['rrf'].get('k', self.settings.rrf_k)
            self.settings.rrf_weight_bm25 = config_dict['rrf'].get('weight_bm25', self.settings.rrf_weight_bm25)
            self.settings.rrf_weight_vector = config_dict['rrf'].get('weight_vector', self.settings.rrf_weight_vector)
        
        if 'rerank' in config_dict:
            self.settings.rerank_enabled = config_dict['rerank'].get('enabled', self.settings.rerank_enabled)
            self.settings.rerank_top_k = config_dict['rerank'].get('top_k', self.settings.rerank_top_k)
        
        if 'search' in config_dict:
            self.settings.search_top_k = config_dict['search'].get('top_k', self.settings.search_top_k)
            self.settings.search_mode = config_dict['search'].get('mode', self.settings.search_mode)
        
        print(f"Performance configuration loaded from {config_path}", flush=True)


# Global performance tuner instance
performance_tuner = PerformanceTuner()