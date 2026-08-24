# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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