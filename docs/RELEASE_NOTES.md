# Release Notes

## [0.6.0] - 2026-09-04

### Enterprise RAG Optimization - Major Release
- **Advanced Retrieval System**: BM25 sparse search with complete index builder and weighted RRF fusion
- **BGE-Reranker Integration**: Advanced reranking using sentence-transformers (v5.5.1) for improved result precision
- **RAGAS Evaluation Framework**: Comprehensive quality assessment framework (v0.4.3) with 15+ quality metrics
- **Performance Tuning System**: YAML-based configuration with speed/accuracy/balance optimization profiles
- **Knowledge Graph Enhancement**: Proper node naming with document titles and content-based ID mapping
- **Multi-Knowledge Base System**: Product isolation with separate knowledge bases and unified management
- **Anti-Hallucination System**: LLM-level quality control with strict system prompts and answer validation
- **Comprehensive Monitoring**: Structured logging, performance metrics, and health check endpoints
- **OCR Document Support**: Scanned PDF processing with OCR integration for enhanced document parsing
- **GPU Acceleration**: CUDA support for embedding and reranking operations with result caching

### New API Endpoints
- 50+ new endpoints for advanced search, evaluation, monitoring, and management
- Dual GET/POST support for browser compatibility
- Enhanced API documentation with interactive examples
- Performance endpoints for monitoring integration

### Technical Improvements
- New modules: retrieval, evaluation, monitoring, graph_analysis, maintenance
- Dependency updates: sentence-transformers v5.5.1, ragas v0.4.3, torch v2.13.0
- Performance optimizations with GPU support and result caching
- 30+ new test files with integration, performance, and regression tests
- Enhanced error handling, logging, and validation across all modules

### Breaking Changes
- None (fully backward compatible with v0.5.x)

### Migration Guide
Existing installations can upgrade safely:
```bash
pip install -e .[all]
```
For performance optimization, copy `configs/performance.yaml` and tune parameters according to use case.

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