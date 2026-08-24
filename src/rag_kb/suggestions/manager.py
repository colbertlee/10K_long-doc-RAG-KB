"""Search suggestions and quick questions system."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Suggestion:
    """Search suggestion data structure."""
    suggestion_id: str
    text: str
    category: str
    frequency: int = 0
    last_used: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'suggestion_id': self.suggestion_id,
            'text': self.text,
            'category': self.category,
            'frequency': self.frequency,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'metadata': self.metadata
        }


class SuggestionManager:
    """Manager for search suggestions and quick questions."""
    
    def __init__(self):
        """Initialize suggestion manager."""
        from rag_kb.config import settings
        self.suggestion_file = settings.data_dir / 'search_suggestions.json'
        self.suggestions = self._load_suggestions()
        self._initialize_default_suggestions()
    
    def _load_suggestions(self) -> Dict[str, Any]:
        """Load suggestions from file."""
        if self.suggestion_file.exists():
            with open(self.suggestion_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'suggestions': [],
            'categories': {
                'frequent': '高频问题',
                'entities': '核心实体',
                'troubleshooting': '故障排查',
                'configuration': '配置管理',
                'general': '通用问题'
            }
        }
    
    def _save_suggestions(self):
        """Save suggestions to file."""
        with open(self.suggestion_file, 'w', encoding='utf-8') as f:
            json.dump(self.suggestions, f, indent=2, ensure_ascii=False)
    
    def _initialize_default_suggestions(self):
        """Initialize default suggestions if empty."""
        if not self.suggestions['suggestions']:
            default_suggestions = [
                {
                    'suggestion_id': 'sug_001',
                    'text': '如何初始化网络配置？',
                    'category': 'configuration',
                    'frequency': 10,
                    'last_used': None,
                    'metadata': {'product': 'all'}
                },
                {
                    'suggestion_id': 'sug_002',
                    'text': '控制器故障如何排除？',
                    'category': 'troubleshooting',
                    'frequency': 8,
                    'last_used': None,
                    'metadata': {'product': 'all'}
                },
                {
                    'suggestion_id': 'sug_003',
                    'text': '系统架构是什么？',
                    'category': 'general',
                    'frequency': 6,
                    'last_used': None,
                    'metadata': {'product': 'all'}
                },
                {
                    'suggestion_id': 'sug_004',
                    'text': '如何升级固件？',
                    'category': 'configuration',
                    'frequency': 5,
                    'last_used': None,
                    'metadata': {'product': 'all'}
                },
                {
                    'suggestion_id': 'sug_005',
                    'text': '错误代码0x8004如何解决？',
                    'category': 'troubleshooting',
                    'frequency': 4,
                    'last_used': None,
                    'metadata': {'product': 'all'}
                }
            ]
            
            self.suggestions['suggestions'] = default_suggestions
            self._save_suggestions()
    
    def add_suggestion(self, text: str, category: str = 'general', 
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a new suggestion.
        
        Args:
            text: Suggestion text
            category: Suggestion category
            metadata: Additional metadata
            
        Returns:
            Addition result
        """
        try:
            import uuid
            
            suggestion = {
                'suggestion_id': f'sug_{uuid.uuid4().hex[:8]}',
                'text': text,
                'category': category,
                'frequency': 1,
                'last_used': None,
                'metadata': metadata or {}
            }
            
            self.suggestions['suggestions'].append(suggestion)
            self._save_suggestions()
            
            return {
                'success': True,
                'suggestion': suggestion,
                'message': 'Suggestion added successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to add suggestion'
            }
    
    def get_suggestions(self, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get suggestions.
        
        Args:
            category: Filter by category (optional)
            limit: Maximum number of suggestions
            
        Returns:
            List of suggestions
        """
        suggestions = self.suggestions['suggestions']
        
        if category:
            suggestions = [s for s in suggestions if s['category'] == category]
        
        # Sort by frequency and recency
        suggestions = sorted(
            suggestions,
            key=lambda x: (x['frequency'], x['last_used'] or ''),
            reverse=True
        )
        
        return suggestions[:limit]
    
    def get_suggestions_by_prefix(self, prefix: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get suggestions by text prefix (for autocomplete).
        
        Args:
            prefix: Text prefix to match
            limit: Maximum number of suggestions
            
        Returns:
            List of matching suggestions
        """
        prefix_lower = prefix.lower()
        
        matching = [
            s for s in self.suggestions['suggestions']
            if s['text'].lower().startswith(prefix_lower)
        ]
        
        return matching[:limit]
    
    def record_suggestion_use(self, suggestion_id: str) -> Dict[str, Any]:
        """Record that a suggestion was used.
        
        Args:
            suggestion_id: Suggestion ID
            
        Returns:
            Update result
        """
        try:
            for suggestion in self.suggestions['suggestions']:
                if suggestion['suggestion_id'] == suggestion_id:
                    suggestion['frequency'] += 1
                    suggestion['last_used'] = datetime.now().isoformat()
                    self._save_suggestions()
                    
                    return {
                        'success': True,
                        'message': 'Suggestion use recorded'
                    }
            
            return {
                'success': False,
                'message': 'Suggestion not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to record suggestion use'
            }
    
    def get_categories(self) -> Dict[str, str]:
        """Get available suggestion categories.
        
        Returns:
            Dictionary of category IDs and names
        """
        return self.suggestions['categories']
    
    def get_quick_questions(self, product_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Get quick questions for a specific product.
        
        Args:
            product_id: Product ID (optional)
            limit: Maximum number of questions
            
        Returns:
            List of quick questions
        """
        suggestions = self.suggestions['suggestions']
        
        if product_id:
            suggestions = [
                s for s in suggestions
                if s['metadata'].get('product') in [product_id, 'all']
            ]
        
        # Get high-frequency suggestions
        suggestions = sorted(
            suggestions,
            key=lambda x: x['frequency'],
            reverse=True
        )
        
        return suggestions[:limit]


# Global instance
suggestion_manager = SuggestionManager()