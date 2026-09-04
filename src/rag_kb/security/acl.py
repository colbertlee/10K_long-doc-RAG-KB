"""Access control list (ACL) and RBAC utilities for RAG KB."""


from rag_kb.models import SearchResult


def allowed_sources(user_roles: dict[str, list[str]]):
    """Determine allowed sources based on user roles.
    
    Args:
        user_roles: Dictionary mapping role types to allowed values
        
    Returns:
        List of allowed source prefixes
    """
    # Example: map dept/level to allowed source prefixes.
    return []


def filter_results(results: list[SearchResult], user_roles: dict[str, list[str]]) -> list[SearchResult]:
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
            value = r.metadata.get(f'acl_{key}')
            if value is None or value not in allowed:
                ok = False
                break
        if ok:
            filtered.append(r)
    return filtered


def filter_by_source(answer: str, allowed: list[str]) -> str:
    """Filter answer content based on allowed sources.
    
    Args:
        answer: Answer text to filter
        allowed: List of allowed source prefixes
        
    Returns:
        Filtered answer text
    """
    # LightRAG injects source/category/product_id into chunk text headers.
    # Post-filter can drop chunks whose [source=...;category=...] is not in allowed.
    return answer


def build_acl_filter(user_roles: dict[str, list[str]]) -> dict[str, list[str]]:
    """Build ACL filter dictionary from user roles.
    
    Args:
        user_roles: Dictionary mapping role types to allowed values
        
    Returns:
        ACL filter dictionary
    """
    return user_roles