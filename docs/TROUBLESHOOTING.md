# 故障排除指南

## Open WebUI 启动问题

### 问题: HuggingFace 模型下载失败

**错误信息**:
```
huggingface_hub.errors.LocalEntryNotFoundError: Got: ConnectError: [WinError 10054] An existing connection was forcibly closed by the remote host
```

**原因**: Open WebUI 默认尝试从 HuggingFace 下载 sentence-transformers 模型，但由于网络连接问题导致失败。

**解决方案**:

1. **使用 Ollama 嵌入模型** (推荐):
   ```powershell
   # 确保 Ollama 正在运行
   ollama serve
   
   # 安装嵌入模型
   ollama pull nomic-embed-text
   
   # 使用修复后的启动脚本
   .\scripts\open_webui.ps1
   ```

2. **手动启动 Open WebUI**:
   ```powershell
   open-webui serve --ollama-embedding-model nomic-embed-text --embedding-engine ollama
   ```

3. **检查 Ollama 模型**:
   ```powershell
   # 查看已安装的模型
   ollama list
   
   # 确保包含 nomic-embed-text
   ```

## PowerShell 脚本问题

### 问题: open_webui.ps1 无法启动

**原因**: 脚本未配置 Open WebUI 使用 Ollama 嵌入模型。

**解决方案**: 使用更新后的脚本，已自动配置 Ollama 参数。

## 接口集成问题

### 问题: 文档管理和聊天界面分离

**解决方案**: 

1. **从文档管理界面访问聊天界面**:
   - 访问 http://localhost:8000/docs/docs-ui
   - 点击顶部的 "💬 打开聊天界面 (Open WebUI)" 链接

2. **从 Open WebUI 访问文档管理**:
   - 访问 http://localhost:8080
   - 在设置中添加自定义链接指向 http://localhost:8000/docs/docs-ui

3. **推荐工作流程**:
   - 使用文档管理界面上传和管理文档
   - 使用 Open WebUI 进行查询和对话
   - 两个界面通过链接快速切换

## 网络连接问题

### 问题: 无法连接到 HuggingFace

**解决方案**:

1. **使用 Ollama 本地模型** (推荐):
   - 所有模型都在本地运行，无需网络连接

2. **配置代理** (如果需要使用 HuggingFace):
   ```powershell
   $env:HF_ENDPOINT = "https://hf-mirror.com"
   ```

3. **离线模式**:
   - 预先下载所需模型
   - 配置 Open WebUI 使用本地缓存

## 端口冲突

### 问题: 端口 8000 或 8080 被占用

**解决方案**:

1. **检查端口占用**:
   ```powershell
   netstat -ano | findstr :8000
   netstat -ano | findstr :8080
   ```

2. **更改端口**:
   ```powershell
   # 更改 RAG KB API 端口
   python -m uvicorn rag_kb.api.main:app --port 8001
   
   # 更改 Open WebUI 端口
   open-webui serve --port 8081
   ```

3. **终止占用进程**:
   ```powershell
   # 找到进程 ID 后终止
   taskkill /PID <进程ID> /F
   ```

## Ollama 问题

### 问题: Ollama 服务未启动

**解决方案**:

```powershell
# 启动 Ollama
ollama serve

# 在另一个终端测试
ollama list
```

### 问题: Ollama 模型未安装

**解决方案**:

```powershell
# 安装 LLM 模型
ollama pull qwen2.5

# 安装嵌入模型
ollama pull nomic-embed-text

# 验证安装
ollama list
```

## 性能问题

### 问题: 文档处理速度慢

**解决方案**:

1. **使用更快的嵌入模型**:
   ```powershell
   ollama pull bge-m3  # 更快的嵌入模型
   ```

2. **调整 LightRAG 配置**:
   ```yaml
   lightrag:
     chunk_token_size: 800  # 减小块大小
     enable_llm_cache: true  # 启用缓存
   ```

3. **增加系统资源**:
   - 确保 Ollama 有足够的内存
   - 考虑使用 GPU 加速

## 权限问题

### 问题: 文件夹导入失败

**解决方案**:

1. **检查文件权限**:
   ```powershell
   # 确保对目标文件夹有读取权限
   icacls "C:\path\to\folder"
   ```

2. **使用绝对路径**:
   - 避免使用相对路径
   - 使用完整的文件夹路径

3. **检查文件格式**:
   - 确保文件格式受支持 (PDF, DOCX, MD, TXT)

## 获取帮助

如果以上解决方案都无法解决您的问题：

1. **检查日志**:
   - RAG KB API 日志: 控制台输出
   - Open WebUI 日志: Open WebUI 界面中的日志

2. **查看文档**:
   - [安装指南](INSTALLATION.md)
   - [Open WebUI 集成指南](OPENWEBUI_INTEGRATION.md)
   - [用户指南](USER_GUIDE.md)

3. **提交问题**:
   - 在项目仓库中创建 issue
   - 提供详细的错误信息和系统环境