# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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