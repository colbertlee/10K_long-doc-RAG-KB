"""Access control list (ACL) and RBAC utilities for RAG KB."""

from typing import Dict, List, Optional, Set
from rag_kb.models import SearchResult, Document
import re


def allowed_sources(user_roles: Dict[str, List[str]]) -> List[str]:
    """Determine allowed sources based on user roles.
    
    Args:
        user_roles: Dictionary mapping role types to allowed values
        
    Returns:
        List of allowed source prefixes
    """
    # Example: map dept/level to allowed source prefixes.
    # This can be extended with custom logic based on organizational structure
    allowed = []
    
    # If user has specific department access, add corresponding source prefixes
    if 'dept' in user_roles and user_roles['dept']:
        for dept in user_roles['dept']:
            allowed.append(f"dept_{dept}")
    
    # If user has specific level access, add corresponding level prefixes
    if 'level' in user_roles and user_roles['level']:
        for level in user_roles['level']:
            allowed.append(f"level_{level}")
    
    return allowed


def filter_results(results: List[SearchResult], user_roles: Dict[str, List[str]]) -> List[SearchResult]:
    """Filter search results based on user ACL.
    
    Args:
        results: List of search results to filter
        user_roles: Dictionary mapping role types to allowed values
        
    Returns:
        Filtered list of search results
    """
    filtered = []
    for r in results:
        ok = True
        for key, allowed in user_roles.items():
            if not allowed:  # Empty list means no restriction for this key
                continue
                
            value = r.metadata.get(f'acl_{key}')
            if value is None or value not in allowed:
                ok = False
                break
        if ok:
            filtered.append(r)
    return filtered


def filter_by_source(answer: str, allowed: List[str]) -> str:
    """Filter answer content based on allowed sources.
    
    Args:
        answer: Answer text to filter
        allowed: List of allowed source prefixes
        
    Returns:
        Filtered answer text
    """
    # LightRAG injects source/category/product_id into chunk text headers.
    # Post-filter can drop chunks whose [source=...;category=...] is not in allowed.
    if not allowed:
        return answer
    
    # Split answer into chunks based on LightRAG's data markers
    chunks = re.split(r'(\[DATA:[^\]]+\])', answer)
    filtered_chunks = []
    
    for i in range(0, len(chunks), 2):
        text_part = chunks[i] if i < len(chunks) else ''
        data_part = chunks[i + 1] if i + 1 < len(chunks) else ''
        
        # Check if data part contains allowed sources
        if data_part:
            # Extract source information from data marker
            source_match = re.search(r'source=([^;\]]+)', data_part)
            if source_match:
                source = source_match.group(1)
                # Check if source is allowed
                if any(allowed_source in source for allowed_source in allowed):
                    filtered_chunks.append(text_part)
                    filtered_chunks.append(data_part)
            else:
                # If no source info, include by default (conservative approach)
                filtered_chunks.append(text_part)
                filtered_chunks.append(data_part)
        else:
            filtered_chunks.append(text_part)
    
    return ''.join(filtered_chunks)


def build_acl_filter(user_roles: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Build ACL filter dictionary from user roles.
    
    Args:
        user_roles: Dictionary mapping role types to allowed values
        
    Returns:
        ACL filter dictionary
    """
    return user_roles


def check_document_access(document: Document, user_roles: Dict[str, List[str]]) -> bool:
    """Check if user has access to a document based on ACL.
    
    Args:
        document: Document to check
        user_roles: User's role-based access control
        
    Returns:
        True if user has access, False otherwise
    """
    if not document.acl:
        # No ACL means document is accessible by default
        return True
    
    for key, required_roles in user_roles.items():
        if required_roles:  # Only check if there are requirements for this key
            doc_roles = document.acl.get(key, [])
            # If document has specific roles for this key, user must have at least one
            if doc_roles and not any(role in doc_roles for role in required_roles):
                return False
    
    return True


def build_lightrag_acl_filter(user_roles: Dict[str, List[str]]) -> str:
    """Build LightRAG-compatible ACL filter string.
    
    Args:
        user_roles: Dictionary mapping role types to allowed values
        
    Returns:
        ACL filter string for LightRAG queries
    """
    filters = []
    for key, values in user_roles.items():
        if values:
            # Build filter like "dept=Sales|Marketing" or "level=Internal"
            filter_str = f"{key}={'|'.join(values)}"
            filters.append(filter_str)
    
    return " AND ".join(filters) if filters else ""


def extract_acl_from_metadata(metadata: Dict[str, any]) -> Dict[str, List[str]]:
    """Extract ACL information from document metadata.
    
    Args:
        metadata: Document metadata dictionary
        
    Returns:
        ACL dictionary with role types and allowed values
    """
    acl = {}
    for key, value in metadata.items():
        if key.startswith('acl_'):
            role_type = key[4:]  # Remove 'acl_' prefix
            if isinstance(value, list):
                acl[role_type] = value
            elif isinstance(value, str):
                acl[role_type] = [value]
    return acl


def apply_pre_filter_query(query: str, user_roles: Dict[str, List[str]]) -> str:
    """Apply ACL pre-filtering to search query.
    
    Args:
        query: Original search query
        user_roles: User's role-based access control
        
    Returns:
        Enhanced query with ACL constraints
    """
    acl_filter = build_lightrag_acl_filter(user_roles)
    if acl_filter:
        return f"{query} (filter: {acl_filter})"
    return query


class ACLContext:
    """Context manager for ACL-aware operations."""
    
    def __init__(self, user_roles: Dict[str, List[str]]):
        """Initialize ACL context.
        
        Args:
            user_roles: User's role-based access control
        """
        self.user_roles = user_roles
        self.original_roles = None
    
    def __enter__(self):
        """Enter ACL context."""
        # Store original roles if needed for rollback
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit ACL context."""
        # Cleanup if needed
        return False
    
    def can_access(self, document: Document) -> bool:
        """Check if current context can access document.
        
        Args:
            document: Document to check
            
        Returns:
            True if accessible, False otherwise
        """
        return check_document_access(document, self.user_roles)
    
    def get_filter_string(self) -> str:
        """Get LightRAG filter string for current context.
        
        Returns:
            ACL filter string
        """
        return build_lightrag_acl_filter(self.user_roles)