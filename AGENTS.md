# RAG KB Project - Agent Information

## Project Overview

This is an enterprise-grade RAG (Retrieval-Augmented Generation) knowledge base system designed to handle 10,000+ long documents efficiently. The system integrates LightRAG for hybrid retrieval, BM25 for sparse search, Cross-Encoder reranking, comprehensive security, evaluation, and deployment capabilities.

## Latest Implementation Status (v0.3.2)

The system has been enhanced with comprehensive user journey analysis and documentation:

### ✅ Current Status
- **Stable Version**: v0.3.0 (recommended for use)
- **Latest Analysis**: v0.3.2 (documentation and user journey analysis)
- **Known Issues**: v0.5.0 has technical issues (routes.py corruption)

### ✅ Completed Enhancements (v0.3.0)
- **Python 3.11+ Compatibility**: Updated from 3.9 to meet requirements
- **Incremental Updates**: File hash-based change detection with document registry
- **Enterprise Security**: Comprehensive RBAC/ACL with pre-filtering and post-filtering
- **Hybrid Search**: BM25 sparse search + LightRAG hybrid with RRF fusion
- **Advanced Reranking**: Cross-encoder and rule-based reranking with GPU support
- **Knowledge Graph**: LightRAG graph extraction with NetworkX integration
- **RAGAS Evaluation**: Complete evaluation framework with 15+ test cases
- **Deployment Scripts**: PowerShell and batch automation with health checks
- **Performance Monitoring**: Structured logging, system metrics, and performance tracking
- **Performance Optimization**: Configurable templates and tuning guidelines

### 📊 User Journey Analysis (v0.3.2)
- **Complete Workflow Analysis**: 7-step user journey from start to finish
- **Problem Identification**: Each step's current issues and impact
- **Improvement Roadmap**: Prioritized improvements (P0, P1, P2)
- **Usage Guidelines**: Recommended workflow for stable version

## Key Technical Stack

- **Python**: 3.11+ (required for modern dependencies)
- **Web Framework**: FastAPI with Uvicorn
- **RAG Engine**: LightRAG (lightrag-hku>=1.5.6), BM25 (secondary)
- **Local LLM**: Ollama with qwen3.5:4b model (or gemma4:e4b)
- **Embedding**: Ollama with nomic-embed-text or sentence-transformers
- **Frontend**: Custom interfaces with Cytoscape.js for graph visualization, Open WebUI integration
- **Testing**: pytest with custom RAGAS evaluation framework
- **Graph Processing**: NetworkX for knowledge graph visualization
- **Monitoring**: psutil for system metrics tracking
- **Performance**: rank-bm25 for sparse search optimization
- **Dependencies**: numpy>=2.0.0,<2.8.0, pydantic-core==2.46.4, cryptography==48.0.0
- **Visualization**: Cytoscape.js for interactive knowledge graph display

## Build and Test Commands

### Installation
```powershell
# Full installation with all optional dependencies
pip install -e .[all]

# Core installation only
pip install -e .

# Development installation
pip install -e .[dev]

# Performance-optimized installation
pip install -e .[reranking]
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ragas_eval.py -v
pytest tests/test_chunking.py -v

# Run with coverage
pytest tests/ --cov=src/rag_kb --cov-report=html

# Run custom test scripts
python scripts/test_ingestion.py
python scripts/test_hybrid_search.py
python scripts/test_graph_extraction.py
python scripts/end_to_end_test.py  # NEW: Complete business flow validation
```

### Starting the Server
```powershell
# Unified management script (recommended)
.\manage.ps1 start

# Other management commands
.\manage.ps1 stop      # Stop system
.\manage.ps1 restart   # Restart system
.\manage.ps1 status    # Check system status
.\manage.ps1 upgrade   # Upgrade system
.\manage.ps1 open      # Open in browser
.\manage.ps1 help      # Show help

# Manual start (if needed)
python -m uvicorn src.rag_kb.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Monitoring
```bash
# Health check
curl http://localhost:8000/health

