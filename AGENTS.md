# RAG KB Project - Agent Information

## Project Overview

This is an enterprise-grade RAG (Retrieval-Augmented Generation) knowledge base system designed to handle 10,000+ long documents efficiently. The system integrates LightRAG for hybrid retrieval, BM25 for sparse search, Cross-Encoder reranking, comprehensive security, evaluation, and deployment capabilities.

## Latest Implementation Status (v0.6.0)

The system has been enhanced with comprehensive enterprise-grade RAG capabilities:

### ✅ Current Status
- **Stable Version**: v0.6.0 (recommended for use) - Enterprise RAG Optimization
- **Latest Enhancement**: Advanced retrieval system with BM25, BGE-Reranker, and RAGAS evaluation
- **Previous Version**: v0.5.55 (document processing pipeline)

### ✅ Completed Enhancements (v0.6.0 - Enterprise RAG Optimization)
- **Advanced Retrieval System**:
  - BM25 sparse search with complete index builder and persistence
  - BGE-Reranker integration using sentence-transformers (v5.5.1)
  - Weighted RRF fusion for optimal hybrid search (configurable BM25/vector weights)
  - Multi-path retrieval with parallel query execution and intelligent fusion
  - GPU acceleration support for embedding and reranking operations
  - Result caching with configurable TTL for performance optimization
- **Evaluation & Quality Framework**:
  - RAGAS evaluation framework (v0.4.3) with 15+ quality metrics
  - Performance tuning system with YAML-based configuration profiles
  - Quality monitoring with real-time thresholds and performance metrics
  - Automated regression testing framework with baseline comparison
  - Answer validation with strict citation rules and contradiction detection
- **Knowledge Graph Enhancement**:
  - Proper node naming with meaningful document titles instead of hash IDs
  - Content-based ID mapping between LightRAG and document registry
  - Enhanced interactive graph visualization with Cytoscape.js integration
  - Incremental graph updates without full rebuild for changed documents
  - Graph statistics with node/edge counts and connectivity metrics
- **Enterprise Features**:
  - Multi-knowledge base system with product isolation and unified management
  - Enhanced RBAC/ACL security with pre-filtering and post-filtering
  - Comprehensive monitoring system with structured logging and health checks
  - Maintenance tools for automated cleanup, reindexing, and recovery
  - Configuration management with YAML-based configs and history tracking
- **Document Processing Enhancements**:
  - OCR support for scanned PDF documents
  - Enhanced parsers (PDF, Markdown, DOCX) with structure detection
  - Structure-aware chunking with semantic and boundary detection strategies
  - Rich chunk metadata (source_file, page_num, section_title, chunk_type, offset, length)
  - Ingestion reconciliation with complete pipeline tracking and integrity checks
- **API Enhancements**:
  - 50+ new endpoints for advanced search, evaluation, and monitoring
  - Dual GET/POST support for browser compatibility
  - Enhanced API documentation with interactive examples
  - Comprehensive error handling with detailed recovery suggestions
  - Performance endpoints for monitoring integration
- **Technical Improvements**:
  - New modules: retrieval, evaluation, monitoring, graph_analysis, maintenance
  - Dependency updates: sentence-transformers v5.5.1, ragas v0.4.3, torch v2.13.0
  - Performance optimizations with GPU support and result caching
  - 30+ new test files with integration, performance, and regression tests
  - Enhanced error handling, logging, and validation across all modules

### ✅ Previous Enhancements (v0.5.55 - Document Processing Pipeline)
- **Complete Document Processing Pipeline**: Comprehensive parser registry with PDF, Markdown, and text support
- **Data Cleaning**: Enhanced text cleaning with PII masking and noise removal
- **Document Chunking**: Structure-aware chunking with configurable token size and overlap
- **Vectorization**: Ollama-based embedding with configurable timeout settings
- **Vector Database Storage**: LightRAG integration with nano-vector database
- **Processing Pipeline**: Created complete document processing pipeline module
- **Simple Processor**: Added simple processor bypassing LightRAG complexity
- **Configuration Optimization**: Increased embedding timeout to 20 minutes
- **Worker Management**: Reduced concurrent workers to 1 to avoid timeout
- **Chunk Size**: Reduced chunk size to 600 tokens for better performance

