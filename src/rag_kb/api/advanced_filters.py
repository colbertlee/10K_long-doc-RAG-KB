"""Advanced filtering capabilities for RAG KB."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from rag_kb.models import SearchResult, Document
import re


class AdvancedFilter:
    """Advanced filtering for search results and documents."""
    
    def __init__(self):
        """Initialize advanced filter."""
        self.filter_types = {
            'time_range': self.filter_by_time_range,
            'document_type': self.filter_by_document_type,
            'custom_metadata': self.filter_by_custom_metadata,
            'content_length': self.filter_by_content_length,
            'author': self.filter_by_author,
            'tags': self.filter_by_tags
        }
    
    def apply_filters(self, results: List[SearchResult], filters: Dict[str, Any]) -> List[SearchResult]:
        """Apply multiple filters to search results.
        
        Args:
            results: List of search results to filter
            filters: Dictionary of filter criteria
            
        Returns:
            Filtered list of search results
        """
        filtered = results
        
        for filter_type, filter_value in filters.items():
            if filter_type in self.filter_types and filter_value:
                filter_func = self.filter_types[filter_type]
                filtered = filter_func(filtered, filter_value)
        
        return filtered
    
    def filter_by_time_range(self, results: List[SearchResult], time_range: Dict[str, str]) -> List[SearchResult]:
        """Filter results by time range.
        
        Args:
            results: List of search results
            time_range: Dictionary with 'start' and 'end' dates (ISO format)
            
        Returns:
            Filtered results
        """
        if not time_range or 'start' not in time_range:
            return results
        
        try:
            start_date = datetime.fromisoformat(time_range['start'])
            end_date = datetime.fromisoformat(time_range.get('end', datetime.now().isoformat()))
            
            filtered = []
            for result in results:
                # Check if result has timestamp metadata
                result_time = result.metadata.get('timestamp') or result.metadata.get('created_at')
                if result_time:
                    try:
                        result_date = datetime.fromisoformat(result_time)
                        if start_date <= result_date <= end_date:
                            filtered.append(result)
                    except (ValueError, TypeError):
                        # If timestamp parsing fails, include the result
                        filtered.append(result)
                else:
                    # If no timestamp, include the result
                    filtered.append(result)
            
            return filtered
        except (ValueError, TypeError) as e:
            print(f"Error parsing time range: {e}")
            return results
    
    def filter_by_document_type(self, results: List[SearchResult], doc_types: List[str]) -> List[SearchResult]:
        """Filter results by document type.
        
        Args:
            results: List of search results
            doc_types: List of document types to include
            
        Returns:
            Filtered results
        """
        if not doc_types:
            return results
        
        doc_types_lower = [dt.lower() for dt in doc_types]
        filtered = []
        
        for result in results:
            # Check document type from metadata or filename
            doc_type = result.metadata.get('document_type') or result.metadata.get('file_type')
            if doc_type:
                if doc_type.lower() in doc_types_lower:
                    filtered.append(result)
            else:
                # Try to infer from filename
                filename = result.metadata.get('filename', '')
                for doc_type in doc_types_lower:
                    if filename.lower().endswith(doc_type):
                        filtered.append(result)
                        break
        
        return filtered
    
    def filter_by_custom_metadata(self, results: List[SearchResult], metadata_filters: Dict[str, Any]) -> List[SearchResult]:
        """Filter results by custom metadata.
        
        Args:
            results: List of search results
            metadata_filters: Dictionary of metadata field to value mappings
            
        Returns:
            Filtered results
        """
        if not metadata_filters:
            return results
        
        filtered = []
        
        for result in results:
            match = True
            for field, value in metadata_filters.items():
                result_value = result.metadata.get(field)
                if result_value != value:
                    match = False
                    break
            
            if match:
                filtered.append(result)
        
        return filtered
    
    def filter_by_content_length(self, results: List[SearchResult], length_range: Dict[str, int]) -> List[SearchResult]:
        """Filter results by content length.
        
        Args:
            results: List of search results
            length_range: Dictionary with 'min' and 'max' character counts
            
        Returns:
            Filtered results
        """
        if not length_range:
            return results
        
        min_length = length_range.get('min', 0)
        max_length = length_range.get('max', float('inf'))
        
        filtered = []
        for result in results:
            content_length = len(result.content)
            if min_length <= content_length <= max_length:
                filtered.append(result)
        
        return filtered
    
    def filter_by_author(self, results: List[SearchResult], authors: List[str]) -> List[SearchResult]:
        """Filter results by author.
        
        Args:
            results: List of search results
            authors: List of author names to include
            
        Returns:
            Filtered results
        """
        if not authors:
            return results
        
        authors_lower = [author.lower() for author in authors]
        filtered = []
        
        for result in results:
            author = result.metadata.get('author', '')
            if author.lower() in authors_lower:
                filtered.append(result)
        
        return filtered
    
    def filter_by_tags(self, results: List[SearchResult], tags: List[str]) -> List[SearchResult]:
        """Filter results by tags.
        
        Args:
            results: List of search results
            tags: List of tags to include (results must have at least one)
            
        Returns:
            Filtered results
        """
        if not tags:
            return results
        
        tags_lower = [tag.lower() for tag in tags]
        filtered = []
        
        for result in results:
            result_tags = result.metadata.get('tags', [])
            if isinstance(result_tags, list):
                result_tags_lower = [tag.lower() for tag in result_tags]
                # Check if any tag matches
                if any(tag in result_tags_lower for tag in tags_lower):
                    filtered.append(result)
        
        return filtered


class FilterBuilder:
    """Builder for constructing complex filter queries."""
    
    def __init__(self):
        """Initialize filter builder."""
        self.filters = {}
    
    def add_time_range(self, start_date: str, end_date: Optional[str] = None) -> 'FilterBuilder':
        """Add time range filter.
        
        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format (optional)
            
        Returns:
            Self for method chaining
        """
        self.filters['time_range'] = {
            'start': start_date,
            'end': end_date or datetime.now().isoformat()
        }
        return self
    
    def add_document_type(self, doc_types: List[str]) -> 'FilterBuilder':
        """Add document type filter.
        
        Args:
            doc_types: List of document types
            
        Returns:
            Self for method chaining
        """
        self.filters['document_type'] = doc_types
        return self
    
    def add_custom_metadata(self, metadata: Dict[str, Any]) -> 'FilterBuilder':
        """Add custom metadata filter.
        
        Args:
            metadata: Dictionary of metadata field to value mappings
            
        Returns:
            Self for method chaining
        """
        self.filters['custom_metadata'] = metadata
        return self
    
    def add_content_length(self, min_length: int, max_length: int) -> 'FilterBuilder':
        """Add content length filter.
        
        Args:
            min_length: Minimum character count
            max_length: Maximum character count
            
        Returns:
            Self for method chaining
        """
        self.filters['content_length'] = {
            'min': min_length,
            'max': max_length
        }
        return self
    
    def add_author(self, authors: List[str]) -> 'FilterBuilder':
        """Add author filter.
        
        Args:
            authors: List of author names
            
        Returns:
            Self for method chaining
        """
        self.filters['author'] = authors
        return self
    
    def add_tags(self, tags: List[str]) -> 'FilterBuilder':
        """Add tags filter.
        
        Args:
            tags: List of tags
            
        Returns:
            Self for method chaining
        """
        self.filters['tags'] = tags
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the final filter dictionary.
        
        Returns:
            Dictionary of all filters
        """
        return self.filters