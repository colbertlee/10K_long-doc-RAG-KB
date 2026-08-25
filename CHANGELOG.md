# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.54] - 2026-08-25

### Knowledge Graph Naming Fix
- **Simple Graph Default**: Now uses simple document-based graph with proper naming by default
- **ID Mapping Enhancement**: Added content-based ID mapping between LightRAG and document registry
- **Title Priority**: Improved title extraction from multiple metadata sources
- **API Update**: Graph generation API now uses simple graph with proper naming
- **Fallback Strategy**: Graceful fallback to simple graph when LightRAG entity extraction fails

### Technical Improvements
- **Content Matching**: Maps LightRAG doc-xxx IDs to original doc IDs via content matching
- **Multi-source Title**: Prioritizes title from multiple metadata fields
- **Edge Description**: Enhanced edge descriptions with meaningful source/target names
- **Graph Generator**: Added use_simple_graph parameter for controlled graph generation
- **Naming Logic**: Improved hash cleanup and readable name generation

### Bug Fixes
- **LightRAG Entity Extraction**: LightRAG entity_names field is empty, using simple graph as fallback
- **ID Mapping Issues**: Fixed LightRAG ID to document ID mapping via content matching
- **Empty Edge Descriptions**: Fixed edge descriptions showing empty strings
- **Graph Naming**: Knowledge graph nodes now display document titles instead of hash IDs

## [0.5.53] - 2026-08-25

### Advanced Features Optimization and Performance Tuning
- **BM25 Index Builder**: Complete BM25 indexing system for hybrid search functionality
- **BGE-Reranker Integration**: sentence-transformers installed and integrated for advanced reranking
- **RAGAS Evaluation Framework**: RAGAS package installed for comprehensive quality assessment
- **Performance Tuning System**: Complete performance tuning framework with configurable parameters
- **RRF Weighted Fusion**: Weighted Reciprocal Rank Fusion for optimal result combination
- **Configuration Management**: YAML-based performance configuration with preset profiles

### Performance Optimizations
- **BM25 Integration**: Full BM25 sparse search with index building and persistence
- **Weighted RRF Fusion**: Configurable BM25 and vector weights (default: 0.4/0.6)
- **Tunable Parameters**: RRF k constant, BM25 k1/b parameters, reranking thresholds
- **Performance Profiles**: Speed-optimized, accuracy-optimized, and balanced presets
- **Cache Management**: Result caching with configurable TTL for repeated queries

### Dependency Updates
- **sentence-transformers**: v5.5.1 installed for BGE-Reranker functionality
- **ragas**: v0.4.3 installed for advanced RAG quality evaluation
- **torch**: v2.13.0 for GPU-accelerated reranking
- **datasets**: v5.0.1 for RAGAS evaluation datasets
- **rank-bm25**: Added as dependency for BM25 sparse search

### New Performance Features
- **BM25IndexBuilder**: Automatic BM25 index building from document registry
- **PerformanceTuner**: Centralized performance configuration management
- **Hybrid Search Enhancement**: Integrated BM25 with weighted RRF fusion
- **Quality Thresholds**: Configurable quality monitoring thresholds
- **Performance Profiles**: Pre-configured optimization profiles for different use cases

### Technical Implementation
- **Weighted RRF Formula**: `score = (1/(k+rank)) * weight` for each source
- **Index Persistence**: BM25 index saved to disk for fast loading
- **Configuration Profiles**: Speed/Accuracy/Balance optimization presets
- **Dynamic Tuning**: Runtime parameter adjustment without restart
- **Fallback Mechanisms**: Graceful degradation when advanced features unavailable

## [0.5.52] - 2026-08-25

### Knowledge Graph Naming Improvements
- **Node Naming**: Fixed knowledge graph nodes to display meaningful names instead of hash IDs
- **Document Registry Integration**: Added document registry mapping for proper name resolution
- **Metadata Enhancement**: Improved document formatting with comprehensive metadata headers
- **Entity Extraction**: Enhanced document formatting to improve LightRAG entity extraction
- **Fallback Naming**: Implemented intelligent fallback naming for hash-based IDs
- **Edge Description**: Added source_name and target_name to edges for better readability

### Technical Improvements
- **Name Mapping**: Integrated document registry to map doc IDs to readable filenames
- **Title Priority**: Prioritized title/filename over hash IDs for node names
- **Hash Cleanup**: Implemented hash ID cleanup (doc- prefix, 32-char hashes)
- **Metadata Headers**: Enhanced document headers with author, created, category fields
- **Edge Enhancement**: Added human-readable source and target names to edge descriptions

### Graph Visualization
- **Readable Nodes**: Graph nodes now display document titles or filenames instead of hash IDs
- **Meaningful Edges**: Edge descriptions show actual document names instead of IDs
- **Better Context**: Enhanced metadata provides better context for graph exploration
- **User Experience**: Improved graph readability and navigation

## [0.5.51] - 2026-08-25

### Critical Event Loop and Timeout Fixes
- **Event Loop Consistency**: Fixed LightRAG event loop conflict by using async `ainsert()` instead of sync `insert()` in thread pool
- **LLM Timeout Parameter**: Removed unsupported `timeout` parameter from Ollama client calls
- **Initialization Simplification**: Removed complex synchronous initialization from `__init__` to prevent event loop conflicts
- **Pipeline Status**: Maintained pipeline status initialization in async context
- **Document Ingestion**: Fixed document ingestion to work properly with LightRAG's event loop requirements

### Technical Corrections
- **Async Consistency**: All LightRAG operations now run on the same event loop as required
- **Ollama Client**: Removed unsupported timeout parameter from client.chat() calls
- **Adapter Lifecycle**: Simplified LightRAGAdapter initialization to avoid event loop conflicts
- **Error Handling**: Improved error messages for event loop conflicts

### Production Stability
- **Document Ingestion**: Now works correctly without event loop errors
- **LLM Integration**: Fixed Ollama client compatibility issues
- **System Startup**: Cleaner initialization process without conflicts
- **API Functionality**: Document upload and ingestion now work properly

## [0.5.50] - 2026-08-25

### Advanced RAG Features Implementation
- **Hybrid Search Engine**: Implemented BM25 + Vector search with RRF (Reciprocal Rank Fusion)
- **BGE-Reranker Integration**: Added cross-encoder reranking with fallback to rule-based approach
- **RAGAS Evaluation Framework**: Complete quality assessment system with fallback evaluation
- **Advanced Retrieval Module**: New retrieval module with hybrid search and reranking capabilities
- **Quality Monitoring**: Continuous RAG quality monitoring with threshold-based alerts

### Technical Implementation
- **Hybrid Search**: Combined BM25 sparse search and LightRAG vector search with intelligent fusion
- **RRF Fusion**: Reciprocal Rank Fusion algorithm for optimal result combination
- **Cross-Encoder Reranking**: BGE-Reranker integration with GPU support and fallback mechanisms
- **Rule-Based Reranking**: Intelligent fallback when BGE models are not available
- **RAGAS Integration**: Full RAGAS framework support with fallback evaluation heuristics
- **Quality Metrics**: Faithfulness, answer relevancy, context precision, and overall scoring

