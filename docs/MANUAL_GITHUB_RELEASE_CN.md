# 手动 GitHub 发布说明 for colbertlee

## 🚀 GitHub 发布完整流程

由于 PowerShell 执行策略限制，请按照以下步骤手动进行 GitHub 发布：

### Step 1: 创建 GitHub 仓库

1. 访问：https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `10K_long-doc-RAG-KB`
   - **Description**: `Enterprise-grade RAG Knowledge Base for 10K+ long documents with LightRAG graph-enhanced retrieval`
   - **Visibility**: Public（推荐）
   - **重要**: 不要初始化 README、.gitignore 或 license
3. 点击"Create repository"

### Step 2: 推送代码到 GitHub

在 PowerShell 中执行：

```powershell
cd "C:\Users\liz8\OneDrive - Dell Technologies\Documents\BaiduSyncdisk\Works\Vibe_Coding\10K_long-doc-RAG-KB"

# 添加远程仓库
git remote add origin https://github.com/colbertlee/10K_long-doc-RAG-KB.git

# 推送代码
git push -u origin master

# 推送标签
git push origin v0.1.0
```

### Step 3: 创建 GitHub Release

**方法 A：使用 GitHub CLI（自动）**

```powershell
# 创建 Release
gh release create v0.1.0 `
  --title "Version 0.1.0 - Initial Release" `
  --notes-file docs/RELEASE_NOTES_CN.md `
  --repo colbertlee/10K_long-doc-RAG-KB
```

**方法 B：使用 GitHub 网页界面（手动）**

1. 访问：https://github.com/colbertlee/10K_long-doc-RAG-KB/releases
2. 点击"Create a new release"
3. 选择标签：`v0.1.0`
4. Release title: `Version 0.1.0 - Initial Release`
5. Description: 复制`docs/RELEASE_NOTES_CN.md`的内容
6. 点击"Publish release"

### Step 4: 验证发布

1. 检查 Release 是否出现在：https://github.com/colbertlee/10K_long-doc-RAG-KB/releases
2. 验证发布说明是否正确显示
3. 测试安装：`pip install git+https://github.com/colbertlee/10K_long-doc-RAG-KB.git`

## 🔄 未来版本的自动发布

### 自动发布流程已配置

GitHub Actions 工作流（`.github/workflows/release.yml`）已配置为：
- 在版本标签（v*）时自动触发
- 自动构建 Python 包
- 自动创建包含资源的 GitHub Release

### 未来发布步骤

**每个新版本：**

1. **更新 pyproject.toml 中的版本：**
   ```toml
   version = "0.2.0"  # 增加版本号
   ```

2. **更新发布说明：**
   - 编辑`docs/RELEASE_NOTES_CN.md`
   - 添加新版本部分

3. **提交更改：**
   ```bash
   git add .
   git commit -m "chore: bump version to 0.2.0"
   ```

4. **创建并推送标签：**
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin master
   git push origin v0.2.0
   ```

5. **自动发布：**
   - GitHub Actions 将自动构建包
   - GitHub Actions 将创建包含资源的 Release
   - 无需手动干预

### 使用脚本自动化

使用提供的脚本进行未来发布：

```powershell
# 首先在脚本中更新版本
# scripts/github_release.ps1
$VERSION = "v0.2.0"

# 运行脚本
.\scripts\github_release.ps1
```

## 📋 发布后检查清单

- [ ] 在 GitHub 上创建仓库
- [ ] 代码成功推送
- [ ] 标签成功推送
- [ ] 使用正确说明创建 Release
- [ ] 从 GitHub 测试安装
- [ ] 文档链接正常工作
- [ ] CI/CD 工作流成功运行

## 🎯 当前状态

**一旦 GitHub 仓库创建完成，即可进行 GitHub 发布。**

所有代码已提交、标记并准备就绪。唯一剩余的步骤是在 GitHub 上创建仓库并推送代码。

**仓库 URL：** https://github.com/colbertlee/10K_long-doc-RAG-KB

## 🔧 PowerShell 执行策略（可选）

如果需要运行 PowerShell 脚本，可以临时更改执行策略：

```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 运行脚本
.\scripts\create_github_repo.ps1

# 恢复原始策略
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope Process
```

但建议使用上述手动步骤，这样更安全可靠。