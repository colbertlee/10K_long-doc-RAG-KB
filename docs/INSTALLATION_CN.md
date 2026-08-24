# 安装指南 - RAG 知识库

**当前版本**: v0.4.0 (稳定版本)  
**发布日期**: 2026-08-24

> **版本说明**: v0.4.0 包含知识管理功能，支持自动文档分类、批量操作和质量分析。

## 系统要求

### 硬件要求
- **CPU**: 推荐 4 核或更多
- **内存**: 最低 8GB，推荐 16GB
- **存储**: 10GB 可用空间用于文档和索引
- **GPU**: 可选（用于 Ollama 加速）

### 软件要求
- **操作系统**: Windows 10/11（原生），Linux/macOS（需修改）
- **Python**: 3.11 或更高版本（Open WebUI 必需）
- **Ollama**: 最新版本，用于本地 LLM 和嵌入模型

## 安装方法

### 方法 1: 标准安装（推荐）

#### 步骤 1: 克隆仓库
```bash
git clone <repository-url>
cd 10K_long-doc-RAG-KB
```

#### 步骤 2: 创建虚拟环境
```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### 步骤 3: 安装依赖
```bash
pip install -e .
```

#### 步骤 4: 安装 Ollama
1. 从 https://ollama.ai 下载 Ollama
2. 安装并运行 Ollama
3. 验证安装：
   ```bash
   ollama --version
   ```

#### 步骤 5: 拉取所需模型
```bash
ollama serve
ollama pull qwen2.5
ollama pull nomic-embed-text
```

#### 步骤 6: 配置系统
```bash
copy configs\config.example.yaml configs\config.yaml
copy .env.example .env
```

根据您的设置编辑 `configs\config.yaml` 和 `.env`。

### 方法 2: 开发安装

适用于想要修改代码的开发者：

```bash
# 克隆仓库
git clone <repository-url>
cd 10K_long-doc-RAG-KB

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 以开发模式安装
pip install -e ".[dev]"

# 安装 pre-commit hooks（可选）
pre-commit install
```

### 方法 3: Docker 安装（实验性）

```bash
# 构建 Docker 镜像
docker build -t rag-kb .

# 运行容器
docker run -p 8000:8000 -p 11434:11434 rag-kb
```

## Ollama 设置

### 安装
1. 从 https://ollama.ai 下载 Ollama 安装程序
2. 运行安装程序
3. 启动 Ollama 服务：
   ```bash
   ollama serve
   ```

### 模型选择

**推荐模型：**
- **LLM**: `qwen2.5`（中英文），`llama3.1`（英文），`deepseek-r1`（推理）
- **嵌入**: `nomic-embed-text`（快速），`mxbai-embed-large`（高质量）

**拉取模型：**
```bash
# 中英文 LLM
ollama pull qwen2.5

# 英文 LLM
ollama pull llama3.1

# 推理 LLM
ollama pull deepseek-r1

# 快速嵌入
ollama pull nomic-embed-text

# 高质量嵌入
ollama pull mxbai-embed-large
```

### GPU 加速
如果您有 NVIDIA GPU：

1. 安装 NVIDIA 驱动程序
2. 安装 CUDA 工具包
3. 如果可用，Ollama 将自动使用 GPU

验证 GPU 使用：
```bash
ollama run qwen2.5
# 在任务管理器中检查 GPU 利用率
```

## Open WebUI 安装（可选）

### 安装
```bash
pip install open-webui
```

### 启动 Open WebUI
```bash
open-webui serve
```

访问地址：http://localhost:8080

### 配置 Open WebUI
1. 打开 http://localhost:8080
2. 进入设置 → 连接
3. 配置：
   - **OpenAI API Base URL**: `http://localhost:8000/api/v1`
   - **API Key**: `not-needed-for-local`
   - **Default Model**: `rag-kb-pipeline`

## v0.4.0 新功能

### 知识管理功能
v0.4.0 引入了高级知识管理功能：