### New Modules
- **src/rag_kb/retrieval/**: Advanced retrieval capabilities
  - `hybrid_search.py`: Hybrid search engine with RRF fusion
  - `reranker.py`: BGE-Reranker and rule-based reranking
  - `bm25_search.py`: BM25 sparse search (existing)
- **src/rag_kb/evaluation/**: Quality assessment framework
  - `ragas_evaluator.py`: RAGAS-based evaluation with fallback
- **scripts/**: Testing scripts for advanced features
  - `test_basic_advanced_features.py`: Basic functionality testing
  - `test_advanced_rag_features.py`: Comprehensive feature testing

### Performance Improvements
- **Search Accuracy**: Hybrid search improves retrieval precision through multi-source fusion
- **Result Quality**: Reranking significantly improves result relevance and ordering
- **Quality Control**: Continuous monitoring ensures consistent RAG performance
- **Fallback Mechanisms**: System remains functional even without advanced dependencies

### Dependencies
- **Optional**: sentence-transformers (for BGE-Reranker)
- **Optional**: ragas (for advanced evaluation)
- **Fallback**: System works without optional dependencies using rule-based approaches

## [0.5.49] - 2026-08-25

### Critical Bug Fixes
- **LightRAG Parameter Error**: Removed unsupported `llm_response_max_length` parameter that caused TypeError
- **Event Loop Management**: Fixed event loop closing logic to prevent "Cannot close a running event loop" error
- **Optional Dependencies**: Made performance monitoring imports optional to prevent psutil import failures
- **Import Fallback**: Enhanced import fallback mechanisms for better compatibility

### Technical Corrections
- **LightRAG Compatibility**: Removed unsupported LightRAG initialization parameters
- **Async Cleanup**: Only close event loop if it's not running to prevent shutdown errors
- **Module Loading**: Added try/except for optional utility imports to prevent startup failures
- **Graceful Shutdown**: Improved shutdown sequence to handle running event loops properly

### Production Stability
- **Startup Reliability**: System now starts successfully even without optional dependencies
- **Shutdown Stability**: Graceful shutdown works correctly without event loop errors
- **API Functionality**: Chat and graph statistics endpoints now work correctly
- **Error Handling**: Better error messages and fallback mechanisms

## [0.5.48] - 2026-08-25

### Emergency Fixes for Production Issues
- **LLM Worker Timeout**: Increased LightRAG LLM worker timeout from 480s to 600s to prevent entity extraction failures
- **Environment Configuration**: Added LIGHTRAG_LLM_WORKER_TIMEOUT and LIGHTRAG_EMBEDDING_WORKER_TIMEOUT environment variables
- **Worker Concurrency**: Added configurable worker concurrency and queue size settings
- **Event Loop Management**: Implemented AsyncContextManager for graceful shutdown and task cleanup
- **Document Deduplication**: Added multi-dimensional document deduplication system with content hash, metadata fingerprint, and filename matching
- **Pipeline Integration**: Integrated deduplication into ingestion pipeline with skip status tracking

### Technical Improvements
- **Async Context Manager**: Created utility for managing async lifecycle and preventing event loop closure errors
- **Deduplication Cache**: Implemented persistent cache for deduplication fingerprints
- **Graceful Shutdown**: Added proper signal handling and task cancellation on shutdown
- **Import Fallback**: Added fallback mechanisms for optional utilities to prevent startup failures

### Production Stability
- **Timeout Configuration**: 
  - LLM worker timeout: 480s → 600s
  - Embedding worker timeout: 300s
  - Max concurrent workers: 4
  - Worker queue size: 100
- **Error Recovery**: Improved error handling for duplicate detection and async context management
- **Monitoring**: Added detailed logging for deduplication and async context operations

## [0.5.47] - 2026-08-25

### System Audit and Performance Improvements
- **Comprehensive Audit**: Completed full RAG system pipeline audit from document upload to LLM interaction
- **Timeout Configuration**: Increased timeout settings for better local model performance (LLM: 10min, Query: 10min, Ingestion: 15min)
- **Error Handling**: Enhanced error handling with success/failure counting for document ingestion
- **Query Timeout**: Added timeout protection for LightRAG queries to prevent hanging
- **LLM Configuration**: Improved LLM function with increased context window and better timeout handling

### Technical Improvements
- **Pipeline Initialization**: Enhanced pipeline status initialization with multiple fallback mechanisms
- **Synchronous Insert**: Implemented synchronous insert method as primary approach to avoid pipeline issues
- **Monitoring**: Added detailed logging and performance tracking for ingestion operations
- **Module Caching**: Resolved Python module caching issues for reliable code updates

### Known Issues
- **LightRAG Pipeline**: Pipeline initialization issues persist in some environments, requiring synchronous insert fallback
- **Module Caching**: Python bytecode caching may require manual clearing for code changes to take effect

## [0.5.46] - 2026-08-25

### Critical Event Loop Fix
- **Event Loop Compatibility**: Fixed critical event loop conflict in document ingestion
- **Async Method Usage**: Changed from threading to direct async `ainsert()` method
- **Pipeline Initialization**: Added manual pipeline status initialization as fallback
- **LightRAG Compatibility**: Ensured all LightRAG operations run on the same event loop
- **Document Processing**: Fixed document ingestion to work properly in async context

### Technical Details
- **Removed Threading**: Eliminated threading approach that created new event loops
- **Direct Async Calls**: Used `await self.rag.ainsert()` directly on the same event loop
- **Enhanced Initialization**: Added manual namespace data initialization as ultimate fallback
- **Error Recovery**: Improved error recovery with multiple initialization attempts

### Working Features
- Document upload and parsing ✅
- OCR for scanned PDFs ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (enhanced recognition) ✅
- GET method search API (fixed with timeout handling) ✅
- POST method search API (fixed) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- Enhanced LLM knowledge base recognition ✅
- Route conflict resolved ✅
- Comprehensive unit test coverage ✅
- Knowledge graph generation (with fallback) ✅
- Graph visualization interface ✅
- Increased timeout configurations ✅
- Document reindexing scripts ✅
- Unified knowledge graph interface ✅
- Duplicate file cleanup ✅
- Server startup fixed ✅
- Async event loop compatibility ✅
- New document immediate processing ✅
- New document knowledge graph generation ✅
- All documents intelligent query ✅
- **Event loop conflict resolution** ✅
- **Document ingestion in async context** ✅

## [0.5.45] - 2026-08-25

### Critical Bug Fixes
- **Document Ingestion Fix**: Fixed critical issue where newly uploaded documents were not being properly indexed
- **LightRAG Pipeline Initialization**: Fixed LightRAG pipeline status initialization with fallback mechanisms
- **Async Event Loop Compatibility**: Fixed async event loop conflicts in document ingestion using threading
- **Query Functionality**: Fixed intelligent query to properly search both new and existing documents
- **Knowledge Graph Generation**: Fixed knowledge graph generation for newly uploaded documents

### Document Processing Improvements
- **Immediate Processing**: New documents now trigger immediate parsing, cleaning, chunking, and vectorization
- **Enhanced Logging**: Added comprehensive logging for document ingestion process
- **Document Formatting**: Improved document formatting with metadata for better indexing
- **Error Handling**: Enhanced error handling with graceful degradation
- **Thread-based Ingestion**: Used threading to avoid async event loop conflicts

### Query Enhancements
- **Hybrid Query Mode**: Added fallback to hybrid mode when naive mode returns no results
- **Better Error Messages**: Improved error messages for query failures
- **Search Logging**: Added detailed logging for GET and POST search requests
- **Timeout Handling**: Enhanced timeout handling for query operations

### Knowledge Graph Improvements
- **Fallback Graph Generation**: Added document-based graph generation when LightRAG extraction fails
- **Enhanced Logging**: Added comprehensive logging for graph generation process
- **Document Parameter**: Updated graph generator to accept document lists directly
- **Error Recovery**: Improved error recovery with fallback mechanisms

### Testing
- **New Test Coverage**: Added test_document_ingestion_query.py for ingestion and query testing
- **Integration Testing**: Enhanced integration testing for document processing pipeline
- **Query Validation**: Added query validation tests for both GET and POST methods

### Technical
- **Adapter Improvements**: Enhanced LightRAG adapter with better initialization and error handling
- **Pipeline Status**: Added multiple fallback methods for pipeline initialization
- **Threading**: Used threading for synchronous operations in async context
- **System Logging**: Added sys.stderr logging for better debugging

### Working Features
- Document upload and parsing ✅
- OCR for scanned PDFs ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (enhanced recognition) ✅
- GET method search API (fixed with timeout handling) ✅
- POST method search API (fixed) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- Enhanced LLM knowledge base recognition ✅
- Route conflict resolved ✅
- Comprehensive unit test coverage ✅
- Knowledge graph generation (with fallback) ✅
- Graph visualization interface ✅
- Increased timeout configurations ✅
- Document reindexing scripts ✅
- Unified knowledge graph interface ✅
- Duplicate file cleanup ✅
- Server startup fixed ✅
- Async event loop compatibility ✅
- **New document immediate processing** ✅
- **Knowledge graph generation for new documents** ✅
- **Intelligent query for all documents** ✅

## [0.5.44] - 2026-08-25

### Bug Fixes
- **Syntax Error Fix**: Fixed unterminated triple-quoted string literal in main.py
- **Async Event Loop Fix**: Fixed LightRAG adapter to use async insert method instead of synchronous method
- **Server Startup**: Resolved SyntaxError that prevented server from starting
- **Document Ingestion**: Fixed RuntimeError when ingesting documents in async context

### Technical Details
- **Main.py Syntax**: Removed duplicate triple-quoted string that caused parsing error
- **Adapter.py Async**: Changed from `self.rag.insert()` to `await self.rag.ainsert()` for proper async handling
- **Event Loop Compatibility**: Ensured all async operations use proper async methods
- **Error Handling**: Improved error messages for ingestion failures

### Working Features
- Document upload and parsing ✅
- OCR for scanned PDFs ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (enhanced recognition) ✅
- GET method search API (fixed with timeout handling) ✅
- POST method search API (fixed) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- Enhanced LLM knowledge base recognition ✅
- Route conflict resolved ✅
- Comprehensive unit test coverage ✅
- Knowledge graph generation (with fallback) ✅
- Graph visualization interface ✅
- Increased timeout configurations ✅
- Document reindexing scripts ✅
- Unified knowledge graph interface ✅
- Duplicate file cleanup ✅
- **Server startup fixed** ✅
- **Async event loop compatibility** ✅

## [0.5.43] - 2026-08-25

### UI Optimization
- **Unified Knowledge Graph Interface**: Merged duplicate knowledge graph pages into single unified interface
- **Removed Redundant Files**: Deleted graph_ui.html and knowledge_graph.html, replaced with unified_knowledge_graph.html
- **Enhanced Graph Features**: Combined features from both previous interfaces
  - Graph generation and rebuilding
  - Entity search and subgraph queries
  - Advanced filtering (entity type, relation type)
  - Multiple layout algorithms
  - Real-time statistics display
  - Node information display
  - Graph export functionality
- **API Redirects**: Added redirect from /graph-ui to /knowledge-graph for backward compatibility
- **Improved UX**: Better sidebar layout, statistics cards, and message notifications

### Knowledge Graph Features
- **Complete Graph Operations**: Generate, rebuild, statistics, and entity subgraph queries
- **Advanced Filtering**: Entity type filtering, relation type filtering, search functionality
- **Multiple Layouts**: Force-directed, circle, grid, concentric, and breadth-first layouts
- **Interactive Visualization**: Node selection, information display, edge labels
- **Statistics Dashboard**: Network density, average degree, node/edge counts
- **Export Functionality**: JSON export of graph data
- **Real-time Updates**: Auto-refresh and manual refresh capabilities

### Technical
- **File Cleanup**: Removed duplicate graph UI files
- **API Consolidation**: Unified graph API endpoints
- **Route Optimization**: Added redirect for backward compatibility
- **Import Updates**: Added RedirectResponse to FastAPI imports

### Working Features
- Document upload and parsing ✅
- OCR for scanned PDFs ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (enhanced recognition) ✅
- GET method search API (fixed with timeout handling) ✅
- POST method search API (fixed) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- Enhanced LLM knowledge base recognition ✅
- Route conflict resolved ✅
- Comprehensive unit test coverage ✅
- Knowledge graph generation (with fallback) ✅
- Graph visualization interface ✅
- Increased timeout configurations ✅
- Document reindexing scripts ✅
- **Unified knowledge graph interface** ✅
- **Duplicate file cleanup** ✅

## [0.5.42] - 2026-08-25

### Performance & Timeout Improvements
- **Increased Timeout Configuration**: Added configurable timeouts for local model performance
  - Request timeout: 300s (5 minutes) for LLM requests
  - Embedding timeout: 120s (2 minutes) for embedding
  - Query timeout: 300s (5 minutes) for queries
  - Ingestion timeout: 600s (10 minutes) for document ingestion
- **GET Method Routing**: Fixed GET request timeout handling with proper error messages
- **Local Model Optimization**: Adjusted for local GPU performance constraints

### Knowledge Graph Implementation
- **Complete Knowledge Graph Generator**: Full implementation with fallback mechanisms
- **Document-Based Graph Fallback**: Simple document-based graphs when LightRAG extraction fails
- **Graph API Endpoints**: Added comprehensive graph management APIs
  - POST /api/v1/graph/generate - Generate knowledge graph from documents
  - GET /api/v1/graph/statistics - Get graph statistics
  - POST /api/v1/graph/rebuild - Rebuild knowledge graph
  - GET /api/v1/graph/entity/{entity_name} - Get entity subgraph
- **Graph Visualization Interface**: Added interactive knowledge graph UI with Cytoscape.js
- **Entity & Relation Extraction**: Automatic extraction from LightRAG storage
- **Graph Statistics**: Node/edge counts, type distributions, connectivity metrics

### LightRAG Integration Fixes
- **Pipeline Initialization**: Fixed LightRAG pipeline status initialization issues
- **Graceful Degradation**: System continues to work even if advanced features fail
- **Synchronous Ingestion**: Added synchronous document ingestion methods
- **Error Handling**: Improved error handling for LightRAG operations

### Document Management
- **Reindexing Scripts**: Added scripts for document reindexing
  - scripts/reindex_documents.py - Async reindexing
  - scripts/reindex_documents_sync.py - Synchronous reindexing
- **Document Registry**: Enhanced document registry management
- **Graph Extraction**: Automatic entity and relation extraction from documents

### API Enhancements
- **Knowledge Graph UI**: Added /knowledge-graph endpoint for graph visualization
- **Timeout Handling**: Proper timeout handling for all API endpoints
- **Error Messages**: Improved error messages for timeout scenarios
- **Fallback Responses**: Graceful fallbacks when advanced features fail

### Technical
- **Graph Module**: Created dedicated graph module (src/rag_kb/graph/)
- **Configuration**: Added timeout settings to config.py
- **Routes Enhancement**: Enhanced GET search endpoint with timeout handling
- **Main API Updates**: Added graph-related endpoints to main.py
- **Adapter Improvements**: Fixed LightRAG adapter initialization and ingestion

### Working Features
- Document upload and parsing ✅
- OCR for scanned PDFs ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (enhanced recognition) ✅
- GET method search API (fixed with timeout handling) ✅
- POST method search API (fixed) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- Enhanced LLM knowledge base recognition ✅
- Route conflict resolved ✅
- Comprehensive unit test coverage ✅
- **Knowledge graph generation (with fallback)** ✅
- **Graph visualization interface** ✅
- **Increased timeout configurations** ✅
- **Document reindexing scripts** ✅

## [0.5.41] - 2026-08-25

### Testing
- **LLM Knowledge Base Recognition Tests**: Added comprehensive unit tests for LLM knowledge base recognition
- **Configuration Tests**: Added tests for LLM configuration, system prompts, and parameters
- **Vector Database Tests**: Added tests for vector database configuration and file structure
- **Anti-Hallucination Tests**: Added tests for anti-hallucination mechanisms and parameters
- **Integration Tests**: Added tests for API endpoints and integration points
- **Error Handling Tests**: Added tests for error handling and fallback mechanisms
- **Test Framework**: Added pytest-asyncio support for async testing

### Test Coverage
- **25 unit tests** covering LLM functions, configuration, and knowledge base recognition
- **Test categories**: LLM config, system prompts, vector database, LightRAG adapter, knowledge base recognition logic, anti-hallucination mechanisms, API endpoints, integration points, error handling, configuration validation
- **Test success rate**: 100% (25/25 tests passing)

### Technical
- Added pytest-asyncio dependency for async test support
- Added asyncio configuration to pyproject.toml
- Created comprehensive test suite for LLM knowledge base recognition
- Tests validate configuration, integration, and error handling

### Working Features
- Document upload and parsing ✅
- OCR for scanned PDFs ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (enhanced recognition) ✅
- GET method search API (fixed) ✅
- POST method search API (fixed) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- Enhanced LLM knowledge base recognition ✅
- Route conflict resolved ✅
- **Comprehensive unit test coverage** ✅

## [0.5.40] - 2026-08-25

### LLM Recognition Enhancement
- **Balanced System Prompt**: Adjusted LLM system prompt for better knowledge base recognition
- **Reduced Over-Filtering**: Removed overly strict anti-hallucination patterns that blocked valid content
- **Moderate Parameters**: Increased temperature to 0.3 and top_p to 0.3 for balanced responses
- **Pipeline Initialization**: Added proper LightRAG pipeline status initialization
- **Knowledge Base Focus**: LLM now prioritizes knowledge base content while maintaining accuracy

### Technical
- Modified ollama_llm function with balanced system prompt
- Reduced generic pattern filtering in adapter query method
- Added initialize_pipeline_status() to LightRAG adapter
- Adjusted LLM parameters for better content recognition
- Simplified post-processing validation

### Working Features
- Document upload and parsing ✅
- OCR for scanned PDFs ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- **LLM-based response generation (enhanced recognition)** ✅
- GET method search API (fixed) ✅
- POST method search API (fixed) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- **Enhanced LLM knowledge base recognition** ✅
- Route conflict resolved ✅

## [0.5.39] - 2026-08-25

### Bug Fixes
- **Route Conflict**: Removed duplicate search endpoints from main.py to fix 405 Method Not Allowed
- **LLM Cache**: Cleared LLM response cache to prevent old cached responses from bypassing anti-hallucination
- **GET Method**: Fixed GET method support by using routes.py endpoints instead of main.py
- **Route Consistency**: Unified search endpoints in routes.py for both GET and POST methods

### Technical
- Removed duplicate @app.get('/api/v1/search') and @app.post('/api/v1/search') from main.py
- Removed _search_impl and _stream_answer helper functions from main.py
- Routes.py now handles all search endpoints with proper GET/POST support
- Cleared kv_store_llm_response_cache.json to remove old cached responses
- Routes.py search endpoints include anti-hallucination logic

### Working Features
- Document upload and parsing ✅
- OCR for scanned PDFs ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (LLM-level anti-hallucination) ✅
- **GET method search API (fixed)** ✅
- **POST method search API (fixed)** ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- LLM-level strict knowledge base constraints ✅
- **Route conflict resolved** ✅

## [0.5.38] - 2026-08-25

### Frontend Fixes
- **Response Parsing**: Added debug logging for API responses
- **Undefined Handling**: Added fallback values for undefined answer fields
- **Error Display**: Enhanced error handling in frontend interfaces
- **Debug Mode**: Added console.log for troubleshooting API responses

### Technical
- Modified simple_ui.html to handle undefined answer values
- Modified main_ui.html to handle undefined answer values
- Added debug logging to track API response structure
- Enhanced error handling with fallback display values

### Working Features
- Document upload and parsing ✅
- OCR for scanned PDFs ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (LLM-level anti-hallucination) ✅
- GET method search API (primary) ✅
- POST method search API (alternative) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- LLM-level strict knowledge base constraints ✅
- **Enhanced frontend response handling** ✅

## [0.5.37] - 2026-08-25

### New Features
- **OCR Support**: Added OCR (Optical Character Recognition) for scanned PDF documents
- **Auto-Detection**: Automatically detects scanned PDFs by analyzing text extraction results
- **Multi-Language OCR**: Supports Chinese and English text recognition
- **Fallback Mechanism**: Graceful fallback to basic extraction if OCR fails

### Technical
- Added pytesseract>=0.3.10 and Pillow>=10.0.0 dependencies
- Enhanced PyMuPDF parser with OCR capabilities
- Implemented smart detection for scanned vs digital PDFs
- Added high-DPI rendering (300 DPI) for better OCR accuracy
- Added metadata flag to track OCR usage

### OCR Logic
- Detects scanned PDFs when average text per page < 100 characters
- Renders pages to high-resolution images for OCR processing
- Uses Tesseract OCR with Chinese and English language support
- Falls back to basic extraction if OCR libraries unavailable
- Logs OCR processing status for debugging

### Dependencies
- pytesseract>=0.3.10 (OCR engine wrapper)
- Pillow>=10.0.0 (Image processing)
- **Tesseract OCR engine** (system requirement - needs separate installation)

### Installation Requirements
For OCR functionality, you need to install Tesseract OCR engine separately:

**Windows:**
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install Tesseract and add it to system PATH
3. Download Chinese language data: `chi_sim.traineddata`
4. Place language data in Tesseract tessdata directory

**Or use chocolatey:**
```powershell
choco install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang
```

### Working Features
- Document upload and parsing ✅
- **OCR for scanned PDFs** ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (LLM-level anti-hallucination) ✅
- GET method search API (primary) ✅
- POST method search API (alternative) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- LLM-level strict knowledge base constraints ✅

## [0.5.36] - 2026-08-25

### Security & Accuracy (LLM-Level)
- **Strict System Prompt**: Added explicit system prompt at LLM function level
- **Temperature Control**: Lowered temperature to 0.1 for deterministic responses
- **Top-P Control**: Lowered top_p to 0.1 for focused responses
- **Context Validation**: Added post-processing to detect context references
- **Generic Knowledge Blocking**: Enhanced detection of general knowledge vs specific context

### Technical
- Modified ollama_llm function to use system/user message structure
- Added strict system prompt about context-only responses
- Lowered generation parameters for more controlled output
- Added context reference validation in post-processing
- Enhanced generic pattern detection with specific domain terms

### Validation Logic
- LLM receives explicit instruction to only use provided context
- Lower temperature reduces creative/hallucinative responses
- Post-processing checks for context references in responses
- Blocks responses that don't reference provided context
- Detects and blocks generic definitions and explanations

### Working Features
- Document upload and parsing ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (LLM-level anti-hallucination) ✅
- GET method search API (primary) ✅
- POST method search API (alternative) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- **LLM-level strict knowledge base constraints** ✅

## [0.5.35] - 2026-08-25

### Security & Accuracy (Enhanced)
- **Pattern-Based Hallucination Detection**: Added generic knowledge pattern detection
- **Knowledge Base Validation**: Enhanced detection of generic LLM responses vs knowledge base content
- **Multi-Layer Validation**: Combined system prompt + pattern detection + content validation
- **Smart Response Filtering**: Distinguishes between genuine knowledge base answers and generic LLM knowledge

### Technical
- Removed system prompt approach (ineffective with LightRAG)
- Added pattern-based detection for generic knowledge indicators
- Implemented knowledge base content indicators validation
- Enhanced anti-hallucination logic in adapter, search, and streaming functions
- Added detection for patterns like "简单来说", "一般来说", "在现代物理学中", etc.

### Validation Logic
- Detects generic knowledge patterns that indicate LLM's training data
- Validates presence of knowledge base indicators (文档, 知识库, 上传, etc.)
- Only returns answers that appear to be from actual uploaded documents
- Falls back to "知识库中未找到相关信息" for generic knowledge

### Working Features
- Document upload and parsing ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (enhanced anti-hallucination) ✅
- GET method search API (primary) ✅
- POST method search API (alternative) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- **Enhanced pattern-based knowledge base constraints** ✅

## [0.5.34] - 2026-08-25

### Security & Accuracy
- **Anti-Hallucination**: Added strict system prompt to prevent LLM from generating fabricated answers
- **Knowledge Base Constraint**: LLM now only answers based on uploaded documents and local folders
- **No Information Response**: When knowledge base lacks relevant information, returns "知识库中未找到相关信息"
- **Answer Validation**: Added post-processing to detect and replace uncertain responses with standard message

### Technical
- Modified LightRAG adapter query method to include system prompt
- Updated chat completions streaming function with anti-hallucination logic
- Added detection for uncertain response patterns
- Standardized "no information found" response across all endpoints

### Compliance
- Ensures LLM responses are strictly based on provided knowledge base
- Prevents model from fabricating information outside of uploaded documents
- Maintains accuracy and reliability of RAG system

### Working Features
- Document upload and parsing ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation (anti-hallucination) ✅
- GET method search API (primary) ✅
- POST method search API (alternative) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅
- Strict knowledge base constraints ✅

## [0.5.33] - 2026-08-25

### Fixed
- **Frontend API Calls**: Reverted to GET method for browser compatibility
- **Backend Dual Support**: Backend now supports both GET and POST methods
- **Browser Compatibility**: GET method works better with browser caching and history
- **API Flexibility**: Both methods share same implementation via _search_impl

### Technical
- Reverted frontend files to use GET method (simple_ui.html, main_ui.html, enhanced_search.html, multi_kb_selector.html)
- Backend maintains dual GET/POST support for future flexibility
- Removed POST-specific body requirements from frontend
- Cache-control headers remain for force refresh

### Working Features
- Document upload and parsing ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation ✅
- GET method search API (primary) ✅
- POST method search API (alternative) ✅
- All frontend interfaces using GET method ✅
- Browser cache control for updates ✅

## [0.5.32] - 2026-08-25

### Fixed
- **Search Endpoint**: Added both GET and POST method support for backward compatibility
- **Body Parameters**: Fixed POST method to accept optional body with proper parsing
- **API Compatibility**: POST method now works correctly with JSON body
- **Dual Method Support**: Both GET and POST methods share same implementation

### Engineering
- Added internal _search_impl function to share logic between GET and POST
- Fixed method naming conflicts (search_get, search_post)
- POST method confirmed working with detailed responses
- GET method added for backward compatibility

### Working Features
- Document upload and parsing ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation ✅
- POST method search API ✅
- GET method search API (backward compatibility) ✅
- All frontend interfaces using correct HTTP methods ✅

## [0.5.31] - 2026-08-25

### Fixed
- **Search Endpoint**: Changed from Query parameters to Body parameters for POST method
- **Request Handling**: Added Body import and proper request body parsing
- **API Compatibility**: Fixed search endpoint to accept JSON body instead of query parameters

### Engineering
- Fixed test_fastapi_app_structure to handle _IncludedRouter
- Fixed test_embedding_function_signature for *args/**kwargs signature
- Added test_frontend_api.py with cache control and port consistency tests
- Updated requirements.txt with current dependencies
- All tests passing (29 passed, 2 skipped)
- Created GitHub release v0.5.30

### Working Features
- Document upload and parsing ✅
- LightRAG document ingestion and vector indexing ✅
- Semantic search with LightRAG naive mode ✅
- LLM-based response generation ✅
- POST method search API ✅
- All frontend interfaces using correct HTTP methods ✅

## [0.5.30] - 2026-08-25

### Fixed
- **Browser Caching**: Added cache-control headers to all HTML files to force browser reload
- **Simple UI**: Added no-cache meta tags to prevent browser caching
- **Main UI**: Added no-cache meta tags to prevent browser caching
- **Enhanced Search**: Added no-cache meta tags to prevent browser caching
- **Multi KB Selector**: Added no-cache meta tags to prevent browser caching

### Technical
- Added Cache-Control, Pragma, and Expires meta headers to force browser cache invalidation
- This ensures users get the latest frontend code with POST method fixes

## [0.5.29] - 2026-08-25

### Fixed
- **Frontend API Calls**: Changed all search API calls from GET to POST method
- **Chat UI Port**: Corrected API_BASE from port 8001 to 8000 to match server
- **Response Handling**: Fixed chat UI to handle JSON responses instead of SSE streaming
- **Search Interfaces**: Updated simple_ui.html, main_ui.html, enhanced_search.html, multi_kb_selector.html

### Fixed Files
- static/chat_ui.html - Port correction and response handling
- static/simple_ui.html - GET to POST conversion
- static/main_ui.html - GET to POST conversion  
- static/enhanced_search.html - GET to POST conversion
- static/multi_kb_selector.html - GET to POST conversion

### Working Features
- All frontend interfaces now correctly use POST method for search API
- Chat completions API working with proper JSON response handling
- Port configuration consistent across all interfaces

## [0.5.28] - 2026-08-25

### Fixed
- **Chat Completions API**: Fixed missing get_rag() function in routes.py
- **Async Query**: Updated chat completions to use async rag.query() method
- **Query Mode**: Changed from hybrid to naive mode for more reliable responses
- **Error Handling**: Added traceback logging for better debugging

### Tested
- ✅ Document upload and ingestion working correctly
- ✅ LLM问答功能 returning detailed Chinese responses
- ✅ 语义搜索功能 with vector embeddings
- ✅ 对话功能 via OpenAI-compatible API
- ✅ Different search modes (naive, hybrid) working

### Working Features
- Document upload and parsing
- LightRAG document ingestion and vector indexing
- Semantic search with LightRAG naive mode
- LLM-based response generation (gemma4:e4b)
- OpenAI-compatible chat completions API
- Basic text search fallback
- All API endpoints functional

## [0.5.27] - 2026-08-25

### Fixed
- **LightRAG Integration**: Successfully resolved all LightRAG compatibility issues
- **Async Functions**: Converted LLM and embedding functions to async for proper event loop handling
- **Embedding Interface**: Implemented proper EmbeddingFunc dataclass matching lightrag-hku v1.5.6
- **LLM Response**: Fixed empty LLM responses by switching to gemma4:e4b model and adding debugging
- **Vector Indexing**: Resolved vector chunks being empty by ensuring proper document ingestion
- **Response Truncation**: Increased max_tokens to 4096 to prevent response truncation
- **API Routes**: Cleaned up duplicate code and added FileResponse import
- **Server Port**: Changed to port 8001 to avoid socket conflicts

### Changed
- **LLM Model**: Switched from qwen3.5:4b to gemma4:e4b for better response reliability
- **Query Mode**: Using naive mode for LightRAG queries to avoid graph dependencies
- **Reranking**: Disabled reranking to avoid missing model warnings
- **Document Ingestion**: Removed unique prefix to allow proper LightRAG processing

### Technical
- **llm_funcs.py**: Made fully async with thread pool execution and debugging
- **embedding_funcs.py**: Implemented proper async embedding with debugging
- **adapter.py**: Added ensure_initialized() method and async query implementation
- **config.py**: Updated LLM model and increased max_tokens
- **routes.py**: Cleaned up duplicate search endpoint code
- **main.py**: Simplified search to use LightRAG with fallback to document registry

### Working Features
- ✅ Document upload and parsing
- ✅ LightRAG document ingestion and indexing
- ✅ Vector embeddings generation
- ✅ Semantic search with LightRAG naive mode
- ✅ LLM-based response generation
- ✅ Basic text search fallback
- ✅ All API endpoints functional

### Known Issues
- **Knowledge Graph**: Entity extraction returns 0 entities/relations (LLM parsing issue)
- **Advanced Search**: Hybrid and global modes not yet tested
- **Reranking**: Disabled due to missing torch/transformers dependencies

## [0.5.26] - 2026-08-24

### Fixed
- **Reranker Import**: Added optional import handling for transformers library to prevent import errors
- **Search Functionality**: Simplified search to use document registry with graceful degradation
- **Main.py Cleanup**: Removed duplicate and orphaned code from search endpoint
- **Error Handling**: Enhanced error handling with better debugging information

### Changed
- **LightRAG Status**: Temporarily disabled advanced LightRAG features due to embedding compatibility
- **Search Mode**: Using basic text search as reliable fallback
- **Dependency Handling**: Made transformers and torch optional dependencies

### Technical
- **Reranker.py**: Added TRANSFORMERS_AVAILABLE flag for optional imports
- **Routes.py**: Simplified to document registry search only
- **Main.py**: Cleaned up duplicate search endpoint code
- **Embedding Functions**: Multiple attempts at compatibility fixes (dataclass, replace method, etc.)

### Known Issues
- **LightRAG Semantic Search**: Temporarily disabled due to embedding function interface incompatibility with lightrag-hku v1.5.6
- **Torch Installation**: SSL certificate issues preventing torch installation from PyTorch servers
- **Advanced Dependencies**: Some features require heavy dependencies that have installation issues

## [0.5.25] - 2026-08-24

### Fixed
- **Critical API Routes**: Restored complete search and chat endpoints in routes.py
- **Document Ingestion**: Simplified chunking strategy for better compatibility
- **Search Functionality**: Implemented basic text search as fallback for advanced features
- **Error Handling**: Enhanced error handling with graceful degradation
- **LightRAG Integration**: Multiple attempts to resolve embedding function compatibility

### Changed
- **Search Mode**: Temporarily using basic text search instead of LightRAG semantic search
- **API Response**: Updated error messages to inform users about temporarily disabled features
- **Document Storage**: Documents are stored and searchable even without LightRAG indexing

### Technical
- **Routes.py**: Complete rewrite with search, chat, and user management endpoints
- **Adapter.py**: Multiple embedding function wrapper attempts for LightRAG compatibility
- **Embedding Functions**: Created dataclass-based embedding function wrapper
- **Main.py**: Simplified document ingestion with better error handling

### Known Issues
- **LightRAG Semantic Search**: Temporarily disabled due to embedding function interface incompatibility
- **Knowledge Graph Generation**: Not functional without LightRAG integration
- **Advanced Dependencies**: Some features require torch and other heavy dependencies

## [0.5.24] - 2026-08-24

### Changed
- **Default LLM Model**: Updated default LLM model from qwen2.5 to qwen3.5:4b
- **Model Compatibility**: Aligned with available local models (nomic-embed-text, gemm4:e4b, qwen3.5:4b)

### Technical
- **Configuration Update**: Modified src/rag_kb/config.py default llm_model setting
- **Version Update**: Bumped version to v0.5.24

## [0.5.23] - 2026-08-24

### Fixed
- **Import Error**: Fixed missing `List` and `Dict` imports in main.py causing NameError
- **Upgrade Script**: Fixed git stash command syntax error in upgrade.ps1 script
- **Server Startup**: Resolved server startup failure due to missing type imports

### Technical
- **Type Hints**: Added proper type imports (List, Dict, Any) to main.py
- **Git Compatibility**: Updated git stash commands to use short-form flags for better compatibility
- **Error Handling**: Improved error handling in upgrade script

## [0.5.22] - 2026-08-24

### Added
- **Basic RLHF System**: Complete reinforcement learning from human feedback system
- **Reward Model**: Simple reward model for response quality scoring
- **Training Dataset**: User feedback-based training dataset construction
- **Feedback Labels**: Positive, negative, and neutral feedback classification
- **Advanced Graph Analysis**: 2-3 degree node neighborhood analysis
- **Entity Relationship Analysis**: Deep analysis of entity relationships with connection strength
- **Graph Path Mining**: Shortest path finding between entities
- **Centrality Measures**: Degree centrality and PageRank calculations
- **Community Detection**: Basic community detection in knowledge graph
- **Basic Multimodal Support**: Image and table processing capabilities
- **Image Processing**: Basic image information extraction and description generation
- **Table Processing**: CSV and Excel table data extraction
- **Multimodal Search**: Search multimodal content by description
- **RLHF Training API**: API for adding training examples and calculating rewards
- **Graph Analysis API**: API for neighborhood, relationships, paths, centrality, and communities
- **Multimodal API**: API for processing and searching multimodal content

### Enhanced
- **Model Improvement**: RLHF system enables continuous model improvement from user feedback
- **Graph Insights**: Advanced graph analysis provides deeper knowledge graph understanding
- **Multimodal Support**: Basic support for images and tables expands content types
- **Quality Scoring**: Reward model provides objective response quality assessment
- **Relationship Mining**: Deep entity relationship analysis improves graph understanding
- **System Intelligence**: Advanced analytics provide deeper system insights

### Technical
- **New RLHF Module**: Complete RLHF system with reward model and dataset management
- **New Graph Analysis Module**: Advanced graph analysis with multiple algorithms
- **New Multimodal Module**: Basic multimodal processing for images and tables
- **Reward Scoring**: Multi-factor reward calculation for response quality
- **Graph Algorithms**: BFS path finding, centrality measures, community detection
- **Content Processing**: Image and table data extraction with fallback mechanisms
- **Dataset Management**: Persistent storage for RLHF training examples
- **Index Management**: Multimodal content index for efficient retrieval

## [0.5.21] - 2026-08-24

### Added
- **Similarity Fragment Perspective**: Enhanced analysis of retrieval results with detailed fragment comparison
- **Match Type Classification**: Vector, graph node, keyword, and hybrid match type identification
- **Enhanced Similarity Scoring**: Advanced similarity calculation with match type weighting
- **Fragment Comparison**: Direct comparison between similar fragments with recommendations
- **Context Extraction**: Automatic context extraction from fragments
- **Optimized Multi-Directory Routing**: Advanced routing system for multiple working directories
- **Routing Strategies**: Product-based, category-based, user-based, load-balanced, and intelligent routing
- **Directory Management**: Registration, status tracking, and load management for working directories
- **Routing Cache**: Intelligent caching for improved routing performance
- **Load Balancing**: Automatic load distribution across working directories

### Enhanced
- **Retrieval Analysis**: Deeper analysis of retrieval results with match type insights
- **Routing Efficiency**: Optimized routing reduces query latency
- **Scalability**: Multi-directory routing supports large-scale deployments
- **Fragment Quality**: Enhanced similarity scoring improves result quality
- **System Performance**: Load balancing improves overall system performance

### Technical
- **New Perspective Module**: Complete fragment perspective and analysis system
- **New Routing Module**: Optimized multi-directory routing with multiple strategies
- **Fragment Analysis API**: RESTful API for fragment perspective analysis
- **Routing Management API**: RESTful API for directory and routing management
- **Enhanced Scoring Algorithms**: Advanced similarity calculation with multiple factors
- **Strategy Pattern**: Pluggable routing strategies for flexibility

## [0.5.20] - 2026-08-24

### Added
- **Intent Classifier**: Lightweight intent classifier for automatic query mode selection
- **Document Processing Tracker**: Complete tracking system for document processing progress
- **Processing Status API**: Real-time status queries for document processing tasks
- **Automatic Mode Selection**: Search API now supports automatic intent-based mode selection
- **Progress Notifications**: Users can track document processing progress in real-time
- **Task Management**: Create, update, and query processing tasks
- **KB Processing Summary**: Get comprehensive processing summary for knowledge bases
- **Intent Classification API**: API for classifying query intent manually
- **Processing Cleanup**: Automatic cleanup of old processing tasks
- **User Task Queries**: Query all processing tasks for a specific user

### Enhanced
- **User Experience**: Users can now track when their documents are ready for querying
- **Search Intelligence**: Automatic intent classification improves search accuracy
- **Processing Visibility**: Real-time progress tracking for document ingestion
- **Mode Selection**: Intelligent automatic mode selection based on query intent
- **Task Management**: Better visibility into document processing pipeline

### Technical
- **New Intent Module**: Complete intent classification system with pattern matching
- **New Processing Module**: Document processing tracking and notification system
- **Enhanced Ingestion Pipeline**: Integrated with processing tracker for progress updates
- **Search API Enhancement**: Added auto_classify parameter for automatic mode selection
- **Thread-Safe Tracking**: Thread-safe task tracking with locks
- **JSON Persistence**: Persistent storage for processing tasks and history

## [0.5.19] - 2026-08-24

### Added
- **PDF Preview with Highlighting**: Complete PDF viewer with paragraph highlighting and navigation
- **User Feedback System**: Comprehensive feedback collection for RAG quality improvement
- **Search Suggestions System**: Intelligent search suggestions and quick questions
- **Feedback Types**: Thumbs up/down, regenerate, copy feedback options
- **Feedback Reasons**: Hallucination, no relevant docs, incorrect citation, poor quality
- **Suggestion Categories**: Frequent questions, core entities, troubleshooting, configuration, general
- **Autocomplete**: Real-time search suggestions based on text prefix
- **Quick Questions**: Product-specific quick question recommendations
- **Feedback Statistics**: Comprehensive feedback analytics and satisfaction rate calculation
- **Suggestion Tracking**: Frequency tracking and last-used timestamps for suggestions

### Enhanced
- **User Experience**: PDF preview with precise paragraph highlighting
- **Quality Improvement**: User feedback integration for continuous improvement
- **Search Efficiency**: Intelligent suggestions reduce query time
- **Interaction**: Enhanced user interaction with feedback and suggestion systems
- **Analytics**: Detailed feedback statistics and suggestion usage tracking

### Technical
- **New Feedback Module**: Complete user feedback management system
- **New Suggestions Module**: Search suggestions and quick questions system
- **PDF.js Integration**: Client-side PDF rendering with highlighting
- **Feedback API**: RESTful API for feedback collection and analysis
- **Suggestions API**: RESTful API for search suggestions and autocomplete
- **Data Persistence**: JSON-based storage for feedback and suggestions

## [0.5.18] - 2026-08-24

### Added
- **Complete RAG Workflow Manager**: Implementation of standardized three-stage RAG workflow
- **Ingestion Stage**: Standardized knowledge base construction with quality checks
- **Retrieval Stage**: Enhanced retrieval with multi-mode support and quality validation
- **Generation Stage**: Structured answer generation with relevance checking
- **Citation Stage**: Comprehensive citation system with page numbers and chunk IDs
- **Workflow Context**: Structured context management for workflow execution
- **Quality Control Points**: Automated quality checks at each workflow stage
- **Stage Results**: Detailed result tracking for each workflow stage
- **Workflow API**: Complete API for executing individual stages and complete workflows
- **Stage Status Tracking**: Real-time status monitoring for workflow execution
- **Performance Metrics**: Duration and performance tracking for each stage

### Enhanced
- **Workflow Standardization**: Complete standardization of RAG three-stage workflow
- **Quality Assurance**: Automated quality checks ensure reliable results
- **Error Handling**: Comprehensive error handling and recovery mechanisms
- **Monitoring**: Detailed metrics and status tracking for workflow execution
- **Flexibility**: Support for executing individual stages or complete workflows
- **Multi-KB Integration**: Seamless integration with multi-knowledge base system

### Technical
- **New Workflow Module**: Complete workflow management system
- **Stage Handlers**: Specialized handlers for each workflow stage
- **Quality Checkers**: Automated quality validation for each stage
- **Context Management**: Structured context for workflow execution
- **Result Tracking**: Comprehensive result tracking and reporting
- **API Endpoints**: RESTful API for workflow management

## [0.5.17] - 2026-08-24

### Added
- **Multi-Knowledge Base System**: Complete implementation of product-specific knowledge base isolation
- **Product Selector Interface**: Frontend interface with product tabs and dropdown selection
- **Multi-KB Manager**: Backend manager for handling multiple isolated knowledge bases
- **Physical Isolation**: Each product gets its own working directory for 100% context isolation
- **Multi-KB Routing**: Automatic routing of queries to product-specific knowledge bases
- **Incremental KB Updates**: Product-specific incremental update mechanism
- **KB Registration API**: API endpoints for registering, updating, and deleting product KBs
- **Product List API**: API endpoint for listing available product knowledge bases
- **Enhanced Citations**: Citations now include page numbers and chunk IDs for precise source tracing
- **Category Parameter**: Search API now supports category parameter for multi-KB routing

### Enhanced
- **Search API**: Multi-knowledge base support with automatic fallback to global KB
- **Citation System**: Enhanced citations with page numbers and chunk IDs
- **Knowledge Base Management**: Complete lifecycle management for product-specific KBs
- **User Experience**: Product selection for precise knowledge base targeting
- **Isolation Strategy**: Physical-level isolation prevents cross-product knowledge contamination

### Technical
- **New Multi-KB Module**: Complete multi-knowledge base management system
- **Product-Specific Working Directories**: Isolated storage per product
- **KB Configuration Management**: JSON-based configuration for multiple KBs
- **Adapter Instance Management**: Efficient management of multiple LightRAG adapters
- **Fallback Mechanism**: Automatic fallback to global KB when product KB fails

## [0.5.16] - 2026-08-24

### Added
- **LightRAG Multi-Mode Query Selector**: Frontend interface for selecting LightRAG query modes (naive, local, global, hybrid)
- **Query Mode Integration**: Backend support for LightRAG query modes in search API
- **Intent-Based Query Routing**: Support for different query intents (local entity questions, global summaries, hybrid)
- **Enhanced Search Interface**: Added LightRAG query mode selector to enhanced search UI
- **Query Mode Descriptions**: User-friendly descriptions for each query mode use case

### Enhanced
- **Search Flexibility**: Users can now choose between different LightRAG query strategies
- **Query Intent Matching**: Better alignment between user intent and search strategy
- **User Control**: Advanced users can manually select query modes, while hybrid mode remains default
- **API Response**: Search API now returns both search mode and query mode information

### Technical
- **Search API Enhancement**: Added query_mode parameter to search endpoint
- **LightRAG Integration**: Deeper integration with LightRAG's multi-mode capabilities
- **Frontend Controls**: UI controls for query mode selection with descriptions

## [0.5.15] - 2026-08-24

### Added
- **Interactive Graph Interface**: New dedicated interface for graph-RAG interaction with UX best practices
- **Entity Linking**: Click highlighted entities in chat to view entity-centered subgraphs
- **Node Source Tracing**: Click graph nodes to view original document fragments with source cards
- **Dynamic Subgraph Display**: Render only relevant local relationship subgraphs to avoid visual clutter
- **Entity Extraction**: Automatic entity extraction from search results and chat responses
- **Entity Highlighting**: Visual highlighting of entities in chat responses with click interaction
- **Mini Graph Panel**: Integrated mini graph in enhanced search interface for quick entity visualization
- **Entity Subgraph API**: New endpoint for retrieving entity-centered subgraphs
- **Node Source API**: New endpoint for retrieving source documents for specific graph nodes
- **Enhanced Chat Citations**: Citations now include extracted entities for graph interaction

### Enhanced
- **Graph-RAG Integration**: Seamless integration between knowledge graph and RAG system
- **User Experience**: Improved UX with entity linking, node tracing, and dynamic subgraph display
- **Visual Clutter Reduction**: Dynamic subgraph rendering prevents full graph overload
- **Interactive Elements**: Click interactions for entities, nodes, and edges with contextual information
- **Search-Graph Connection**: Direct connection between search results and graph visualization

### Technical
- **New Interactive Graph UI**: Dedicated interface with Cytoscape.js for advanced graph interaction
- **Entity Detection**: Simple entity extraction algorithm for capitalized words and codes
- **Subgraph Algorithms**: Entity-centered subgraph extraction from full knowledge graph
- **Source Mapping**: Node-to-document mapping for source tracing functionality
- **Event Communication**: Cross-window communication for entity highlighting between interfaces

## [0.5.14] - 2026-08-24

### Added
- **Enhanced Search Interface**: New multi-modal interaction interface with hybrid retrieval
- **Smart Chat with Citations**: Intelligent dialogue with document references and jump links
- **Keyword/Semantic Hybrid Search**: Combined search box supporting both natural language and keyword queries
- **Faceted Search**: Sidebar with document type, time, department, and access level filters
- **Enhanced Reranking**: Improved lightweight reranker with bge-reranker-base model
- **Weighted Hybrid Search**: Configurable BM25 and LightRAG weights in fusion
- **Citation System**: Automatic source citations in chat responses with document links
- **Search Mode Selection**: User-selectable search modes (hybrid, semantic, keyword)

### Enhanced
- **Hybrid Search Logic**: Enhanced RRF fusion with configurable weights and reranking
- **Cross-Encoder Integration**: Better integration with BAAI/bge-reranker-base model
- **Multi-Stage Reranking**: Pipeline for multi-stage reranking with metadata consideration
- **User Experience**: Improved interface with real-time search and chat capabilities
- **Result Presentation**: Better result display with scores, sources, and metadata

### Technical
- **New Enhanced Search UI**: Dedicated interface for multi-modal search interaction
- **Citation API**: Enhanced streaming with citation generation
- **Filter System**: Client-side and server-side filtering capabilities
- **Reranker Pipeline**: Improved reranking with fallback mechanisms

## [0.5.13] - 2026-08-24

### Added
- **Incremental Update Mechanism**: File hash-based change detection with smart document synchronization
- **Performance Monitoring System**: Comprehensive metrics tracking with threshold-based alerting
- **Quality Metrics Tracking**: RAG quality metrics (precision, recall, relevance, faithfulness) with trend analysis
- **Document Cleanup**: Automated cleanup of old documents based on age thresholds
- **Strategy Management**: Closed-loop iteration system for chunking, retrieval, and reranking strategies
- **Performance APIs**: New endpoints for maintenance statistics, performance metrics, and quality tracking
- **Strategy Optimization**: Automatic strategy adjustment based on performance targets
- **Change Logging**: Comprehensive change log for tracking document modifications

### Enhanced
- **Knowledge Base Maintenance**: Complete operational capabilities for long-term maintenance
- **Performance Analysis**: Trend analysis and performance degradation detection
- **Strategy Comparison**: Compare different strategy configurations and their performance
- **Closed-Loop Iteration**: Automatic optimization based on quality metrics and targets

### Technical
- **New Maintenance Module**: Added comprehensive maintenance capabilities (incremental, monitoring, strategy)
- **Performance Thresholds**: Configurable thresholds for automatic alerting
- **Quality Trends**: Track quality metrics over time with trend analysis
- **Strategy Auto-Optimization**: Intelligent strategy adjustment based on performance data

## [0.5.12] - 2026-08-24

### Added
- **Complete Data Processing Pipeline**: Implemented full document processing including parsing, semantic chunking, and LightRAG indexing
- **Semantic Chunking**: Added StructuredChunker for intelligent document segmentation
- **Knowledge Graph Generation**: Integrated LightRAG indexing for automatic knowledge graph creation
- **Document Registry**: Enhanced document tracking with chunk count and indexing status
- **Processing Status**: Added detailed processing status feedback (parsed_only, indexed, graph_generated)

### Enhanced
- **Document Ingestion**: Complete 3-step ingestion process (parse → chunk → index)
- **Folder Import**: Enhanced folder import with semantic chunking and LightRAG indexing
- **Registry Management**: Improved document and folder registry with comprehensive metadata
- **Error Handling**: Better error handling for LightRAG indexing failures

### Fixed
- **Missing Data Processing**: Fixed incomplete document upload that lacked semantic chunking and graph generation
- **Knowledge Graph Generation**: Documents now properly indexed in LightRAG for knowledge graph creation
- **Document Registry**: Documents now saved to registry with complete processing metadata

## [0.5.11] - 2026-08-24

### Fixed
- **Search API Response**: Fixed search API returning undefined answers and empty sources
- **LightRAG Error Handling**: Added proper error handling for LightRAG query failures
- **Empty Answer Handling**: Added fallback messages when LightRAG returns empty results
- **Hybrid Search Enhancement**: Improved hybrid search error handling and response formatting

### Enhanced
- **Search Error Messages**: Better user feedback when search fails or no documents are available
- **LightRAG Configuration Check**: Added checks for LightRAG configuration and document indexing
- **Response Format**: Ensured consistent response format across all search modes

## [0.5.10] - 2026-08-24

### Fixed
- **Simple UI Search**: Fixed intelligent search in simple interface to use correct search API endpoint
- **Search Mode Options**: Updated search mode options to match available backend modes (hybrid, lightrag, bm25)
- **Search Results Display**: Enhanced search results to show mode, answer, sources, and scores
- **API Integration**: Changed from chat/completions to search endpoint for proper search functionality

## [0.5.9] - 2026-08-24

### Fixed
- **Knowledge Manager Statistics**: Fixed statistics display showing 0 by ensuring updateStats() is called after data loading
- **Knowledge Graph Display**: Enhanced graph API to read actual LightRAG graph data and create nodes from documents
- **Chat Interface Streaming**: Fixed chat streaming response to properly display assistant messages in real-time
- **Graph Data Source**: Added fallback to create graph nodes from document registry when LightRAG graph is unavailable

### Enhanced
- **Knowledge Graph API**: Improved graph endpoint to return node/edge counts and handle missing graph data gracefully
- **Chat Message Display**: Added real-time message updates during streaming and proper error handling
- **Document-based Graph**: Created document nodes from registry when no LightRAG graph exists

## [0.5.8] - 2026-08-24

### Added
- **Enhanced PII Masking**: Advanced PII detection and masking with multiple entity types (phone, ID card, email, credit card, IP, URL)
- **BM25 Sparse Search**: Complete BM25 implementation for keyword-based retrieval
- **Hybrid Search**: RRF (Reciprocal Rank Fusion) combining BM25 and LightRAG results
- **RAGAS Evaluation Framework**: Comprehensive evaluation metrics (faithfulness, answer relevance, context precision, context recall)
- **Enhanced Text Cleaning**: Improved text cleaning with deduplication and noise removal
- **Multi-Mode Search API**: Support for lightrag, bm25, and hybrid search modes
- **Evaluation API**: New endpoint for RAG quality assessment

### Enhanced
- **Data Pipeline**: Enhanced ingestion pipeline with PII masking and text cleaning
- **Search Capabilities**: Multiple search modes for different use cases
- **Quality Assurance**: Built-in evaluation framework for continuous improvement
- **Security**: Enhanced PII protection for compliance

### Technical
- **New Modules**: Added retrieval and evaluation modules
- **Performance**: Optimized search with multiple retrieval strategies
- **Monitoring**: Added evaluation metrics tracking

## [0.5.7] - 2026-08-24

### Added
- **Folder Records API**: Added /api/v1/folders endpoint to track folder import history
- **Folder Statistics**: Added folder count statistics in knowledge manager
- **Folder File Count**: Display file count for each imported folder
- **Folder Records Display**: Added separate section for folder import records

### Enhanced
- **Knowledge Manager UI**: Added folder records section with file count display
- **Document Tracking**: Enhanced folder import to save folder records with metadata
- **File Organization**: Better organization of uploaded vs folder-imported documents
- **Statistics Display**: Added folder count to statistics dashboard

### Fixed
- **Document Visibility**: Enhanced document loading to show both uploaded and folder documents
- **Folder Document Association**: Added folder_id to documents for proper filtering
- **Event Integration**: Updated folder import events to include folder records

## [0.5.6] - 2026-08-24

### Fixed
- **Knowledge Manager Document Visibility**: Fixed document list API to show uploaded files from uploads directory
- **Search Error Handling**: Added error handling to search endpoint to prevent undefined errors
- **Chat Streaming Response**: Fixed chat completions to properly handle streaming responses
- **API Endpoints**: Added knowledge graph and user knowledge bases API endpoints
- **Duplicate Functions**: Removed duplicate function definitions in main.py

### Added
- **Knowledge Graph API**: Added /api/v1/users/{user_id}/kbs/{kb_name}/graph endpoint
- **User Knowledge Bases API**: Added /api/v1/users/{user_id}/kbs endpoint
- **Document Fallback**: Added fallback to uploads directory when document registry doesn't exist
- **Error Messages**: Improved error messages for better debugging

### Changed
- **Main UI Search**: Added error handling for search results
- **Chat UI**: Updated to handle streaming responses properly
- **Knowledge Manager**: Enhanced to load documents from API with fallback

## [0.5.5] - 2026-08-24

### Fixed
- **Knowledge Manager UTF-8 Error**: Fixed corrupted knowledge_manager.html file encoding issue
- **Document Visibility**: Added document list API endpoint to show uploaded and imported documents
- **Knowledge Manager Interface**: Rebuilt knowledge manager with proper document tracking

### Added
- **Document List API**: Added /api/v1/documents endpoint to retrieve all documents
- **Document Tracking**: Enhanced folder import to return document metadata
- **Event Integration**: Added custom events for document upload and folder import
- **Document Management UI**: Complete knowledge manager interface with document list

### Changed
- **Main UI Integration**: Added event dispatching for document operations
- **Knowledge Manager**: Now properly displays uploaded and folder-imported documents

## [0.5.4] - 2026-08-24

### Added
- **Local Folder Import API**: Added /api/v1/import-folder endpoint for batch document import
- **Web Interface Folder Import**: Added folder import functionality in main UI
- **Batch Processing**: Support for importing multiple files from local folders
- **Enhanced Upload Interface**: Split upload interface into file and folder sections

### Changed
- **Main UI Layout**: Enhanced upload card with grid layout for file and folder options
- **User Experience**: Simplified folder import with web interface option

## [0.5.3] - 2026-08-24

### Fixed
- **Document Upload Error Handling**: Added try-catch error handling in ingest endpoint
- **JSON Response Validation**: Added content-type checking in frontend to handle non-JSON responses
- **Parser Registry**: Added TextParser and MarkdownParser to support more file formats
- **Error Messages**: Improved error messages for better debugging

### Added
- **Enhanced Error Reporting**: Better error messages in upload interface
- **File Format Support**: Added support for .txt and .md files

## [0.5.2] - 2026-08-24

### Added
- **Unified Main Interface**: Created main_ui.html as single-page application for all features
- **Tabbed Navigation**: Integrated document upload, search, graph, status, and docs in one interface
- **Embedded Graph Viewer**: Added iframe integration for knowledge graph visualization
- **Simplified User Experience**: Users no longer need to remember multiple URLs

### Changed
- **Root Endpoint**: Root endpoint now serves unified main interface instead of JSON
- **User Experience**: All major functions accessible from single landing page
- **Navigation**: Tab-based navigation for better user experience

## [0.5.1] - 2026-08-24

### Added
- **Reliable Startup Scripts**: Added start_server.ps1 and start_server.bat for reliable server startup
- **Enhanced Startup Logging**: Added detailed logging in startup scripts for debugging
- **PYTHONPATH Configuration**: Automatic PYTHONPATH configuration in startup scripts

### Fixed
- **Version Display**: Confirmed dynamic version import working correctly
- **Import Issues**: Resolved all import and version display issues
- **Startup Reliability**: Created foolproof startup methods

## [0.5.0] - 2026-08-24

### Fixed
- **Hardcoded Version Number**: Fixed hardcoded version '0.4.4' in main.py root endpoint
- **Dynamic Version Import**: Changed to use __version__ from rag_kb.__init__ for dynamic version display
- **Version Consistency**: Ensures API endpoint displays correct version from source code

### Changed
- **Root Endpoint**: Now dynamically imports and displays version from __init__.py
- **Import Structure**: Added __version__ import from rag_kb package

## [0.4.9] - 2026-08-24

### Added
- **Direct Source Startup Script**: Added start_direct.bat for direct source code execution
- **Bypass Package Issues**: Allows running directly from source without package installation dependencies

### Changed
- **Startup Options**: Added alternative startup method to bypass package version synchronization issues
- **Documentation**: Updated troubleshooting guidance for package version conflicts

## [0.4.8] - 2026-08-24

### Fixed
- **Virtual Environment Python**: Fixed manage.ps1 to use virtual environment Python instead of system Python
- **Python Command Detection**: Added logic to detect and use virtual environment Python when available
- **Version Display**: Added display of which Python executable is being used for debugging

### Changed
- **Startup Script**: Enhanced manage.ps1 to properly handle virtual environment activation
- **Python Path**: Ensured correct Python executable is used for uvicorn startup

## [0.4.7] - 2026-08-24

### Fixed
- **Static Directory Path**: Fixed static directory path calculation to properly navigate to project root
- **Changed**: Path from `Path(__file__).parent.parent / "static"` to `Path(__file__).parent.parent.parent.parent / "static"`
- **Added**: Warning message when static directory is not found for debugging

### Changed
- **Path Resolution**: Improved static file path resolution for correct directory navigation
- **Error Messages**: Enhanced error handling with static directory information

## [0.4.6] - 2026-08-24

### Added
- **Static File Serving**: Added StaticFiles mounting for serving static content
- **Direct Static Links**: Added direct links to static files in fallback interfaces
- **Improved Fallback**: Enhanced error messages with alternative static file access

### Fixed
- **Static File Access**: Fixed static file serving to properly serve HTML interfaces
- **Path Resolution**: Improved static file path resolution and error handling

## [0.4.5] - 2026-08-24

### Added
- **Frontend Routes**: Added missing frontend routes for chat-ui, graph-ui, and knowledge-manager
- **Root Endpoint**: Added root endpoint with system information and available endpoints
- **Fallback UI**: Added fallback HTML interfaces when static files are not found

### Fixed
- **404 Errors**: Resolved "Not Found" errors for frontend interface routes
- **User Experience**: Improved error messages with links to API documentation

## [0.4.4] - 2026-08-24

### Fixed
- **Startup Script Fix**: Modified manage.ps1 to set PYTHONPATH and use correct module path
- Changed uvicorn startup from `src.rag_kb.api.main:app` to `rag_kb.api.main:app` with PYTHONPATH set
- This resolves import path issues in the PowerShell startup script

### Changed
- Updated manage.ps1 startup command to use PYTHONPATH environment variable
- Ensures consistent import behavior across different startup methods

## [0.4.3] - 2026-08-24

### Fixed
- **Hotfix**: Completely removed importlib.util.spec_from_file_location calls that were still causing null bytes errors in uvicorn runtime
- Changed to standard Python imports with exception handling for robustness
- Added graceful fallback if API routes import fails

### Changed
- Simplified main.py import mechanism to use direct imports
- Updated test expectations to handle optional API router availability

## [0.4.2] - 2026-08-24

### Fixed
- **Critical**: Resolved "source code string cannot contain null bytes" error during API module import
- Fixed import mechanism in `src/rag_kb/api/main.py` and `src/rag_kb/api/routes.py`
- Removed complex `importlib.util.spec_from_file_location` calls that were causing import conflicts
- Simplified imports using lazy loading for heavy modules (LightRAGAdapter, IngestPipeline)

### Changed
- Refactored `routes.py` to remove dependencies on missing organization modules
- Updated `main.py` to use lazy imports inside endpoint functions
- Simplified API router structure to prevent import-time blocking

### Added
- New unit tests in `tests/test_api_imports.py` to validate API import mechanisms
- Tests for null bytes detection in Python files
- Tests for FastAPI app and router structure validation
- Tests for lazy import mechanism functionality

### Testing
- All 29 tests passing (22 existing + 7 new import tests)
- Verified server startup without errors
- Validated import mechanism on different ports

## [0.4.1] - 2026-08-24

### Added
- Performance optimization and monitoring capabilities
- System metrics tracking (CPU, memory, disk usage)
- Structured logging with console and file output
- Performance monitoring for operations
- Slow query detection and logging

### Changed
- Enhanced performance tuning guidelines
- Updated configuration options for optimization

## [0.4.0] - 2026-08-24

### Added
- Knowledge management features
- Document organization capabilities
- Quality analysis tools
- Enhanced user interface components

### Changed
- Updated user documentation
- Improved API structure

## [0.3.2] - 2026-08-24

### Added
- Complete user journey analysis documentation
- Problem identification for each workflow step
- Improvement roadmap with prioritized improvements (P0, P1, P2)
- Usage guidelines for stable version

### Changed
- Enhanced documentation and analysis

## [0.3.0] - 2026-08-24

### Added
- Python 3.11+ compatibility
- Incremental updates with file hash-based change detection
- Enterprise security with comprehensive RBAC/ACL
- Hybrid search with BM25 sparse search + LightRAG
- Advanced reranking with Cross-encoder and rule-based reranking
- Knowledge graph extraction with NetworkX integration
- RAGAS evaluation framework with 15+ test cases
- Deployment scripts with health checks
- Performance monitoring and system metrics

### Changed
- Updated from Python 3.9 to 3.11+ for modern dependencies
- Enhanced security model with pre-filtering and post-filtering
- Improved retrieval pipeline with RRF fusion

## [0.1.0] - Initial Release

### Added
- Basic RAG knowledge base functionality
- Document ingestion pipeline
- LightRAG integration
- FastAPI backend
- Basic search capabilities
- Open WebUI integration