# RAG Knowledge Base for 10K Long Documents

An enterprise-grade RAG (Retrieval-Augmented Generation) knowledge base system designed for processing and querying 10,000+ long documents with LightRAG graph-enhanced retrieval.

**Current Version**: v0.5.2 (Stable)  
**Release Date**: 2026-08-24

> **Version Note**: v0.5.2 introduces a unified main interface that integrates all features into a single page, eliminating the need for users to remember multiple URLs.

## Features

- **Structure-aware Chunking**: Semantic document segmentation preserving hierarchy and context
- **LightRAG Integration**: Graph-enhanced retrieval with hybrid/local/global/naive query modes
- **Multi-format Parsing**: Support for PDF, Word, HTML, and Markdown documents
- **Data Cleaning**: Built-in deduplication and PII masking
- **Security**: RBAC/ACL support for document access control
- **Incremental Updates**: Efficient document updates without full reindexing
- **Windows Native**: Designed for Windows deployment with Ollama local models
- **Open WebUI Integration**: Modern chat interface for querying
- **FastAPI Backend**: RESTful API with OpenAI-compatible endpoints

## Architecture

The system follows a layered pipeline architecture:

1. **Data Ingestion & Cleaning**: Parse documents, remove duplicates, mask PII
2. **Semantic Chunking**: Structure-aware splitting with parent-child relationships
3. **LightRAG Indexing**: Build vector+graph indexes with metadata injection
4. **Multi-mode Query**: Hybrid retrieval combining vector similarity and graph relationships
5. **Generation**: LLM-powered answer generation with source citations
6. **Frontend Delivery**: Open WebUI chat interface with streaming responses

## Installation

### Prerequisites

- Python 3.11 or higher (required for Open WebUI)
- Ollama for local LLM and embedding models
- Windows 10/11 (native deployment)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd 10K_long-doc-RAG-KB
   ```

2. **Create virtual environment**:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

4. **Install Ollama models**:
   ```bash
   ollama serve
   ollama pull qwen2.5
   ollama pull nomic-embed-text
   ```

5. **Configure settings**:
   ```bash
   copy configs\config.example.yaml configs\config.yaml
   # Edit config.yaml with your settings
   ```

## Usage

### Starting the Services

Use the provided PowerShell script to start all services:

```powershell
.\scripts\start.ps1
```

This will start:
- Ollama service (localhost:11434)
- FastAPI backend (localhost:8000)
- Open WebUI (localhost:8080, if installed)

### Manual Startup

Start services individually:

```powershell
# Start Ollama
ollama serve

# Start FastAPI backend
python -m uvicorn rag_kb.api.main:app --reload --host 0.0.0.0 --port 8000

# Start Open WebUI (optional)
open-webui serve
```

### Bulk Document Ingestion

Place documents in `data/raw/` directory and run:

```bash
python scripts\ingest_bulk.py
```

### API Endpoints

- `GET /health` - Health check
- `POST /api/v1/ingest` - Upload and index documents
- `POST /api/v1/search` - Search the knowledge base
- `POST /api/v1/chat/completions` - OpenAI-compatible chat endpoint
- `GET /docs` - Interactive API documentation

### Configuration

Edit `configs/config.yaml` to customize:

- **Embedding settings**: Ollama vs sentence-transformers, model selection
- **LLM settings**: Local Ollama vs remote OpenAI-compatible APIs
- **LightRAG settings**: Chunk size, query mode, caching
- **Security settings**: Default ACL policies

## Project Structure

```
rag-kb-project/
├── configs/                 # Configuration files
├── data/                    # Data storage
│   ├── raw/                # Source documents
│   ├── uploads/            # Uploaded files
│   └── category_dbs/       # Category-specific indexes
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
│   ├── start.ps1           # Service startup script
│   └── ingest_bulk.py      # Bulk ingestion script
├── src/rag_kb/             # Source code
│   ├── api/                # FastAPI application
│   ├── chunkers/           # Document chunking
│   ├── ingest/             # Data ingestion pipeline
│   ├── lightrag/           # LightRAG integration
│   ├── parsers/            # Document parsers
│   ├── security/           # ACL and RBAC
│   └── utils/              # Utilities
└── tests/                  # Test suite
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

The project follows these principles:
- **MVP First**: Core functionality before optimization
- **Interface-First**: Define interfaces before implementation
- **Test-Driven**: Validate each phase with tests
- **Security by Design**: ACL and RBAC built into every layer
- **Observable**: Structured logging and metrics

## Phase Implementation

The implementation follows 8 phases:

1. **Phase 0**: Project skeleton and dependencies ✅
2. **Phase 1**: Data ingestion and parsing ✅
3. **Phase 2**: Semantic chunking ✅
4. **Phase 3**: LightRAG integration ✅
5. **Phase 4**: Query modes and generation ✅
6. **Phase 5**: FastAPI backend and Open WebUI ✅
7. **Phase 6**: Testing and evaluation ✅
8. **Phase 7**: Incremental updates and security ✅
9. **Phase 8**: Advanced LightRAG features (future)

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **RAG Engine**: LightRAG (lightrag-hku)
- **Vector Store**: NanoVectorDB (built into LightRAG)
- **Graph Store**: NetworkX (built into LightRAG)
- **LLM**: Ollama (qwen2.5, llama3.1, deepseek-r1)
- **Embeddings**: Ollama (nomic-embed-text, bge-m3)
- **Frontend**: Open WebUI
- **Parsing**: PyMuPDF, pdfplumber, python-docx
- **Testing**: pytest

