# RAG KB - 万级长文档知识库系统

企业级 RAG 知识库系统，支持万级长文档的高效检索、知识图谱可视化和权限管理。

**当前版本**: v0.5.0  
**发布日期**: 2026-08-23

## 🌟 核心特性

- **🚀 高性能检索**: LightRAG 混合检索 + BM25 稀疏检索 + Cross-Encoder 重排序
- **🔐 企业级安全**: RBAC/ACL 权限控制，支持部门级和密级管理
- **📊 知识图谱**: 基于 LightRAG 的自动知识图谱提取和可视化
- **🔄 增量更新**: 基于文件哈希的智能增量更新机制
- **🎯 精准分块**: 结构化语义分块 + 父子块策略
- **📈 可观测性**: 内置 RAGAS 评估指标和性能监控
- **🖥️ 现代化前端**: 智能对话界面、知识图谱可视化、Open WebUI 集成
- **🛠️ 开箱即用**: 统一管理脚本，一键启动配置
- **📊 性能优化**: 多级缓存策略，支持万级文档处理
- **🔍 全面监控**: 系统指标跟踪，慢查询日志，性能分析
- **💬 智能对话**: 多轮对话支持，对话历史管理，上下文保持
- **🎯 高级搜索**: 时间范围、文档类型、自定义元数据过滤
- **🕸️ 知识图谱**: 交互式图谱可视化，多种布局算法
- **📊 质量管理**: 用户反馈收集，统计分析，改进建议
- **🎛️ 统一管理**: 单一管理脚本，简化部署和运维

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端层 (Frontend)                        │
│              Open WebUI + 自定义管理界面                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   API 层 (FastAPI)                           │
│         RESTful API + OpenAI-compatible 接口                  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  检索层 (Retrieval)                           │
│  LightRAG (混合检索) + BM25 (稀疏检索) + Reranker (重排序)    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 处理层 (Processing)                           │
│  解析器 → 清洗 → 分块 → 向量化 → 索引构建                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 存储层 (Storage)                              │
│  LightRAG (向量+图) + BM25 索引 + 文档存储                    │
└─────────────────────────────────────────────────────────────┘
```

## 📋 系统要求

- **Python**: 3.11+ (必需)
- **操作系统**: Windows 10/11 (原生支持)，Linux/macOS
- **内存**: 建议 8GB+ (处理万级文档)，16GB+ 更佳
- **存储**: 建议 50GB+ 可用空间，SSD 推荐
- **Ollama**: 用于本地 LLM 和 Embedding
- **可选**: NVIDIA GPU (用于重排序加速)

## 🚀 快速开始

### 1. 安装依赖

```powershell
# 克隆项目
git clone <repository-url>
cd 10K_long-doc-RAG-KB

# 运行安装脚本 (Windows PowerShell)
.\scripts\install.ps1

# 或使用批处理文件
.\scripts\install.bat
```

### 2. 安装 Ollama

```powershell
# 下载并安装 Ollama
# 访问: https://ollama.ai/

# 启动 Ollama 服务
ollama serve

# 下载所需模型 (新终端)
ollama pull nomic-embed-text  # Embedding 模型
ollama pull qwen3.5:4b       # LLM 模型 (推荐)
# 或者使用其他模型: ollama pull gemma4:e4b
```

### 3. 配置系统

编辑 `configs/config.yaml`:

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
  model: qwen3.5:4b
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

### 4. 启动系统

```powershell
# 使用统一管理脚本启动
.\manage.ps1 start

# 其他管理命令
.\manage.ps1 stop      # 停止系统
.\manage.ps1 restart   # 重启系统
.\manage.ps1 status    # 查看系统状态
.\manage.ps1 upgrade   # 升级系统
.\manage.ps1 open      # 在浏览器中打开系统
.\manage.ps1 help      # 显示帮助信息
```

### 5. 访问系统

- **统一知识管理**: http://localhost:8000/knowledge-manager
- **智能对话界面**: http://localhost:8000/chat-ui
- **知识图谱可视化**: http://localhost:8000/graph-ui
- **简易管理界面**: http://localhost:8000/
- **API 文档**: http://localhost:8000/docs
- **管理界面**: http://localhost:8000/docs/docs-ui
- **集成界面**: http://localhost:8000/rag-kb-integration
- **健康检查**: http://localhost:8000/health
- **性能指标**: http://localhost:8000/metrics

## 📚 使用指南

### 快速测试

系统提供了完整的测试脚本用于验证功能：

```powershell
# 测试文档导入功能
python scripts/test_ingestion.py

# 测试混合搜索功能
python scripts/test_hybrid_search.py

# 测试知识图谱提取
python scripts/test_graph_extraction.py

