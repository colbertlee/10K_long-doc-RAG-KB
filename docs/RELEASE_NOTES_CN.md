# 发布说明

## [0.3.0] - 2026-08-18

### 发布说明
- 添加缺失的集成端点（/openwebui-integration 和 /rag-kb-integration）
- 修复集成页面的404错误
- 改进文件夹选择功能
- 为集成端点添加适当的错误处理
- 更新健康检查以反映当前版本

### 变更内容

#### API端点:
- 添加/openwebui-integration端点提供静态HTML
- 添加/rag-kb-integration端点提供静态HTML
- 添加静态文件缺失时的回退HTML
- 修复用户报告的404错误

#### 集成改进:
- 集成页面现在可以正确访问
- 为缺失的静态文件提供更好的错误消息
- 改进集成工作流的用户体验

### 优势
- ✅ 集成端点现在正常工作
- ✅ 集成页面不再有404错误
- ✅ 更好的错误处理和用户反馈
- ✅ 改进的集成工作流

### 修复
- 修复/openwebui-integration的404 Not Found错误
- 修复/rag-kb-integration的404 Not Found错误
- 修复健康检查版本显示

## [0.2.9] - 2026-08-18

### 发布说明
- 修复文档管理界面中的文件夹选择按钮
- 添加selectFolder函数以正确触发文件夹选择器
- 为空文件夹选择添加更好的错误处理
- 修复loadDocuments函数中的toFixed错误
- 添加文件夹选择问题的故障排除文档

### 变更内容

#### 文档管理界面修复:
- 用专用的selectFolder函数替换内联onclick
- 在loadDocuments中为total_size_mb添加空值检查
- 改进文件夹选择的错误消息
- 当没有选择文件时添加有用的反馈

#### 文档更新:
- 添加文件夹选择问题故障排除
- 添加loadDocuments toFixed错误故障排除
- 使用手动步骤更新升级指南
- 添加综合升级故障排除

### 优势
- ✅ 文件夹选择现在在支持的浏览器中正常工作
- ✅ 更好的错误处理和用户反馈
- ✅ 更健壮的文档加载
- ✅ 综合故障排除文档

### 修复
- 修复文件夹选择按钮不触发文件选择器
- 修复加载文档统计时的toFixed错误
- 改进文件夹导入的用户体验

## [0.2.8] - 2026-08-18

### 发布说明
- 修复pyproject.toml中的UTF-8 BOM导致pip安装失败
- 移除BOM以防止安装期间的tomllib.TOMLDecodeError
- 文件现在使用标准UTF-8编码，不带BOM

### 变更内容

#### 错误修复:
- 从pyproject.toml中移除UTF-8 BOM
- BOM导致Python的tomllib解析文件失败
- 现在使用标准UTF-8编码

### 优势
- ✅ pip install现在可以正常工作
- ✅ 安装期间不再有TOMLDecodeError
- ✅ 与Python的tomllib模块更好的兼容性

## [0.2.7] - 2026-08-18

### 发布说明
- 修复upgrade.ps1脚本以处理未跟踪文件的Git冲突
- 更新升级文档移除PyPI引用
- 添加git stash以防止本地配置文件冲突
- 改进Git操作的错误处理
- 修复升级后版本显示问题

### 变更内容

#### 升级脚本修复:
- 添加拉取更新前的自动git stash
- 防止configs/config.yaml和其他本地文件冲突
- 更好的错误处理和用户反馈
- 升级后重新读取版本以显示正确版本
- 优雅处理未跟踪文件

#### 文档更新:
- 更新UPGRADE_GUIDE.md移除PyPI升级方法
- 更新UPGRADE_GUIDE_CN.md移除PyPI升级方法
- 添加明确警告说明项目未发布到PyPI
- 记录仅使用GitHub的正确升级方法

### 优势
- ✅ 升级脚本现在可以正确处理本地配置文件
- ✅ 升级期间不再有Git冲突
- ✅ 升级后准确的版本显示
- ✅ 更好的升级用户体验
- ✅ 清晰的升级过程文档

### 修复
- 修复upgrade.ps1在configs/config.yaml冲突时失败
- 修复升级后显示旧版本
- 修复文档建议不工作的PyPI命令

## [0.2.6] - 2026-08-18

### 发布说明
- 更新Open WebUI集成以使用Python 3.12确保兼容性
- 简化集成方法以使用分离界面
- 更新文档以反映当前集成方法
- 由于路由冲突移除复杂的iframe集成
- Open WebUI现在独立运行，带有HuggingFace警告（非关键）
- 文档管理界面保持完全功能，包含所有特性

### 变更内容

