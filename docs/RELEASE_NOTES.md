# Release Notes

## [0.4.0] - 2026-08-24

### Knowledge Management Features
- **Automatic Document Classification**: Intelligent categorization (technical, product, project, business, legal)
- **Smart Tagging**: Automatic tag extraction from document content
- **Entity Recognition**: Identify technologies, dates, emails, and URLs
- **Quality Analysis**: Document quality assessment with improvement suggestions
- **Batch Operations**: Efficient multi-document processing (delete, reindex, move, tag)
- **Knowledge Management Interface**: Unified interface at `/knowledge-manager`

### New API Endpoints
- `POST /api/v1/knowledge/organize` - Document organization and classification
- `POST /api/v1/knowledge/batch-operation` - Batch document operations
- `GET /knowledge-manager` - Knowledge management interface

### Technical Improvements
- **Stability**: Resolved null bytes corruption from v0.5.0
- **Progressive Integration**: Clean implementation of v0.5.0 features
- **Testing**: 100% test pass rate for new features
- **Documentation**: Comprehensive user guides and examples

### Documentation Updates
- Updated USER_GUIDE.md with knowledge management features
- Updated USER_GUIDE_CN.md with knowledge management features
- Added examples/knowledge_management_examples.py
- Updated INSTALLATION.md and INSTALLATION_CN.md to v0.4.0
- Added CI/CD configuration for automated testing and deployment

### Usage Examples
See `examples/knowledge_management_examples.py` for comprehensive usage examples.

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