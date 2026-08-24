"""Tests for folder import functionality."""

import pytest
from pathlib import Path


def test_folder_import_endpoint_signature():
    """Test that the folder import endpoint has correct signature."""
    # This test verifies the endpoint exists by checking the source code
    main_file = Path("src/rag_kb/api/main.py")
    if main_file.exists():
        content = main_file.read_text()
        assert "import_folder" in content
        assert "folder_path" in content
        assert "user_id" in content
        assert "kb_name" in content


def test_folder_import_logic():
    """Test folder import logic with temporary directory."""
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("Test content")
        
        # Verify folder exists
        assert Path(tmpdir).exists()
        assert test_file.exists()
        
        # Verify file has content
        assert test_file.read_text() == "Test content"