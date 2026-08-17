# User Guide - RAG Knowledge Base

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Document Ingestion](#document-ingestion)
4. [Querying the Knowledge Base](#querying-the-knowledge-base)
5. [Using Open WebUI](#using-open-webui)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Ollama installed and running
- Windows 10/11 (for native deployment)

### Quick Start

1. **Install the system:**
   ```bash
   pip install -e .
   ```

2. **Start Ollama and pull models:**
   ```bash
   ollama serve
   ollama pull qwen2.5
   ollama pull nomic-embed-text
   ```

3. **Start the services:**
   ```powershell
   .\scripts\start.ps1
   ```

4. **Access the interface:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Open WebUI: http://localhost:8080 (if installed)

## Basic Usage

### Health Check
Verify the system is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

## Document Ingestion

### Single Document Upload

Upload a document via API:
```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -F "file=@document.pdf" \
  -F "dept=Engineering" \
  -F "level=Internal"
```

Response:
```json
{
  "doc_id": "abc123...",
  "title": "document",
  "pages": 15
}
```

### Bulk Document Ingestion

1. Place documents in `data/raw/` directory
2. Run the bulk ingestion script:
   ```bash
   python scripts\ingest_bulk.py
   ```

Supported formats:
- PDF (.pdf)
- Word (.docx)
- Markdown (.md)
- Text (.txt)

### Access Control

Set access control during ingestion:
- `dept`: Department (e.g., "Engineering", "Sales")
- `level`: Access level (e.g., "Internal", "Confidential")

## Querying the Knowledge Base

### Direct API Query

```bash
curl -X POST "http://localhost:8000/api/v1/search?q=What%20are%20the%20system%20requirements?&dept=Engineering&level=Internal&top_k=5"
```

### Chat Completions (OpenAI-compatible)

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What are the system requirements?"}
    ]
  }'
```

## Using Open WebUI

### Configuration

1. Open Open WebUI (http://localhost:8080)
2. Go to Settings → Connections
3. Configure OpenAI API:
   - **API Base URL**: `http://localhost:8000/api/v1`
   - **API Key**: `not-needed-for-local`
   - **Default Model**: `rag-kb-pipeline`

### Chat Interface

1. Start a new conversation
2. Ask questions about your documents
3. View responses with source citations
4. Use streaming for real-time answers

### Features
- Real-time streaming responses
- Source citation and reference
- Conversation history
- Multi-language support

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Application
RAGKB_APP_NAME=rag-kb
RAGKB_DATA_DIR=./data
RAGKB_LOG_LEVEL=INFO

# Embedding
RAGKB_EMBEDDING_PROVIDER=ollama
RAGKB_EMBEDDING_MODEL=nomic-embed-text

# LLM
RAGKB_LLM_PROVIDER=ollama
RAGKB_LLM_MODEL=qwen2.5
RAGKB_LLM_TEMPERATURE=0.3

# LightRAG
RAGKB_LIGHTRAG_QUERY_MODE=hybrid
RAGKB_LIGHTRAG_CHUNK_TOKEN_SIZE=1200
```

### YAML Configuration

Edit `configs/config.yaml`:

```yaml
app:
  name: rag-kb
  data_dir: ./data

embedding:
  provider: ollama
  model: nomic-embed-text

llm:
  provider: ollama
  model: qwen2.5
  temperature: 0.3

lightrag:
  query_mode: hybrid
  chunk_token_size: 1200
```

### Model Selection

**Ollama Models (Local):**
- LLM: `qwen2.5`, `llama3.1`, `deepseek-r1`
- Embedding: `nomic-embed-text`, `mxbai-embed-large`

**OpenAI-compatible (Remote):**
```yaml
llm:
  provider: openai
  base_url: https://api.openai.com/v1
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o
```

## Troubleshooting

### Common Issues

**Ollama connection failed:**
- Ensure Ollama is running: `ollama serve`
- Check Ollama is accessible at http://localhost:11434

**Python version error:**
- Open WebUI requires Python 3.11+
- Use: `python --version` to check

**Memory issues:**
- Reduce `lightrag_chunk_token_size` in config
- Use smaller LLM models
- Process documents in smaller batches

**Slow indexing:**
- Check Ollama GPU support
- Reduce batch size in ingestion script
- Use faster embedding models

**Permission errors:**
- Ensure data directory has write permissions
- Run PowerShell as Administrator if needed

### Debug Mode

Enable debug logging:
```bash
RAGKB_LOG_LEVEL=DEBUG python -m uvicorn rag_kb.api.main:app --reload
```

### Test Installation

Run the test suite:
```bash
pytest
```

## Advanced Usage

### Query Modes

- **hybrid**: Combines vector and graph search (default)
- **local**: Entity-relationship focused
- **global**: Global summary and patterns
- **naive**: Simple vector search

### Incremental Updates

The system automatically detects file changes:
- Modified files are reindexed
- Deleted files are removed from index
- New files are added automatically

### Security

**Access Control:**
- Documents are tagged with ACL during ingestion
- Queries are filtered based on user permissions
- PII is automatically masked in content

**Audit Trail:**
- All queries are logged
- Document access is tracked
- Modifications are recorded

## Performance Tips

1. **Use appropriate chunk sizes**: 1200 tokens for most documents
2. **Enable LLM cache**: Set `enable_llm_cache: true`
3. **Batch processing**: Use bulk ingestion for multiple documents
4. **GPU acceleration**: Enable Ollama GPU support if available
5. **Regular maintenance**: Clean up old indexes periodically

## Support

- **Documentation**: See `/docs` directory
- **API Reference**: http://localhost:8000/docs
- **Issues**: Report via GitHub Issues
- **Configuration**: See `configs/config.example.yaml`