# 端到端业务流程验证 (推荐)
python scripts/end_to_end_test.py
```

端到端测试会验证：
- ✅ Ollama 服务可用性
- ✅ 配置文件完整性
- ✅ 目录结构正确性
- ✅ Python 依赖完整性
- ✅ API 服务器启动
- ✅ 健康检查端点
- ✅ 性能指标端点
- ✅ 文档导入功能
- ✅ 搜索功能
- ✅ ACL 权限过滤
- ✅ 知识图谱端点

# 运行完整测试套件
pytest tests/ -v
```

### 🎯 新功能亮点 (v0.5.0)

#### 🎛️ 统一知识管理平台
- **一站式管理**: 整合上传、管理、检索功能到单一界面
- **智能分类**: 自动文档分类和标签提取
- **拖拽上传**: 支持拖拽文件上传和实时处理反馈
- **知识导航**: 左侧知识树和标签云导航
- **批量操作**: 高效的批量处理功能
- **质量分析**: 文档质量评估和改进建议

#### 🎛️ 统一管理脚本
- **单一入口**: 只需记住一个命令 `.\manage.ps1`
- **完整功能**: 启动、停止、重启、状态检查、升级、安装
- **用户友好**: 清晰的操作提示和错误处理
- **简化部署**: 消除了多个脚本的混乱

#### 💬 智能对话界面
- **多轮对话**: 支持连续对话，保持上下文
- **对话历史**: 本地存储对话历史，支持历史查看
- **实时反馈**: 每个回答都有有用/无用反馈按钮
- **搜索设置**: 可调节搜索模式和结果数量

#### 🔍 高级搜索功能
- **时间范围过滤**: 按日期范围过滤搜索结果
- **文档类型过滤**: 按文件类型（PDF、DOCX等）过滤
- **自定义元数据**: 支持任意元数据字段过滤
- **相关性评分**: 显示文档相关性百分比

#### 🕸️ 知识图谱可视化
- **交互式图谱**: 使用Cytoscape.js实现交互式浏览
- **多种布局**: 力导向、环形、网格、同心圆布局
- **实体搜索**: 实时搜索和过滤实体
- **图谱统计**: 显示节点数、边数、网络密度

#### 📊 质量管理系统
- **反馈收集**: 完整的用户反馈收集系统
- **统计分析**: 实时统计正面/负面反馈
- **趋势分析**: 分析反馈趋势和质量变化
- **改进建议**: 基于反馈提供系统改进建议

### 文档导入

```bash
# 单文件导入
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -F "file=@document.pdf" \
  -F "dept=Engineering" \
  -F "level=Internal"

# 批量导入文件夹
curl -X POST "http://localhost:8000/api/v1/import-local-folder" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/path/to/documents", "user_id": "default", "kb_name": "default"}'
```

### 智能检索

```bash
# 基础检索
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"q": "机器学习基础", "dept": "Engineering", "level": "Internal", "top_k": 8}'

# OpenAI 兼容接口
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "什么是深度学习？"}],
    "user_roles": {"dept": ["Engineering"], "level": ["Internal"]}
  }'
```

### 知识图谱

```bash
# 获取知识图谱数据
curl "http://localhost:8000/api/v1/users/default/kbs/default/graph"
```

## 🔧 高级配置

### 混合检索配置

系统支持三种检索模式：

- **hybrid**: LightRAG 混合检索 (默认)
- **bm25_only**: 仅 BM25 稀疏检索
- **vector_only**: 仅向量检索

```python
from rag_kb.retrieval.hybrid_search import HybridSearchEngine

# 创建混合检索引擎
hybrid_engine = HybridSearchEngine(
    enable_reranking=True,
    reranker_device='cpu'  # 或 'cuda' 如果有 GPU
)

# 执行检索
results = hybrid_engine.search(
    query="机器学习算法",
    top_k=10,
    mode='hybrid',
    bm25_weight=0.3,
    vector_weight=0.7,
    user_roles={'dept': ['Engineering'], 'level': ['Internal']}
)
```

### 权限管理

系统支持基于 RBAC 的权限控制：

```python
from rag_kb.security.acl import ACLContext

# 创建权限上下文
with ACLContext(user_roles={'dept': ['Engineering'], 'level': ['Internal']}) as acl:
    # 检查文档访问权限
    if acl.can_access(document):
        # 处理文档
        pass
    
    # 获取 LightRAG 过滤字符串
    filter_string = acl.get_filter_string()
```

### 增量更新

```python
from rag_kb.ingest.incremental import plan_incremental_update

# 规划增量更新
to_add, to_delete, to_update = plan_incremental_update(docs_dir=Path('./documents'))

print(f"新增文件: {len(to_add)}")
print(f"删除文件: {len(to_delete)}")
print(f"更新文件: {len(to_update)}")
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_ragas_eval.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=src/rag_kb --cov-report=html
```

## 📊 评估指标

系统内置 RAGAS 评估框架：

