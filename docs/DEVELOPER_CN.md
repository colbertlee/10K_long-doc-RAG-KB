# 开发者指南 - RAG 知识库

## 目录
1. [开发环境设置](#开发环境设置)
2. [项目结构](#项目结构)
3. [架构概览](#架构概览)
4. [开发工作流](#开发工作流)
5. [测试](#测试)
6. [代码风格](#代码风格)
7. [贡献指南](#贡献指南)
8. [API 文档](#api-文档)
9. [性能优化](#性能优化)

## 开发环境设置

### 前置要求
- Python 3.11+
- Git
- Ollama（用于本地测试）
- IDE（VS Code、PyCharm 等）

### 设置步骤

1. **克隆和设置：**
   ```bash
   git clone <repository-url>
   cd 10K_long-doc-RAG-KB
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **安装开发工具：**
   ```bash
   # 代码格式化
   pip install black isort
   
   # 代码检查
   pip install flake8 pylint
   
   # 测试
   pip install pytest pytest-cov pytest-asyncio
   
   # Pre-commit hooks
   pip install pre-commit
   pre-commit install
   ```

3. **配置开发环境：**
   ```bash
   copy .env.example .env
   # 编辑 .env 进行开发设置
   ```

4. **启动开发服务：**
   ```bash
   # 终端 1：启动 Ollama
   ollama serve
   
   # 终端 2：启动 FastAPI 热重载
   python -m uvicorn rag_kb.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 项目结构

```
rag-kb-project/
├── configs/                 # 配置文件
│   └── config.example.yaml
├── data/                    # 数据存储
│   ├── raw/                # 源文档
│   ├── uploads/            # 上传文件
│   └── category_dbs/       # 分类特定索引
├── docs/                    # 文档
├── scripts/                 # 实用脚本
├── src/rag_kb/             # 源代码
│   ├── api/                # FastAPI 应用
│   │   ├── main.py        # 主应用
│   │   └── routes.py      # API 路由
│   ├── chunkers/           # 文档切片
│   │   ├── base.py        # 基础切片器接口
│   │   ├── structured.py  # 结构感知切片器
│   │   └── parent_child.py # 父子块切片器
│   ├── ingest/             # 数据导入
│   │   ├── cleaner.py     # 数据清洗
│   │   ├── incremental.py # 增量更新
│   │   └── pipeline.py    # 导入管道
│   ├── lightrag/           # LightRAG 集成
│   │   ├── adapter.py     # LightRAG 适配器
│   │   ├── llm_funcs.py   # LLM 函数
│   │   └── embedding_funcs.py # 嵌入函数
│   ├── parsers/            # 文档解析器
│   │   ├── base.py        # 基础解析器接口
│   │   ├── pdf_pymupdf.py # PyMuPDF 解析器
│   │   ├── pdf_pdfplumber.py # PDFPlumber 解析器
│   │   └── registry.py    # 解析器注册表
│   ├── security/           # 安全工具
│   │   └── acl.py         # ACL 实现
│   ├── utils/              # 工具函数
│   │   └── hashing.py     # 哈希工具
│   ├── config.py          # 配置管理
│   └── models.py          # 领域模型
├── tests/                  # 测试套件
│   ├── conftest.py        # Pytest 配置
│   ├── test_ingest.py     # 导入测试
│   ├── test_chunking.py   # 切片测试
│   ├── test_lightrag.py   # LightRAG 测试
│   └── test_eval.py       # 评估测试
├── pyproject.toml         # 项目元数据
├── requirements.txt       # Python 依赖
└── README.md             # 项目文档
```

## 架构概览

### 分层管道架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端层                                    │
│  (Open WebUI / 直接 API / 自定义客户端)                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      API 层                                   │
│  (FastAPI 路由 / 身份验证 / 速率限制)                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    业务逻辑层                                 │
│  (查询处理 / ACL 过滤 / 响应生成)                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   RAG 引擎层                                  │
│  (LightRAG / 向量搜索 / 图遍历)                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   存储层                                      │
│  (NanoVectorDB / NetworkX / JSON KV / 文件系统)             │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

**1. 文档处理管道**
- **解析器**：从各种格式提取文本和元数据
- **清洗器**：去重、PII 脱敏、内容标准化
- **切片器**：将文档分割为语义块

**2. LightRAG 集成**
- **适配器**：使用自定义 LLM/嵌入函数包装 LightRAG
- **查询模式**：hybrid、local、global、naive
- **索引管理**：插入、更新、删除操作

**3. 安全层**
- **ACL**：文档级访问控制
- **RBAC**：基于角色的权限
- **PII 保护**：自动敏感数据脱敏

**4. API 层**
- **FastAPI**：具有 OpenAI 兼容性的 RESTful API
- **流式传输**：SSE 支持实时响应
- **身份验证**：准备集成身份验证

## 开发工作流

### 功能开发

1. **创建功能分支：**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **实现更改：**
   - 遵循项目约定编写代码
   - 为新功能添加测试
   - 更新文档

3. **本地测试：**
   ```bash
   # 运行测试
   pytest
   
   # 运行覆盖率测试
   pytest --cov=src/rag_kb --cov-report=html
   
   # 运行特定测试
   pytest tests/test_chunking.py
   ```

4. **代码质量检查：**
   ```bash
   # 格式化代码
   black src/ tests/
   isort src/ tests/
   
   # 代码检查
   flake8 src/ tests/
   pylint src/
   ```

5. **提交更改：**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **推送并创建 PR：**
   ```bash
   git push origin feature/your-feature-name
   ```

### 错误修复

1. **创建错误修复分支：**
   ```bash
   git checkout -b fix/bug-description
   ```

2. **重现和修复：**
   - 添加失败的测试用例
   - 修复问题
   - 验证测试通过

3. **使用约定式提交：**
   ```bash
   git commit -m "fix: resolve bug description"
   ```

## 测试

### 测试结构

```python
# 单元测试示例
def test_function():
    # 准备
    input_data = "test"
    
    # 执行
    result = function_to_test(input_data)
    
    # 断言
    assert result == expected_output
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行详细输出
pytest -v

# 运行特定测试文件
pytest tests/test_chunking.py

# 运行特定测试函数
pytest tests/test_chunking.py::test_structure_chunker_preserves_headings

# 运行覆盖率测试
pytest --cov=src/rag_kb --cov-report=html

# 仅运行上次失败的测试
pytest --lf
```

### 测试类别

1. **单元测试**：测试单个函数和类
2. **集成测试**：测试组件交互
3. **端到端测试**：测试完整工作流
4. **性能测试**：测试负载下的系统性能

### 编写测试

```python
import pytest
from rag_kb.chunkers.structured import StructuredChunker
from rag_kb.models import Document

def test_chunker_with_sample_document():
    """使用真实文档测试切片器。"""
    doc = Document(
        doc_id="test123",
        content="# Title\nSome content\n## Section\nMore content"
    )
    
    chunker = StructuredChunker()
    chunks = chunker.chunk(doc)
    
    assert len(chunks) > 0
    assert all(c.chunk_id for c in chunks)
    assert all(c.doc_id == "test123" for c in chunks)
```

## 代码风格

### Python 风格指南

遵循 PEP 8 和以下项目特定约定：

**命名约定：**
- 类：`PascalCase`
- 函数/变量：`snake_case`
- 常量：`UPPER_SNAKE_CASE`
- 私有：`_leading_underscore`

**文档：**
```python
def function_name(param1: str, param2: int) -> bool:
    """函数的简要描述。
    
    Args:
        param1: param1 的描述
        param2: param2 的描述
        
    Returns:
        返回值的描述
        
    Raises:
        ValueError: 如果输入无效
    """
    pass
```

**类型提示：**
```python
from typing import List, Optional, Dict, Any

def process_data(items: List[str]) -> Dict[str, Any]:
    """处理项目列表并返回字典。"""
    result = {}
    for item in items:
        result[item] = len(item)
    return result
```

### Git 提交消息

遵循约定式提交：
- `feat:` 新功能
- `fix:` 错误修复
- `docs:` 文档更改
- `style:` 代码风格更改
- `refactor:` 代码重构
- `test:` 测试更改
- `chore:` 维护任务

## 贡献指南

### 贡献指南

1. **Fork 仓库**
2. **创建功能分支**
3. **进行更改**
4. **添加测试**
5. **更新文档**
6. **提交拉取请求**

### 代码审查流程

1. 自动检查必须通过
2. 至少需要一个批准
3. 解决所有审查意见
4. 根据需要更新文档

### 发布流程

1. 更新 `pyproject.toml` 中的版本
2. 更新 `CHANGELOG.md`
3. 创建发布分支
4. 标记发布
5. 创建 GitHub Release

## API 文档

### 交互式 API 文档

启动服务器并访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API 端点

**健康检查：**
```http
GET /health
```

**文档导入：**
```http
POST /api/v1/ingest
Content-Type: multipart/form-data

{
  "file": <binary>,
  "dept": "工程部",
  "level": "内部"
}
```

**搜索：**
```http
POST /api/v1/search?q=query&dept=工程部&level=内部&top_k=5
```

**聊天完成：**
```http
POST /api/v1/chat/completions
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "您的问题"}
  ]
}
```

## 性能优化

### 性能分析

```python
import cProfile
import pstats

# 分析函数
def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    # 您的代码
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### 优化策略

1. **批处理**：一起处理多个项目
2. **缓存**：缓存频繁访问的数据
3. **异步操作**：对 I/O 操作使用异步
4. **连接池**：重用数据库连接
5. **索引优化**：优化数据库索引

### 监控

```python
import time
import logging

# 添加性能日志
def timed_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} 耗时 {end_time - start_time:.2f}s")
        return result
    return wrapper
```

## 调试

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("调试消息")
logger.info("信息消息")
logger.error("错误消息")
```

### 调试技巧

1. 使用 `print()` 语句进行快速调试
2. 使用 Python 调试器：`import pdb; pdb.set_trace()`
3. 检查 `data/logs/` 目录中的日志
4. 使用 API 文档测试端点

## 部署

### 生产设置

1. **环境变量：**
   ```bash
   RAGKB_LOG_LEVEL=WARNING
   RAGKB_LIGHTRAG_ENABLE_LLM_CACHE=true
   ```

2. **性能调优：**
   - 根据文档类型调整块大小
   - 为 Ollama 启用 GPU 加速
   - 使用生产级 WSGI 服务器

3. **监控：**
   - 设置应用程序监控
   - 配置错误跟踪
   - 监控资源使用

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "-m", "uvicorn", "rag_kb.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 资源

- **LightRAG 文档**: https://github.com/HKUDS/LightRAG
- **FastAPI 文档**: https://fastapi.tiangolo.com/
- **Ollama 文档**: https://ollama.ai/docs
- **项目规划**: RAG_KB_Plan.html
- **实施框架**: RAG_KB_Implementation_Framework.html