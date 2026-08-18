# Open WebUI iframe集成配置

## 快速集成方案

### 方案1: 通过Open WebUI自定义链接（最简单）

在Open WebUI中添加自定义链接：

1. **访问Open WebUI**: http://localhost:8080
2. **进入设置**: 点击右上角设置图标
3. **添加自定义链接**:
   - 名称: "📚 文档管理"
   - URL: `http://localhost:8000/docs/docs-ui`
   - 描述: "管理RAG知识库文档"

### 方案2: 通过iframe嵌入（推荐）

在Open WebUI的自定义页面中添加iframe：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文档管理 - RAG知识库</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
        }
        .iframe-container {
            flex: 1;
            padding: 20px;
            background: #f5f5f5;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 RAG知识库文档管理</h1>
            <p>上传、导入和管理您的文档</p>
        </div>
        <div class="iframe-container">
            <iframe 
                src="http://localhost:8000/docs/docs-ui" 
                title="文档管理界面"
                allow="clipboard-write; clipboard-read">
            </iframe>
        </div>
    </div>
</body>
</html>
```

### 方案3: 使用预构建的集成页面

我们提供了一个预构建的集成页面，包含服务状态监控和美观的界面：

访问: `http://localhost:8000/openwebui-integration`

这个页面包含：
- ✅ 美观的渐变头部设计
- ✅ 实时服务状态监控
- ✅ 加载状态指示器
- ✅ 错误处理和重试功能
- ✅ 响应式设计
- ✅ 快捷操作按钮

## 集成步骤

### 步骤1: 启动RAG知识库服务

```powershell
cd C:\Users\liz8\OneDrive - Dell Technologies\Documents\BaiduSyncdisk\Works\Vibe_Coding\10K_long-doc-RAG-KB
.\scripts\start.ps1
```

### 步骤2: 启动Open WebUI

```powershell
cd C:\Users\liz8\OneDrive - Dell Technologies\Documents\BaiduSyncdisk\Works\Vibe_Coding\10K_long-doc-RAG-KB
.\scripts\open_webui.ps1
```

### 步骤3: 配置Open WebUI

1. 访问 http://localhost:8080
2. 登录Open WebUI
3. 进入设置 → 界面 → 自定义页面
4. 添加新的自定义页面：
   - 名称: "文档管理"
   - 类型: "iframe"
   - URL: `http://localhost:8000/openwebui-integration`
   - 图标: 📚

### 步骤4: 配置Open WebUI连接到RAG知识库

1. 进入设置 → 连接
2. 添加新的连接：
   - 名称: "RAG知识库"
   - Base URL: `http://localhost:8000/api/v1`
   - API Key: `not-needed-for-local`
   - 模型: 选择您的Ollama模型

## 使用流程

### 完整工作流程

1. **启动服务**: 运行启动脚本
2. **访问Open WebUI**: http://localhost:8080
3. **进入文档管理**: 点击侧边栏的"文档管理"
4. **上传文档**: 使用文档管理界面上传文件
5. **返回聊天**: 返回Open WebUI聊天界面
6. **查询文档**: 在聊天中查询上传的文档

## 高级配置

### 自定义样式

如果您想自定义iframe的外观，可以修改CSS：

```css
/* 更紧凑的布局 */
.iframe-container {
    padding: 10px;
}

/* 更大的iframe */
iframe {
    height: 900px;
}

/* 自定义颜色 */
.header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}
```

### 添加加载指示器

```html
<div class="iframe-container">
    <div id="loading" class="loading">
        <p>⏳ 正在加载文档管理界面...</p>
    </div>
    <iframe 
        src="http://localhost:8000/docs/docs-ui" 
        onload="document.getElementById('loading').style.display='none'"
        title="文档管理界面">
    </iframe>
</div>
```

### 响应式设计

```css
@media (max-width: 768px) {
    .header h1 {
        font-size: 18px;
    }
    .iframe-container {
        padding: 10px;
    }
}
```

## 故障排除

### iframe无法加载

**问题**: iframe显示空白或无法加载

**解决方案**:
1. 检查RAG知识库服务是否启动
2. 检查端口8000是否可访问
3. 检查浏览器控制台是否有CORS错误
4. 确保URL正确: `http://localhost:8000/docs/docs-ui`

### 样式问题

**问题**: iframe样式不正确

**解决方案**:
1. 检查CSS是否正确加载
2. 尝试清除浏览器缓存
3. 检查iframe的width和height设置

### 性能问题

**问题**: iframe加载缓慢

**解决方案**:
1. 优化RAG知识库服务性能
2. 减少iframe中的内容
3. 使用懒加载: `loading="lazy"`

## 安全考虑

### 同源策略

由于iframe跨域，需要确保：
1. RAG知识库API已配置CORS
2. 使用适当的CORS头
3. 考虑使用代理服务器

### 认证

在生产环境中，建议添加认证：
```python
# 在docs_ui.py中添加认证依赖
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.get("/docs-ui", dependencies=[Depends(security)])
async def document_management_ui():
    # 认证后的界面
    pass
```

## 总结

通过iframe集成，您可以：
- ✅ 在Open WebUI中直接访问文档管理功能
- ✅ 保持两个系统的独立性
- ✅ 快速实施，无需修改Open WebUI源码
- ✅ 易于维护和升级
- ✅ 使用预构建的集成页面获得更好的用户体验

这是最快见效的集成方案，适合大多数使用场景。