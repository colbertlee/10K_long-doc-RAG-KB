"""Document management UI for RAG Knowledge Base."""

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Optional
import shutil
import json
import os

router = APIRouter()


def get_current_user_id():
    """Get current user ID from environment or default."""
    return os.environ.get('RAGKB_CURRENT_USER', 'default')


@router.get("/docs-ui", response_class=HTMLResponse)
async def document_management_ui():
    """Serve the document management UI."""
    ui_path = Path(__file__).parent.parent.parent / "static" / "docs-ui.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(encoding='utf-8'))
    
    # Return embedded HTML if file doesn't exist
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG知识库 - 文档管理</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .card { background: white; border-radius: 10px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card h2 { color: #333; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        .form-group input, .form-group select { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: #667eea; }
        .btn { background: #667eea; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: 600; transition: background 0.3s; }
        .btn:hover { background: #5568d3; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #5a6268; }
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #218838; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .upload-area { border: 2px dashed #667eea; border-radius: 10px; padding: 40px; text-align: center; background: #f8f9ff; cursor: pointer; transition: all 0.3s; }
        .upload-area:hover { background: #e8ebff; border-color: #5568d3; }
        .upload-area.dragover { background: #d1d5ff; border-color: #4c5fd5; }
        .upload-area p { color: #667eea; font-size: 18px; margin-bottom: 10px; }
        .upload-area small { color: #999; }
        .progress-bar { width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; margin-top: 10px; }
        .progress-bar-fill { height: 100%; background: #667eea; transition: width 0.3s; }
        .status { padding: 15px; border-radius: 5px; margin-top: 15px; }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.info { background: #d1ecf1; color: #0c5460; }
        .document-list { margin-top: 20px; }
        .document-item { background: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 5px; border-left: 4px solid #667eea; }
        .document-item h4 { color: #333; margin-bottom: 5px; }
        .document-item p { color: #666; font-size: 14px; }
        .tabs { display: flex; margin-bottom: 20px; border-bottom: 2px solid #ddd; }
        .tab { padding: 15px 25px; cursor: pointer; background: #f8f9fa; border: 1px solid #ddd; border-bottom: none; margin-right: 5px; border-radius: 5px 5px 0 0; }
        .tab.active { background: white; border-bottom: 2px solid white; margin-bottom: -2px; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }
        .stat-card h3 { font-size: 2em; color: #667eea; margin-bottom: 5px; }
        .stat-card p { color: #666; }
        .kb-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .kb-card { background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #667eea; }
        .kb-card h3 { color: #333; margin-bottom: 15px; }
        .kb-actions { display: flex; gap: 10px; margin-top: 15px; }
        .btn-sm { padding: 8px 15px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 RAG知识库 - 文档管理</h1>
            <p>轻松管理您的文档，构建智能知识库</p>
            <div style="margin-top: 15px;">
                <a href="http://localhost:8080" target="_blank" style="color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 5px; margin-right: 10px;">💬 打开聊天界面 (Open WebUI)</a>
                <a href="http://localhost:8000/docs" target="_blank" style="color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 5px;">📖 API文档</a>
            </div>
        </div>

        <div class="card">
            <div class="tabs">
                <div class="tab active" onclick="switchTab('upload')">📄 文档上传</div>
                <div class="tab" onclick="switchTab('folder')">📁 文件夹导入</div>
                <div class="tab" onclick="switchTab('kbs')">🗄️ 知识库管理</div>
                <div class="tab" onclick="switchTab('graph')">🕸️ 知识图谱</div>
                <div class="tab" onclick="switchTab('manage')">📋 文档管理</div>
            </div>

            <!-- 文档上传 -->
            <div id="upload-tab" class="tab-content active">
                <h2>上传文档</h2>
                <div class="form-group">
                    <label>用户ID</label>
                    <input type="text" id="upload-user-id" value="" placeholder="输入用户ID">
                    <small style="color: #666;">当前登录用户</small>
                </div>
                <div class="form-group">
                    <label>知识库名称</label>
                    <input type="text" id="upload-kb-name" value="default" placeholder="输入知识库名称">
                </div>
                <div class="upload-area" id="upload-area" onclick="document.getElementById('file-input').click()">
                    <p>📤 点击或拖拽文件到此处上传</p>
                    <small>支持 PDF, Word, Markdown, Text 格式</small>
                    <input type="file" id="file-input" multiple style="display: none" accept=".pdf,.docx,.md,.txt,.html">
                </div>
                <div id="upload-progress" class="progress-bar" style="display: none;">
                    <div class="progress-bar-fill" id="upload-progress-fill" style="width: 0%"></div>
                </div>
                <div id="upload-status" class="status" style="display: none;"></div>
                <button class="btn" onclick="uploadDocuments()" style="margin-top: 20px;">开始上传</button>
            </div>

            <!-- 文件夹导入 -->
            <div id="folder-tab" class="tab-content">
                <h2>导入本地文件夹</h2>
                <div class="form-group">
                    <label>用户ID</label>
                    <input type="text" id="folder-user-id" value="" placeholder="输入用户ID">
                    <small style="color: #666;">当前登录用户</small>
                </div>
                <div class="form-group">
                    <label>知识库名称</label>
                    <input type="text" id="folder-kb-name" value="default" placeholder="输入知识库名称">
                </div>
                <div class="form-group">
                    <label>文件夹路径</label>
                    <input type="text" id="folder-path" placeholder="C:\\Users\\YourName\\Documents\\KB">
                </div>
                <div class="form-group">
                    <label>或选择文件夹（支持批量文件选择）</label>
                    <input type="file" id="folder-input" webkitdirectory directory multiple style="display: none" onchange="handleFolderSelect(event)">
                    <button class="btn btn-secondary" onclick="selectFolder()">📁 选择文件夹</button>
                    <small style="color: #666; display: block; margin-top: 5px;">支持选择文件夹内的所有文件进行批量导入</small>
                </div>
                <div id="folder-progress" class="progress-bar" style="display: none;">
                    <div class="progress-bar-fill" id="folder-progress-fill" style="width: 0%"></div>
                </div>
                <div id="folder-status" class="status" style="display: none;"></div>
                <button class="btn btn-success" onclick="importFolder()" style="margin-top: 20px;">开始导入</button>
            </div>

            <!-- 知识库管理 -->
            <div id="kbs-tab" class="tab-content">
                <h2>知识库管理</h2>
                <div class="form-group">
                    <label>用户ID</label>
                    <input type="text" id="kb-user-id" value="" placeholder="输入用户ID">
                    <small style="color: #666;">当前登录用户</small>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <button class="btn" onclick="loadKnowledgeBases()">🔄 刷新知识库列表</button>
                    <button class="btn btn-success" onclick="showCreateKbModal()">➕ 创建新知识库</button>
                </div>
                
                <div id="kb-list" class="kb-list">
                    <p style="color: #666; text-align: center;">点击"刷新知识库列表"查看您的知识库</p>
                </div>
                
                <!-- 创建知识库模态框 -->
                <div id="create-kb-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
                    <div style="background: white; padding: 30px; border-radius: 10px; width: 400px; margin: 100px auto; position: relative;">
                        <h3 style="margin-top: 0;">创建新知识库</h3>
                        <div class="form-group">
                            <label>知识库名称</label>
                            <input type="text" id="new-kb-name" placeholder="输入知识库名称" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        </div>
                        <div style="margin-top: 20px;">
                            <button class="btn btn-success" onclick="createKnowledgeBase()">创建</button>
                            <button class="btn btn-secondary" onclick="hideCreateKbModal()">取消</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 知识图谱 -->
            <div id="graph-tab" class="tab-content">
                <h2>知识图谱可视化</h2>
                <div class="form-group">
                    <label>用户ID</label>
                    <input type="text" id="graph-user-id" value="" placeholder="输入用户ID">
                    <small style="color: #666;">当前登录用户</small>
                </div>
                <div class="form-group">
                    <label>知识库名称</label>
                    <select id="graph-kb-name" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px;">
                        <option value="default">default</option>
                    </select>
                </div>
                <div style="margin-bottom: 20px;">
                    <button class="btn" onclick="loadKnowledgeGraph()">🔄 加载知识图谱</button>
                    <button class="btn btn-secondary" onclick="clearGraph()">🗑️ 清除图谱</button>
                </div>
                
                <div id="graph-stats" class="stats-grid" style="display: none;">
                    <div class="stat-card">
                        <h3 id="graph-nodes">0</h3>
                        <p>实体节点</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="graph-edges">0</h3>
                        <p>关系边</p>
                    </div>
                </div>
                
                <div id="graph-container" style="width: 100%; height: 500px; border: 1px solid #ddd; border-radius: 10px; background: #f8f9fa; display: none; position: relative;">
                    <canvas id="graph-canvas" style="width: 100%; height: 100%;"></canvas>
                    <div id="graph-info" style="position: absolute; bottom: 10px; left: 10px; background: rgba(255,255,255,0.9); padding: 10px; border-radius: 5px; font-size: 12px; display: none;">
                        <strong>节点信息:</strong> <span id="node-info"></span>
                    </div>
                </div>
                
                <div id="graph-placeholder" style="text-align: center; padding: 60px; color: #666;">
                    <p>🕸️ 知识图谱可视化</p>
                    <p style="font-size: 14px; margin-top: 10px;">LightRAG在后台自动构建知识图谱，包含文档中的实体和关系。</p>
                    <p style="font-size: 14px; margin-top: 10px;">点击"加载知识图谱"按钮查看图谱结构。</p>
                    <div style="margin-top: 20px; font-size: 13px; color: #888;">
                        <p>注意：需要先导入文档才能看到知识图谱</p>
                    </div>
                </div>
            </div>

            <!-- 文档管理 -->
            <div id="manage-tab" class="tab-content">
                <h2>文档管理</h2>
                <div class="form-group">
                    <label>用户ID</label>
                    <input type="text" id="manage-user-id" value="" placeholder="输入用户ID">
                    <small style="color: #666;">当前登录用户</small>
                </div>
                <div class="form-group">
                    <label>知识库名称</label>
                    <select id="manage-kb-name" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px;">
                        <option value="default">default</option>
                    </select>
                </div>
                <button class="btn" onclick="loadDocuments()" style="margin-bottom: 20px;">加载文档列表</button>
                
                <div id="document-stats" class="stats-grid" style="display: none;">
                    <div class="stat-card">
                        <h3 id="stat-total">0</h3>
                        <p>总文档数</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="stat-size">0 MB</h3>
                        <p>总大小</p>
                    </div>
                </div>
                
                <div id="document-list" class="document-list"></div>
            </div>
        </div>
    </div>

    <script>
        // Load current user ID on page load
        async function loadCurrentUserId() {
            try {
                const response = await fetch('/api/v1/current-user');
                const userData = await response.json();
                const currentUserId = userData.user_id || 'default';
                
                // Set current user ID in all input fields
                document.getElementById('upload-user-id').value = currentUserId;
                document.getElementById('folder-user-id').value = currentUserId;
                document.getElementById('manage-user-id').value = currentUserId;
                document.getElementById('kb-user-id').value = currentUserId;
                document.getElementById('graph-user-id').value = currentUserId;
                
                // Update placeholder text
                document.getElementById('upload-user-id').placeholder = `当前用户: ${currentUserId}`;
                document.getElementById('folder-user-id').placeholder = `当前用户: ${currentUserId}`;
                document.getElementById('manage-user-id').placeholder = `当前用户: ${currentUserId}`;
                document.getElementById('kb-user-id').placeholder = `当前用户: ${currentUserId}`;
                document.getElementById('graph-user-id').placeholder = `当前用户: ${currentUserId}`;
            } catch (error) {
                console.error('Failed to load current user:', error);
                // Fallback to default
                const defaultUser = 'default';
                document.getElementById('upload-user-id').value = defaultUser;
                document.getElementById('folder-user-id').value = defaultUser;
                document.getElementById('manage-user-id').value = defaultUser;
                document.getElementById('kb-user-id').value = defaultUser;
                document.getElementById('graph-user-id').value = defaultUser;
            }
        }
        
        // Load current user when page loads
        window.addEventListener('DOMContentLoaded', loadCurrentUserId);

        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            
            // Auto-load knowledge bases when switching to KB management tab
            if (tabName === 'kbs') {
                loadKnowledgeBases();
            }
            
            // Auto-load KB list when switching to document management
            if (tabName === 'manage') {
                loadKnowledgeBasesForSelect();
            }
            
            // Auto-load KB list when switching to graph tab
            if (tabName === 'graph') {
                loadKnowledgeBasesForGraph();
            }
        }

        function showStatus(elementId, message, type) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.className = 'status ' + type;
            element.style.display = 'block';
        }

        function updateProgress(elementId, percentage) {
            const fill = document.getElementById(elementId + '-fill');
            const bar = document.getElementById(elementId);
            fill.style.width = percentage + '%';
            bar.style.display = 'block';
        }

        async function uploadDocuments() {
            const userId = document.getElementById('upload-user-id').value;
            const kbName = document.getElementById('upload-kb-name').value;
            const fileInput = document.getElementById('file-input');
            const files = fileInput.files;

            if (files.length === 0) {
                showStatus('upload-status', '请选择要上传的文件', 'error');
                return;
            }

            showStatus('upload-status', '正在上传文档...', 'info');
            updateProgress('upload-progress', 10);

            try {
                // Create knowledge base if needed
                await fetch('/api/v1/users/' + userId + '/kbs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: 'kb_name=' + encodeURIComponent(kbName)
                });

                updateProgress('upload-progress', 30);

                // Upload files
                let uploadedCount = 0;
                for (let i = 0; i < files.length; i++) {
                    const formData = new FormData();
                    formData.append('file', files[i]);

                    await fetch('/api/v1/users/' + userId + '/kbs/' + kbName + '/upload', {
                        method: 'POST',
                        body: formData
                    });

                    uploadedCount++;
                    updateProgress('upload-progress', 30 + (uploadedCount / files.length) * 60);
                }

                // Ingest documents
                updateProgress('upload-progress', 90);
                await fetch('/api/v1/users/' + userId + '/kbs/' + kbName + '/ingest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        acl: { read: [userId], write: [userId] }
                    })
                });

                updateProgress('upload-progress', 100);
                showStatus('upload-status', '成功上传 ' + files.length + ' 个文档！', 'success');
                fileInput.value = '';

            } catch (error) {
                showStatus('upload-status', '上传失败: ' + error.message, 'error');
            }
        }

        function browseFolder() {
            // Use the folder input instead
            document.getElementById('folder-input').click();
        }

        function selectFolder() {
            // Trigger folder selection
            const folderInput = document.getElementById('folder-input');
            folderInput.click();
        }

        function handleFolderSelect(event) {
            const files = event.target.files;
            if (files.length > 0) {
                // Get the folder path from the first file's webkitRelativePath
                const firstFile = files[0];
                const folderPath = firstFile.webkitRelativePath.split('/')[0];
                
                // Update the folder path input with the folder name
                document.getElementById('folder-path').value = folderPath;
                
                // Show selected files count
                showStatus('folder-status', `已选择文件夹: ${folderPath}，包含 ${files.length} 个文件`, 'info');
                
                // Store files for later upload
                window.selectedFolderFiles = files;
            } else {
                // No files selected, show helpful message
                showStatus('folder-status', '未选择文件。请确保选择了包含文档的文件夹。', 'warning');
            }
        }

        async function importFolder() {
            const userId = document.getElementById('folder-user-id').value;
            const kbName = document.getElementById('folder-kb-name').value;
            const folderPath = document.getElementById('folder-path').value;

            // Check if files were selected via folder picker
            if (window.selectedFolderFiles && window.selectedFolderFiles.length > 0) {
                await importSelectedFiles(userId, kbName);
                return;
            }

            // Fallback to server-side folder import
            if (!folderPath) {
                showStatus('folder-status', '请选择文件夹或输入文件夹路径', 'error');
                return;
            }

            showStatus('folder-status', '正在通过服务器导入文件夹...', 'info');
            updateProgress('folder-progress', 20);

            try {
                const response = await fetch('/api/v1/import-local-folder', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        folder_path: folderPath,
                        user_id: userId,
                        kb_name: kbName,
                        acl: { read: [userId], write: [userId] }
                    })
                });

                const result = await response.json();

                if (result.success) {
                    updateProgress('folder-progress', 100);
                    showStatus('folder-status', 
                        '成功导入 ' + result.files_processed + ' 个文档！\\n' +
                        '跳过: ' + result.files_skipped + ' 个文件\\n' +
                        '失败: ' + result.files_failed + ' 个文件', 
                        'success');
                } else {
                    showStatus('folder-status', '导入失败', 'error');
                }

            } catch (error) {
                showStatus('folder-status', '导入失败: ' + error.message, 'error');
            }
        }

        async function importSelectedFiles(userId, kbName) {
            const files = window.selectedFolderFiles;
            
            showStatus('folder-status', '正在上传选中的文件...', 'info');
            updateProgress('folder-progress', 10);

            try {
                // Create knowledge base if needed
                await fetch('/api/v1/users/' + userId + '/kbs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: 'kb_name=' + encodeURIComponent(kbName)
                });

                updateProgress('folder-progress', 20);

                // Upload files
                let uploadedCount = 0;
                for (let i = 0; i < files.length; i++) {
                    const formData = new FormData();
                    formData.append('file', files[i]);

                    await fetch('/api/v1/users/' + userId + '/kbs/' + kbName + '/upload', {
                        method: 'POST',
                        body: formData
                    });

                    uploadedCount++;
                    updateProgress('folder-progress', 20 + (uploadedCount / files.length) * 60);
                }

                // Ingest documents
                updateProgress('folder-progress', 90);
                await fetch('/api/v1/users/' + userId + '/kbs/' + kbName + '/ingest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        acl: { read: [userId], write: [userId] }
                    })
                });

                updateProgress('folder-progress', 100);
                showStatus('folder-status', '成功导入 ' + files.length + ' 个文档！', 'success');
                
                // Clear selected files
                window.selectedFolderFiles = null;
                document.getElementById('folder-input').value = '';
                document.getElementById('folder-path').value = '';

            } catch (error) {
                showStatus('folder-status', '导入失败: ' + error.message, 'error');
            }
        }

        async function loadDocuments() {
            const userId = document.getElementById('manage-user-id').value;
            const kbName = document.getElementById('manage-kb-name').value;

            try {
                const response = await fetch('/api/v1/users/' + userId + '/kbs/' + kbName + '/stats');
                const stats = await response.json();

                if (stats.error) {
                    showStatus('document-list', '知识库不存在: ' + stats.error, 'error');
                    return;
                }

                // Show stats
                document.getElementById('stat-total').textContent = stats.file_count;
                const totalSize = stats.total_size_mb || 0;
                document.getElementById('stat-size').textContent = totalSize.toFixed(2) + ' MB';
                document.getElementById('document-stats').style.display = 'grid';

                // Load document list (placeholder)
                const listDiv = document.getElementById('document-list');
                listDiv.innerHTML = '<p>文档列表功能正在开发中...</p>';

            } catch (error) {
                showStatus('document-list', '加载失败: ' + error.message, 'error');
            }
        }

        // Knowledge Base Management Functions
        async function loadKnowledgeBases() {
            const userId = document.getElementById('kb-user-id').value;
            const kbListDiv = document.getElementById('kb-list');
            
            try {
                kbListDiv.innerHTML = '<p style="color: #666; text-align: center;">加载中...</p>';
                
                const response = await fetch('/api/v1/users/' + userId + '/kbs');
                const data = await response.json();
                
                if (data.knowledge_bases && data.knowledge_bases.length > 0) {
                    let kbHTML = '<div class="kb-grid">';
                    data.knowledge_bases.forEach(kb => {
                        kbHTML += '<div class="kb-card"><h3>📚 ' + kb + '</h3><div class="kb-actions"><button class="btn btn-sm" onclick="loadKbStats(\'' + userId + '\', \'' + kb + '\')">📊 统计</button><button class="btn btn-sm btn-danger" onclick="deleteKnowledgeBase(\'' + userId + '\', \'' + kb + '\')">🗑️ 删除</button></div></div>';
                    });
                    kbHTML += '</div>';
                    kbListDiv.innerHTML = kbHTML;
                } else {
                    kbListDiv.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><p>还没有知识库</p><button class="btn btn-success" onclick="showCreateKbModal()" style="margin-top: 15px;">➕ 创建第一个知识库</button></div>';
                }
            } catch (error) {
                kbListDiv.innerHTML = '<p style="color: red; text-align: center;">加载失败: ' + error.message + '</p>';
            }
        }

        async function loadKnowledgeBasesForSelect() {
            const userId = document.getElementById('manage-user-id').value;
            const kbSelect = document.getElementById('manage-kb-name');
            
            try {
                const response = await fetch('/api/v1/users/' + userId + '/kbs');
                const data = await response.json();
                
                // Clear existing options except default
                kbSelect.innerHTML = '<option value="default">default</option>';
                
                if (data.knowledge_bases && data.knowledge_bases.length > 0) {
                    data.knowledge_bases.forEach(kb => {
                        if (kb !== 'default') {
                            const option = document.createElement('option');
                            option.value = kb;
                            option.textContent = kb;
                            kbSelect.appendChild(option);
                        }
                    });
                }
            } catch (error) {
                console.error('Failed to load knowledge bases:', error);
            }
        }

        function showCreateKbModal() {
            document.getElementById('create-kb-modal').style.display = 'block';
            document.getElementById('new-kb-name').value = '';
            document.getElementById('new-kb-name').focus();
        }

        function hideCreateKbModal() {
            document.getElementById('create-kb-modal').style.display = 'none';
        }

        async function createKnowledgeBase() {
            const userId = document.getElementById('kb-user-id').value;
            const kbName = document.getElementById('new-kb-name').value.trim();
            
            if (!kbName) {
                alert('请输入知识库名称');
                return;
            }
            
            try {
                const formData = new FormData();
                formData.append('kb_name', kbName);
                
                const response = await fetch('/api/v1/users/' + userId + '/kbs', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    hideCreateKbModal();
                    loadKnowledgeBases();
                    alert('知识库创建成功！');
                } else {
                    alert('创建失败: ' + JSON.stringify(result));
                }
            } catch (error) {
                alert('创建失败: ' + error.message);
            }
        }

        async function deleteKnowledgeBase(userId, kbName) {
            if (!confirm('确定要删除知识库 "' + kbName + '" 吗？此操作不可恢复。')) {
                return;
            }
            
            try {
                const response = await fetch('/api/v1/users/' + userId + '/kbs/' + kbName, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    loadKnowledgeBases();
                    alert('知识库删除成功！');
                } else {
                    alert('删除失败: ' + JSON.stringify(result));
                }
            } catch (error) {
                alert('删除失败: ' + error.message);
            }
        }

        async function loadKbStats(userId, kbName) {
            try {
                const response = await fetch('/api/v1/users/' + userId + '/kbs/' + kbName + '/stats');
                const stats = await response.json();
                
                if (stats.error) {
                    alert('获取统计信息失败: ' + stats.error);
                } else {
                    alert('知识库 "' + kbName + '" 统计信息:\n\n文档数: ' + stats.file_count + '\n总大小: ' + stats.total_size_mb.toFixed(2) + ' MB\n文件数: ' + (stats.total_files || 0));
                }
            } catch (error) {
                alert('获取统计信息失败: ' + error.message);
            }
        }

        // Knowledge Graph Visualization Functions
        async function loadKnowledgeBasesForGraph() {
            const userId = document.getElementById('graph-user-id').value;
            const kbSelect = document.getElementById('graph-kb-name');
            
            try {
                const response = await fetch('/api/v1/users/' + userId + '/kbs');
                const data = await response.json();
                
                kbSelect.innerHTML = '<option value="default">default</option>';
                
                if (data.knowledge_bases && data.knowledge_bases.length > 0) {
                    data.knowledge_bases.forEach(kb => {
                        if (kb !== 'default') {
                            const option = document.createElement('option');
                            option.value = kb;
                            option.textContent = kb;
                            kbSelect.appendChild(option);
                        }
                    });
                }
            } catch (error) {
                console.error('Failed to load knowledge bases for graph:', error);
            }
        }

        async function loadKnowledgeGraph() {
            const userId = document.getElementById('graph-user-id').value;
            const kbName = document.getElementById('graph-kb-name').value;
            
            try {
                // Show loading state
                document.getElementById('graph-placeholder').style.display = 'none';
                document.getElementById('graph-container').style.display = 'block';
                document.getElementById('graph-stats').style.display = 'grid';
                
                // Try to get graph data from LightRAG
                const response = await fetch('/api/v1/users/' + userId + '/kbs/' + kbName + '/graph');
                
                if (response.ok) {
                    const graphData = await response.json();
                    
                    if (graphData.nodes && graphData.edges) {
                        // Update stats
                        document.getElementById('graph-nodes').textContent = graphData.nodes.length;
                        document.getElementById('graph-edges').textContent = graphData.edges.length;
                        
                        // Draw graph
                        drawGraph(graphData);
                    } else {
                        showGraphPlaceholder('没有找到知识图谱数据。请先导入文档以生成知识图谱。');
                    }
                } else {
                    // Graph endpoint not available, show info
                    showGraphPlaceholder('知识图谱可视化功能正在开发中。LightRAG在后台构建知识图谱，但可视化界面还需要进一步开发。');
                }
            } catch (error) {
                showGraphPlaceholder('加载知识图谱失败: ' + error.message + '。此功能需要后端API支持。');
            }
        }

        function showGraphPlaceholder(message) {
            document.getElementById('graph-container').style.display = 'none';
            document.getElementById('graph-stats').style.display = 'none';
            document.getElementById('graph-placeholder').style.display = 'block';
            document.getElementById('graph-placeholder').innerHTML = '<p style="color: #666;">' + message + '</p>';
        }

        function clearGraph() {
            const canvas = document.getElementById('graph-canvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            document.getElementById('graph-info').style.display = 'none';
            showGraphPlaceholder('知识图谱已清除。点击"加载知识图谱"重新加载。');
        }

        function drawGraph(graphData) {
            const canvas = document.getElementById('graph-canvas');
            const ctx = canvas.getContext('2d');
            
            // Set canvas size
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
            
            // Simple force-directed layout
            const nodes = graphData.nodes.map((node, i) => ({
                id: node.id || i,
                label: node.label || node.id || 'Node ' + i,
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: 0,
                vy: 0
            }));
            
            const edges = graphData.edges.map(edge => ({
                source: nodes.find(n => n.id === edge.source),
                target: nodes.find(n => n.id === edge.target)
            })).filter(e => e.source && e.target);
            
            // Simple layout simulation
            for (let i = 0; i < 100; i++) {
                // Repulsion between nodes
                for (let j = 0; j < nodes.length; j++) {
                    for (let k = j + 1; k < nodes.length; k++) {
                        const dx = nodes[k].x - nodes[j].x;
                        const dy = nodes[k].y - nodes[j].y;
                        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                        const force = 1000 / (dist * dist);
                        
                        nodes[j].vx -= (dx / dist) * force;
                        nodes[j].vy -= (dy / dist) * force;
                        nodes[k].vx += (dx / dist) * force;
                        nodes[k].vy += (dy / dist) * force;
                    }
                }
                
                // Attraction along edges
                edges.forEach(edge => {
                    const dx = edge.target.x - edge.source.x;
                    const dy = edge.target.y - edge.source.y;
                    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                    const force = (dist - 100) * 0.01;
                    
                    edge.source.vx += (dx / dist) * force;
                    edge.source.vy += (dy / dist) * force;
                    edge.target.vx -= (dx / dist) * force;
                    edge.target.vy -= (dy / dist) * force;
                });
                
                // Apply velocity
                nodes.forEach(node => {
                    node.x += node.vx;
                    node.y += node.vy;
                    node.vx *= 0.9;
                    node.vy *= 0.9;
                    
                    // Keep in bounds
                    node.x = Math.max(20, Math.min(canvas.width - 20, node.x));
                    node.y = Math.max(20, Math.min(canvas.height - 20, node.y));
                });
            }
            
            // Draw edges
            ctx.strokeStyle = '#ccc';
            ctx.lineWidth = 1;
            edges.forEach(edge => {
                ctx.beginPath();
                ctx.moveTo(edge.source.x, edge.source.y);
                ctx.lineTo(edge.target.x, edge.target.y);
                ctx.stroke();
            });
            
            // Draw nodes
            nodes.forEach(node => {
                ctx.beginPath();
                ctx.arc(node.x, node.y, 8, 0, Math.PI * 2);
                ctx.fillStyle = '#667eea';
                ctx.fill();
                ctx.strokeStyle = '#5568d3';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Draw labels
                ctx.fillStyle = '#333';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(node.label.substring(0, 10), node.x, node.y - 12);
            });
            
            // Add click interaction
            canvas.onclick = function(e) {
                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                nodes.forEach(node => {
                    const dx = x - node.x;
                    const dy = y - node.y;
                    if (Math.sqrt(dx * dx + dy * dy) < 12) {
                        document.getElementById('node-info').textContent = node.label;
                        document.getElementById('graph-info').style.display = 'block';
                    }
                });
            };
        }

        // Drag and drop handling
        const uploadArea = document.getElementById('upload-area');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            const fileInput = document.getElementById('file-input');
            fileInput.files = files;
        });
    </script>
</body>
</html>
    """)


