# User Guide - RAG Knowledge Base

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Document Management UI](#document-management-ui)
4. [Document Ingestion](#document-ingestion)
5. [Local Folder Import](#local-folder-import)
6. [Querying the Knowledge Base](#querying-the-knowledge-base)
7. [Using Open WebUI](#using-open-webui)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)

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

   **Optional parameters:**
   ```powershell
   # Don't start Open WebUI
   .\scripts\start.ps1 -NoOpenWebUI

   # Don't auto-open browser
   .\scripts\start.ps1 -NoBrowser
   ```

4. **Access the interface:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Document Management UI: http://localhost:8000/docs/docs-ui
   - Open WebUI: http://localhost:8080 (if installed)

### Start Open WebUI Separately

If you only want to start the Open WebUI interface:

```powershell
.\scripts\open_webui.ps1
```

**Optional parameters:**
```powershell
# Specify port
.\scripts\open_webui.ps1 -Port 8080

# Don't auto-open browser
.\scripts\open_webui.ps1 -NoBrowser
```

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

## Document Management UI

The RAG Knowledge Base provides a modern web interface for document management, including document upload, folder import, and document management features.

### Access Document Management UI

After starting the service, access:
```
http://localhost:8000/docs/docs-ui
```

### Interface Features

The document management interface includes three main feature tabs:

#### 1. 📄 Document Upload
- Support for batch file upload
- Drag and drop upload support
- Real-time upload progress display
- Support for PDF, Word, Markdown, Text formats

#### 2. 📁 Folder Import
- Folder selection via browser file picker
- Local folder path input (alternative method)
- One-click import of entire folders
- Import progress and statistics display
- Automatic duplicate file skipping

#### 3. 📋 Document Management
- View document list in knowledge base
- Document statistics information
- User and knowledge base management

### Using Document Management Interface

#### Upload Documents
1. Access http://localhost:8000/docs/docs-ui
2. Select "Document Upload" tab
3. Enter user ID and knowledge base name
4. Click upload area or drag files
5. Click "Start Upload"

#### Import Folder
1. Select "Folder Import" tab
2. Enter user ID and knowledge base name
3. Choose one of the following methods:
   - **Method 1 (Recommended)**: Click "Select Folder" button and choose a folder from your computer
   - **Method 2**: Manually enter the local folder path (e.g., `C:\Users\YourName\Documents\KB`)
4. Click "Start Import"

**Note**: The folder selection method works directly in the browser and uploads files from your selected folder. The manual path method requires server-side access to the specified folder.

#### Manage Documents
1. Select "Document Management" tab
2. Enter user ID and knowledge base name
3. Click "Load Document List"
4. View document statistics and list

### Integration with Open WebUI

The document management interface can be seamlessly integrated with Open WebUI:

1. **Start Service**: `.\scripts\start.ps1`
2. **Access Open WebUI**: http://localhost:8080
3. **Configure Connection**: Settings → Connection → API URL: `http://localhost:8000/api/v1`
4. **Access Document Management**: Add custom link in Open WebUI to document management interface
5. **Import Documents**: Use document management interface to import documents
6. **Query Documents**: Return to Open WebUI for RAG queries

For detailed integration guide, refer to [Open WebUI Integration Guide](OPENWEBUI_INTEGRATION.md).

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

## Local Folder Import

### Import Using PowerShell Script

The RAG Knowledge Base provides convenient local folder import functionality, allowing you to import entire folders from your computer directly into the knowledge base.

#### Basic Usage

```powershell
# Import local folder (simple mode)
.\scripts\import_local_folder.ps1 -FolderPath "C:\Users\YourName\Documents\KB"

# Specify user and knowledge base name
.\scripts\import_local_folder.ps1 -FolderPath "C:\Documents\Technical" -UserId "john" -KbName "tech_docs"

# Use simple mode (auto-create user and knowledge base)
.\scripts\import_local_folder.ps1 -FolderPath "C:\Documents" -SimpleMode
```

#### Parameters

- **-FolderPath**: Local folder path to import (required)
- **-UserId**: User ID (default: "default")
- **-KbName**: Knowledge base name (default: "default")
- **-ApiUrl**: API address (default: "http://localhost:8000/api/v1")
- **-SimpleMode**: Simple mode, auto-create user and knowledge base

#### Import Process

The script will automatically:
1. Scan all files in the specified folder
2. Count file numbers and total size
3. Copy files to the knowledge base's raw directory
4. Process each document (parse, clean, chunk)
5. Display import result statistics

#### Import Result Example

```
=== RAG Knowledge Base Local Folder Import ===

Import Configuration:
  Folder: C:\Users\YourName\Documents\KB
  User ID: default
  Knowledge Base: default
  API Address: http://localhost:8000/api/v1
  Simple Mode: False

Folder Information:
  File Count: 25
  Total Size: 45.67 MB

Starting import...
Import completed!

Import Results:
  Success: True
  Source Folder: C:\Users\YourName\Documents\KB
  Total Files Found: 25
  Files Processed: 23
  Files Skipped: 2
  Files Failed: 0

Processed Documents:
  - document1.pdf
  - document2.docx
  - notes.md
  ...

Import completed! You can now query the knowledge base.
```

### Import Using API

If you prefer to use the API directly to import folders:

#### Simple Import (Recommended)

```bash
curl -X POST "http://localhost:8000/api/v1/import-local-folder" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "C:\\Users\\YourName\\Documents\\KB",
    "user_id": "default",
    "kb_name": "default",
    "acl": {
      "read": ["default"],
      "write": ["default"]
    }
  }'
```

#### Advanced Import (requires creating user and knowledge base first)

```bash
# 1. Create user knowledge base
curl -X POST "http://localhost:8000/api/v1/users/john/kbs" \
  -d "kb_name=my_documents"

# 2. Import folder
curl -X POST "http://localhost:8000/api/v1/users/john/kbs/my_documents/import-folder" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "C:\\Documents\\Technical",
    "acl": {
      "read": ["john", "team"],
      "write": ["john"]
    }
  }'
```

### Supported File Formats

Folder import supports the following file formats:
- PDF (.pdf)
- Word (.docx)
- Markdown (.md)
- Text (.txt)
- HTML (.html)

### Import Best Practices

1. **Folder Organization**: Group related documents in the same folder
2. **File Naming**: Use clear file names for easy identification
3. **File Size**: Individual files should not exceed 100MB
4. **Batch Import**: For large numbers of files, import in batches
5. **Permission Settings**: Set ACL permissions as needed

### Troubleshooting

**Common import failure reasons**:
- Folder path does not exist
- API service not started
- File format not supported
- File corrupted or encrypted

**Solutions**:
1. Confirm the folder path is correct
2. Check API service status: `curl http://localhost:8000/health`
3. Review error messages from the import script
4. Check if files can be opened normally

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