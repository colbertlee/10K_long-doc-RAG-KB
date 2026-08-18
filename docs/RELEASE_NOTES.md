# Release Notes

## [0.2.0] - 2026-08-18

### Major Updates
- Complete Open WebUI iframe integration
- Document parser system refactoring
- Added text and Markdown parser support
- Fixed parser inheritance issues

### New Features
- Added Open WebUI iframe integration page
- Created pre-built integration page with service monitoring
- Added TextParser for .txt files
- Added MarkdownParser for .md files
- Added static file serving
- Real-time service status monitoring

### Fixes
- Fixed parser inheritance (inherit from BaseParser)
- Fixed document indexing functionality
- Fixed user ID validation (avoid reserved names)
- Updated Open WebUI installation script to handle npm issues

### Documentation Updates
- Added Open WebUI iframe integration guide (English and Chinese)
- Added naming conventions documentation (English and Chinese)
- Updated all README files
- Added detailed integration step instructions

### Improvements
- Added /openwebui-integration endpoint
- Improved health check endpoint to show new endpoints
- Optimized integration page user experience
- Added responsive design support

## [0.1.9] - 2026-08-18

### New Features
- Added Open WebUI iframe integration functionality
- Created pre-built Open WebUI integration page
- Added real-time service status monitoring
- Implemented static file serving
- Added beautiful gradient header design
- Added loading states and error handling
- Added responsive design support
- Added quick action buttons

### Documentation Updates
- Added Open WebUI iframe integration guide (English and Chinese)
- Updated README files with new documentation links
- Provided detailed integration steps and configuration instructions

### Improvements
- Added /openwebui-integration endpoint
- Improved health check endpoint to show new integration endpoint
- Optimized integration page user experience

## [0.1.8] - 2026-08-18

### Fixes
- Fixed LightRAG v1.5.6 compatibility issues
- Updated adapter to support new LightRAG API
- Fixed EmbeddingFunc initialization errors
- Added proper async LLM and embedding functions
- Used wrap_embedding_func_with_attrs decorator

### Testing
- Verified health check endpoint works correctly
- Tested current user API endpoint
- Validated user ID and knowledge base name validation
- Tested user and knowledge base creation functionality

## [0.1.7] - 2026-08-18

### New Features
- Added user ID and knowledge base name validation
- Implemented current user ID auto-display
- Added path sanitization to prevent path traversal attacks
- Enhanced health check endpoint with detailed system status
- Added current user API endpoint (/api/v1/current-user)
- Document management UI auto-loads current user ID

### Security Improvements
- Input validation to prevent special characters and security risks
- Path sanitization to prevent directory traversal attacks
- Reserved username validation (prevents using reserved names)
- Length limits to prevent excessively long names

### Improvements
- Added CORS middleware for better API access
- Friendly error messages
- Enhanced health check showing service status
- Document management UI user experience improvements

### Documentation Updates
- Updated health check endpoint description
- Added user ID naming conventions
- Provided security best practices guidance

## [0.1.6] - 2026-08-18

### New Features
- Created dedicated Open WebUI startup script (scripts/open_webui.ps1)
- Enhanced start.ps1 script with optional parameters
- Support for disabling Open WebUI startup (-NoOpenWebUI parameter)
- Support for disabling auto-browser opening (-NoBrowser parameter)
- Open WebUI script supports custom port (-Port parameter)

### Improvements
- More flexible service management options
- Users can selectively start services
- Improved user experience for startup scripts
- Better error handling and dependency checking

### Documentation Updates
- Updated user guide with new script usage instructions
- Updated installation guide with new startup options
- Updated README files with new script documentation
- Provided detailed parameter descriptions

## [0.1.5] - 2026-08-18

### Fixes
- Fixed NameError on startup (IncrementalIndexer undefined)
- Removed IncrementalIndexer usage from user_manager.py
- Removed unused imports from docs_ui.py
- Fixed document management UI not loading issue

### Improvements
- Service now starts correctly
- Document management UI is accessible
- Resolved circular dependency issues

## [0.1.4] - 2026-08-18

### New Features
- Created automatic upgrade script (scripts/upgrade.ps1)
- Support for automatic version checking and upgrade
- Support for specific version upgrade
- Automatic backup functionality

