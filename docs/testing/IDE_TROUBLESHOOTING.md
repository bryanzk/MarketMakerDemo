# IDE Pytest 故障排除指南 / IDE Pytest Troubleshooting Guide

## 问题：终端可以运行测试，但 IDE 显示 "no tests found"

### 快速诊断步骤

1. **验证终端可以运行测试**
   ```bash
   /opt/homebrew/bin/pytest tests/unit/web/test_evaluation_cancellation.py --collect-only -v
   ```
   应该能看到 3 个测试被收集。

2. **检查 IDE 的 Python 解释器**
   - 按 `Cmd+Shift+P` → 输入：`Python: Select Interpreter`
   - 确保选择的是：`/opt/homebrew/opt/python@3.13/bin/python3.13`
   - 或者：`/opt/homebrew/bin/python3`

3. **检查 IDE 的 Pytest 设置**
   - 按 `Cmd+Shift+P` → 输入：`Preferences: Open Workspace Settings (JSON)`
   - 确保有以下配置：
   ```json
   {
     "python.testing.pytestEnabled": true,
     "python.testing.unittestEnabled": false,
     "python.testing.pytestArgs": ["tests"],
     "python.testing.pytestPath": "/opt/homebrew/bin/pytest",
     "python.defaultInterpreterPath": "/opt/homebrew/opt/python@3.13/bin/python3.13"
   }
   ```

### 常见问题和解决方案

#### 问题 1：IDE 使用了错误的 Python 解释器

**解决方案**：
1. 查看状态栏右下角的 Python 版本
2. 点击它，选择正确的解释器
3. 或者按 `Cmd+Shift+P` → `Python: Select Interpreter`

#### 问题 2：Pytest 扩展未启用

**解决方案**：
1. 按 `Cmd+Shift+X` 打开扩展面板
2. 搜索 "Python"（Microsoft 官方扩展）
3. 确保已安装并启用
4. 搜索 "Pytest" 扩展（如果有单独的）
5. 确保已安装并启用

#### 问题 3：工作区设置未生效

**解决方案**：
1. 检查是否有 `.vscode/settings.json` 文件
2. 如果没有，创建它：
   ```bash
   mkdir -p .vscode
   ```
3. 创建 `.vscode/settings.json` 并添加配置（见上面）

#### 问题 4：IDE 缓存问题

**解决方案**：
1. 清除 pytest 缓存：
   ```bash
   rm -rf .pytest_cache
   ```
2. 重新加载 IDE 窗口：
   - `Cmd+Shift+P` → `Developer: Reload Window`
3. 如果还不行，重启 IDE

#### 问题 5：测试发现被过滤

**检查 pytest.ini 配置**：
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

确保没有过滤掉 unit 测试。

### 手动触发测试发现

1. **打开 Test Explorer**
   - 点击侧边栏的烧杯图标（Test Explorer）
   - 或按 `Cmd+Shift+T`

2. **手动刷新**
   - 点击 Test Explorer 顶部的刷新按钮
   - 或右键点击测试文件夹 → "Refresh Tests"

3. **检查输出**
   - 打开 "Output" 面板（`Cmd+Shift+U`）
   - 选择 "Python Test Log" 查看详细日志

### 验证配置

运行以下命令检查配置：

```bash
# 检查 pytest 路径
which pytest
/opt/homebrew/bin/pytest

# 检查 Python 解释器
which python3
/opt/homebrew/bin/python3

# 检查 pytest 版本
pytest --version
pytest 9.0.1

# 检查测试发现
pytest tests/unit/web/test_evaluation_cancellation.py --collect-only -q
```

### 如果以上都不行

1. **检查 IDE 日志**
   - `Cmd+Shift+P` → `Developer: Toggle Developer Tools`
   - 查看 Console 标签页的错误信息

2. **尝试使用不同的测试框架**
   - 临时禁用 pytest，使用 unittest
   - 看是否能发现问题

3. **重新安装 Python 扩展**
   - 卸载 Python 扩展
   - 重启 IDE
   - 重新安装 Python 扩展

4. **检查项目结构**
   - 确保 `tests/` 目录在项目根目录
   - 确保 `pytest.ini` 在项目根目录
   - 确保测试文件遵循命名规范：`test_*.py`

### 当前项目配置

- **Python 解释器**: `/opt/homebrew/opt/python@3.13/bin/python3.13`
- **Pytest 路径**: `/opt/homebrew/bin/pytest`
- **Pytest 版本**: 9.0.1
- **测试路径**: `tests/`
- **配置文件**: `pytest.ini`

### 测试文件验证

当前测试文件 `test_evaluation_cancellation.py`：
- ✓ 语法正确
- ✓ 包含 3 个测试函数
- ✓ 终端可以正常发现
- ✓ 遵循 pytest 命名规范


