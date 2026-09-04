"""Pytest configuration and fixtures for modular testing."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_data_dir():
    """Sample data directory fixture."""
    data_dir = Path(__file__).parent.parent / "data" / "test_samples"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def temp_dir():
    """Temporary directory fixture."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_document():
    """Sample document fixture."""
    return {
        "doc_id": "test_doc_1",
        "content": "# Test Document\n\nThis is a test document for testing purposes.\n\n## Section 1\nContent for section 1.\n\n## Section 2\nContent for section 2."
    }


@pytest.fixture
def sample_query():
    """Sample query fixture."""
    return "What is the main topic of the document?"


@pytest.fixture
def minimax_config():
    """Minimax configuration fixture."""
    return {
        "api_key": "test_api_key",
        "group_id": "2030841473657737564",
        "model": "abab6.5s-chat",
        "base_url": "https://api.minimax.chat/v1",
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 1536
    }


@pytest.fixture
def test_config(sample_data_dir, temp_dir):
    """Test configuration fixture."""
    class TestEnvironmentConfig:
        def __init__(self, test_data_dir, temp_dir):
            self.test_data_dir = test_data_dir
            self.temp_dir = temp_dir
            self.config_backup = None
        
        def setup_test_environment(self):
            """Setup test environment."""
            print(f"✅ Test environment setup: {self.temp_dir}")
        
        def teardown_test_environment(self):
            """Cleanup test environment."""
            print(f"✅ Test environment cleaned up")
        
        def get_test_config(self) -> Dict[str, Any]:
            """Get test configuration."""
            return {
                "test_data_dir": str(self.test_data_dir),
                "temp_dir": str(self.temp_dir),
                "use_real_llm": False,
                "test_timeout": 30
            }
        
        def create_test_document(self, content: str, filename: str = "test_doc.txt") -> Path:
            """Create a test document."""
            test_file = self.test_data_dir / filename
            test_file.write_text(content, encoding='utf-8')
            return test_file
    
    config = TestEnvironmentConfig(sample_data_dir, temp_dir)
    config.setup_test_environment()
    yield config
    config.teardown_test_environment()


# Import fixtures from fixtures package for global availability
try:
    from tests.fixtures.test_documents import (
        simple_doc, technical_doc, multi_section_doc, chinese_doc,
        large_doc, code_doc, table_doc, mixed_format_doc, doc_collection, qa_doc
    )
except ImportError:
    # Fixtures may not be available yet
    pass

try:
    from tests.fixtures.test_queries import (
        simple_query, technical_query, multi_part_query, chinese_query,
        code_query, comparison_query, procedural_query, ambiguous_query,
        complex_query, domain_specific_query, query_collection, 
        query_with_context, query_with_filters
    )
except ImportError:
    # Fixtures may not be available yet
    pass