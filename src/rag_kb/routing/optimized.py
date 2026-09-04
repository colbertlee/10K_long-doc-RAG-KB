"""Optimized multi-working directory routing system."""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RoutingStrategy(Enum):
    """Routing strategies for multi-working directory."""
    PRODUCT_BASED = "product_based"  # Route by product ID
    CATEGORY_BASED = "category_based"  # Route by document category
    USER_BASED = "user_based"  # Route by user preference
    LOAD_BALANCED = "load_balanced"  # Distribute across directories
    INTELLIGENT = "intelligent"  # AI-based routing decision


@dataclass
class WorkingDirectory:
    """Working directory configuration."""
    dir_id: str
    dir_path: str
    product_id: str | None = None
    category: str | None = None
    user_id: str | None = None
    capacity: int = 1000
    current_load: int = 0
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dir_id': self.dir_id,
            'dir_path': self.dir_path,
            'product_id': self.product_id,
            'category': self.category,
            'user_id': self.user_id,
            'capacity': self.capacity,
            'current_load': self.current_load,
            'enabled': self.enabled,
            'metadata': self.metadata
        }


class OptimizedRouter:
    """Optimized router for multi-working directory management."""
    
    def __init__(self, strategy: RoutingStrategy = RoutingStrategy.PRODUCT_BASED):
        """Initialize optimized router.
        
        Args:
            strategy: Routing strategy to use
        """
        from rag_kb.config import settings
        self.strategy = strategy
        self.router_file = settings.data_dir / 'optimized_router.json'
        self.working_directories: dict[str, WorkingDirectory] = {}
        self.routing_cache = {}
        self._load_directories()
    
    def _load_directories(self):
        """Load working directories from file."""
        if self.router_file.exists():
            try:
                with open(self.router_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for dir_id, dir_data in data.get('directories', {}).items():
                        self.working_directories[dir_id] = self._dict_to_directory(dir_data)
            except Exception as e:
                print(f"Error loading directories: {e}")
    
    def _save_directories(self):
        """Save working directories to file."""
        try:
            data = {
                'directories': {
                    dir_id: directory.to_dict()
                    for dir_id, directory in self.working_directories.items()
                },
                'strategy': self.strategy.value
            }
            with open(self.router_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving directories: {e}")
    
    def _dict_to_directory(self, data: dict[str, Any]) -> WorkingDirectory:
        """Convert dictionary to directory object."""
        return WorkingDirectory(
            dir_id=data['dir_id'],
            dir_path=data['dir_path'],
            product_id=data.get('product_id'),
            category=data.get('category'),
            user_id=data.get('user_id'),
            capacity=data.get('capacity', 1000),
            current_load=data.get('current_load', 0),
            enabled=data.get('enabled', True),
            metadata=data.get('metadata', {})
        )
    
    def register_working_directory(self, dir_id: str, dir_path: str,
                                  product_id: str = None, category: str = None,
                                  user_id: str = None, capacity: int = 1000) -> dict[str, Any]:
        """Register a new working directory.
        
        Args:
            dir_id: Directory ID
            dir_path: Directory path
            product_id: Product ID (optional)
            category: Category (optional)
            user_id: User ID (optional)
            capacity: Maximum capacity
            
        Returns:
            Registration result
        """
        directory = WorkingDirectory(
            dir_id=dir_id,
            dir_path=dir_path,
            product_id=product_id,
            category=category,
            user_id=user_id,
            capacity=capacity
        )
        
        self.working_directories[dir_id] = directory
        self._save_directories()
        
        return {
            'success': True,
            'dir_id': dir_id,
            'message': 'Working directory registered successfully'
        }
    
    def route_query(self, query: str, product_id: str = None,
                   category: str = None, user_id: str = None) -> str | None:
        """Route query to optimal working directory.
        
        Args:
            query: Search query
            product_id: Product ID (optional)
            category: Category (optional)
            user_id: User ID (optional)
            
        Returns:
            Working directory ID or None
        """
        # Check cache first
        cache_key = f"{query}_{product_id}_{category}_{user_id}"
        if cache_key in self.routing_cache:
            return self.routing_cache[cache_key]
        
        # Apply routing strategy
        if self.strategy == RoutingStrategy.PRODUCT_BASED:
            dir_id = self._route_by_product(product_id)
        elif self.strategy == RoutingStrategy.CATEGORY_BASED:
            dir_id = self._route_by_category(category)
        elif self.strategy == RoutingStrategy.USER_BASED:
            dir_id = self._route_by_user(user_id)
        elif self.strategy == RoutingStrategy.LOAD_BALANCED:
            dir_id = self._route_by_load()
        elif self.strategy == RoutingStrategy.INTELLIGENT:
            dir_id = self._route_intelligent(query, product_id, category, user_id)
        else:
            dir_id = self._route_by_product(product_id)
        
        # Cache result
        if dir_id:
            self.routing_cache[cache_key] = dir_id
        
        return dir_id
    
    def _route_by_product(self, product_id: str) -> str | None:
        """Route by product ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Working directory ID
        """
        if not product_id:
            return None
        
        for dir_id, directory in self.working_directories.items():
            if directory.product_id == product_id and directory.enabled:
                return dir_id
        
        return None
    
    def _route_by_category(self, category: str) -> str | None:
        """Route by category.
        
        Args:
            category: Category
            
        Returns:
            Working directory ID
        """
        if not category:
            return None
        
        for dir_id, directory in self.working_directories.items():
            if directory.category == category and directory.enabled:
                return dir_id
        
        return None
    
    def _route_by_user(self, user_id: str) -> str | None:
        """Route by user preference.
        
        Args:
            user_id: User ID
            
        Returns:
            Working directory ID
        """
        if not user_id:
            return None
        
        for dir_id, directory in self.working_directories.items():
            if directory.user_id == user_id and directory.enabled:
                return dir_id
        
        return None
    
    def _route_by_load(self) -> str | None:
        """Route by load balancing.
        
        Returns:
            Working directory ID with lowest load
        """
        enabled_dirs = [
            (dir_id, directory)
            for dir_id, directory in self.working_directories.items()
            if directory.enabled
        ]
        
        if not enabled_dirs:
            return None
        
        # Find directory with lowest load percentage
        min_load_dir = min(
            enabled_dirs,
            key=lambda x: x[1].current_load / x[1].capacity
        )
        
        return min_load_dir[0]
    
    def _route_intelligent(self, query: str, product_id: str = None,
                         category: str = None, user_id: str = None) -> str | None:
        """Intelligent routing using multiple factors.
        
        Args:
            query: Search query
            product_id: Product ID
            category: Category
            user_id: User ID
            
        Returns:
            Working directory ID
        """
        # Priority: product > category > user > load
        if product_id:
            dir_id = self._route_by_product(product_id)
            if dir_id:
                return dir_id
        
        if category:
            dir_id = self._route_by_category(category)
            if dir_id:
                return dir_id
        
        if user_id:
            dir_id = self._route_by_user(user_id)
            if dir_id:
                return dir_id
        
        return self._route_by_load()
    
    def update_directory_load(self, dir_id: str, load_change: int):
        """Update directory load.
        
        Args:
            dir_id: Directory ID
            load_change: Load change (positive or negative)
        """
        if dir_id in self.working_directories:
            directory = self.working_directories[dir_id]
            directory.current_load = max(0, directory.current_load + load_change)
            self._save_directories()
    
    def get_directory_status(self, dir_id: str) -> dict[str, Any] | None:
        """Get directory status.
        
        Args:
            dir_id: Directory ID
            
        Returns:
            Directory status
        """
        if dir_id in self.working_directories:
            return self.working_directories[dir_id].to_dict()
        return None
    
    def get_all_directories(self) -> list[dict[str, Any]]:
        """Get all working directories.
        
        Returns:
            List of directory configurations
        """
        return [directory.to_dict() for directory in self.working_directories.values()]
    
    def set_routing_strategy(self, strategy: RoutingStrategy):
        """Change routing strategy.
        
        Args:
            strategy: New routing strategy
        """
        self.strategy = strategy
        self.routing_cache.clear()  # Clear cache on strategy change
        self._save_directories()


# Global instance
optimized_router = OptimizedRouter()