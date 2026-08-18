# 升级指南 - RAG 知识库

## 版本 0.1.0 → 未来版本

### 检查当前版本

检查当前安装的版本：

```bash
pip show rag-kb
```

### 从 GitHub 升级

#### 方法 1：使用 pip（推荐）

```bash
# 升级到最新版本
pip install --upgrade rag-kb

# 或升级到特定版本
pip install rag-kb==0.2.0
```

#### 方法 2：从 GitHub 仓库

```bash
# 克隆或拉取最新更改
cd 10K_long-doc-RAG-KB
git pull origin master

# 使用最新更改重新安装
pip install -e .
```

### 升级后步骤

#### 1. 备份当前数据

升级前始终备份您的数据：

```bash
# 备份数据目录
Copy-Item -Recurse data data_backup_$(Get-Date -Format 'yyyyMMdd')

# 备份 LightRAG 数据库
Copy-Item -Recurse lightrag_db lightrag_db_backup_$(Get-Date -Format 'yyyyMMdd')
```

#### 2. 更新配置

检查最新的 `config.example.yaml` 中是否有新的配置选项：

```bash
# 比较您的配置与示例配置
Compare-Object (Get-Content configs\config.yaml) (Get-Content configs\config.example.yaml)
```

#### 3. 更新依赖

```bash
# 更新所有依赖
pip install --upgrade -r requirements.txt

# 或更新特定的可选依赖
pip install --upgrade -e ".[lightrag,sentence-transformers]"
```

#### 4. 数据库迁移（如需要）

某些版本可能需要数据库迁移。查看发布说明中的具体迁移说明。

```bash
# 如果需要迁移，按照发布说明中的具体说明操作
```

#### 5. 重启服务

```bash
# 停止当前服务
# （停止 Ollama、FastAPI、Open WebUI）

# 使用新版本启动服务
.\scripts\start.ps1
```

### 特定版本升级说明

#### 升级到 v0.2.0（示例）

当 v0.2.0 发布时，按照以下步骤操作：

1. **查看发布说明**：阅读 v0.2.0 的 `docs/RELEASE_NOTES_CN.md`
2. **备份数据**：备份您的 `data/` 和 `lightrag_db/` 目录
3. **更新配置**：添加任何新的配置选项
4. **运行迁移**：如果数据库架构更改，运行迁移脚本
5. **测试**：在生产使用前验证基本功能

### 回滚说明

如果您需要回滚到以前的版本：

```bash
# 安装特定的先前版本
pip install rag-kb==0.1.0

# 或从 git
git checkout tags/v0.1.0
pip install -e .
```

### 升级故障排除

#### 升级后导入错误

如果遇到导入错误：

```bash
# 清除 Python 缓存
python -m pip cache purge

# 重新安装包
pip uninstall rag-kb
pip install -e .
```

#### 配置问题

如果配置不兼容：

```bash
# 备份当前配置
copy configs\config.yaml configs\config.yaml.backup

# 复制新的示例配置
copy configs\config.example.yaml configs\config.yaml

# 手动合并您的设置
```

#### 数据库兼容性问题

如果 LightRAG 数据库不兼容：

```bash
# 备份当前数据库
Copy-Item -Recurse lightrag_db lightrag_db_backup

# 重建索引（如需要）
python scripts\ingest_bulk.py
```

### 自动升级脚本

使用提供的自动升级脚本：

```powershell
# 升级到最新版本
.\scripts\upgrade.ps1

# 升级到特定版本
.\scripts\upgrade.ps1 -TargetVersion "0.1.3"

# 跳过备份（不推荐）
.\scripts\upgrade.ps1 -SkipBackup
```

升级脚本会自动：
1. 检查当前版本和最新版本
2. 创建数据备份
3. 停止运行中的服务
4. 拉取最新代码
5. 更新依赖
6. 验证安装
7. 提供重启服务的指导

### 监控升级健康状态

升级后，监控系统：

1. **检查日志**：查看日志中的任何错误
2. **测试查询**：运行示例查询以验证功能
3. **性能**：检查性能是否下降
4. **兼容性**：验证所有功能按预期工作

### 获取帮助

如果在升级过程中遇到问题：

1. 查看[发布说明](RELEASE_NOTES_CN.md)了解已知问题
2. 查看[故障排除](USER_GUIDE_CN.md#故障排除)部分
3. 提交 GitHub Issue，提供详细的错误信息
4. 查看 GitHub Discussions 获取社区帮助

### 最佳实践

1. **始终备份**：升级时绝不备份数据
2. **先测试**：在暂存环境中测试升级
3. **阅读发布说明**：升级前了解更改内容
4. **升级后监控**：在最初 24 小时内注意问题
5. **保持文档更新**：维护本地升级说明

### 升级计划

建议的升级计划：

- **关键安全更新**：立即
- **功能更新**：1-2 周内
- **错误修复**：根据需要
- **主要版本**：仔细计划和测试

### 发布渠道

- **稳定版**：推荐用于生产环境
- **测试版**：新功能，谨慎使用
- **开发版**：最新功能，可能不稳定

根据您的需求选择合适的发布渠道。