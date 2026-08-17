# Manual GitHub Release Instructions for colbertlee

## 🚀 GitHub Release Process

由于PowerShell执行策略限制，请按照以下步骤手动进行GitHub发布：

### Step 1: 创建GitHub仓库

1. 访问：https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `10K_long-doc-RAG-KB`
   - **Description**: `Enterprise-grade RAG Knowledge Base for 10K+ long documents with LightRAG graph-enhanced retrieval`
   - **Visibility**: Public（推荐）
   - **重要**: 不要初始化README、.gitignore或license
3. 点击"Create repository"

### Step 2: 推送代码到GitHub

在PowerShell中执行：

```powershell
cd "C:\Users\liz8\OneDrive - Dell Technologies\Documents\BaiduSyncdisk\Works\Vibe_Coding\10K_long-doc-RAG-KB"

# 添加远程仓库
git remote add origin https://github.com/colbertlee/10K_long-doc-RAG-KB.git

# 推送代码
git push -u origin master

# 推送标签
git push origin v0.1.0
```

### Step 3: 创建GitHub Release

**方法A：使用GitHub CLI（自动）**

```powershell
# 创建Release
gh release create v0.1.0 `
  --title "Version 0.1.0 - Initial Release" `
  --notes-file docs/RELEASE_NOTES.md `
  --repo colbertlee/10K_long-doc-RAG-KB
```

**方法B：使用GitHub网页界面（手动）**

1. 访问：https://github.com/colbertlee/10K_long-doc-RAG-KB/releases
2. 点击"Create a new release"
3. 选择标签：`v0.1.0`
4. Release title: `Version 0.1.0 - Initial Release`
5. Description: 复制`docs/RELEASE_NOTES.md`的内容
6. 点击"Publish release"

### Step 4: 验证发布

1. 检查Release是否出现在：https://github.com/colbertlee/10K_long-doc-RAG-KB/releases
2. 验证发布说明是否正确显示
3. 测试安装：`pip install git+https://github.com/colbertlee/10K_long-doc-RAG-KB.git`

## 🔄 未来版本的自动发布

### 自动发布流程已配置

GitHub Actions工作流（`.github/workflows/release.yml`）已配置为：
- 在版本标签（v*）时自动触发
- 自动构建Python包
- 自动创建包含资源的GitHub Release

### 未来发布步骤

**每个新版本：**

1. **更新pyproject.toml中的版本：**
   ```toml
   version = "0.2.0"  # 增加版本号
   ```

2. **更新发布说明：**
   - 编辑`docs/RELEASE_NOTES.md`
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
   - GitHub Actions将自动构建包
   - GitHub Actions将创建包含资源的Release
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

- [ ] 在GitHub上创建仓库
- [ ] 代码成功推送
- [ ] 标签成功推送
- [ ] 使用正确说明创建Release
- [ ] 从GitHub测试安装
- [ ] 文档链接正常工作
- [ ] CI/CD工作流成功运行

## 🎯 当前状态

**一旦GitHub仓库创建完成，即可进行GitHub发布。**

所有代码已提交、标记并准备就绪。唯一剩余的步骤是在GitHub上创建仓库并推送代码。

**仓库URL：** https://github.com/colbertlee/10K_long-doc-RAG-KB

## 🔧 PowerShell执行策略（可选）

如果需要运行PowerShell脚本，可以临时更改执行策略：

```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 运行脚本
.\scripts\create_github_repo.ps1

# 恢复原始策略
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope Process
```

但建议使用上述手动步骤，这样更安全可靠。