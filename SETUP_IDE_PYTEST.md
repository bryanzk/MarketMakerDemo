# 快速修复 IDE Pytest "No Tests Found" 问题

## 问题确认
- ✅ 终端可以运行测试（已验证：3 个测试可以收集）
- ❌ IDE 显示 "no tests found"

## 立即解决方案

### 步骤 1：临时修改 .cursorignore

1. 打开 `.cursorignore` 文件
2. 找到这一行：`.vscode/`
3. 临时注释掉或删除它：
   ```
   # .vscode/  # 临时注释以创建配置文件
   ```

### 步骤 2：创建 .vscode/settings.json

在项目根目录创建 `.vscode/settings.json` 文件，内容如下：

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "python.testing.cwd": "${workspaceFolder}",
  "python.defaultInterpreterPath": "/opt/homebrew/opt/python@3.13/bin/python3.13",
  "python.testing.pytestPath": "/opt/homebrew/bin/pytest",
  "python.analysis.extraPaths": [
    "${workspaceFolder}"
  ],
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  }
}
```

### 步骤 3：重新加载 IDE

1. 按 `Cmd+Shift+P`
2. 输入：`Developer: Reload Window`
3. 按 Enter

### 步骤 4：验证

1. 打开 Test Explorer（侧边栏烧杯图标）
2. 应该能看到 `tests/unit/web/test_evaluation_cancellation.py`
3. 展开后应该看到 3 个测试

### 步骤 5：恢复 .cursorignore（可选）

如果不想让 `.vscode/` 被索引，可以恢复 `.cursorignore`：
```
.vscode/
```

但保留 `.vscode/settings.json` 文件。

## 如果仍然不行

### 方法 A：通过命令面板直接设置

1. `Cmd+Shift+P` → `Preferences: Open User Settings (JSON)`
2. 添加配置（见上面）
3. 保存并重新加载

### 方法 B：检查 Python 扩展

1. `Cmd+Shift+X` 打开扩展
2. 搜索 "Python"（Microsoft）
3. 确保已安装并启用
4. 点击扩展设置，检查 pytest 相关选项

### 方法 C：手动触发测试发现

1. 打开 Test Explorer
2. 右键点击项目根目录
3. 选择 "Discover Tests" 或 "Refresh Tests"

## 验证命令

在终端运行以下命令确认配置：

```bash
# 检查 pytest
/opt/homebrew/bin/pytest tests/unit/web/test_evaluation_cancellation.py --collect-only -q

# 应该输出：
# ========================== 3 tests collected ==========================
```

## 当前配置信息

- **Pytest 路径**: `/opt/homebrew/bin/pytest`
- **Python 解释器**: `/opt/homebrew/opt/python@3.13/bin/python3.13`
- **测试路径**: `tests/`
- **测试文件**: `tests/unit/web/test_evaluation_cancellation.py` (3 个测试)