### ✅ Historical Enhancements (v0.4.0 - v0.5.54)
- **Document Parsing Enhancements**:
  - DOCX parser with python-docx integration
  - Enhanced PDF parser with structure detection (headings, lists, tables)
  - Enhanced Markdown parser with structure analysis
  - Updated parser registry with priority ordering
- **Advanced Chunking**:
  - Semantic chunker using sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
  - Structure-aware chunker respecting document boundaries
  - Enhanced Chunk model with source_file, page_num, section_title, chunk_type, offset, length
  - Fallback mechanisms for model unavailability
- **Ingestion Reconciliation**:
  - Complete pipeline tracking (upload → parsing → indexing)
  - Comprehensive reconciliation reports with integrity checks
  - Failure logging and retry mechanisms
  - New API endpoints: `/api/v1/ingestion/reconciliation`, `/api/v1/ingestion/document/{doc_id}`, `/api/v1/ingestion/retry/{doc_id}`, `/api/v1/ingestion/cleanup`
- **Testing Coverage**: 28+ new test cases across all enhanced modules

### 🔄 Multi-Step RAG Enhancements (v0.4.0)
- **Query Decomposition**: Intelligent reference resolution and sub-query generation
- **Multi-Step Retrieval**: Parallel query execution with deduplication and RRF fusion
- **Enhanced Answer Generation**: Strict citation rules and contradiction detection
- **Conversation History**: Context-aware reference resolution for follow-up questions
- **Fallback Mechanisms**: Graceful handling of insufficient information and system failures
- **Advanced API Endpoints**: New `/multi-step-search` and `/multi-step-debug` endpoints

### �📊 User Journey Analysis (v0.3.2)
- **Complete Workflow Analysis**: 7-step user journey from start to finish
- **Problem Identification**: Each step's current issues and impact
- **Improvement Roadmap**: Prioritized improvements (P0, P1, P2)
- **Usage Guidelines**: Recommended workflow for stable version

## Key Technical Stack

- **Python**: 3.11+ (required for modern dependencies)
- **Web Framework**: FastAPI with Uvicorn
- **RAG Engine**: LightRAG (lightrag-hku>=1.5.6), BM25 sparse search, Hybrid retrieval with RRF fusion
- **Reranking**: BGE-Reranker using sentence-transformers (v5.5.1) with GPU support
- **Local LLM**: Ollama with qwen3.5:4b model (or gemma4:e4b), Minimax API support
- **Embedding**: Ollama with nomic-embed-text or sentence-transformers with GPU acceleration
- **Evaluation**: RAGAS framework (v0.4.3) with 15+ quality metrics
- **Frontend**: Custom interfaces with Cytoscape.js for graph visualization, Open WebUI integration
- **Testing**: pytest with RAGAS evaluation framework, 30+ comprehensive test files
- **Graph Processing**: NetworkX for knowledge graph visualization and analysis
- **Monitoring**: psutil for system metrics, structured logging, performance tracking
- **Performance**: rank-bm25 for sparse search, weighted RRF fusion, result caching
- **Dependencies**: numpy>=2.0.0,<2.8.0, pydantic-core==2.46.4, cryptography==48.0.0, sentence-transformers>=5.5.1, ragas>=0.4.3, torch>=2.13.0
- **Visualization**: Cytoscape.js for interactive knowledge graph display
- **GPU Support**: CUDA acceleration for embedding and reranking operations

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
python scripts/test_multi_step_workflow.py  # NEW: Multi-step RAG workflow testing
python scripts/test_enhanced_parsers_real.py  # NEW: Enhanced parsers testing
python scripts/test_simple_enhanced.py  # NEW: Simple enhanced testing
python scripts/test_direct_enhanced.py  # NEW: Direct enhanced testing

