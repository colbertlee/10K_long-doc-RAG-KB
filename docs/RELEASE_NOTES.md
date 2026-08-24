# Release Notes

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