# Installation Guide - RAG Knowledge Base

**Current Version**: v0.6.0 (Stable)  
**Release Date**: 2026-09-04

> **Version Note**: v0.6.0 is a major enterprise RAG optimization release featuring advanced retrieval (BM25 + BGE-Reranker), comprehensive evaluation framework (RAGAS), enhanced knowledge graph, multi-knowledge base system, and performance monitoring.

## System Requirements

### Hardware Requirements
- **CPU**: 4 cores or more recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space for documents and indexes
- **GPU**: Optional (for Ollama acceleration)

### Software Requirements
- **Operating System**: Windows 10/11 (native), Linux/macOS (with modifications)
- **Python**: 3.11 or higher (required for Open WebUI)
- **Ollama**: Latest version for local LLM and embedding models

## Installation Methods

### Method 1: Standard Installation (Recommended)

#### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd 10K_long-doc-RAG-KB
```

#### Step 2: Create Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### Step 3: Install Dependencies
```bash
pip install -e .
```

#### Step 4: Install Ollama
1. Download Ollama from https://ollama.ai
2. Install and run Ollama
3. Verify installation:
   ```bash
   ollama --version
   ```

#### Step 5: Pull Required Models
```bash
ollama serve
ollama pull qwen2.5
ollama pull nomic-embed-text
```

#### Step 6: Configure the System
```bash
copy configs\config.example.yaml configs\config.yaml
copy .env.example .env
```

Edit `configs\config.yaml` and `.env` with your settings.

### Method 2: Development Installation

For developers who want to modify the code:

```bash
# Clone repository
git clone <repository-url>
cd 10K_long-doc-RAG-KB

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Method 3: Docker Installation (Experimental)

```bash
# Build Docker image
docker build -t rag-kb .

# Run container
docker run -p 8000:8000 -p 11434:11434 rag-kb
```

## Ollama Setup

### Installation
1. Download Ollama installer from https://ollama.ai
2. Run the installer
3. Start Ollama service:
   ```bash
   ollama serve
   ```

### Model Selection

**Recommended Models:**
- **LLM**: `qwen2.5` (Chinese/English), `llama3.1` (English), `deepseek-r1` (Reasoning)
- **Embedding**: `nomic-embed-text` (Fast), `mxbai-embed-large` (High quality)

**Pull Models:**
```bash
# Chinese/English LLM
ollama pull qwen2.5

# English LLM
ollama pull llama3.1

# Reasoning LLM
ollama pull deepseek-r1

# Fast embedding
ollama pull nomic-embed-text

# High-quality embedding
ollama pull mxbai-embed-large
```

### GPU Acceleration
If you have an NVIDIA GPU:

1. Install NVIDIA drivers
2. Install CUDA toolkit
3. Ollama will automatically use GPU if available

Verify GPU usage:
```bash
ollama run qwen2.5
# Check GPU utilization in Task Manager
```

## Open WebUI Installation (Optional)

### Installation
```bash
pip install open-webui
```

### Start Open WebUI
```bash
open-webui serve
```

Access at: http://localhost:8080

### Configure Open WebUI
1. Open http://localhost:8080
2. Go to Settings → Connections
3. Configure:
   - **OpenAI API Base URL**: `http://localhost:8000/api/v1`
   - **API Key**: `not-needed-for-local`
   - **Default Model**: `rag-kb-pipeline`

## New Features in v0.4.0

### Knowledge Management Features
v0.4.0 introduces advanced knowledge management capabilities:

- **Automatic Document Classification**: Intelligent categorization (technical, product, project, business, legal)
- **Smart Tagging**: Automatic tag extraction from document content
- **Entity Recognition**: Identify technologies, dates, emails, and URLs
- **Quality Analysis**: Document quality assessment with improvement suggestions
- **Batch Operations**: Efficient multi-document processing
- **Knowledge Management Interface**: Unified interface at `/knowledge-manager`

### New API Endpoints
- `POST /api/v1/knowledge/organize` - Document organization and classification
- `POST /api/v1/knowledge/batch-operation` - Batch document operations
- `GET /knowledge-manager` - Knowledge management interface

## Configuration

### Environment Variables
Create `.env` file from `.env.example`:

