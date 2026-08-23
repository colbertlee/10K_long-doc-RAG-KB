# RAG KB 统一管理脚本使用指南

## 🎯 概述

`manage.ps1` 是 RAG KB 系统的统一管理脚本，整合了所有启动、停止、升级和管理功能。用户只需要记住一个命令即可完成所有操作。

## 📋 基本用法

```powershell
.\manage.ps1 <action> [options]
```

## 🚀 可用操作

### 1. start - 启动系统
```powershell
.\manage.ps1 start
```

**功能**:
- 检查 Python 安装
- 检查目录结构
- 检查 Ollama 服务
- 启动 API 服务器
- 显示访问地址

**输出示例**:
```
🚀 启动 RAG KB 系统...
📋 检查 Python 安装...
✅ Python: Python 3.11.5
📁 检查目录结构...
✅ 目录存在: data
🔍 检查 Ollama 服务...
✅ Ollama 服务运行中
🌐 启动 API 服务器...
   API: http://localhost:8000
   对话界面: http://localhost:8000/chat-ui
   知识图谱: http://localhost:8000/graph-ui
   按 Ctrl+C 停止服务器
```

### 2. stop - 停止系统
```powershell
.\manage.ps1 stop
```

**功能**:
- 停止 API 服务器
- 停止 Open WebUI
- 清理相关进程

### 3. restart - 重启系统
```powershell
.\manage.ps1 restart
```

**功能**:
- 停止当前运行的服务
- 等待 2 秒
- 重新启动系统

### 4. status - 查看系统状态
```powershell
.\manage.ps1 status
```

**功能**:
- 检查 API 服务器状态
- 检查 Ollama 服务状态
- 显示运行进程
- 显示端口占用情况

**输出示例**:
```
📊 RAG KB 系统状态

🌐 API 服务器:
  ✅ 状态: ok
  📦 版本: 0.4.0
  🔧 Ollama: available

🤖 Ollama 服务:
  ✅ 运行中
  📦 模型: qwen3.5:4b, nomic-embed-text

🔄 运行进程:
  ✅ API 服务器 (PID: 12345)

🔌 端口占用:
  ✅ 端口 8000 被占用
```

### 5. upgrade - 升级系统
```powershell
.\manage.ps1 upgrade [-TargetVersion <version>] [-SkipBackup]
```

**功能**:
- 停止运行中的服务
- 创建备份（默认）
- 拉取最新代码
- 切换到指定版本
- 更新依赖
- 重新启动系统

**选项**:
- `-TargetVersion`: 指定目标版本（默认：latest）
- `-SkipBackup`: 跳过备份创建

**示例**:
```powershell
# 升级到最新版本
.\manage.ps1 upgrade

# 升级到指定版本
.\manage.ps1 upgrade -TargetVersion v0.4.0

# 升级但不创建备份
.\manage.ps1 upgrade -SkipBackup
```

### 6. install - 首次安装
```powershell
.\manage.ps1 install
```

**功能**:
- 检查 Python 版本
- 创建虚拟环境
- 安装依赖
- 创建目录结构
- 配置系统

**输出示例**:
```
📦 安装 RAG KB 系统...
📋 检查 Python 版本...
✅ Python: Python 3.11.5
🐍 创建虚拟环境...
✅ 虚拟环境创建完成
📦 安装依赖...
✅ 依赖安装完成
📁 创建目录结构...
✅ 创建目录: data
✅ 创建目录: data/uploads
⚙️  配置系统...
✅ 配置文件创建完成
✅ 安装完成！
💡 使用 .\manage.ps1 start 启动系统
```

### 7. open - 在浏览器中打开
```powershell
.\manage.ps1 open
```

**功能**:
- 检查服务器是否运行
- 在默认浏览器中打开对话界面

### 8. help - 显示帮助
```powershell
.\manage.ps1 help
```

**功能**:
- 显示所有可用操作
- 显示使用示例
- 显示选项说明

## 🔧 高级选项

### -NoBrowser
启动时不自动打开浏览器

```powershell
.\manage.ps1 start -NoBrowser
```

### -NoOpenWebUI
启动时不启动 Open WebUI

```powershell
.\manage.ps1 start -NoOpenWebUI
```

### -TargetVersion
升级到指定版本

```powershell
.\manage.ps1 upgrade -TargetVersion v0.4.0
```