#### Open WebUI集成:
- 更新open_webui.ps1通过`py -3.12`使用Python 3.12
- 配置Open WebUI使用Ollama嵌入模型（nomic-embed-text）
- 在.env文件中添加环境变量配置
- 简化启动脚本以提高可靠性

#### 文档更新:
- 更新OPENWEBUI_INTEGRATION.md包含简化的集成指南
- 更新OPENWEBUI_INTEGRATION_CN.md包含中文版本
- 更新README.md反映当前集成方法
- 更新README_CN.md包含中文版本
- 移除对复杂iframe集成的引用

#### 代码清理:
- 移除重复的集成路由
- 简化main.py路由结构
- 清理docs_ui.py集成端点
- 移除未使用的静态文件集成尝试

### 优势
- ✅ 更可靠的Open WebUI启动
- ✅ 更清晰的关注点分离
- ✅ 更准确的文档
- ✅ 简化的用户工作流程
- ✅ 保留所有核心功能

### 已知问题
- Open WebUI启动时显示HuggingFace模型下载警告（非关键）
- 这不影响基本聊天和查询功能
- 用户可以安全忽略这些警告

## [0.2.5] - 2026-08-18

### 发布说明
- 版本从0.2.4升级到0.2.5
- 详细变更请查看提交历史

## [0.2.4] - 2026-08-18

### 发布说明
- 版本从0.2.3升级到0.2.4
- 详细变更请查看提交历史

## [0.2.3] - 2026-08-18

### 发布说明
- 版本从0.2.2升级到0.2.3
- 详细变更请查看提交历史

## [0.2.2] - 2026-08-18

### 错误修复
- 修复文档管理界面中的文件夹浏览按钮错误
- 实现使用浏览器文件选择API的正确文件夹选择
- 用功能性的文件夹选择替换错误警报

### 新功能
- 添加文档导入的浏览器文件夹选择
- 实现双重导入方法（浏览器选择器 + 手动路径）
- 选择文件夹时显示文件数量
- 改进文件夹导入过程中的用户反馈

### 变更内容

#### 文档管理界面 (src/rag_kb/api/docs_ui.py):
- 使用webkitdirectory替换错误警报以实现功能性文件夹选择
- 添加带有webkitdirectory和directory属性的HTML文件输入
- 实现handleFolderSelect()函数处理选定的文件
- 添加importSelectedFiles()函数用于基于浏览器的文件上传
- 保持与服务器端文件夹导入的向后兼容性
- 选择文件夹时显示文件数量和文件夹名称
- 在导入过程中提供清晰的用户反馈

#### 用户体验改进:
- 用户现在可以点击"选择文件夹"按钮选择文件夹
- 系统自动上传选定文件夹中的所有文件
- 显示为导入选择的文件数量
- 保持手动路径输入作为替代方法
- 文件上传期间清晰的进度指示

#### 文档更新:
- 更新故障排除指南包含文件夹选择说明
- 更新用户指南包含新的文件夹导入工作流程
- 添加浏览器兼容性说明
- 提供清晰的分步说明

### 优势
- ✅ 文件夹选择现在在现代浏览器中工作
- ✅ 浏览文件夹时不再有错误警报
- ✅ 更好的文件夹导入用户体验
- ✅ 支持基于浏览器和服务器端的导入
- ✅ 导入过程中清晰的反馈

### 技术细节
- 使用webkitdirectory属性支持Chrome/Edge
- 回退到手动路径输入用于服务器端访问
- 保持现有API端点以实现向后兼容
- 通过现有上传管道处理文件

## [0.2.1] - 2026-08-18

### 关键修复
- 修复由于HuggingFace模型下载问题导致的Open WebUI启动失败
- 解决Open WebUI尝试下载模型时的PowerShell脚本启动失败
- 消除Open WebUI启动的网络依赖

### 新功能
- 添加生产就绪配置文件（configs/config.yaml）
- 添加综合故障排除指南（英文和中文）
- 添加文档管理和聊天界面之间的导航链接

### 变更内容

#### 启动脚本（scripts/open_webui.ps1, scripts/start.ps1）:
- 配置Open WebUI使用Ollama嵌入而不是HuggingFace
- 添加--ollama-embedding-model nomic-embed-text参数
- 添加--embedding-engine ollama参数
- 消除对HuggingFace模型下载的依赖

#### 配置（configs/config.yaml）:
- 添加带有Ollama默认值的生产就绪配置文件
- 配置嵌入提供程序为ollama，使用nomic-embed-text模型
- 配置LLM提供程序为ollama，使用qwen2.5模型
- 包含sentence-transformers和OpenAI的注释替代方案

#### 界面集成（src/rag_kb/api/docs_ui.py）:
- 添加从文档管理到Open WebUI的导航链接
- 添加到API文档的导航链接
- 改进用户体验，界面切换清晰

