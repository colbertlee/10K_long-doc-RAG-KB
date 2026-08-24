# 用户指南 - RAG 知识库

## 目录
1. [快速开始](#快速开始)
2. [基本使用](#基本使用)
3. [文档导入](#文档导入)
4. [知识管理功能 (v0.4.0)](#知识管理功能-v040)
5. [查询知识库](#查询知识库)
6. [使用 Open WebUI](#使用-open-webui)
7. [配置](#配置)
8. [故障排除](#故障排除)

## 快速开始

### 前置要求
- Python 3.11 或更高版本
- 已安装并运行 Ollama
- Windows 10/11（用于原生部署）

### 快速启动

1. **安装系统：**
   ```bash
   pip install -e .
   ```

2. **启动 Ollama 并拉取模型：**
   ```bash
   ollama serve
   ollama pull qwen2.5
   ollama pull nomic-embed-text
   ```

3. **启动服务：**
   ```powershell
   .\scripts\start.ps1
   ```

4. **访问界面：**
   - API: http://localhost:8000
   - API 文档: http://localhost:8000/docs
   - Open WebUI: http://localhost:8080（如果已安装）

## 基本使用

### 健康检查
验证系统是否正常运行：
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{"status": "ok"}
```

## 文档导入

### 单个文档上传

通过 API 上传文档：
```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -F "file=@document.pdf" \
  -F "dept=工程部" \
  -F "level=内部"
```

响应：
```json
{
  "doc_id": "abc123...",
  "title": "document",
  "pages": 15
}
```

### 批量文档导入

1. 将文档放入 `data/raw/` 目录
2. 运行批量导入脚本：
   ```bash
   python scripts\ingest_bulk.py
   ```

支持的格式：
- PDF (.pdf)
- Word (.docx)
- Markdown (.md)
- 文本 (.txt)

### 访问控制

在导入时设置访问控制：
- `dept`：部门（如"工程部"、"销售部"）
- `level`：访问级别（如"内部"、"机密"）

## 知识管理功能 (v0.4.0)

### 知识组织 API

知识组织 API 提供自动文档分类、智能标签和质量分析功能。

#### 文档组织

对文档进行自动分类和组织：
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/organize" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Python是一种编程语言，广泛应用于机器学习和人工智能领域。",
    "filename": "tech_doc.txt",
    "metadata": {}
  }'
```

响应：
```json
{
  "organization": {
    "category": "technical",
    "tags": ["Python", "txt", "tech_doc"],
    "entities": {
      "technologies": ["Python"],
      "dates": [],
      "emails": [],
      "urls": []
    },
    "suggested_folder": "技术文档",
    "summary": "Python是一种编程语言，广泛应用于机器学习和人工智能领域。",
    "confidence": 0.8
  },
  "quality_analysis": {
    "overall_score": 0.37,
    "metrics": {
      "completeness": 0.2,
      "readability": 0.4,
      "structure": 0.5
    },
    "suggestions": [
      "建议补充文档元数据（标题、分类、标签）",
      "建议增加文档内容长度",
      "建议优化句子长度，提高可读性"
    ]
  }
}
```

#### 支持的分类

系统自动将文档分类到以下类别：
- **technical**: 技术文档、架构、开发
- **product**: 产品需求、功能、用户体验
- **project**: 项目管理、里程碑、资源
- **business**: 业务流程、政策、战略
- **legal**: 法律文档、合同、合规
- **general**: 其他文档

### 批量操作 API

高效地对多个文档执行批量操作。

#### 批量标签

一次为多个文档添加标签：
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/batch-operation" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "tag",
    "document_ids": ["doc1", "doc2", "doc3"],
    "parameters": {
      "tags": ["技术", "Python"]
    }
  }'
```

响应：
```json
{
  "operation": "tag",
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "doc_id": "doc1",
      "status": "tagged",
      "tags": ["技术", "Python"]
    },
    {
      "doc_id": "doc2",
      "status": "tagged",
      "tags": ["技术", "Python"]
    },
    {
      "doc_id": "doc3",
      "status": "tagged",
      "tags": ["技术", "Python"]
    }
  ]
}
```

#### 支持的操作

- **delete**: 删除多个文档
- **reindex**: 重新索引文档以供搜索
- **tag**: 为文档添加标签
- **move**: 将文档移动到不同分类

### 知识管理界面

访问统一的知识管理界面：
```
http://localhost:8000/knowledge-manager
```

#### 界面功能

- **拖拽上传**: 轻松上传文档
- **实时处理**: 实时处理状态更新
- **批量操作**: 多文档管理
- **质量分析**: 文档质量评估
- **智能建议**: 改进建议

## 查询知识库

### 直接 API 查询

```bash
curl -X POST "http://localhost:8000/api/v1/search?q=系统要求是什么？&dept=工程部&level=内部&top_k=5"
```

### 聊天完成（OpenAI 兼容）

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "系统要求是什么？"}
    ]
  }'
```

## 使用 Open WebUI

### 配置

1. 打开 Open WebUI (http://localhost:8080)
2. 进入设置 → 连接
3. 配置 OpenAI API：
   - **API Base URL**: `http://localhost:8000/api/v1`
   - **API Key**: `not-needed-for-local`
   - **Default Model**: `rag-kb-pipeline`

### 聊天界面

1. 开始新对话
2. 询问关于文档的问题
3. 查看带有来源引用的响应
4. 使用流式传输获取实时答案

### 功能特性
- 实时流式响应
- 来源引用和参考
- 对话历史
- 多语言支持

## 配置

### 环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
# 应用程序
RAGKB_APP_NAME=rag-kb
RAGKB_DATA_DIR=./data
RAGKB_LOG_LEVEL=INFO

# 嵌入模型
RAGKB_EMBEDDING_PROVIDER=ollama
RAGKB_EMBEDDING_MODEL=nomic-embed-text

# 大语言模型
RAGKB_LLM_PROVIDER=ollama
RAGKB_LLM_MODEL=qwen2.5
RAGKB_LLM_TEMPERATURE=0.3

# LightRAG
RAGKB_LIGHTRAG_QUERY_MODE=hybrid
RAGKB_LIGHTRAG_CHUNK_TOKEN_SIZE=1200
```

### YAML 配置

编辑 `configs/config.yaml`：

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

### 模型选择

**Ollama 模型（本地）：**
- LLM: `qwen2.5`, `llama3.1`, `deepseek-r1`
- 嵌入: `nomic-embed-text`, `mxbai-embed-large`

**OpenAI 兼容（远程）：**
```yaml
llm:
  provider: openai
  base_url: https://api.openai.com/v1
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o
```

## 故障排除

### 常见问题

**Ollama 连接失败：**
- 确保 Ollama 正在运行：`ollama serve`
- 检查 Ollama 是否可在 http://localhost:11434 访问

**Python 版本错误：**
- Open WebUI 需要 Python 3.11+
- 使用：`python --version` 检查

**内存问题：**
- 在配置中减少 `lightrag_chunk_token_size`
- 使用更小的 LLM 模型
- 分批处理文档

**索引速度慢：**
- 检查 Ollama GPU 支持
- 减少导入脚本中的批处理大小
- 使用更快的嵌入模型

**权限错误：**
- 确保数据目录具有写入权限
- 如需要，以管理员身份运行 PowerShell

### 调试模式

启用调试日志：
```bash
RAGKB_LOG_LEVEL=DEBUG python -m uvicorn rag_kb.api.main:app --reload
```

### 测试安装

运行测试套件：
```bash
pytest
```

## 高级使用

### 查询模式

- **hybrid**: 结合向量和图搜索（默认）
- **local**: 专注于实体关系
- **global**: 全局摘要和模式
- **naive**: 简单向量搜索

### 增量更新

系统自动检测文件更改：
- 修改的文件会被重新索引
- 删除的文件会从索引中移除
- 新文件会自动添加

### 安全性

**访问控制：**
- 文档在导入时标记 ACL
- 查询根据用户权限过滤
- 内容中的 PII 自动脱敏

**审计跟踪：**
- 所有查询都被记录
- 文档访问被跟踪
- 修改被记录

## 性能优化建议

1. **使用适当的块大小**：大多数文档使用 1200 tokens
2. **启用 LLM 缓存**：设置 `enable_llm_cache: true`
3. **批处理**：对多个文档使用批量导入
4. **GPU 加速**：如果可用，启用 Ollama GPU 支持
5. **定期维护**：定期清理旧索引

## 支持

- **文档**：参见 `/docs` 目录
- **API 参考**：http://localhost:8000/docs
- **问题报告**：通过 GitHub Issues 报告
- **配置**：参见 `configs/config.example.yaml`