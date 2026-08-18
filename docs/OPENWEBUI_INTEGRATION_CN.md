# Open WebUI 集成指南

## 概述

RAG知识库提供了完整的文档管理界面，可与Open WebUI配合使用，提供统一的用户体验。

## 集成方式

### 方式1: 分离界面使用（推荐）

由于技术限制，推荐使用分离界面方式：

#### 文档管理界面
- **URL**: http://localhost:8000/docs/docs-ui
- **功能**: 文档上传、文件夹导入、知识库管理、知识图谱可视化

#### Open WebUI
- **URL**: http://localhost:8080
- **功能**: 聊天对话、智能查询、RAG检索

### 方式2: Open WebUI自定义链接

在Open WebUI中添加自定义链接访问文档管理：

1. **访问Open WebUI**: http://localhost:8080
2. **进入设置**: 点击右上角设置图标
3. **添加自定义链接**:
   - 名称: "文档管理"
   - URL: `http://localhost:8000/docs/docs-ui`
   - 图标: 📚

## 使用Python 3.12启动Open WebUI

Open WebUI现在使用Python 3.12启动，确保兼容性：

```powershell
# 检查Python 3.12是否可用
py -3.12 --version

# 启动Open WebUI
.\scripts\open_webui.ps1
```

## 完整工作流程

### 推荐工作流程

1. **启动RAG KB服务**:
   ```powershell
   .\scripts\start.ps1 -NoOpenWebUI
   ```

2. **启动Open WebUI**:
   ```powershell
   .\scripts\open_webui.ps1
   ```

3. **使用文档管理界面**:
   - 访问 http://localhost:8000/docs/docs-ui
   - 上传/导入文档
   - 查看知识图谱可视化

4. **使用Open WebUI进行查询**:
   - 访问 http://localhost:8080
   - 进行智能查询

## 功能对比

| 功能 | 文档管理界面 | Open WebUI |
|------|-------------|------------|
| 文档上传 | ✅ 批量上传 | ✅ 单文件上传 |
| 文件夹导入 | ✅ 本地文件夹导入 | ❌ 不支持 |
| 知识库管理 | ✅ 独立知识库 | ❌ 不支持 |
| 知识图谱 | ✅ 可视化 | ❌ 不支持 |
| 聊天对话 | ❌ 不支持 | ✅ 支持 |
| 智能查询 | ❌ 不支持 | ✅ 支持 |

## 技术实现

### Open WebUI配置
- **Python版本**: Python 3.12
- **嵌入模型**: Ollama (nomic-embed-text)
- **嵌入引擎**: ollama
- **端口**: 8080
- **注意**: 启动时会有HuggingFace模型下载警告，但不影响基本功能

### RAG KB配置
- **API端口**: 8000
- **文档管理**: /docs/docs-ui
- **OpenAI兼容**: /api/v1/chat/completions

## 故障排除

### Open WebUI启动失败
- 确保Python 3.12已安装: `py -3.12 --version`
- 手动安装: `py -3.12 -m pip install open-webui`
- 检查端口8080是否被占用

### HuggingFace模型下载警告
- 这是正常现象，不影响基本功能
- Open WebUI会尝试下载默认嵌入模型
- 可以忽略此警告继续使用

### 文档管理界面无法访问
- 确保RAG KB服务正在运行: `.\scripts\start.ps1`
- 检查端口8000是否可访问
- 检查健康状态: http://localhost:8000/health

## 总结

RAG知识库的文档管理界面提供了：

- ✅ 现代化的用户界面
- ✅ 完整的文档管理功能
- ✅ 与Open WebUI的配合使用
- ✅ 多用户和知识库支持
- ✅ 本地文件夹导入功能
- ✅ 知识图谱可视化

通过上述集成方法，用户可以在两个界面之间切换，享受完整的文档管理和RAG查询体验。