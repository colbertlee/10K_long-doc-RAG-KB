# 故障排除指南

## 依赖版本问题

### 问题: 依赖版本冲突导致启动失败

**错误信息**:
```
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
AttributeError: module 'numpy' has no attribute 'long'
```

**原因**: Python依赖包版本不兼容，特别是pydantic_core、cryptography和numpy。

**解决方案**:

1. **重新安装依赖**:
   ```powershell
   # 卸载现有依赖
   pip uninstall pydantic-core cryptography numpy -y
   
   # 安装兼容版本
   pip install pydantic-core==2.46.4
   pip install cryptography==48.0.0
   pip install "numpy>=2.0.0,<2.8.0"
   pip install lightrag-hku>=1.5.6
   ```

2. **使用项目配置重新安装**:
   ```powershell
   pip install -e .[all]
   ```

3. **验证依赖版本**:
   ```powershell
   pip list | findstr -i "pydantic numpy cryptography lightrag"
   ```

### 问题: LightRAG 导入失败

**错误信息**:
```
ImportError: cannot import name 'LightRAG' from 'lightrag'
```

**原因**: LightRAG包导入路径不正确或包版本不兼容。

**解决方案**:

1. **确认正确的包**:
   ```powershell
   pip uninstall lightrag -y
   pip install lightrag-hku>=1.5.6
   ```

2. **验证导入**:
   ```powershell
   python -c "from lightrag.lightrag import LightRAG; print('LightRAG imported successfully')"
   ```

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

1. **使用文件夹选择器** (推荐):
   - 点击"选择文件夹"按钮
   - 选择包含文档的文件夹
   - 系统会自动上传文件夹内的所有文件

2. **手动输入文件夹路径**:
   - 确保对目标文件夹有读取权限
   - 使用完整的文件夹路径（绝对路径）
   - 避免使用相对路径

3. **检查文件格式**:
   - 确保文件格式受支持 (PDF, DOCX, MD, TXT)
   - 检查文件是否损坏或加密

4. **浏览器兼容性**:
   - 现代浏览器支持文件夹选择功能
   - 如遇问题，请尝试使用Chrome或Edge浏览器

## 升级问题

### 问题: Git pull 失败 - config.yaml 冲突

**错误信息**:
```
error: The following untracked working tree files would be overwritten by merge:
        configs/config.yaml
```

**原因**: 本地有未跟踪的 `configs/config.yaml` 文件，与远程版本冲突。

**解决方案**:

1. **备份本地配置**:
   ```powershell
   Copy-Item configs\config.yaml configs\config.yaml.local.backup
   ```

2. **删除冲突文件**:
   ```powershell
   Remove-Item configs\config.yaml
   ```

3. **重新拉取**:
   ```powershell
   git pull origin master
   ```

4. **合并配置**:
   ```powershell
   # 如果需要，恢复并手动合并
   Copy-Item configs\config.yaml.local.backup configs\config.yaml
   # 手动合并新的配置选项
   ```

### 问题: pip install 失败 - TOMLDecodeError

**错误信息**:
```
tomllib.TOMLDecodeError: Invalid statement (at line 1, column 1)
```

**原因**: `pyproject.toml` 文件包含 UTF-8 BOM（字节顺序标记），导致 Python 的 tomllib 无法解析。

**解决方案**:

1. **移除 BOM**:
   ```powershell
   python -c "from pathlib import Path; f = Path('pyproject.toml'); content = f.read_bytes(); content = content.decode('utf-8-sig').encode('utf-8'); f.write_bytes(content)"
   ```

2. **重新安装**:
   ```powershell
   pip install -e .
   ```

### 问题: 升级后版本未更新

**原因**: Git pull 失败或 pip install 未成功执行。

**解决方案**:

1. **检查 Git 状态**:
   ```powershell
   git status
   ```

2. **强制拉取**:
   ```powershell
   git fetch origin
   git reset --hard origin/master
   ```

3. **重新安装**:
   ```powershell
   pip uninstall rag-kb
   pip install -e .
   ```

4. **验证版本**:
   ```powershell
   Get-Content pyproject.toml | Select-String "version"
   ```

### Problem: upgrade.ps1 script fails

**Error message**: Git operation failed or version display incorrect.

**Solution**:

1. **Use updated script**:
   ```powershell
   git pull origin master
   .\scripts\upgrade.ps1
   ```

2. **Manual upgrade**:
   Refer to the manual upgrade steps above.

## Document Management UI Issues

### Problem: Folder selection button shows "Cannot browse folder directly"

**Error message**:
```
Please manually enter the folder path in the folder path input box, or use the file picker.
Note: Due to browser security restrictions, direct folder browsing is not possible.
```

**Cause**:
1. Browser does not support `webkitdirectory` attribute
2. Browser security policies restrict folder access
3. Incompatible browser version

**Solution**:

1. **Use supported browser**:
   - Recommended: Chrome or Edge (latest version)
   - Firefox also supports folder selection
   - Avoid using older browser versions

2. **Manually enter folder path**:
   ```powershell
   # Enter full path in the folder path input box
   C:\Users\YourName\Documents\MyDocuments
   ```

3. **Check browser compatibility**:
   - Ensure browser is latest version
   - Clear browser cache
   - Try using incognito mode

4. **Use file picker alternative**:
   - Click "Select Folder" button
   - Select all files in the folder (multi-select)
   - System will batch upload selected files

5. **Server-side folder import**:
   - Ensure server has read access to target folder
   - Use absolute path instead of relative path
   - Avoid using network paths (e.g., `\\server\share`)

### Problem: Load document list fails - toFixed error

**Error message**:
```
Load failed: Cannot read properties of undefined (reading 'toFixed')
```

**Cause**: The `total_size_mb` field in the API response is `undefined` or `null`.

**Solution**:

1. **Ensure knowledge base exists**:
   - Create knowledge base first
   - Ensure knowledge base has documents

2. **Check API response**:
   - Open browser developer tools
   - Check network requests
   - Examine `/api/v1/users/{user_id}/kbs/{kb_name}/stats` response

3. **Manual verification**:
   ```powershell
   # Test API endpoint
   curl http://localhost:8000/api/v1/users/default/kbs/default/stats
   ```

**Temporary solution**:
- Added null check in code
- If problem persists, ensure knowledge base has document data

## Getting Help

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