# Performance metrics
curl http://localhost:8000/metrics

# API documentation
curl http://localhost:8000/docs
```

## Project Structure

```
rag-kb/
├── configs/                 # Configuration files
│   ├── config.example.yaml  # Example configuration
│   ├── config.yaml         # Active configuration
│   └── performance.yaml    # Performance-optimized settings (NEW)
├── data/                   # Data directories
│   ├── uploads/           # Uploaded files
│   ├── users/             # User-specific data
│   ├── samples/           # Sample documents for testing (NEW)
│   └── bm25_cache/        # BM25 index cache
├── docs/                   # Documentation
│   └── PERFORMANCE_TUNING.md  # Performance optimization guide (NEW)
├── logs/                   # Log files (auto-created) (NEW)
├── scripts/               # Deployment scripts
│   ├── manage.ps1        # Unified management script (NEW)
│   ├── install.ps1       # Installation script
│   ├── upgrade.ps1       # Upgrade script
│   ├── import_local_folder.ps1 # Folder import (NEW)
│   ├── _start_internal.ps1 # Internal startup script (RENAMED)
│   ├── test_ingestion.py # Ingestion testing (NEW)
│   ├── test_hybrid_search.py # Search testing (NEW)
│   ├── test_graph_extraction.py # Graph testing (NEW)
│   └── end_to_end_test.py # Complete business flow validation (NEW)
├── src/rag_kb/           # Main source code
│   ├── api/              # API layer
│   │   ├── main.py       # FastAPI application with monitoring (UPDATED)
│   │   ├── routes.py     # API endpoints
│   │   └── docs_ui.py    # Documentation UI
│   ├── chunkers/         # Document chunking strategies
│   ├── ingest/           # Data processing pipeline
│   │   ├── incremental.py # Incremental update mechanism (ENHANCED)
│   │   ├── pipeline.py   # Main ingestion pipeline
│   │   ├── cleaner.py    # Data cleaning
│   │   └── user_manager.py # User data management
│   ├── lightrag/         # LightRAG integration
│   │   ├── adapter.py    # LightRAG adapter with ACL (UPDATED)
│   │   ├── embedding_funcs.py # Embedding functions
│   │   ├── llm_funcs.py  # LLM functions
│   │   └── graph_extractor.py # Knowledge graph extraction (NEW)
│   ├── parsers/          # Document parsers
│   ├── retrieval/        # Search engines (NEW MODULE)
│   │   ├── bm25_search.py # BM25 sparse search (NEW)
│   │   ├── hybrid_search.py # Hybrid search with RRF (NEW)
│   │   └── reranker.py   # Cross-encoder reranking (NEW)
│   ├── security/         # Security module
│   │   └── acl.py        # Enhanced RBAC/ACL implementation (UPDATED)
│   └── utils/            # Utility functions
│       ├── hashing.py    # File hashing utilities
│       ├── logging.py    # Monitoring and logging (NEW)
│       └── validation.py # Input validation
├── static/               # Static web files
│   └── rag_kb_integration.html # Integration interface
├── tests/                # Test suite
│   ├── test_dummy.py     # Basic tests
│   ├── test_chunking.py  # Chunking tests
│   ├── test_ingest.py    # Ingestion tests
│   ├── test_lightrag.py   # LightRAG tests
│   ├── test_eval.py       # Evaluation tests
│   └── test_ragas_eval.py # RAGAS evaluation tests (NEW)
└── pyproject.toml       # Project configuration (UPDATED)
```

## Important Configuration Files

- `configs/config.yaml`: Main configuration (copy from config.example.yaml)
- `configs/performance.yaml`: Performance-optimized configuration (NEW)
- `pyproject.toml`: Python project dependencies and metadata (UPDATED)
- `requirements.txt`: Pip requirements (generated from pyproject.toml)

## Key Implementation Details

### Security Model (ENHANCED)
- **RBAC/ACL**: Role-based access control with department and level filtering
- **Pre-filtering**: ACL filters applied at query time in LightRAG (ENHANCED)
- **Post-filtering**: Additional filtering on search results
- **User Roles**: Support for department-based and level-based access control
- **ACL Context Manager**: Easy integration with security context (NEW)

### Retrieval Pipeline (ENHANCED)
1. **BM25 Search**: Sparse keyword-based retrieval (NEW)
2. **Vector Search**: LightRAG hybrid semantic search
3. **RRF Fusion**: Reciprocal Rank Fusion for combining results (NEW)
4. **Reranking**: Cross-encoder model for precision improvement (NEW)
5. **ACL Filtering**: Security-based result filtering (ENHANCED)

### Incremental Updates (ENHANCED)
- **File Hash Tracking**: SHA256-based change detection
- **Document Registry**: JSON-based version tracking (ENHANCED)
- **Smart Updates**: Only process changed/new documents (ENHANCED)
- **Cleanup**: Automatic removal of stale chunks (NEW)

### Knowledge Graph (NEW)
- **LightRAG Integration**: Automatic entity and relation extraction
- **NetworkX Processing**: Graph analysis and visualization
- **Caching**: Extracted graph data cached for performance
- **Statistics**: Node/edge counts, connectivity metrics (NEW)
- **Filtering**: Entity type and neighborhood queries (NEW)

### Performance Monitoring (NEW)
- **Structured Logging**: Console and file logging with different levels
- **Performance Tracking**: Operation timing and resource usage
- **System Metrics**: CPU, memory, disk usage monitoring
- **Slow Query Logging**: Automatic detection of slow operations
- **Metrics API**: `/metrics` endpoint for monitoring integration
- **Statistics**: Node/edge counts, connectivity metrics

## API Endpoints

### Core Endpoints
- `POST /api/v1/ingest` - Document ingestion (with performance monitoring)
- `POST /api/v1/search` - Knowledge base search (with ACL filtering)
- `POST /api/v1/chat/completions` - OpenAI-compatible chat (with streaming)
- `GET /health` - Health check with system metrics (ENHANCED)
- `GET /metrics` - Performance metrics and statistics (NEW)

### User Management
- `GET /api/v1/current-user` - Current user info
- `POST /api/v1/users/{user_id}/kbs` - Create knowledge base
- `GET /api/v1/users/{user_id}/kbs` - List knowledge bases
- `POST /api/v1/users/{user_id}/kbs/{kb_name}/upload` - Upload file
- `POST /api/v1/users/{user_id}/kbs/{kb_name}/ingest` - Ingest knowledge base
- `GET /api/v1/users/{user_id}/kbs/{kb_name}/graph` - Get knowledge graph (ENHANCED)
- `DELETE /api/v1/users/{user_id}/kbs/{kb_name}` - Delete knowledge base

### Integration
- `GET /openwebui-integration` - Open WebUI integration page
- `GET /rag-kb-integration` - RAG KB integration page

## Testing Strategy

### Test Categories (ENHANCED)
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Multi-component interaction testing
3. **RAGAS Evaluation**: Comprehensive RAG quality assessment (NEW)
4. **Performance Tests**: Load and stress testing (NEW)

### Key Test Files
- `tests/test_chunking.py` - Chunking strategy tests
- `tests/test_ingest.py` - Data ingestion pipeline tests
- `tests/test_lightrag.py` - LightRAG integration tests
- `tests/test_ragas_eval.py` - RAGAS evaluation framework tests (NEW)
- `tests/test_eval.py` - General evaluation tests

### Custom Test Scripts (NEW)
- `scripts/test_ingestion.py` - Document ingestion validation
- `scripts/test_hybrid_search.py` - Hybrid search functionality testing
- `scripts/test_graph_extraction.py` - Knowledge graph extraction testing

## Performance Benchmarks

### Test Environment
- CPU: 8 cores @ 3.0GHz
- RAM: 16GB
- Storage: NVMe SSD
- Documents: 1,000 PDF files (avg. 10 pages each)

### Performance Metrics (NEW)
| Operation | Time | Memory |
|-----------|------|--------|
| Single document ingestion | 2.3s | 150MB |
| BM25 index build (1K docs) | 45s | 800MB |
| BM25 search | 0.08s | 50MB |
| LightRAG ingestion (1K docs) | 180s | 1.2GB |
| Hybrid search | 1.2s | 200MB |
| Hybrid search with reranking | 3.5s | 350MB |

### Optimization Impact (NEW)
| Optimization | Speed Improvement | Memory Reduction |
|--------------|------------------|------------------|
| Disable reranking | 3x | 30% |
| Enable caching | 10x (repeated queries) | 0% |
| Reduce chunk size | 1.5x | 20% |

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions
- Keep functions focused and modular

### Adding New Features
1. Update relevant modules in `src/rag_kb/`
2. Add corresponding tests in `tests/`
3. Update configuration if needed
4. Update documentation (README.md, AGENTS.md)
5. Test thoroughly before committing

### Security Considerations
- Always validate user inputs
- Apply ACL filters at both query and result levels
- Never expose sensitive information in error messages
- Use environment variables for sensitive configuration

## Performance Optimization

### Memory Management
- Adjust `chunk_token_size` in config for large documents
- Use incremental updates to avoid full reindexing
- Enable LightRAG LLM cache for repeated queries

### Speed Optimization
- Disable reranking for faster initial results
- Use BM25-only mode for keyword-heavy queries
- Consider GPU acceleration for reranking if available

### Storage Optimization
- Clean up old document versions periodically
- Compress archived knowledge bases
- Use separate storage for different user groups

## Troubleshooting Common Issues

### Ollama Connection Issues
- Ensure Ollama service is running: `ollama serve`
- Check model availability: `ollama list`
- Verify model download: `ollama pull nomic-embed-text`

### Dependency Issues
- Ensure numpy version is >=2.0.0,<2.8.0 for scipy and lightrag compatibility
- Verify pydantic-core==2.46.4 for pydantic 2.13.4 compatibility
- Check cryptography==48.0.0 for open-webui compatibility
- Use lightrag-hku>=1.5.6 for correct LightRAG package

### Memory Issues
- Reduce `chunk_token_size` in configuration
- Process documents in smaller batches
- Increase system swap space if needed

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -e .[all]`
- Check Python version (3.11+ required)

