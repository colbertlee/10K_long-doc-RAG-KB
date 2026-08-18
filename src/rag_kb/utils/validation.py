"""Validation utilities for user IDs and knowledge base names."""

import re
from typing import Tuple


def validate_user_id(user_id: str) -> Tuple[bool, str]:
    """Validate user ID format.
    
    Args:
        user_id: User identifier to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not user_id:
        return False, "User ID cannot be empty"
    
    if len(user_id) > 50:
        return False, "User ID cannot exceed 50 characters"
    
    # Only allow letters, numbers, underscores, and hyphens
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, user_id):
        return False, "User ID can only contain letters, numbers, underscores, and hyphens"
    
    # Check for reserved names
    reserved_names = ['default', 'admin', 'system', 'root', 'guest']
    if user_id.lower() in reserved_names:
        return False, f"'{user_id}' is a reserved user ID"
    
    return True, ""


def validate_kb_name(kb_name: str) -> Tuple[bool, str]:
    """Validate knowledge base name format.
    
    Args:
        kb_name: Knowledge base name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not kb_name:
        return False, "Knowledge base name cannot be empty"
    
    if len(kb_name) > 100:
        return False, "Knowledge base name cannot exceed 100 characters"
    
    # Only allow letters, numbers, spaces, underscores, and hyphens
    pattern = r'^[a-zA-Z0-9_\- ]+$'
    if not re.match(pattern, kb_name):
        return False, "Knowledge base name can only contain letters, numbers, spaces, underscores, and hyphens"
    
    # Check for names that start or end with space
    if kb_name.startswith(' ') or kb_name.endswith(' '):
        return False, "Knowledge base name cannot start or end with a space"
    
    return True, ""


def sanitize_path_component(name: str) -> str:
    """Sanitize path component to prevent path traversal attacks.
    
    Args:
        name: Path component to sanitize
        
    Returns:
        Sanitized path component
    """
    # Remove dangerous characters that could be used for path traversal
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    sanitized = name
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    return sanitized


def get_current_user() -> str:
    """Get current logged-in user ID.
    
    For now, returns 'default' as placeholder.
    In future, this should integrate with authentication system.
    
    Returns:
        Current user ID
    """
    # TODO: Integrate with authentication system
    # For now, return default user
    import os
    return os.environ.get('RAGKB_CURRENT_USER', 'default')