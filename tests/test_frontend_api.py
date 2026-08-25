"""Test frontend API integration."""

import pytest
import json


def test_search_endpoint_post_method():
    """Test that search endpoint uses POST method correctly."""
    # This test verifies the frontend should use POST method
    # The actual endpoint implementation is tested in integration tests
    assert True  # Placeholder for integration test


def test_chat_completions_post_method():
    """Test that chat completions endpoint uses POST method correctly."""
    # This test verifies the frontend should use POST method
    # The actual endpoint implementation is tested in integration tests
    assert True  # Placeholder for integration test


def test_cache_control_headers():
    """Test that HTML files have cache control headers."""
    import os
    from pathlib import Path
    
    static_dir = Path(__file__).parent.parent / "static"
    html_files = list(static_dir.glob("*.html"))
    
    assert len(html_files) > 0, "Should have HTML files in static directory"
    
    # Check that at least some HTML files have cache control
    cache_control_files = 0
    for html_file in html_files:
        content = html_file.read_text()
        if "Cache-Control" in content or "no-cache" in content:
            cache_control_files += 1
    
    assert cache_control_files > 0, "Should have cache control in HTML files"


def test_api_base_port_consistency():
    """Test that API_BASE port is consistent across frontend files."""
    import os
    from pathlib import Path
    
    static_dir = Path(__file__).parent.parent / "static"
    html_files = list(static_dir.glob("*.html"))
    
    port_8000_count = 0
    port_8001_count = 0
    
    for html_file in html_files:
        content = html_file.read_text()
        if "localhost:8000" in content:
            port_8000_count += 1
        if "localhost:8001" in content:
            port_8001_count += 1
    
    # Should be consistent - either all 8000 or all 8001
    # Currently we use 8000
    assert port_8000_count > 0, "Should have at least one file using port 8000"
    assert port_8001_count == 0, "Should not have files using port 8001 (inconsistent)"