- **检索指标**: Precision, Recall, F1, MRR, Hit Rate
- **上下文指标**: Context Relevance, Context Utilization
- **答案指标**: Answer Relevance, Answer Completeness
- **忠实度指标**: Faithfulness, Groundedness

```python
from tests.test_ragas_eval import RAGASEvaluator

evaluator = RAGASEvaluator()

# 综合评估
evaluation = evaluator.comprehensive_evaluation(
    query="什么是机器学习？",
    retrieved_results=search_results,
    contexts=retrieved_contexts,
    answer=generated_answer,
    ground_truth=["doc1", "doc2"]
)

print(f"总体评分: {evaluation['overall_score']:.2f}")
```

## 🛠️ 开发指南

### 项目结构

```
rag-kb/
├── configs/                 # 配置文件
├── data/                   # 数据目录
│   ├── uploads/           # 上传文件
│   ├── users/             # 用户数据
│   └── bm25_cache/        # BM25 缓存
├── scripts/               # 脚本文件
│   ├── start.ps1         # PowerShell 启动脚本
│   ├── install.ps1       # 安装脚本
│   └── start.bat         # 批处理启动脚本
├── src/rag_kb/           # 源代码
│   ├── api/              # API 层
│   ├── chunkers/         # 分块器
│   ├── ingest/           # 数据处理
│   ├── lightrag/         # LightRAG 集成
│   ├── parsers/          # 文档解析
│   ├── retrieval/        # 检索引擎
│   ├── security/         # 安全模块
│   └── utils/            # 工具函数
├── static/               # 静态文件
├── tests/                # 测试文件
└── pyproject.toml        # 项目配置
```

### 添加新的解析器

```python
# src/rag_kb/parsers/custom_parser.py
from rag_kb.parsers.base import BaseParser
from rag_kb.models import Document

class CustomParser(BaseParser):
    supported_ext = ('.custom',)
    
    def parse(self, path):
        # 实现解析逻辑
        content = self._extract_text(path)
        return Document(
            doc_id=self._generate_id(content),
            title=path.stem,
            source=str(path),
            content=content,
            metadata={'parser': 'custom'}
        )
```

### 自定义检索策略

```python
# src/rag_kb/retrieval/custom_search.py
from rag_kb.retrieval.hybrid_search import HybridSearchEngine

class CustomSearchEngine(HybridSearchEngine):
    def search(self, query, **kwargs):
        # 自定义检索逻辑
        results = super().search(query, **kwargs)
        
        # 添加自定义后处理
        results = self._custom_post_processing(results)
        
        return results
```

## 🔍 故障排除

### Ollama 连接失败

```bash
# 检查 Ollama 服务状态
curl http://localhost:11434/api/tags

# 重启 Ollama
ollama serve
```

### 内存不足

```yaml
# 在 config.yaml 中调整 LightRAG 参数
lightrag:
  chunk_token_size: 800  # 减小块大小
  max_token: 2048        # 减少最大 token 数
```

### 检索速度慢

```python
# 禁用重排序以提高速度
hybrid_engine = HybridSearchEngine(enable_reranking=False)

# 或使用 BM25 模式
results = hybrid_engine.search(query, mode='bm25_only')
```

### 测试失败

```bash
# 重新安装依赖
pip install -e .[all]

# 运行特定测试
pytest tests/test_chunking.py -v

# 查看详细错误信息
pytest tests/ -v -s
```

## 📊 测试覆盖

系统包含完整的测试套件：

- **单元测试**: 核心组件功能验证
- **集成测试**: 多组件协作测试
- **RAGAS评估**: 检索质量评估
- **性能测试**: 负载和压力测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试类别
pytest tests/test_ragas_eval.py -v
pytest tests/test_chunking.py -v

# 生成覆盖率报告
pytest tests/ --cov=src/rag_kb --cov-report=html
```

## 📚 相关文档

- **[实施框架](RAG_KB_Implementation_Framework.html)** - 详细的技术实施指南
- **[架构设计](万级长文档 RAG 知识库系统架构与前端设计指南.html)** - 系统架构和前端设计
- **[构建方案](海量长文档（万级）知识库构建方案.html)** - 工程化构建思路
- **[落地指南](海量长文档企业级 RAG 知识库落地指南.html)** - 企业级实施指南
- **[性能调优](docs/PERFORMANCE_TUNING.md)** - 性能优化详细指南
- **[实施总结](docs/IMPLEMENTATION_SUMMARY.md)** - 完整实施总结

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 🙏 致谢

- [LightRAG](https://github.com/HKUDS/LightRAG) - 轻量级 RAG 框架
- [Ollama](https://ollama.ai/) - 本地 LLM 运行环境
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [Open WebUI](https://openwebui.com/) - 开源 AI 界面

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 文档: [项目 Wiki]

---

**注意**: 本系统为企业级 RAG 知识库解决方案，适合处理万级长文档。在生产环境使用前，请确保充分测试并根据实际需求调整配置参数。