```bash
# Application
RAGKB_APP_NAME=rag-kb
RAGKB_DATA_DIR=./data
RAGKB_LIGHTRAG_WORKING_DIR=./lightrag_db
RAGKB_LOG_LEVEL=INFO

# Embedding
RAGKB_EMBEDDING_PROVIDER=ollama
RAGKB_EMBEDDING_BASE_URL=http://localhost:11434
RAGKB_EMBEDDING_MODEL=nomic-embed-text

# LLM
RAGKB_LLM_PROVIDER=ollama
RAGKB_LLM_BASE_URL=http://localhost:11434
RAGKB_LLM_MODEL=qwen2.5
RAGKB_LLM_TEMPERATURE=0.3
RAGKB_LLM_TOP_P=0.9
RAGKB_LLM_MAX_TOKENS=2048

# LightRAG
RAGKB_LIGHTRAG_CHUNK_TOKEN_SIZE=1200
RAGKB_LIGHTRAG_MAX_TOKEN=4096
RAGKB_LIGHTRAG_QUERY_MODE=hybrid
RAGKB_LIGHTRAG_ENABLE_LLM_CACHE=true
```

### YAML Configuration
Edit `configs/config.yaml`:

```yaml
app:
  name: rag-kb
  data_dir: ./data
  lightrag_working_dir: ./lightrag_db
  log_level: INFO

embedding:
  provider: ollama
  base_url: http://localhost:11434
  model: nomic-embed-text

llm:
  provider: ollama
  base_url: http://localhost:11434
  model: qwen2.5
  temperature: 0.3
  top_p: 0.9
  max_tokens: 2048

lightrag:
  working_dir: ./lightrag_db
  chunk_token_size: 1200
  max_token: 4096
  query_mode: hybrid
  enable_llm_cache: true

security:
  default_acl:
    dept: []
    level: ['Internal']
```

## Verification

### Test Installation
```bash
# Run test suite
pytest

# Test health endpoint
curl http://localhost:8000/health

# Test Ollama connection
ollama list
```

### Expected Results
- All tests should pass
- Health endpoint returns `{"status": "ok"}`
- Ollama lists pulled models

## Troubleshooting

### Python Version Issues
**Problem**: Open WebUI requires Python 3.11+
**Solution**: 
```bash
# Check Python version
python --version

# Install correct Python version from python.org
# Create new virtual environment with correct version
python3.11 -m venv .venv
```

### Ollama Connection Issues
**Problem**: Cannot connect to Ollama
**Solution**:
```bash
# Check if Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### Dependency Installation Failures
**Problem**: pip install fails
**Solution**:
```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies individually
pip install pydantic fastapi uvicorn

# Use wheel files for Windows
pip install --only-binary :all: <package-name>
```

### Memory Issues
**Problem**: Out of memory during indexing
**Solution**:
- Reduce `lightrag_chunk_token_size` in config
- Use smaller LLM models
- Process documents in smaller batches
- Close other applications

### Permission Issues
**Problem**: Cannot write to data directories
**Solution**:
```powershell
# Run PowerShell as Administrator
# Or change directory permissions
icacls "data" /grant Users:F
```

## Uninstallation

### Remove Application
```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
Remove-Item -Recurse -Force .venv

# Remove application files
Remove-Item -Recurse -Force 10K_long-doc-RAG-KB
```

### Remove Ollama Models
```bash
# List models
ollama list

# Remove specific model
ollama rm qwen2.5

# Remove all models
ollama rm $(ollama list | awk '{print $1}')
```

### Remove Open WebUI
```bash
pip uninstall open-webui
```

## Upgrading

### Upgrade Application
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -e .

# Restart services
.\scripts\start.ps1
```

### Upgrade Ollama Models
```bash
# Update Ollama
# Download latest installer from ollama.ai

# Pull latest model versions
ollama pull qwen2.5
ollama pull nomic-embed-text
```

## Next Steps

After installation:

1. Read the [User Guide](USER_GUIDE.md)
2. Import your first documents
3. Configure access control
4. Set up monitoring and logging
5. Customize for your specific use case

## Support

- **Documentation**: See `/docs` directory
- **Issues**: Report via GitHub Issues
- **Community**: Join our Discord/Slack community