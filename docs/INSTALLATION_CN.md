# 安装指南 - RAG 知识库

## 系统要求

### 硬件要求
- **CPU**: 推荐 4 核或更多
- **内存**: 最低 8GB，推荐 16GB
- **存储**: 10GB 可用空间用于文档和索引
- **GPU**: 可选（用于 Ollama 加速）

### 软件要求
- **操作系统**: Windows 10/11（原生支持）
- **Python**: 3.9 或更高版本（推荐 3.11+ 用于 Open WebUI）
- **Ollama**: 最新版本，用于本地 LLM 和嵌入模型
- **Git**: 用于克隆仓库（可选）

## 安装方法

### 方法 1: Windows 标准安装（推荐）

#### 步骤 1: 下载或克隆项目

**选项 A: 从 GitHub 克隆（推荐）**
```powershell
git clone https://github.com/colbertlee/10K_long-doc-RAG-KB.git
cd 10K_long-doc-RAG-KB
```

**选项 B: 直接下载 ZIP**
1. 访问 https://github.com/colbertlee/10K_long-doc-RAG-KB/releases
2. 下载最新版本的 ZIP 文件
3. 解压到您选择的目录
4. 进入解压后的目录

#### 步骤 2: 检查 Python 版本
```powershell
python --version
```

确保 Python 版本为 3.9 或更高。如果版本过低，请从 https://www.python.org/downloads/ 下载安装。

#### 步骤 3: 创建虚拟环境
```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### 步骤 4: 安装依赖
```powershell
pip install --upgrade pip
pip install -e .
```

#### 步骤 5: 安装 Ollama
1. 访问 https://ollama.ai/download
2. 下载 Windows 版本的 Ollama 安装程序
3. 运行安装程序并按照提示完成安装
4. 验证安装：
   ```powershell
   ollama --version
   ```

#### 步骤 6: 启动 Ollama 并拉取模型
```powershell
# 在新的 PowerShell 窗口中启动 Ollama
ollama serve

# 在另一个 PowerShell 窗口中拉取模型
ollama pull qwen2.5
ollama pull nomic-embed-text
```

#### 步骤 7: 配置系统
```powershell
copy configs\config.example.yaml configs\config.yaml
copy .env.example .env
```

根据您的环境编辑 `configs\config.yaml` 和 `.env` 文件。

### 方法 2: 开发安装

适用于想要修改代码的开发者：

```powershell
# 克隆仓库
git clone https://github.com/colbertlee/10K_long-doc-RAG-KB.git
cd 10K_long-doc-RAG-KB

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 以开发模式安装
pip install -e ".[dev]"

# 安装 pre-commit hooks（可选）
pre-commit install
```

### 方法 3: 从 GitHub 直接安装

```powershell
# 直接从 GitHub 安装最新版本
pip install git+https://github.com/colbertlee/10K_long-doc-RAG-KB.git

# 或安装特定版本
pip install git+https://github.com/colbertlee/10K_long-doc-RAG-KB.git@v0.1.1
```

## Ollama 设置

### Windows 安装
1. 访问 https://ollama.ai/download
2. 下载 Windows 版本（ollama-windows-amd64.exe）
3. 运行安装程序，默认安装路径为 `C:\Users\<YourUsername>\AppData\Local\Programs\Ollama`
4. 安装完成后，Ollama 会自动在后台运行

### 启动 Ollama 服务
```powershell
# 方法 1: 直接运行（推荐）
ollama serve

# 方法 2: 作为 Windows 服务（可选）
# 需要额外配置，建议使用方法 1
```

### 验证 Ollama 安装
```powershell
# 检查版本
ollama --version

# 检查服务状态
curl http://localhost:11434/api/tags
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

### Windows 安装要求
- Python 3.11 或更高版本（必需）
- 足够的系统内存（推荐 16GB+）

### 安装步骤
```powershell
# 确保虚拟环境已激活
.venv\Scripts\activate

# 安装 Open WebUI
pip install open-webui
```

### 启动 Open WebUI
```powershell
# 启动 Open WebUI 服务
open-webui serve

# 或指定端口
open-webui serve --port 8080
```

访问地址：http://localhost:8080