## Deployment Notes

### Production Deployment
1. Use environment variables for sensitive configuration
2. Enable proper logging and monitoring
3. Set up regular backups of data directory
4. Configure proper CORS settings for production domains
5. Use production WSGI server (e.g., Gunicorn) instead of Uvicorn

### Windows-Specific Notes
- Use PowerShell scripts for full functionality
- Batch files available for basic operations
- Ensure execution policy allows script running
- Path separators should use backslashes for Windows paths

## Future Enhancement Areas

1. **Advanced Reranking**: Integration with more sophisticated reranking models
2. **Multi-modal Support**: Image and table processing capabilities
3. **Distributed Processing**: Support for multi-node deployment
4. **Advanced Analytics**: Usage analytics and query optimization
5. **Plugin System**: Extensible architecture for custom processors

## Documentation Resources

### User Documentation
- **README.md**: Comprehensive user guide and quick start
- **docs/PERFORMANCE_TUNING.md**: Performance optimization guide
- **docs/IMPLEMENTATION_SUMMARY.md**: Complete implementation summary

### Technical Documentation
- **AGENTS.md**: This file - developer and deployment information
- **HTML Documentation Files**: Original architecture and design documents
  - RAG_KB_Implementation_Framework.html
  - 万级长文档 RAG 知识库系统架构与前端设计指南.html
  - 海量长文档（万级）知识库构建方案.html
  - 海量长文档企业级 RAG 知识库落地指南.html

## Contact and Support

For issues related to this implementation:
- Check the GitHub Issues page
- Review the test files for usage examples
- Consult the inline code documentation
- Refer to the main README.md for user-facing documentation