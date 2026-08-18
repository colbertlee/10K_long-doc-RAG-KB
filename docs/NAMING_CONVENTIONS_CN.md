# 用户ID和知识库名称规范

## 命名规范

### 用户ID规范

**允许的字符**:
- 字母（a-z, A-Z）
- 数字（0-9）
- 下划线（_）
- 连字符（-）

**限制**:
- 长度：1-50个字符
- 不能为空
- 不能使用保留名称：`default`, `admin`, `system`, `root`, `guest`

**有效示例**:
- `john_doe`
- `user123`
- `team-alpha`
- `developer_01`

**无效示例**:
- `john doe`（包含空格）
- `john@doe`（包含特殊字符）
- `john.doe`（包含点）
- `../admin`（路径遍历攻击）
- `admin`（保留名称）

### 知识库名称规范

**允许的字符**:
- 字母（a-z, A-Z）
- 数字（0-9）
- 空格（ ）
- 下划线（_）
- 连字符（-）

**限制**:
- 长度：1-100个字符
- 不能为空
- 不能以空格开头或结尾

**有效示例**:
- `technical_docs`
- `Project Knowledge Base`
- `team-alpha-docs`
- `2024_reports`

**无效示例**:
- `docs/`（包含斜杠）
- `docs*`（包含特殊字符）
- ` docs`（以空格开头）
- `docs `（以空格结尾）

## 安全特性

### 输入验证
- 自动验证用户ID和知识库名称格式
- 拒绝不符合规范的输入
- 提供清晰的错误提示

### 路径清理
- 自动移除危险字符（如 `..`, `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`）
- 防止路径遍历攻击
- 确保文件系统安全

### 保留名称
- 防止使用系统保留名称
- 避免命名冲突
- 提高系统安全性

## 当前用户ID

### 获取当前用户
系统会自动显示当前登录的用户ID：
- **环境变量**: `RAGKB_CURRENT_USER`
- **默认值**: `default`
- **API端点**: `GET /api/v1/current-user`

### 设置当前用户
```powershell
# 设置环境变量
$env:RAGKB_CURRENT_USER = "your_username"

# 或在启动脚本中设置
.\scripts\start.ps1
```

### 文档管理界面
文档管理界面会自动加载当前用户ID：
- 页面加载时自动获取当前用户
- 在所有用户ID输入框中自动填充
- 显示为"当前登录用户"

## 健康检查端点

### 端点信息
- **URL**: `GET /health`
- **用途**: 检查系统健康状态
- **返回**: JSON格式的系统状态信息

### 响应示例
```json
{
  "status": "ok",
  "service": "rag-kb",
  "version": "0.1.7",
  "data_dir_exists": true,
  "ollama_status": "running",
  "endpoints": {
    "api_docs": "/docs",
    "docs_ui": "/docs/docs-ui",
    "current_user": "/api/v1/current-user"
  }
}
```

### 使用方法
```powershell
# 使用curl
curl http://localhost:8000/health

# 使用PowerShell
Invoke-RestMethod -Uri http://localhost:8000/health

# 在浏览器中直接访问
# http://localhost:8000/health
```

### 状态说明
- **status**: `ok`（正常）或 `error`（错误）
- **service**: 服务名称
- **version**: 当前版本
- **data_dir_exists**: 数据目录是否存在
- **ollama_status**: Ollama服务状态（`running`, `not_running`, `unknown`）
- **endpoints**: 可用的API端点列表

### 浏览器访问
用户可以直接在浏览器中访问 `http://localhost:8000/health` 来查看系统状态。这对于：
- 检查服务是否正常运行
- 验证Ollama连接状态
- 查看可用的API端点
- 系统监控和调试

## 错误处理

### 验证错误示例
```json
{
  "detail": "Invalid user ID: User ID can only contain letters, numbers, underscores, and hyphens"
}
```

```json
{
  "detail": "Invalid knowledge base name: Knowledge base name cannot start or end with a space"
}
```

### 安全错误示例
```json
{
  "detail": "Invalid user ID: 'admin' is a reserved user ID"
}
```

## 最佳实践

### 用户ID命名
- 使用有意义的用户名
- 避免使用个人信息
- 保持一致性
- 遵循组织命名规范

### 知识库名称命名
- 使用描述性名称
- 避免过长的名称
- 使用一致的命名约定
- 考虑多语言支持

### 安全建议
- 不要使用特殊字符
- 避免使用路径相关字符
- 定期检查用户权限
- 监控异常访问模式

## 故障排除

### 验证失败
**问题**: 用户ID或知识库名称验证失败
**解决方案**:
1. 检查命名规范
2. 移除特殊字符
3. 确保长度在限制范围内
4. 避免使用保留名称

### 健康检查失败
**问题**: 健康检查返回错误
**解决方案**:
1. 检查服务是否启动
2. 验证Ollama是否运行
3. 检查数据目录权限
4. 查看服务日志

### 当前用户显示问题
**问题**: 当前用户ID显示不正确
**解决方案**:
1. 检查环境变量设置
2. 验证API端点是否可访问
3. 检查浏览器控制台错误
4. 刷新页面重试