## Security

- **PII Masking**: Automatic detection and masking of sensitive information
- **ACL Support**: Document-level access control
- **RBAC**: Role-based permissions for queries
- **Audit Logging**: Track all access and modifications

## Performance

- **Hybrid Search**: Combines vector similarity and graph relationships
- **Parent-Child Chunking**: High precision retrieval with context preservation
- **Incremental Updates**: Efficient document updates without full reindexing
- **Caching**: LLM response caching for repeated queries

## Limitations

- LightRAG uses local storage (NetworkX + NanoVectorDB + JSON)
- For 10K+ documents with dense graphs, consider external vector/graph databases
- Windows-specific deployment (though core Python code is cross-platform)

## Future Enhancements

- External vector database integration (Qdrant, Milvus)
- Advanced graph database support (Neo4j)
- Reranking models for improved precision
- Multi-language support
- Advanced evaluation metrics (RAGAS integration)

## Contributing

This is an enterprise-grade implementation following the RAG_KB_Plan.html and RAG_KB_Implementation_Framework.html specifications.

## License

Specify your license here.

## References

- [RAG_KB_Plan.html](./RAG_KB_Plan.html) - Planning and design document
- [RAG_KB_Implementation_Framework.html](./RAG_KB_Implementation_Framework.html) - Implementation framework
- [LightRAG](https://github.com/HKUDS/LightRAG) - Graph-enhanced RAG engine
- [Open WebUI](https://github.com/open-webui/open-webui) - Chat interface

## Support

For issues and questions, please refer to the project documentation or create an issue in the repository.

## Recent Fixes

### v0.5.2 (2026-08-24) - Unified Main Interface
- **Added**: main_ui.html as single-page application for all features
- **Added**: Tabbed navigation for document upload, search, graph, status, and docs
- **Added**: Embedded graph viewer with iframe integration
- **Changed**: Root endpoint now serves unified main interface
- **Improved**: User experience with single landing page for all functions

### v0.5.1 (2026-08-24) - Reliable Startup Scripts
- **Added**: start_server.ps1 and start_server.bat for reliable server startup
- **Added**: Enhanced startup logging for debugging
- **Added**: Automatic PYTHONPATH configuration in startup scripts
- **Fixed**: Confirmed dynamic version import working correctly
- **Fixed**: Resolved all import and version display issues

### v0.5.0 (2026-08-24) - Hardcoded Version Fix
- **Fixed**: Hardcoded version '0.4.4' in main.py root endpoint
- **Changed**: Dynamic version import from __init__.py for consistency
- **Fixed**: API endpoint now displays correct version from source code

### v0.4.9 (2026-08-24) - Direct Source Startup Script
- **Added**: start_direct.bat for direct source code execution
- **Added**: Alternative startup method to bypass package version synchronization issues
- **Changed**: Updated troubleshooting guidance for package version conflicts

### v0.4.8 (2026-08-24) - Virtual Environment Python Fix
- **Fixed**: manage.ps1 to use virtual environment Python instead of system Python
- **Added**: Logic to detect and use virtual environment Python when available
- **Added**: Display of which Python executable is being used for debugging
- **Changed**: Enhanced manage.ps1 to properly handle virtual environment activation

### v0.4.7 (2026-08-24) - Static Directory Path Fix
- **Fixed**: Static directory path calculation to properly navigate to project root
- **Changed**: Path resolution from src/rag_kb/api to project root static directory
- **Added**: Warning message when static directory is not found for debugging
- **Improved**: Error handling with static directory information

### v0.4.6 (2026-08-24) - Static File Serving Fix
- **Added**: StaticFiles mounting for serving static content
- **Added**: Direct links to static files in fallback interfaces
- **Fixed**: Static file serving to properly serve HTML interfaces
- **Improved**: Path resolution and error handling for static files

### v0.4.5 (2026-08-24) - Frontend Routes Fix
- **Added**: Missing frontend routes for chat-ui, graph-ui, and knowledge-manager
- **Added**: Root endpoint with system information and available endpoints
- **Fixed**: 404 errors for web interface routes
- **Improved**: User experience with fallback HTML interfaces and documentation links

### v0.4.4 (2026-08-24) - Startup Script Fix
- **Fixed**: Modified manage.ps1 to set PYTHONPATH and use correct module path
- **Changed**: uvicorn startup from `src.rag_kb.api.main:app` to `rag_kb.api.main:app` with PYTHONPATH set
- **Resolved**: Import path issues in PowerShell startup script

### v0.4.3 (2026-08-24) - Hotfix
- **Hotfix**: Completely removed importlib.util calls that were still causing null bytes errors in uvicorn runtime
- **Improved**: Changed to standard Python imports with exception handling for robustness
- **Added**: Graceful fallback if API routes import fails
- **Verified**: Server startup confirmed working in production environment

### v0.4.2 (2026-08-24)
- **Critical Fix**: Resolved import mechanism issues in API modules that caused "source code string cannot contain null bytes" errors during startup
- **Improved**: Simplified import structure using lazy imports for heavy modules
- **Added**: Unit tests for API import mechanisms to prevent regression
- **Verified**: All 29 tests passing (22 existing + 7 new import tests)