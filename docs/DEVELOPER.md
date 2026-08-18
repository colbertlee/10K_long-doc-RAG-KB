# Developer Guide - RAG Knowledge Base

## Table of Contents
1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Architecture Overview](#architecture-overview)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Contributing](#contributing)
8. [API Documentation](#api-documentation)
9. [Performance Optimization](#performance-optimization)

## Development Setup

### Prerequisites
- Python 3.11+
- Git
- Ollama (for local testing)
- IDE (VS Code, PyCharm, etc.)

### Setup Steps

1. **Clone and Setup:**
   ```bash
   git clone <repository-url>
   cd 10K_long-doc-RAG-KB
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Install Development Tools:**
   ```bash
   # Code formatting
   pip install black isort
   
   # Linting
   pip install flake8 pylint
   
   # Testing
   pip install pytest pytest-cov pytest-asyncio
   
   # Pre-commit hooks
   pip install pre-commit
   pre-commit install
   ```

3. **Configure Development Environment:**
   ```bash
   copy .env.example .env
   # Edit .env for development settings
   ```

4. **Start Development Services:**
   ```bash
   # Terminal 1: Start Ollama
   ollama serve
   
   # Terminal 2: Start FastAPI with hot reload
   python -m uvicorn rag_kb.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Project Structure

```
rag-kb-project/
├── configs/                 # Configuration files
│   └── config.example.yaml
├── data/                    # Data storage
│   ├── raw/                # Source documents
│   ├── uploads/            # Uploaded files
│   └── category_dbs/       # Category-specific indexes
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── src/rag_kb/             # Source code
│   ├── api/                # FastAPI application
│   │   ├── main.py        # Main application
│   │   └── routes.py      # API routes
│   ├── chunkers/           # Document chunking
│   │   ├── base.py        # Base chunker interface
│   │   ├── structured.py  # Structure-aware chunker
│   │   └── parent_child.py # Parent-child chunker
│   ├── ingest/             # Data ingestion
│   │   ├── cleaner.py     # Data cleaning
│   │   ├── incremental.py # Incremental updates
│   │   └── pipeline.py    # Ingestion pipeline
│   ├── lightrag/           # LightRAG integration
│   │   ├── adapter.py     # LightRAG adapter
│   │   ├── llm_funcs.py   # LLM functions
│   │   └── embedding_funcs.py # Embedding functions
│   ├── parsers/            # Document parsers
│   │   ├── base.py        # Base parser interface
│   │   ├── pdf_pymupdf.py # PyMuPDF parser
│   │   ├── pdf_pdfplumber.py # PDFPlumber parser
│   │   └── registry.py    # Parser registry
│   ├── security/           # Security utilities
│   │   └── acl.py         # ACL implementation
│   ├── utils/              # Utilities
│   │   └── hashing.py     # Hashing utilities
│   ├── config.py          # Configuration management
│   └── models.py          # Domain models
├── tests/                  # Test suite
│   ├── conftest.py        # Pytest configuration
│   ├── test_ingest.py     # Ingestion tests
│   ├── test_chunking.py   # Chunking tests
│   ├── test_lightrag.py   # LightRAG tests
│   └── test_eval.py       # Evaluation tests
├── pyproject.toml         # Project metadata
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Architecture Overview

### Layered Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                            │
│  (Open WebUI / Direct API / Custom Clients)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                               │
│  (FastAPI Routes / Authentication / Rate Limiting)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  (Query Processing / ACL Filtering / Response Generation)   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   RAG Engine Layer                           │
│  (LightRAG / Vector Search / Graph Traversal)                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                              │
│  (NanoVectorDB / NetworkX / JSON KV / File System)           │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

**1. Document Processing Pipeline**
- **Parsers**: Extract text and metadata from various formats
- **Cleaners**: Remove duplicates, mask PII, normalize content
- **Chunkers**: Split documents into semantic chunks

**2. LightRAG Integration**
- **Adapter**: Wraps LightRAG with custom LLM/Embedding functions
- **Query Modes**: hybrid, local, global, naive
- **Index Management**: Insert, update, delete operations

**3. Security Layer**
- **ACL**: Document-level access control
- **RBAC**: Role-based permissions
- **PII Protection**: Automatic sensitive data masking

**4. API Layer**
- **FastAPI**: RESTful API with OpenAI compatibility
- **Streaming**: SSE support for real-time responses
- **Authentication**: Ready for auth integration

## Development Workflow

### Feature Development

1. **Create Feature Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement Changes:**
   - Write code following project conventions
   - Add tests for new functionality
   - Update documentation

3. **Test Locally:**
   ```bash
   # Run tests
   pytest
   
   # Run with coverage
   pytest --cov=src/rag_kb --cov-report=html
   
   # Run specific test
   pytest tests/test_chunking.py
   ```

4. **Code Quality Checks:**
   ```bash
   # Format code
   black src/ tests/
   isort src/ tests/
   
   # Lint code
   flake8 src/ tests/
   pylint src/
   ```

5. **Commit Changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push and Create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Bug Fixing

1. **Create Bug Fix Branch:**
   ```bash
   git checkout -b fix/bug-description
   ```

2. **Reproduce and Fix:**
   - Add failing test case
   - Fix the issue
   - Verify test passes

3. **Commit with Conventional Commits:**
   ```bash
   git commit -m "fix: resolve bug description"
   ```

## Testing

### Test Structure

```python
# Unit test example
def test_function():
    # Arrange
    input_data = "test"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_chunking.py

# Run specific test function
pytest tests/test_chunking.py::test_structure_chunker_preserves_headings

# Run with coverage
pytest --cov=src/rag_kb --cov-report=html

# Run only failing tests from last run
pytest --lf
```

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Test system performance under load

### Writing Tests

```python
import pytest
from rag_kb.chunkers.structured import StructuredChunker
from rag_kb.models import Document

def test_chunker_with_sample_document():
    """Test chunker with realistic document."""
    doc = Document(
        doc_id="test123",
        content="# Title\nSome content\n## Section\nMore content"
    )
    
    chunker = StructuredChunker()
    chunks = chunker.chunk(doc)
    
    assert len(chunks) > 0
    assert all(c.chunk_id for c in chunks)
    assert all(c.doc_id == "test123" for c in chunks)
```

## Code Style

### Python Style Guide

Follow PEP 8 with these project-specific conventions:

**Naming Conventions:**
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**Documentation:**
```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: If invalid input
    """
    pass
```

**Type Hints:**
```python
from typing import List, Optional, Dict, Any

def process_data(items: List[str]) -> Dict[str, Any]:
    """Process list of items and return dictionary."""
    result = {}
    for item in items:
        result[item] = len(item)
    return result
```

### Git Commit Messages

Follow Conventional Commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

## Contributing

### Contribution Guidelines

1. **Fork the Repository**
2. **Create Feature Branch**
3. **Make Changes**
4. **Add Tests**
5. **Update Documentation**
6. **Submit Pull Request**

### Code Review Process

1. Automated checks must pass
2. At least one approval required
3. Address all review comments
4. Update documentation as needed

### Release Process

#### Smart Release (Recommended)

Use the smart release script for automated version management and release:

```powershell
# Patch release (0.2.2 -> 0.2.3)
.\scripts\smart_release.ps1 -VersionType patch

# Minor release (0.2.2 -> 0.3.0)
.\scripts\smart_release.ps1 -VersionType minor

# Major release (0.2.2 -> 1.0.0)
.\scripts\smart_release.ps1 -VersionType major

# Dry run to test
.\scripts\smart_release.ps1 -VersionType patch -DryRun

# Custom release title and notes
.\scripts\smart_release.ps1 -VersionType patch -ReleaseTitle "Fix critical bug" -ReleaseNotes "Custom release notes"
```

The smart release script automatically:
- Reads current version from `pyproject.toml`
- Calculates new version based on type (major/minor/patch)
- Updates version in `pyproject.toml`
- Updates release notes in both English and Chinese
- Commits changes with proper message
- Pushes to GitHub
- Creates GitHub Release with proper formatting

#### Manual Release Process

For manual releases:

1. Update version in `pyproject.toml`
2. Update release notes in `docs/RELEASE_NOTES.md` and `docs/RELEASE_NOTES_CN.md`
3. Commit changes
4. Create git tag
5. Push to GitHub
6. Create GitHub Release

## API Documentation

### Interactive API Documentation

Start the server and access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Endpoints

**Health Check:**
```http
GET /health
```

**Document Ingestion:**
```http
POST /api/v1/ingest
Content-Type: multipart/form-data

{
  "file": <binary>,
  "dept": "Engineering",
  "level": "Internal"
}
```

**Search:**
```http
POST /api/v1/search?q=query&dept=Engineering&level=Internal&top_k=5
```

**Chat Completions:**
```http
POST /api/v1/chat/completions
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Your question"}
  ]
}
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile function
def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    # Your code here
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Optimization Strategies

1. **Batch Processing**: Process multiple items together
2. **Caching**: Cache frequently accessed data
3. **Async Operations**: Use async for I/O operations
4. **Connection Pooling**: Reuse database connections
5. **Index Optimization**: Optimize database indexes

### Monitoring

```python
import time
import logging

# Add performance logging
def timed_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} took {end_time - start_time:.2f}s")
        return result
    return wrapper
```

## Debugging

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Debugging Tips

1. Use `print()` statements for quick debugging
2. Use Python debugger: `import pdb; pdb.set_trace()`
3. Check logs in `data/logs/` directory
4. Use API documentation for testing endpoints

## Deployment

### Production Setup

1. **Environment Variables:**
   ```bash
   RAGKB_LOG_LEVEL=WARNING
   RAGKB_LIGHTRAG_ENABLE_LLM_CACHE=true
   ```

2. **Performance Tuning:**
   - Adjust chunk sizes based on document types
   - Enable GPU acceleration for Ollama
   - Use production-grade WSGI server

3. **Monitoring:**
   - Set up application monitoring
   - Configure error tracking
   - Monitor resource usage

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "-m", "uvicorn", "rag_kb.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Resources

- **LightRAG Documentation**: https://github.com/HKUDS/LightRAG
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Ollama Documentation**: https://ollama.ai/docs
- **Project Planning**: RAG_KB_Plan.html
- **Implementation Framework**: RAG_KB_Implementation_Framework.html