### -SkipBackup
升级时不创建备份

```powershell
.\manage.ps1 upgrade -SkipBackup
```

## 📊 常见使用场景

### 场景 1: 首次安装
```powershell
# 1. 克隆仓库
git clone https://github.com/colbertlee/10K_long-doc-RAG-KB.git
cd 10K_long-doc-RAG-KB

# 2. 安装系统
.\manage.ps1 install

# 3. 启动系统
.\manage.ps1 start

# 4. 在浏览器中打开
.\manage.ps1 open
```

### 场景 2: 日常使用
```powershell
# 启动系统
.\manage.ps1 start

# 检查状态
.\manage.ps1 status

# 停止系统
.\manage.ps1 stop
```

### 场景 3: 系统升级
```powershell
# 1. 检查当前状态
.\manage.ps1 status

# 2. 升级到最新版本
.\manage.ps1 upgrade

# 3. 重启系统
.\manage.ps1 restart

# 4. 验证升级
.\manage.ps1 status
```

### 场景 4: 故障排查
```powershell
# 1. 检查系统状态
.\manage.ps1 status

# 2. 重启系统
.\manage.ps1 restart

# 3. 如果问题持续，停止系统
.\manage.ps1 stop

# 4. 手动检查日志
# 查看 logs/ 目录
```

## ⚠️ 注意事项

### 1. PowerShell 执行策略
如果遇到执行策略错误，请运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 管理员权限
某些操作可能需要管理员权限，建议以管理员身份运行 PowerShell。

### 3. 端口占用
如果端口 8000 被占用，启动会失败。请先停止占用该端口的进程。

### 4. Ollama 服务
确保 Ollama 服务正在运行：
```powershell
ollama serve
```

### 5. 虚拟环境
脚本会自动检测和使用虚拟环境，但建议手动激活：
```powershell
.venv\Scripts\Activate.ps1
```

## 🆘 故障排除

### 问题 1: Python 未找到
**错误**: `❌ Python 未安装。请安装 Python 3.11+`

**解决**:
1. 从 https://www.python.org/downloads/ 下载 Python 3.11+
2. 安装时勾选 "Add Python to PATH"
3. 重启 PowerShell

### 问题 2: Ollama 未运行
**错误**: `⚠️  Ollama 未运行。建议启动: ollama serve`

**解决**:
```powershell
# 启动 Ollama
ollama serve

# 在另一个 PowerShell 窗口中启动 RAG KB
.\manage.ps1 start
```

### 问题 3: 端口被占用
**错误**: `❌ 端口 8000 被占用`

**解决**:
```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000

# 停止该进程
taskkill /PID <进程ID> /F

# 或使用管理脚本停止
.\manage.ps1 stop
```

### 问题 4: 依赖安装失败
**错误**: `❌ 依赖安装失败`

**解决**:
```powershell
# 手动安装依赖
pip install -e .[all]

# 或升级 pip
python -m pip install --upgrade pip
pip install -e .[all]
```

## 📚 相关文档

- **README.md**: 完整的用户指南
- **AGENTS.md**: 开发者信息
- **docs/PERFORMANCE_TUNING.md**: 性能优化指南
- **docs/TROUBLESHOOTING.md**: 故障排除指南

## 💡 最佳实践

1. **定期检查状态**: 使用 `.\manage.ps1 status` 定期检查系统状态
2. **升级前备份**: 升级前让脚本自动创建备份
3. **使用虚拟环境**: 始终在虚拟环境中运行
4. **监控日志**: 定期检查 logs/ 目录中的日志文件
5. **定期清理**: 定期清理旧的备份文件

## 🎯 从旧脚本迁移

如果您之前使用的是分散的脚本，迁移很简单：

| 旧脚本 | 新命令 |
|--------|--------|
| `.\scripts\start.ps1` | `.\manage.ps1 start` |
| `.\scripts\start.bat` | `.\manage.ps1 start` |
| `.\scripts\upgrade.ps1` | `.\manage.ps1 upgrade` |
| `.\scripts\install.ps1` | `.\manage.ps1 install` |
| `.\scripts\open_webui.ps1` | `.\manage.ps1 open` |

## 📞 获取帮助

如果遇到问题：
1. 运行 `.\manage.ps1 help` 查看帮助信息
2. 检查 logs/ 目录中的日志文件
3. 查看相关文档
4. 在 GitHub 上提交 Issue