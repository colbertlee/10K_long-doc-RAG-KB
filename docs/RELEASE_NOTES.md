# Release Notes

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