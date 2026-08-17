# RAG 知识库 - 10K 长文档处理

企业级 RAG（检索增强生成）知识库系统，专为处理和查询 10,000+ 长文档而设计，采用 LightRAG 图增强检索技术。

[English Documentation](README.md) | [中文文档](README_CN.md)

## 特性

- **结构感知切片**：保留层次结构和上下文的语义文档分割
- **LightRAG 集成**：支持 hybrid/local/global/naive 查询模式的图增强检索
- **多格式解析**：支持 PDF、Word、HTML 和 Markdown 文档
- **数据清洗**：内置去重和 PII 掩码
- **安全性**：支持文档访问控制的 RBAC/ACL
- **增量更新**：高效的文档更新，无需完全重建索引
- **Windows 原生**：专为 Windows 部署设计，使用 Ollama 本地模型
- **Open WebUI 集成**：现代化的聊天界面用于查询
- **FastAPI 后端**：提供 OpenAI 兼容端点的 RESTful API

## 架构

系统遵循分层管道架构：

1. **数据导入和清洗**：解析文档，去重，PII 掩码
2. **语义切片**：保留父子关系的结构感知分割
3. **LightRAG 索引**：使用元数据注入构建向量+图索引
4. **多模式查询**：结合向量相似性和图关系的混合检索
5. **生成**：LLM 驱动的答案生成，带来源引用
6. **前端交付**：Open WebUI 聊天界面，支持流式响应

## 安装

### 前置要求

- Python 3.9 或更高版本
- Ollama 用于本地 LLM 和嵌入模型
- Windows 10/11（原生部署）

### 设置

1. **克隆仓库**：
   ```bash
   git clone <repository-url>
   cd 10K_long-doc-RAG-KB
   ```

2. **创建虚拟环境**：
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **安装依赖**：
   ```bash
   pip install -e .
   ```

4. **安装 Ollama 模型**：
   ```bash
   ollama serve
   ollama pull qwen2.5
   ollama pull nomic-embed-text
   ```

5. **配置设置**：
   ```bash
   copy configs\config.example.yaml configs\config.yaml
   # 编辑 config.yaml 配置您的设置
   ```

## 使用

### 启动服务

使用提供的 PowerShell 脚本启动所有服务：

```powershell
.\scripts\start.ps1
```

这将启动：
- Ollama 服务（localhost:11434）
- FastAPI 后端（localhost:8000）
- Open WebUI（localhost:8080，如果已安装）

### 手动启动

单独启动服务：

```powershell
# 启动 Ollama
ollama serve

# 启动 FastAPI 后端
python -m uvicorn rag_kb.api.main:app --reload --host 0.0.0.0 --port 8000

# 启动 Open WebUI（可选）
open-webui serve
```

### 批量文档导入

将文档放在 `data/raw/` 目录中并运行：

```bash
python scripts\ingest_bulk.py
```

### API 端点

- `GET /health` - 健康检查
- `POST /api/v1/ingest` - 上传和索引文档
- `POST /api/v1/search` - 搜索知识库
- `POST /api/v1/chat/completions` - OpenAI 兼容的聊天端点
- `GET /docs` - 交互式 API 文档

### 配置

编辑 `configs/config.yaml` 来自定义：

- **嵌入设置**：Ollama vs sentence-transformers，模型选择
- **LLM 设置**：本地 Ollama vs 远程 OpenAI 兼容 API
- **LightRAG 设置**：块大小，查询模式，缓存
- **安全设置**：默认 ACL 策略

## 项目结构

