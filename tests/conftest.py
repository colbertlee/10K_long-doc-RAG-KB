"""Pytest configuration and fixtures for RAG KB tests."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_data_dir():
    """Fixture providing path to sample data directory."""
    return Path(__file__).parent / 'samples'


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture providing temporary directory for tests."""
    return tmp_path