- **自动文档分类**: 智能分类（技术、产品、项目、业务、法律）
- **智能标签**: 从文档内容自动提取标签
- **实体识别**: 识别技术、日期、邮箱和URL
- **质量分析**: 文档质量评估和改进建议
- **批量操作**: 高效的多文档处理
- **知识管理界面**: 统一的管理界面 `/knowledge-manager`

### 新增 API 端点
- `POST /api/v1/knowledge/organize` - 文档组织和分类
- `POST /api/v1/knowledge/batch-operation` - 批量文档操作
- `GET /knowledge-manager` - 知识管理界面

## 配置

### 环境变量
从 `.env.example` 创建 `.env` 文件：

```bash
# 应用程序
RAGKB_APP_NAME=rag-kb
RAGKB_DATA_DIR=./data
RAGKB_LIGHTRAG_WORKING_DIR=./lightrag_db
RAGKB_LOG_LEVEL=INFO

# 嵌入模型
RAGKB_EMBEDDING_PROVIDER=ollama
RAGKB_EMBEDDING_BASE_URL=http://localhost:11434
RAGKB_EMBEDDING_MODEL=nomic-embed-text

# 大语言模型
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

### YAML 配置
编辑 `configs/config.yaml`：

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

## 验证

### 测试安装
```bash
# 运行测试套件
pytest

# 测试健康端点
curl http://localhost:8000/health

# 测试 Ollama 连接
ollama list
```

### 预期结果
- 所有测试应该通过
- 健康端点返回 `{"status": "ok"}`
- Ollama 列出已拉取的模型

## 故障排除

### Python 版本问题
**问题**: Open WebUI 需要 Python 3.11+
**解决方案**: 
```bash
# 检查 Python 版本
python --version

# 从 python.org 安装正确的 Python 版本
# 使用正确的版本创建新的虚拟环境
python3.11 -m venv .venv
```

### Ollama 连接问题
**问题**: 无法连接到 Ollama
**解决方案**:
```bash
# 检查 Ollama 是否正在运行
ollama serve

# 测试连接
curl http://localhost:11434/api/tags
```

### 依赖安装失败
**问题**: pip install 失败
**解决方案**:
```bash
# 升级 pip
pip install --upgrade pip

# 单独安装依赖
pip install pydantic fastapi uvicorn

# 为 Windows 使用 wheel 文件
pip install --only-binary :all: <package-name>
```

### 内存问题
**问题**: 索引期间内存不足
**解决方案**:
- 在配置中减少 `lightrag_chunk_token_size`
- 使用更小的 LLM 模型
- 分批处理文档
- 关闭其他应用程序

### 权限问题
**问题**: 无法写入数据目录
**解决方案**:
```powershell
# 以管理员身份运行 PowerShell
# 或更改目录权限
icacls "data" /grant Users:F
```

## 卸载

### 移除应用程序
```bash
# 停用虚拟环境
deactivate

# 移除虚拟环境
Remove-Item -Recurse -Force .venv

# 移除应用程序文件
Remove-Item -Recurse -Force 10K_long-doc-RAG-KB
```

### 移除 Ollama 模型
```bash
# 列出模型
ollama list

# 移除特定模型
ollama rm qwen2.5

# 移除所有模型
ollama rm $(ollama list | awk '{print $1}')
```

### 移除 Open WebUI
```bash
pip uninstall open-webui
```

## 升级

### 升级应用程序
```bash
# 拉取最新更改
git pull origin main

# 更新依赖
pip install --upgrade -e .

# 重启服务
.\scripts\start.ps1
```

### 升级 Ollama 模型
```bash
# 更新 Ollama
# 从 ollama.ai 下载最新安装程序

# 拉取最新模型版本
ollama pull qwen2.5
ollama pull nomic-embed-text
```

## 后续步骤

安装完成后：

1. 阅读[用户指南](USER_GUIDE_CN.md)
2. 导入您的第一批文档
3. 配置访问控制
4. 设置监控和日志记录
5. 根据您的特定用例进行定制

## 支持

- **文档**: 参见 `/docs` 目录
- **问题报告**: 通过 GitHub Issues 报告
- **社区**: 加入我们的 Discord/Slack 社区