# Run multi-step RAG specific tests
pytest tests/test_multi_step_rag.py -v  # NEW: Multi-step RAG integration tests

# Run evaluation set tests
pytest tests/test_eval_sets.py -v  # NEW: Evaluation set management tests
python scripts/run_regression_tests.py --mode full  # NEW: Full regression test suite
python scripts/run_regression_tests.py --mode quick  # NEW: Quick demonstration test
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
│   ├── bm25_cache/        # BM25 index cache
│   ├── eval_sets/         # Evaluation set storage (NEW)
│   ├── regression_results/ # Regression test results (NEW)
│   ├── execution_results/  # Execution results (NEW)
│   └── reports/           # Generated reports (NEW)
├── docs/                   # Documentation
│   └── PERFORMANCE_TUNING.md  # Performance optimization guide (NEW)
│   └── EVALUATION_SETS.md  # Evaluation sets documentation (NEW)
├── logs/                   # Log files (auto-created) (NEW)
├── scripts/               # Deployment scripts
│   ├── manage.ps1        # Unified management script (NEW)
│   ├── install.ps1       # Installation script
│   ├── upgrade.ps1       # Upgrade script
│   ├── import_local_folder.ps1 # Folder import (NEW)
│   ├── _start_internal.ps1 # Internal startup script (RENAMED)
│   ├── test_ingestion.py # Ingestion testing (NEW)
│   ├── run_regression_tests.py # Automated regression testing (NEW)
│   ├── test_hybrid_search.py # Search testing (NEW)
│   ├── test_graph_extraction.py # Graph testing (NEW)
│   ├── end_to_end_test.py # Complete business flow validation (NEW)
│   └── test_multi_step_workflow.py # Multi-step RAG workflow testing (NEW)
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
│   │   ├── docx_parser.py # DOCX parser with structure preservation (NEW)
│   │   ├── pdf_pdfplumber.py # Enhanced PDF parser (UPDATED)
│   │   └── markdown_parser.py # Enhanced Markdown parser (UPDATED)
│   ├── engines/          # RAG engines (NEW MODULE)
│   │   ├── rag_query_engine.py # Enterprise RAG query engine (NEW)
│   │   ├── enhanced_answer_generator.py # Enhanced answer generator with citations (NEW)
│   │   └── multi_step_rag_engine.py # Multi-step RAG engine (NEW)
│   ├── retrieval/        # Search engines (NEW MODULE)
│   │   ├── bm25_search.py # BM25 sparse search (NEW)
│   │   ├── hybrid_search.py # Hybrid search with RRF (NEW)
│   │   ├── reranker.py   # Cross-encoder reranking (NEW)
│   │   ├── query_decomposer.py # Query decomposition and reference resolution (NEW)
│   │   └── multi_step_retrieval.py # Multi-step retrieval with parallel execution (NEW)
│   ├── security/         # Security module
│   │   └── acl.py        # Enhanced RBAC/ACL implementation (UPDATED)
│   ├── evaluation/       # Evaluation and testing (NEW MODULE)
│   │   ├── eval_sets.py  # Evaluation set management (NEW)
│   │   ├── regression_tester.py # Regression testing framework (NEW)
│   │   ├── eval_runner.py # Execution and reporting (NEW)
│   │   ├── ragas_evaluator.py # RAGAS evaluation integration (NEW)
│   │   └── rag_judge.py  # Expert judge evaluation (NEW)
│   └── utils/            # Utility functions
│       ├── hashing.py    # File hashing utilities
│       ├── logging.py    # Monitoring and logging (NEW)
│       └── validation.py # Input validation
├── static/               # Static web files
│   └── rag_kb_integration.html # Integration interface
├── tests/                # Test suite
│   ├── test_dummy.py     # Basic tests
│   ├── test_eval_sets.py # Evaluation set management tests (NEW)
│   ├── test_chunking.py  # Chunking tests
│   ├── test_ingest.py    # Ingestion tests
│   ├── test_lightrag.py   # LightRAG tests
│   ├── test_eval.py       # Evaluation tests
│   ├── test_ragas_eval.py # RAGAS evaluation tests (NEW)
│   └── test_multi_step_rag.py # Multi-step RAG integration tests (NEW)
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