### Documentation Updates
- Updated upgrade guide to reference new upgrade script
- Updated installation guide with upgrade instructions
- Updated user guide to ensure document management UI information is accurate
- Updated README files with new features and documentation links
- Ensured all documentation accurately reflects current functionality

### Improvements
- Improved documentation consistency
- Added Open WebUI integration guide links
- Enhanced documentation readability and completeness

## [0.1.3] - 2026-08-18

### Fixes
- Fixed startup import error (IncrementalIndexer import issue)
- Removed unused import in user_manager.py

### Improvements
- Auto-open document management UI on startup
- Display document management UI URL in startup output
- Improved user experience with direct access

### User Experience Enhancements
- Document management interface opens automatically after service startup
- No need to manually enter URL to access the interface
- More intuitive service startup process

## [0.1.2] - 2026-08-18

### New Features
- Modern document management web interface
- Document upload functionality (with drag-and-drop support)
- Local folder import interface
- Document management and statistics features
- Open WebUI integration support
- Real-time progress display
- Multi-user and knowledge base management interface

### Improvements
- Enhanced user experience
- Visual document management
- Simplified document import process
- Support for batch operations

### New Endpoints
- GET /docs/docs-ui - Document management interface
- Full document management operations support

### Documentation Updates
- Added Open WebUI integration guide
- Updated user guide with new UI features
- Detailed interface usage instructions

## [0.1.1] - 2026-08-17

### New Features
- Local folder import functionality
- PowerShell import script
- Simple mode with auto user/knowledge base creation
- Folder import API endpoints
- Detailed import statistics and progress display
- File skipping and error handling

### Improvements
- Updated user guide with folder import instructions
- Enhanced user data management system
- Support for batch document import
- Added file duplicate detection

### New API Endpoints
- POST /users/{user_id}/kbs/{kb_name}/import-folder - Import folder to user knowledge base
- POST /import-local-folder - Simple mode folder import

### Documentation Updates
- Updated USER_GUIDE.md and USER_GUIDE_CN.md
- Added local folder import usage instructions
- Added troubleshooting guide

## [0.1.0] - 2026-08-17

### Added
- Initial release of RAG Knowledge Base for 10K long documents
- Structure-aware document chunking with parent-child relationships
- LightRAG integration with hybrid/local/global/naive query modes
- Multi-format document parsing (PDF, Word, HTML, Markdown)
- Data cleaning with deduplication and PII masking
- FastAPI backend with OpenAI-compatible endpoints
- Open WebUI integration for chat interface
- RBAC/ACL security support
- Incremental document updates
- Comprehensive test suite
- PowerShell startup scripts
- Bulk document ingestion script

### Features
- **Document Processing**: Support for 10,000+ long documents with semantic chunking
- **Graph-Enhanced Retrieval**: LightRAG with vector+graph hybrid search
- **Windows Native**: Optimized for Windows deployment with Ollama local models
- **Security**: Built-in access control and PII protection
- **Performance**: Parent-child chunking for high precision retrieval
- **Extensibility**: Modular architecture with plugin-based parsers and chunkers

### Technology Stack
- Backend: FastAPI, Python 3.11+
- RAG Engine: LightRAG (lightrag-hku)
- Vector Store: NanoVectorDB
- Graph Store: NetworkX
- LLM: Ollama (qwen2.5, llama3.1, deepseek-r1)
- Embeddings: Ollama (nomic-embed-text, bge-m3)
- Frontend: Open WebUI

### Documentation
- Comprehensive README with installation and usage instructions
- API documentation with interactive Swagger UI
- Configuration examples for Ollama and OpenAI-compatible APIs
- Test suite with unit and integration tests

### Known Limitations
- LightRAG uses local storage (NetworkX + NanoVectorDB + JSON)
- For 10K+ documents with dense graphs, consider external vector/graph databases
- Windows-specific deployment (though core Python code is cross-platform)

### Migration Notes
- This is the initial release, no migration needed

### Support
- Documentation: See README.md and /docs directory
- Issues: Please report via GitHub Issues
- References: RAG_KB_Plan.html and RAG_KB_Implementation_Framework.html