```
rag-kb-project/
├── configs/                 # 配置文件
├── data/                    # 数据存储
│   ├── raw/                # 源文档
│   ├── uploads/            # 上传的文件
│   └── category_dbs/       # 分类特定索引
├── docs/                    # 文档
├── scripts/                 # 实用脚本
│   ├── start.ps1           # 服务启动脚本
│   └── ingest_bulk.py      # 批量导入脚本
├── src/rag_kb/             # 源代码
│   ├── api/                # FastAPI 应用
│   ├── chunkers/           # 文档切片
│   ├── ingest/             # 数据导入管道
│   ├── lightrag/           # LightRAG 集成
│   ├── parsers/            # 文档解析器
│   ├── security/           # ACL 和 RBAC
│   └── utils/              # 工具
└── tests/                  # 测试套件
```

## 开发

### 运行测试

```bash
pytest
```

### 代码质量

项目遵循以下原则：
- **MVP 优先**：核心功能优先于优化
- **接口优先**：在实现之前定义接口
- **测试驱动**：用测试验证每个阶段
- **安全设计**：ACL 和 RBAC 内置到每一层
- **可观察**：结构化日志和指标

## 阶段实施

实施遵循 8 个阶段：

1. **Phase 0**：项目骨架和依赖 ✅
2. **Phase 1**：数据导入和解析 ✅
3. **Phase 2**：语义切片 ✅
4. **Phase 3**：LightRAG 集成 ✅
5. **Phase 4**：查询模式和生成 ✅
6. **Phase 5**：FastAPI 后端和 Open WebUI ✅
7. **Phase 6**：测试和评估 ✅
8. **Phase 7**：增量更新和安全 ✅
9. **Phase 8**：高级 LightRAG 功能（未来）

## 技术栈

- **后端**：FastAPI, Python 3.9+
- **RAG 引擎**：LightRAG (lightrag-hku)
- **向量存储**：NanoVectorDB（内置 LightRAG）
- **图存储**：NetworkX（内置 LightRAG）
- **LLM**：Ollama (qwen2.5, llama3.1, deepseek-r1)
- **嵌入**：Ollama (nomic-embed-text, bge-m3)
- **前端**：Open WebUI
- **解析**：PyMuPDF, pdfplumber, python-docx
- **测试**：pytest

## 安全性

- **PII 掩码**：自动检测和掩码敏感信息
- **ACL 支持**：文档级访问控制
- **RBAC**：基于角色的查询权限
- **审计日志**：跟踪所有访问和修改

## 性能

- **混合搜索**：结合向量相似性和图关系
- **父子块切片**：高精度检索，保留上下文
- **增量更新**：高效的文档更新，无需完全重建索引
- **缓存**：LLM 响应缓存，用于重复查询

## 限制

- LightRAG 使用本地存储（NetworkX + NanoVectorDB + JSON）
- 对于 10K+ 密集图文档，考虑外部向量/图数据库
- Windows 特定部署（尽管核心 Python 代码是跨平台的）

## 未来增强

- 外部向量数据库集成（Qdrant, Milvus）
- 高级图数据库支持（Neo4j）
- 重排序模型以提高精度
- 多语言支持
- 高级评估指标（RAGAS 集成）

## 贡献

这是遵循 RAG_KB_Plan.html 和 RAG_KB_Implementation_Framework.html 规范的企业级实施。

## 许可证

在此指定您的许可证。

## 参考资料

- [RAG_KB_Plan.html](./RAG_KB_Plan.html) - 规划和设计文档
- [RAG_KB_Implementation_Framework.html](./RAG_KB_Implementation_Framework.html) - 实施框架
- [LightRAG](https://github.com/HKUDS/LightRAG) - 图增强 RAG 引擎
- [Open WebUI](https://github.com/open-webui/open-webui) - 聊天界面

## 支持

如有问题和疑问，请参考项目文档或在仓库中创建 issue。

## 文档

- [安装指南](docs/INSTALLATION_CN.md)
- [用户指南](docs/USER_GUIDE_CN.md)
- [开发者指南](docs/DEVELOPER_CN.md)
- [升级指南](docs/UPGRADE_GUIDE_CN.md)
- [发布说明](docs/RELEASE_NOTES_CN.md)