### Multi-Step RAG Implementation (NEW)
- **Three-Step Workflow**: Query decomposition → Parallel retrieval → Enhanced answer generation
- **Reference Resolution**: Context-aware resolution of pronouns and references in conversation
- **Query Decomposition**: Intelligent generation of 1-3 complementary sub-queries (core fact, synonym, context)
- **Parallel Retrieval**: Concurrent execution of multiple sub-queries with timeout handling
- **RRF Fusion**: Reciprocal Rank Fusion for combining results from different query paths
- **Deduplication**: Content-based deduplication across multiple retrieval results
- **Strict Citation Rules**: Answer generation with mandatory source citations
- **Contradiction Detection**: Automatic detection and handling of conflicting information
- **Fallback Mechanisms**: Graceful handling of insufficient information and system failures
- **Conversation History**: Session-based context management for follow-up questions

## API Endpoints

### Core Endpoints
- `POST /api/v1/ingest` - Document ingestion (with performance monitoring and reconciliation tracking)
- `POST /api/v1/import-folder` - Local folder batch import (NEW)
- `POST /api/v1/search` - Knowledge base search (with ACL filtering)
- `POST /api/v1/chat/completions` - OpenAI-compatible chat (with streaming)
- `POST /api/v1/multi-step-search` - Multi-step RAG search with query decomposition (NEW)
- `GET /api/v1/multi-step-debug` - Debug endpoint for multi-step workflow (NEW)
- `GET /health` - Health check with system metrics (ENHANCED)
- `GET /metrics` - Performance metrics and statistics (NEW)

### Ingestion Reconciliation Endpoints (NEW)
- `POST /api/v1/ingestion/reconciliation` - Get comprehensive reconciliation report
- `GET /api/v1/ingestion/document/{doc_id}` - Get specific document reconciliation status
- `POST /api/v1/ingestion/retry/{doc_id}` - Retry failed document ingestion
- `POST /api/v1/ingestion/cleanup` - Clean up old reconciliation records

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
5. **Multi-Step RAG Tests**: Three-step workflow validation (NEW)
6. **Enhanced Parser Tests**: Document parser functionality testing (NEW)
7. **Enhanced Chunking Tests**: Advanced chunking strategy testing (NEW)
8. **Ingestion Reconciliation Tests**: Pipeline tracking and validation (NEW)

### Key Test Files
- `tests/test_chunking.py` - Chunking strategy tests
- `tests/test_ingest.py` - Data ingestion pipeline tests
- `tests/test_lightrag.py` - LightRAG integration tests
- `tests/test_ragas_eval.py` - RAGAS evaluation framework tests (NEW)
- `tests/test_eval.py` - General evaluation tests
- `tests/test_multi_step_rag.py` - Multi-step RAG integration tests (NEW)
- `tests/test_enhanced_parsers.py` - Enhanced document parsers tests (NEW)
- `tests/test_enhanced_chunking.py` - Enhanced chunking strategies tests (NEW)
- `tests/test_ingestion_reconciler.py` - Ingestion reconciliation system tests (NEW)

### Custom Test Scripts (NEW)
- `scripts/test_ingestion.py` - Document ingestion validation
- `scripts/test_hybrid_search.py` - Hybrid search functionality testing
- `scripts/test_graph_extraction.py` - Knowledge graph extraction testing
- `scripts/test_enhanced_parsers_real.py` - Enhanced parsers real-world testing (NEW)
- `scripts/test_simple_enhanced.py` - Simple enhanced functionality testing (NEW)
- `scripts/test_direct_enhanced.py` - Direct component testing (NEW)

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

## Stage 1 Implementation Details (v0.4.0)

### Enhanced Document Parsing
- **DOCX Parser**: Supports .docx files with python-docx integration
  - Preserves document structure (headings, paragraphs, tables)
  - Extracts metadata (author, title, creation date)
  - Converts tables to markdown format
  - Maintains heading hierarchy
