# 发布说明

## [0.1.2] - 2026-08-18

### 新增功能
- 现代化文档管理Web界面
- 文档上传功能（支持拖拽上传）
- 本地文件夹导入界面
- 文档管理和统计功能
- Open WebUI集成支持
- 实时进度显示
- 多用户和知识库管理界面

### 改进
- 增强用户体验
- 提供可视化文档管理
- 简化文档导入流程
- 支持批量操作

### 新增端点
- GET /docs/docs-ui - 文档管理界面
- 支持完整的文档管理操作

### 文档更新
- 添加Open WebUI集成指南
- 更新用户指南包含新UI功能
- 提供详细的界面使用说明

## [0.1.1] - 2026-08-17

### 新增功能
- 本地文件夹导入功能
- PowerShell导入脚本
- 简单模式自动创建用户和知识库
- 文件夹导入API端点
- 详细的导入统计和进度显示
- 文件跳过和错误处理

### 改进
- 更新用户指南，添加文件夹导入说明
- 增强用户数据管理系统
- 支持批量文档导入
- 添加文件重复检测

### API新增
- POST /users/{user_id}/kbs/{kb_name}/import-folder - 导入文件夹到用户知识库
- POST /import-local-folder - 简单模式文件夹导入

### 文档更新
- 更新USER_GUIDE.md和USER_GUIDE_CN.md
- 添加本地文件夹导入使用说明
- 添加故障排除指南

## [0.1.0] - 2026-08-17

### 新增功能
- 万级长文档 RAG 知识库系统首次发布
- 结构感知文档切片，支持父子块关系
- LightRAG 集成，支持 hybrid/local/global/naive 查询模式
- 多格式文档解析（PDF、Word、HTML、Markdown）
- 数据清洗，支持去重和 PII 脱敏
- FastAPI 后端，提供 OpenAI 兼容接口
- Open WebUI 集成，提供聊天界面
- RBAC/ACL 安全支持
- 增量文档更新
- 完整的测试套件
- PowerShell 启动脚本
- 批量文档导入脚本

### 核心特性
- **文档处理**：支持 10,000+ 长文档的语义切片
- **图增强检索**：LightRAG 向量+图混合搜索
- **Windows 原生**：针对 Windows 部署优化，使用 Ollama 本地模型
- **安全性**：内置访问控制和 PII 保护
- **性能**：父子块切片实现高精度检索
- **可扩展性**：模块化架构，支持插件式解析器和切片器

### 技术栈
- 后端：FastAPI, Python 3.11+
- RAG 引擎：LightRAG (lightrag-hku)
- 向量存储：NanoVectorDB
- 图存储：NetworkX
- 大模型：Ollama (qwen2.5, llama3.1, deepseek-r1)
- 嵌入模型：Ollama (nomic-embed-text, bge-m3)
- 前端：Open WebUI

### 文档
- 完整的 README，包含安装和使用说明
- API 文档，提供交互式 Swagger UI
- Ollama 和 OpenAI 兼容 API 的配置示例
- 包含单元测试和集成测试的测试套件

### 已知限制
- LightRAG 使用本地存储（NetworkX + NanoVectorDB + JSON）
- 对于 10,000+ 文档且图密集的情况，建议考虑外部向量/图数据库
- Windows 专用部署（虽然核心 Python 代码是跨平台的）

### 迁移说明
- 这是首次发布，无需迁移

### 支持
- 文档：参见 README.md 和 /docs 目录
- 问题反馈：请通过 GitHub Issues 报告
- 参考资料：RAG_KB_Plan.html 和 RAG_KB_Implementation_Framework.html