### 配置 Open WebUI 连接到 RAG 知识库
1. 打开 http://localhost:8080
2. 首次访问时创建管理员账户
3. 进入设置 → 连接
4. 配置：
   - **OpenAI API Base URL**: `http://localhost:8000/api/v1`
   - **API Key**: `not-needed-for-local`
   - **Default Model**: `qwen2.5`

## 配置

### 环境变量配置
从 `.env.example` 创建 `.env` 文件：

```powershell
copy .env.example .env
```

编辑 `.env` 文件（使用记事本或 VS Code）：

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

```powershell
copy configs\config.example.yaml configs\config.yaml
```

使用文本编辑器（如记事本、VS Code）编辑 `configs\config.yaml`：

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
```powershell
# 运行测试套件
pytest

# 测试健康端点
curl http://localhost:8000/health

# 或使用 PowerShell
Invoke-RestMethod -Uri http://localhost:8000/health

# 测试 Ollama 连接
ollama list
```

### 预期结果
- 所有测试应该通过
- 健康端点返回 `{"status": "ok"}`
- Ollama 列出已拉取的模型

### 启动服务测试
```powershell
# 使用提供的启动脚本
.\scripts\start.ps1

# 或手动启动
python -m uvicorn rag_kb.api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

## 故障排除

### Python 版本问题
**问题**: Python 版本过低或不兼容
**解决方案**:
```powershell
# 检查 Python 版本
python --version

# 从 python.org 下载安装 Python 3.9+
# https://www.python.org/downloads/

# 使用正确的版本创建新的虚拟环境
python -m venv .venv
```

### Ollama 连接问题
**问题**: 无法连接到 Ollama
**解决方案**:
```powershell
# 检查 Ollama 是否正在运行
# 在任务管理器中查看 Ollama 进程

# 重新启动 Ollama
ollama serve

# 测试连接
curl http://localhost:11434/api/tags
# 或使用 PowerShell
Invoke-RestMethod -Uri http://localhost:11434/api/tags
```

### 依赖安装失败
**问题**: pip install 失败
**解决方案**:
```powershell
# 升级 pip
python -m pip install --upgrade pip

# 单独安装依赖
pip install pydantic fastapi uvicorn

# 使用国内镜像源
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple

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
- 增加系统虚拟内存

### 权限问题
**问题**: 无法写入数据目录
**解决方案**:
```powershell
# 以管理员身份运行 PowerShell
# 右键点击 PowerShell -> 以管理员身份运行

# 或更改目录权限
icacls "data" /grant Users:F

# 或更改项目文件夹位置到用户目录
```

### PowerShell 执行策略问题
**问题**: 无法运行 PowerShell 脚本
**解决方案**:
```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 运行脚本后恢复原策略
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope Process
```

## 卸载

### 移除应用程序
```powershell
# 停用虚拟环境
deactivate

# 移除虚拟环境
Remove-Item -Recurse -Force .venv

# 移除应用程序文件
Remove-Item -Recurse -Force 10K_long-doc-RAG-KB
```

### 移除 Ollama
```powershell
# 通过 Windows 控制面板卸载
# 设置 -> 应用 -> Ollama -> 卸载

# 或手动删除
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Programs\Ollama"
Remove-Item -Recurse -Force "$env:APPDATA\ollama"
```

### 移除 Ollama 模型
```powershell
# 列出模型
ollama list

# 移除特定模型
ollama rm qwen2.5

# 移除所有模型
ollama rm $(ollama list | ForEach-Object { ($_ -split '\s+')[0] })
```

### 移除 Open WebUI
```powershell
pip uninstall open-webui
```

## 升级

### 使用自动升级脚本（推荐）

```powershell
# 升级到最新版本
.\scripts\upgrade.ps1

# 升级到特定版本
.\scripts\upgrade.ps1 -TargetVersion "0.1.3"
```

详细的升级指南请参考 [升级指南](UPGRADE_GUIDE_CN.md)。

### 手动升级

```powershell
# 拉取最新更改
git pull origin master

# 更新依赖
pip install --upgrade -e .

# 重启服务
.\scripts\start.ps1
```

### 升级 Ollama
```powershell
# 从 ollama.ai 下载最新安装程序
# 运行安装程序覆盖安装

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