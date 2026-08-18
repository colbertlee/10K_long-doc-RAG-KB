# Open WebUI 集成指南

## 概述

RAG知识库提供了一个独立的文档管理界面，可以与Open WebUI集成使用，提供完整的文档上传、文件夹导入和管理功能。

## 访问文档管理界面

### 直接访问

启动RAG知识库服务后，可以直接访问：
```
http://localhost:8000/docs/docs-ui
```

这将打开一个现代化的文档管理界面，包含：
- 📄 文档上传功能
- 📁 本地文件夹导入功能
- 📋 文档管理功能

## Open WebUI 集成方法

### 方法1: 通过自定义链接（推荐）

在Open WebUI中添加自定义链接，方便用户访问文档管理界面：

1. **访问Open WebUI**: http://localhost:8080
2. **进入设置**: 点击右上角设置图标
3. **添加自定义链接**:
   - 名称: "文档管理"
   - URL: `http://localhost:8000/docs/docs-ui`
   - 图标: 📚

这样用户可以在Open WebUI界面中直接访问文档管理功能。

**注意**: 文档管理界面现在也包含了指向Open WebUI的链接，方便用户在两个界面之间切换。

### 方法2: 通过iframe嵌入（高级）

如果您希望将文档管理界面直接嵌入到Open WebUI中，可以使用iframe：

```html
<iframe 
    src="http://localhost:8000/docs/docs-ui" 
    width="100%" 
    height="800px" 
    frameborder="0">
</iframe>
```

### 方法3: 通过Open WebUI的自定义页面

Open WebUI支持自定义页面，您可以：

1. **创建自定义页面配置**:
```json
{
  "custom_pages": [
    {
      "name": "文档管理",
      "url": "http://localhost:8000/docs/docs-ui",
      "icon": "📚"
    }
  ]
}
```

2. **在Open WebUI设置中启用自定义页面**

## 功能对比

### RAG知识库文档管理界面 vs Open WebUI原生功能

| 功能 | RAG知识库界面 | Open WebUI原生 |
|------|---------------|---------------|
| 文档上传 | ✅ 支持批量上传 | ✅ 单文件上传 |
| 文件夹导入 | ✅ 本地文件夹导入 | ❌ 不支持 |
| 用户管理 | ✅ 多用户支持 | ✅ 基础用户管理 |
| 知识库管理 | ✅ 独立知识库 | ❌ 不支持 |
| 进度显示 | ✅ 实时进度 | ✅ 基础进度 |
| 文档统计 | ✅ 详细统计 | ✅ 基础统计 |
| ACL权限 | ✅ 细粒度控制 | ✅ 基础权限 |

## 使用流程

### 推荐工作流程

1. **启动服务**:
   ```powershell
   .\scripts\start.ps1
   ```

2. **访问Open WebUI**: http://localhost:8080

3. **配置Open WebUI连接到RAG知识库**:
   - 设置 → 连接
   - OpenAI API Base URL: `http://localhost:8000/api/v1`
   - API Key: `not-needed-for-local`

4. **访问文档管理界面**:
   - 通过Open WebUI中的自定义链接
   - 或直接访问: http://localhost:8000/docs/docs-ui

5. **导入文档**:
   - 使用文档上传功能上传单个文件
   - 或使用文件夹导入功能批量导入

6. **返回Open WebUI进行查询**:
   - 在Open WebUI中查询导入的文档
   - 享受RAG增强的搜索体验

## 配置示例

### Open WebUI完整配置

```yaml
# Open WebUI 配置示例
connections:
  - name: "RAG知识库"
    base_url: "http://localhost:8000/api/v1"
    api_key: "not-needed-for-local"
    models:
      - "qwen2.5"
      - "llama3.1"

custom_links:
  - name: "文档管理"
    url: "http://localhost:8000/docs/docs-ui"
    icon: "📚"
    description: "管理RAG知识库文档"
```

## 安全考虑

### 跨域访问

由于文档管理界面和Open WebUI运行在不同端口，需要确保：

1. **CORS配置**: RAG知识库API已配置CORS支持
2. **同源策略**: 使用iframe时可能需要处理跨域问题
3. **认证**: 建议在生产环境中添加认证机制

### 访问控制

文档管理界面支持：
- 用户ID隔离
- 知识库级别隔离
- ACL权限控制

## 故障排除

### 无法访问文档管理界面

**问题**: 访问 http://localhost:8000/docs/docs-ui 失败

**解决方案**:
1. 检查RAG知识库服务是否启动: `curl http://localhost:8000/health`
2. 检查端口8000是否被占用
3. 查看服务日志是否有错误

### Open WebUI无法连接到RAG知识库

**问题**: Open WebUI无法连接到API

**解决方案**:
1. 检查API地址配置: `http://localhost:8000/api/v1`
2. 检查RAG知识库服务状态
3. 检查防火墙设置

### 文件夹导入失败

**问题**: 文件夹导入功能不工作

**解决方案**:
1. 检查文件夹路径是否正确
2. 检查文件权限
3. 查看浏览器控制台错误信息

## 高级配置

### 自定义界面样式

如果您想自定义文档管理界面的样式，可以：

1. **创建自定义HTML文件**: 替换嵌入的HTML
2. **添加静态文件服务**: 使用FastAPI静态文件
3. **修改CSS样式**: 调整界面外观

### 添加认证

在生产环境中，建议添加认证：

```python
# 在docs_ui.py中添加认证
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.get("/docs-ui", dependencies=[Depends(security)])
async def document_management_ui():
    # 认证后的界面
    pass
```

## 性能优化

### 大文件上传

对于大文件上传，建议：

1. **增加上传大小限制**: 在FastAPI配置中设置
2. **使用分块上传**: 实现大文件分块上传
3. **添加进度显示**: 实时显示上传进度

### 批量处理

对于大量文件：

1. **使用队列系统**: 后台处理上传任务
2. **添加任务状态查询**: 查询处理进度
3. **实现异步处理**: 不阻塞用户界面

## 总结

RAG知识库的文档管理界面提供了：

- ✅ 现代化的用户界面
- ✅ 完整的文档管理功能
- ✅ 与Open WebUI的无缝集成
- ✅ 多用户和知识库支持
- ✅ 本地文件夹导入功能

通过上述集成方法，用户可以在Open WebUI中享受完整的文档管理和RAG查询体验。