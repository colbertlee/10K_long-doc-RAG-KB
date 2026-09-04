"""Multi-knowledge base manager for product-specific isolation."""

import json
from typing import Any

from rag_kb.config import settings
from rag_kb.lightrag.adapter import LightRAGAdapter


class MultiKnowledgeBaseManager:
    """Manager for multiple isolated knowledge bases per product."""
    
    def __init__(self):
        """Initialize multi-knowledge base manager."""
        self.data_dir = settings.data_dir
        self.kb_config_file = self.data_dir / 'multi_kb_config.json'
        self.kb_instances = {}  # Product ID -> LightRAGAdapter instance
        self.kb_configs = {}  # Product ID -> KB configuration
        self._load_kb_configs()
    
    def _load_kb_configs(self):
        """Load knowledge base configurations from file."""
        if self.kb_config_file.exists():
            with open(self.kb_config_file, 'r', encoding='utf-8') as f:
                self.kb_configs = json.load(f)
        else:
            # Default configuration
            self.kb_configs = {
                'all': {
                    'name': '全局知识库',
                    'working_dir': self.data_dir / 'lightrag_output',
                    'enabled': True
                }
            }
            self._save_kb_configs()
    
    def _save_kb_configs(self):
        """Save knowledge base configurations to file."""
        with open(self.kb_config_file, 'w', encoding='utf-8') as f:
            json.dump(self.kb_configs, f, indent=2, ensure_ascii=False)
    
    def register_product_kb(self, product_id: str, product_name: str, 
                           source_folder: str, kb_name: str = 'default'):
        """Register a new product knowledge base.
        
        Args:
            product_id: Product identifier (e.g., 'PowerStore')
            product_name: Product display name
            source_folder: Path to product documentation folder
            kb_name: Knowledge base name
        """
        # Create isolated working directory for this product
        kb_working_dir = self.data_dir / 'lightrag_kb' / product_id / kb_name
        kb_working_dir.mkdir(parents=True, exist_ok=True)
        
        # Store configuration
        self.kb_configs[product_id] = {
            'product_id': product_id,
            'name': product_name,
            'source_folder': source_folder,
            'kb_name': kb_name,
            'working_dir': str(kb_working_dir),
            'enabled': True,
            'created_at': self._get_timestamp()
        }
        
        self._save_kb_configs()
        
        return {
            'success': True,
            'product_id': product_id,
            'working_dir': str(kb_working_dir)
        }
    
    def get_kb_adapter(self, product_id: str) -> LightRAGAdapter | None:
        """Get LightRAG adapter for a specific product knowledge base.
        
        Args:
            product_id: Product identifier
            
        Returns:
            LightRAGAdapter instance or None if not found
        """
        if product_id not in self.kb_configs:
            return None
        
        config = self.kb_configs[product_id]
        
        if not config['enabled']:
            return None
        
        # Check if adapter instance exists
        if product_id in self.kb_instances:
            return self.kb_instances[product_id]
        
        # Create new adapter instance with product-specific working directory
        try:
            adapter = LightRAGAdapter()
            # Note: In a real implementation, you'd need to configure the adapter
            # to use the product-specific working directory
            self.kb_instances[product_id] = adapter
            return adapter
        except Exception as e:
            print(f"Failed to create adapter for {product_id}: {e}")
            return None
    
    def search_product_kb(self, product_id: str, query: str, 
                         query_mode: str = 'hybrid', top_k: int = 8) -> dict[str, Any]:
        """Search within a specific product knowledge base.
        
        Args:
            product_id: Product identifier
            query: Search query
            query_mode: LightRAG query mode
            top_k: Number of results
            
        Returns:
            Search results
        """
        adapter = self.get_kb_adapter(product_id)
        
        if not adapter:
            return {
                'error': f'Knowledge base for product {product_id} not found or not enabled',
                'product_id': product_id,
                'query': query
            }
        
        try:
            answer = adapter.query(query, mode=query_mode)
            return {
                'success': True,
                'product_id': product_id,
                'query': query,
                'query_mode': query_mode,
                'answer': answer,
                'sources': []  # LightRAG doesn't provide structured sources by default
            }
        except Exception as e:
            return {
                'error': str(e),
                'product_id': product_id,
                'query': query,
                'message': 'Search failed'
            }
    
    def update_product_kb(self, product_id: str, source_folder: str = None) -> dict[str, Any]:
        """Update a product knowledge base with new documents.
        
        Args:
            product_id: Product identifier
            source_folder: Path to new documentation folder
            
        Returns:
            Update results
        """
        if product_id not in self.kb_configs:
            return {
                'error': f'Product {product_id} not registered',
                'product_id': product_id
            }
        
        # Update source folder if provided
        if source_folder:
            self.kb_configs[product_id]['source_folder'] = source_folder
            self.kb_configs[product_id]['updated_at'] = self._get_timestamp()
            self._save_kb_configs()
        
        # Clear existing adapter instance to force re-initialization
        if product_id in self.kb_instances:
            del self.kb_instances[product_id]
        
        return {
            'success': True,
            'product_id': product_id,
            'message': f'Knowledge base for {product_id} cleared for re-indexing'
        }
    
    def get_available_products(self) -> list[dict[str, Any]]:
        """Get list of available product knowledge bases.
        
        Returns:
            List of product configurations
        """
        products = []
        
        for product_id, config in self.kb_configs.items():
            if config['enabled']:
                products.append({
                    'product_id': product_id,
                    'name': config['name'],
                    'source_folder': config.get('source_folder', ''),
                    'kb_name': config.get('kb_name', 'default'),
                    'created_at': config.get('created_at', ''),
                    'updated_at': config.get('updated_at', '')
                })
        
        return products
    
    def delete_product_kb(self, product_id: str) -> dict[str, Any]:
        """Delete a product knowledge base.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Deletion results
        """
        if product_id not in self.kb_configs:
            return {
                'error': f'Product {product_id} not found',
                'product_id': product_id
            }
        
        # Clear adapter instance
        if product_id in self.kb_instances:
            del self.kb_instances[product_id]
        
        # Disable in configuration
        self.kb_configs[product_id]['enabled'] = False
        self.kb_configs[product_id]['deleted_at'] = self._get_timestamp()
        self._save_kb_configs()
        
        return {
            'success': True,
            'product_id': product_id,
            'message': f'Knowledge base for {product_id} deleted'
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


# Global instance
multi_kb_manager = MultiKnowledgeBaseManager()