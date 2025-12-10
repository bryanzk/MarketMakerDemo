# IDE Pytest 配置指南 / IDE Pytest Configuration Guide

## 问题 / Problem

如果终端可以运行 pytest，但 IDE 的 Test Explorer 显示 "no tests found"，通常是 IDE 配置问题。

If terminal can run pytest but IDE Test Explorer shows "no tests found", it's usually an IDE configuration issue.

## 解决方案 / Solution

### VS Code / Cursor 配置

1. **打开设置** / **Open Settings**
   - 按 `Cmd+,` (Mac) 或 `Ctrl+,` (Windows/Linux)
   - 或 `Cmd+Shift+P` → "Preferences: Open Settings"

2. **配置 Python 解释器** / **Configure Python Interpreter**
   - 按 `Cmd+Shift+P` (Mac) 或 `Ctrl+Shift+P` (Windows/Linux)
   - 输入并选择：`Python: Select Interpreter`
   - 选择：`/opt/homebrew/opt/python@3.13/bin/python3.13`

3. **配置 Pytest** / **Configure Pytest**
   
   **方法 A：通过设置界面** / **Method A: Via Settings UI**
   
   - 按 `Cmd+,` (Mac) 或 `Ctrl+,` (Windows/Linux) 打开设置
   - 在顶部搜索框输入：`python.testing.pytestEnabled`
   - 找到 "Python › Testing: Pytest Enabled" 选项
   - 勾选复选框（确保为 `true`）
   - 搜索：`python.testing.pytestArgs`
   - 找到 "Python › Testing: Pytest Args"
   - 点击 "Edit in settings.json" 或直接输入：`["tests"]`
   - 搜索：`python.testing.pytestPath`
   - 找到 "Python › Testing: Pytest Path"
   - 输入：`/opt/homebrew/bin/pytest`
   
   **方法 B：直接编辑 settings.json** / **Method B: Edit settings.json directly**
   
   - 按 `Cmd+Shift+P` → 输入：`Preferences: Open User Settings (JSON)`
   - 或按 `Cmd+Shift+P` → 输入：`Preferences: Open Workspace Settings (JSON)`
   - 添加以下配置：
   ```json
   {
     "python.testing.pytestEnabled": true,
     "python.testing.unittestEnabled": false,
     "python.testing.pytestArgs": ["tests"],
     "python.testing.pytestPath": "/opt/homebrew/bin/pytest"
   }
   ```

4. **重新加载窗口** / **Reload Window**
   - 按 `Cmd+Shift+P` → "Developer: Reload Window"

### 手动创建 `.vscode/settings.json`

如果上述方法不起作用，可以手动创建配置文件：

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
  ]
}
```

**注意**：`.vscode/` 目录在 `.cursorignore` 中，可能需要临时移除该规则来创建配置文件。

### 验证配置

1. 打开 Test Explorer（侧边栏的烧杯图标）
2. 点击刷新按钮
3. 应该能看到 `tests/unit/trading/` 下的所有测试

### 如果仍然无法发现测试

1. **检查 pytest 扩展** / **Check Pytest Extension**
   - 确保安装了 "Python" 扩展（Microsoft）
   - 确保安装了 "Pytest" 扩展（如果单独存在）

2. **检查工作区设置** / **Check Workspace Settings**
   - 确保使用的是工作区设置，而不是用户设置
   - 工作区设置优先级更高

3. **清除缓存** / **Clear Cache**
   ```bash
   rm -rf .pytest_cache
   ```

4. **手动运行测试** / **Manual Test Run**
   - 在终端运行：`pytest tests/unit/trading/test_both_side_orders.py -v`

## 当前配置信息 / Current Configuration Info

- **Python 解释器** / **Python Interpreter**: `/opt/homebrew/opt/python@3.13/bin/python3.13`
- **Pytest 路径** / **Pytest Path**: `/opt/homebrew/bin/pytest`
- **Pytest 版本** / **Pytest Version**: 9.0.1
- **测试路径** / **Test Path**: `tests/`
- **配置文件** / **Config File**: `pytest.ini`

## 测试发现验证 / Test Discovery Verification

运行以下命令验证测试发现：

```bash
pytest tests/unit/trading/test_both_side_orders.py --collect-only -v
```

应该能看到 9 个测试被收集。



