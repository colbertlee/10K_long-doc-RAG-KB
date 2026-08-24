"""Tests for LightRAG integration."""

from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.lightrag.embedding_funcs import ollama_embed
from rag_kb.lightrag.llm_funcs import ollama_llm
from rag_kb.config import settings


def test_lightrag_adapter_initialization():
    """Test that LightRAG adapter can be initialized."""
    # Use a temporary directory for testing
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmpdir:
        adapter = LightRAGAdapter(working_dir=tmpdir)
        assert adapter.working_dir == Path(tmpdir)
        assert adapter.rag is not None


def test_lightrag_adapter_has_required_methods():
    """Test that LightRAG adapter has required methods."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        adapter = LightRAGAdapter(working_dir=tmpdir)
        assert hasattr(adapter, 'insert_chunks')
        assert hasattr(adapter, 'query')
        assert hasattr(adapter, 'stream_query')


def test_embedding_function_signature():
    """Test that embedding function has correct signature."""
    import inspect
    
    sig = inspect.signature(ollama_embed)
    assert 'texts' in sig.parameters


def test_llm_function_signature():
    """Test that LLM function has correct signature."""
    import inspect
    
    sig = inspect.signature(ollama_llm)
    assert 'prompt' in sig.parameters


def test_settings_configuration():
    """Test that settings are properly configured."""
    assert settings.app_name == 'rag-kb'
    assert settings.embedding_provider == 'ollama'
    assert settings.llm_provider == 'ollama'
    assert settings.lightrag_query_mode == 'hybrid'