#### 文档:
- 添加综合故障排除指南（docs/TROUBLESHOOTING.md）
- 添加中文故障排除指南（docs/TROUBLESHOOTING_CN.md）
- 使用新工作流程更新Open WebUI集成指南
- 更新README文件以引用故障排除指南

#### Git配置（.gitignore）:
- 将configs/config.yaml添加到跟踪文件（之前被忽略）
- 将data/users/*添加到忽略用户特定数据
- 改进数据目录结构处理

### 优势
- Open WebUI现在无需网络依赖即可可靠启动
- 所有模型通过Ollama本地运行
- 文档管理和聊天界面之间更好的集成
- 为用户提供综合故障排除文档
- 包含生产就绪配置

### 测试
- 配置文件验证通过
- 设置模块使用Ollama提供程序正确加载
- 所有更改已测试并验证

## [0.2.0] - 2026-08-18

### 主要更新
- 完整的Open WebUI iframe集成
- 文档解析系统重构
- 添加文本和Markdown解析器支持
- 修复解析器继承问题

### 新功能
- 添加Open WebUI iframe集成页面
- 创建带有服务监控的预构建集成页面
- 为.txt文件添加TextParser
- 为.md文件添加MarkdownParser
- 添加静态文件服务
- 实时服务状态监控

### 修复
- 修复解析器继承（从BaseParser继承）
- 修复文档索引功能
- 修复用户ID验证（避免保留名称）
- 更新Open WebUI安装脚本以处理npm问题

### 文档更新
- 添加Open WebUI iframe集成指南（英文和中文）
- 添加命名约定文档（英文和中文）
- 更新所有README文件
- 添加详细的集成步骤说明

### 改进
- 添加/openwebui-integration端点
- 改进健康检查端点以显示新端点
- 优化集成页面用户体验
- 添加响应式设计支持

## [0.1.9] - 2026-08-18

### 新功能
- 添加Open WebUI iframe集成功能
- 创建预构建的Open WebUI集成页面
- 添加实时服务状态监控
- 实现静态文件服务
- 添加漂亮的渐变标题设计
- 添加加载状态和错误处理
- 添加响应式设计支持
- 添加快速操作按钮

### 文档更新
- 添加Open WebUI iframe集成指南（英文和中文）
- 更新README文件包含新文档链接
- 提供详细的集成步骤和配置说明

### 改进
- 添加/openwebui-integration端点
- 改进健康检查端点以显示新集成端点
- 优化集成页面用户体验

## [0.1.8] - 2026-08-18

### 修复
- 修复LightRAG v1.5.6兼容性问题
- 更新适配器以支持新的LightRAG API
- 修复EmbeddingFunc初始化错误
- 添加适当的异步LLM和嵌入函数
- 使用wrap_embedding_func_with_attrs装饰器

### 测试
- 验证健康检查端点正常工作
- 测试当前用户API端点
- 验证用户ID和知识库名称验证
- 测试用户和知识库创建功能

## [0.1.7] - 2026-08-18

### 新功能
- 添加用户ID和知识库名称验证
- 实现当前用户ID自动显示
- 添加路径清理以防止路径遍历攻击
- 增强健康检查端点包含详细系统状态
- 添加当前用户API端点（/api/v1/current-user）
- 文档管理UI自动加载当前用户ID

### 安全改进
- 输入验证以防止特殊字符和安全风险
- 路径清理以防止目录遍历攻击
- 保留用户名验证（防止使用保留名称）
- 长度限制以防止过长的名称

### 改进
- 添加CORS中间件以获得更好的API访问
- 友好的错误消息
- 增强健康检查显示服务状态
- 文档管理UI用户体验改进

### 文档更新
- 更新健康检查端点描述
- 添加用户ID命名约定
- 提供安全最佳实践指导

## [0.1.6] - 2026-08-18

### 新功能
- 创建专用的Open WebUI启动脚本（scripts/open_webui.ps1）
- 增强start.ps1脚本，支持可选参数
- 支持禁用Open WebUI启动（-NoOpenWebUI参数）
- 支持禁用自动浏览器打开（-NoBrowser参数）
- Open WebUI脚本支持自定义端口（-Port参数）

### 改进
- 更灵活的服务管理选项
- 用户可以选择性启动服务
- 改进启动脚本的用户体验
- 更好的错误处理和依赖检查

### 文档更新
- 更新用户指南包含新脚本使用说明
- 更新安装指南包含新启动选项
- 更新README文件包含新脚本文档
- 提供详细的参数描述

## [0.1.5] - 2026-08-18

### 修复
- 修复启动时的NameError（IncrementalIndexer未定义）
- 从user_manager.py中移除IncrementalIndexer使用
- 从docs_ui.py中移除未使用的导入
- 修复文档管理UI无法加载的问题

### 改进
- 服务现在正确启动
- 文档管理UI可访问
- 解决循环依赖问题

## [0.1.4] - 2026-08-18

### 新功能
- 创建自动升级脚本（scripts/upgrade.ps1）
- 支持自动版本检查和升级
- 支持特定版本升级
- 自动备份功能

### 文档更新
- 更新升级指南以引用新升级脚本
- 更新安装指南包含升级说明
- 更新用户指南确保文档管理UI信息准确
- 更新README文件包含新功能和文档链接
- 确保所有文档准确反映当前功能

### 改进
- 改进文档一致性
- 添加Open WebUI集成指南链接
- 增强文档可读性和完整性

## [0.1.3] - 2026-08-18

### 修复
- 修复启动导入错误（IncrementalIndexer导入问题）
- 从user_manager.py中移除未使用的导入

### 改进
- 启动时自动打开文档管理UI
- 在启动输出中显示文档管理UI URL
- 改进用户体验，直接访问

### 用户体验增强
- 服务启动后文档管理界面自动打开
- 无需手动输入URL访问界面
- 更直观的服务启动过程

## [0.1.2] - 2026-08-18

### 新功能
- 现代文档管理Web界面
- 文档上传功能（支持拖放）
- 本地文件夹导入界面
- 文档管理和统计功能
- Open WebUI集成支持
- 实时进度显示
- 多用户和知识库管理界面

### 改进
- 增强用户体验
- 可视化文档管理
- 简化文档导入过程
- 支持批量操作

### 新端点
- GET /docs/docs-ui - 文档管理界面
- 完整的文档管理操作支持

### 文档更新
- 添加Open WebUI集成指南
- 更新用户指南包含新UI功能
- 详细的界面使用说明

## [0.1.1] - 2026-08-17

### 新功能
- 本地文件夹导入功能
- PowerShell导入脚本
- 简单模式，自动用户/知识库创建
- 文件夹导入API端点
- 详细的导入统计和进度显示
- 文件跳过和错误处理

### 改进
- 更新用户指南包含文件夹导入说明
- 增强用户数据管理系统
- 支持批量文档导入
- 添加文件重复检测

### 新API端点
- POST /users/{user_id}/kbs/{kb_name}/import-folder - 导入文件夹到用户知识库
- POST /import-local-folder - 简单模式文件夹导入

### 文档更新
- 更新USER_GUIDE.md和USER_GUIDE_CN.md
- 添加本地文件夹导入使用说明
- 添加故障排除指南

## [0.1.0] - 2026-08-17

### 新增
- 10K长文档RAG知识库初始版本
- 具有父子关系的结构感知文档分块
- LightRAG集成，支持hybrid/local/global/naive查询模式
- 多格式文档解析（PDF、Word、HTML、Markdown）
- 数据清洗，包含去重和PII掩码
- 带有OpenAI兼容端点的FastAPI后端
- 用于聊天界面的Open WebUI集成
- RBAC/ACL安全支持
- 增量文档更新
- 综合测试套件
- PowerShell启动脚本
- 批量文档摄取脚本

### 功能
- **文档处理**：支持10,000+长文档，具有语义分块
- **图增强检索**：LightRAG，支持向量+图混合搜索
- **Windows原生**：为Windows部署优化，使用Ollama本地模型
- **安全性**：内置访问控制和PII保护
- **性能**：父子分块，实现高精度检索
- **可扩展性**：模块化架构，支持基于插件的分析器和分块器

### 技术栈
- 后端：FastAPI, Python 3.11+
- RAG引擎：LightRAG (lightrag-hku)
- 向量存储：NanoVectorDB
- 图存储：NetworkX
- LLM：Ollama (qwen2.5, llama3.1, deepseek-r1)
- 嵌入：Ollama (nomic-embed-text, bge-m3)
- 前端：Open WebUI

### 文档
- 包含安装和使用说明的综合README
- 带有交互式Swagger UI的API文档
- Ollama和OpenAI兼容API的配置示例
- 包含单元和集成测试的测试套件

### 已知限制
- LightRAG使用本地存储（NetworkX + NanoVectorDB + JSON）
- 对于10K+文档的密集图，考虑外部向量/图数据库
- Windows特定部署（尽管核心Python代码是跨平台的）

### 迁移说明
- 这是初始版本，无需迁移

### 支持
- 文档：参见README.md和/docs目录
- 问题：请通过GitHub Issues报告
- 参考：RAG_KB_Plan.html和RAG_KB_Implementation_Framework.html