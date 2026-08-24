# 发布说明

## [0.4.0] - 2026-08-24

### 知识管理功能
- **自动文档分类**: 智能分类（技术、产品、项目、业务、法律）
- **智能标签**: 从文档内容自动提取标签
- **实体识别**: 识别技术、日期、邮箱和URL
- **质量分析**: 文档质量评估和改进建议
- **批量操作**: 高效的多文档处理（删除、重新索引、移动、标签）
- **知识管理界面**: 统一的管理界面 `/knowledge-manager`

### 新增 API 端点
- `POST /api/v1/knowledge/organize` - 文档组织和分类
- `POST /api/v1/knowledge/batch-operation` - 批量文档操作
- `GET /knowledge-manager` - 知识管理界面

### 技术改进
- **稳定性**: 解决了v0.5.0的null bytes损坏问题
- **渐进式集成**: 干净地实现了v0.5.0功能
- **测试**: 新功能100%测试通过率
- **文档**: 完整的用户指南和示例

### 文档更新
- 更新 USER_GUIDE.md 添加知识管理功能
- 更新 USER_GUIDE_CN.md 添加知识管理功能
- 添加 examples/knowledge_management_examples.py
- 更新 INSTALLATION.md 和 INSTALLATION_CN.md 到v0.4.0
- 添加CI/CD配置用于自动化测试和部署

### 使用示例
参见 `examples/knowledge_management_examples.py` 获取完整的使用示例。

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