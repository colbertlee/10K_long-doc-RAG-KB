# 用户指南 - RAG 知识库

## 目录
1. [快速开始](#快速开始)
2. [基本使用](#基本使用)
3. [文档管理界面](#文档管理界面)
4. [文档导入](#文档导入)
5. [本地文件夹导入](#本地文件夹导入)
6. [查询知识库](#查询知识库)
7. [使用 Open WebUI](#使用-open-webui)
8. [配置](#配置)
9. [故障排除](#故障排除)

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

## 文档管理界面

RAG知识库提供了一个现代化的Web界面，用于文档管理，包括文档上传、文件夹导入和文档管理功能。

### 访问文档管理界面

启动服务后，访问：
```
http://localhost:8000/docs/docs-ui
```

### 界面功能

文档管理界面包含三个主要功能标签：

#### 1. 📄 文档上传
- 支持批量文件上传
- 拖拽上传支持
- 实时上传进度显示
- 支持PDF、Word、Markdown、Text格式

#### 2. 📁 文件夹导入
- 本地文件夹路径输入
- 一键导入整个文件夹
- 导入进度和统计显示
- 自动跳过重复文件

#### 3. 📋 文档管理
- 查看知识库中的文档列表
- 文档统计信息
- 用户和知识库管理

### 使用文档管理界面

#### 上传文档
1. 访问 http://localhost:8000/docs/docs-ui
2. 选择"文档上传"标签
3. 输入用户ID和知识库名称
4. 点击上传区域或拖拽文件
5. 点击"开始上传"

#### 导入文件夹
1. 选择"文件夹导入"标签
2. 输入用户ID和知识库名称
3. 输入本地文件夹路径（如：`C:\Users\YourName\Documents\KB`）
4. 点击"开始导入"

#### 管理文档
1. 选择"文档管理"标签
2. 输入用户ID和知识库名称
3. 点击"加载文档列表"
4. 查看文档统计和列表

### 与Open WebUI集成

文档管理界面可以与Open WebUI无缝集成使用：

1. **启动服务**: `.\scripts\start.ps1`
2. **访问Open WebUI**: http://localhost:8080
3. **配置连接**: 设置 → 连接 → API地址: `http://localhost:8000/api/v1`
4. **访问文档管理**: 在Open WebUI中添加自定义链接到文档管理界面
5. **导入文档**: 使用文档管理界面导入文档
6. **查询文档**: 返回Open WebUI进行RAG查询

详细的集成指南请参考 [Open WebUI集成指南](OPENWEBUI_INTEGRATION_CN.md)。

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

## 本地文件夹导入

### 使用PowerShell脚本导入

RAG知识库提供了便捷的本地文件夹导入功能，可以将您电脑上的整个文件夹直接导入到知识库中。

#### 基本用法

```powershell
# 导入本地文件夹（简单模式）
.\scripts\import_local_folder.ps1 -FolderPath "C:\Users\YourName\Documents\KB"

# 指定用户和知识库名称
.\scripts\import_local_folder.ps1 -FolderPath "C:\Documents\Technical" -UserId "john" -KbName "tech_docs"

# 使用简单模式（自动创建用户和知识库）
.\scripts\import_local_folder.ps1 -FolderPath "C:\Documents" -SimpleMode
```

#### 参数说明

- **-FolderPath**: 要导入的本地文件夹路径（必需）
- **-UserId**: 用户ID（默认: "default"）
- **-KbName**: 知识库名称（默认: "default"）
- **-ApiUrl**: API地址（默认: "http://localhost:8000/api/v1"）
- **-SimpleMode**: 简单模式，自动创建用户和知识库

#### 导入过程

脚本会自动：
1. 扫描指定文件夹中的所有文件
2. 统计文件数量和总大小
3. 将文件复制到知识库的raw目录
4. 处理每个文档（解析、清洗、切片）
5. 显示导入结果统计

#### 导入结果示例

```
=== RAG知识库本地文件夹导入 ===

导入配置:
  文件夹: C:\Users\YourName\Documents\KB
  用户ID: default
  知识库: default
  API地址: http://localhost:8000/api/v1
  简单模式: False

文件夹信息:
  文件数量: 25
  总大小: 45.67 MB

开始导入...
导入完成!

导入结果:
  成功: True
  源文件夹: C:\Users\YourName\Documents\KB
  发现文件总数: 25
  处理文件数: 23
  跳过文件数: 2
  失败文件数: 0

处理的文档:
  - document1.pdf
  - document2.docx
  - notes.md
  ...

导入完成! 您现在可以查询知识库了。
```

### 使用API导入文件夹

如果您更喜欢使用API直接导入文件夹：

#### 简单导入（推荐）

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

#### 高级导入（需要先创建用户和知识库）

```bash
# 1. 创建用户知识库
curl -X POST "http://localhost:8000/api/v1/users/john/kbs" \
  -d "kb_name=my_documents"

# 2. 导入文件夹
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

### 支持的文件格式

文件夹导入支持以下文件格式：
- PDF (.pdf)
- Word (.docx)
- Markdown (.md)
- 文本 (.txt)
- HTML (.html)

### 导入最佳实践

1. **文件夹组织**: 将相关文档放在同一文件夹中
2. **文件命名**: 使用清晰的文件名便于识别
3. **文件大小**: 单个文件建议不超过100MB
4. **批量导入**: 大量文件建议分批导入
5. **权限设置**: 根据需要设置ACL权限

### 故障排除

**导入失败常见原因**：
- 文件夹路径不存在
- API服务未启动
- 文件格式不支持
- 文件损坏或加密

**解决方法**：
1. 确认文件夹路径正确
2. 检查API服务状态：`curl http://localhost:8000/health`
3. 查看导入脚本的错误信息
4. 检查文件是否可以正常打开

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