- **Enhanced PDF Parser**: Improved structure detection
  - Heading detection (all caps, numbered patterns, common words)
  - List item detection (bullet points, numbered lists, lettered lists)
  - Table extraction with markdown formatting
  - Page-level content organization
- **Enhanced Markdown Parser**: Structure analysis
  - Heading, list, table, code block detection
  - Metadata flags for structure presence
  - Preserves original markdown formatting

### Advanced Chunking Strategies
- **Semantic Chunker**: Intelligent text segmentation
  - Uses sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
  - Sentence boundary detection
  - Semantic similarity-based grouping
  - Overlap management for context continuity
  - Fallback to simple chunking when model unavailable
- **Structure-Aware Chunker**: Document boundary respect
  - Element type detection (heading, table, list, code, text)
  - Section path tracking
  - Page number extraction
  - Size constraint enforcement
  - Natural boundary preservation

### Enhanced Chunk Model
- **New Metadata Fields**:
  - `source_file`: Original source file name
  - `page_num`: Page number in source document
  - `section_title`: Title of containing section
  - `chunk_type`: Type (text, table, heading, list, code)
  - `offset`: Character offset in document
  - `length`: Chunk length in characters
  - `table_id`: Table identifier if applicable
  - `list_index`: List index if applicable

### Ingestion Reconciliation System
- **Pipeline Tracking**: Complete lifecycle monitoring
  - Upload stage: File hash calculation and registration
  - Parsing stage: Document processing status
  - Indexing stage: LightRAG integration status
  - Error tracking: Detailed failure logging
- **Reconciliation Reports**: Comprehensive validation
  - Summary statistics (uploaded, parsed, indexed, failed)
  - Integrity checks (upload=parsed+failed, parsed=indexed+failed)
  - Failed document analysis
  - Health status calculation
- **Retry Mechanisms**: Error recovery
  - Failed document retry functionality
  - Status reset for reprocessing
  - Retry count tracking
- **Cleanup Operations**: Maintenance
  - Old record cleanup based on age
  - Configurable retention periods
  - Safe deletion of completed documents

### Testing Enhancements
- **Enhanced Parser Tests**: 10 test cases
  - DOCX parser functionality
  - Enhanced PDF parser structure detection
  - Enhanced Markdown parser analysis
  - Parser registry validation
  - Integration testing
- **Enhanced Chunking Tests**: Comprehensive coverage
  - Semantic chunker with fallback
  - Structure-aware chunker functionality
  - Enhanced metadata validation
  - Chunk type detection
  - Size constraint testing
- **Ingestion Reconciliation Tests**: 18 test cases
  - Reconciler initialization
  - Upload/parsing/indexing recording
  - Reconciliation report generation
  - Document status queries
  - Retry functionality
  - Cleanup operations
  - Error recovery scenarios

## Future Enhancement Areas

### Stage 2 - Query Enhancement (Planned)
1. **Query Rewriting**: Context-aware query modification for better retrieval
2. **Reference Resolution**: Pronoun and reference resolution in multi-turn conversations
3. **Conversation History**: Session-based context management
4. **Query Decomposition**: Intelligent sub-query generation

### Stage 2 - Retrieval Enhancement (Planned)
1. **Folder/Type Filtering**: Enhanced filtering capabilities
2. **Advanced Reranking**: More sophisticated reranking models
3. **Hybrid Search Optimization**: Performance tuning for mixed retrieval

### Stage 2 - Answer Enhancement (Planned)
1. **Source Linking**: Precise answer-to-source mapping
2. **Position Tracking**: Character-level position information
3. **Citation Enhancement**: Improved citation accuracy and formatting

### Stage 3 - Advanced Features (Planned)
1. **OCR Support**: Scanned document processing
2. **Folder Monitoring**: Automatic reindexing on file changes
3. **Multi-modal Support**: Image and table processing
4. **Distributed Processing**: Multi-node deployment support

### Legacy Future Areas
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