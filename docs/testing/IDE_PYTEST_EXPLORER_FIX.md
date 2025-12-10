# IDE Pytest Explorer 无内容修复指南

## 问题诊断

**症状**: IDE 的 Test Explorer 显示无内容，但终端可以正常发现测试（已验证：1012 个测试）

**已验证**:
- ✅ 终端测试发现正常：`1012/1016 tests collected`
- ✅ `.venv/bin/pytest` 存在且可用
- ✅ `.venv/bin/python` 存在且可用
- ✅ `pytest.ini` 配置正确
- ✅ `.vscode/settings.json` 配置存在

## 快速修复步骤

### 步骤 1: 检查 IDE 的 Python 解释器

1. 查看 IDE 状态栏右下角的 Python 版本
2. 点击它，或按 `Cmd+Shift+P` → `Python: Select Interpreter`
3. **确保选择**: `/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo/.venv/bin/python`

### 步骤 2: 手动触发测试发现

1. 打开 Test Explorer（侧边栏烧杯图标，或按 `Cmd+Shift+T`）
2. 点击顶部的**刷新按钮**（圆形箭头图标）
3. 或右键点击项目根目录 → 选择 "Discover Tests" 或 "Refresh Tests"

### 步骤 3: 检查 IDE 输出日志

1. 打开 Output 面板：`Cmd+Shift+U`
2. 在下拉菜单中选择 **"Python Test Log"**
3. 查看是否有错误信息

### 步骤 4: 清除缓存并重新加载

```bash
# 清除 pytest 缓存
rm -rf .pytest_cache

# 在 IDE 中重新加载窗口
# Cmd+Shift+P → "Developer: Reload Window"
```

### 步骤 5: 验证配置

运行以下命令验证配置是否正确：

```bash
# 验证 pytest 路径
ls -la .venv/bin/pytest

# 验证测试发现
.venv/bin/pytest --collect-only -q | tail -1
# 应该显示: ============== 1012/1016 tests collected (4 deselected) in X.XXs ==============
```

## 如果仍然无内容

### 方法 A: 检查 Python 扩展

1. 按 `Cmd+Shift+X` 打开扩展面板
2. 搜索 "Python"（Microsoft 官方扩展）
3. 确保已安装并启用
4. 点击扩展设置，检查：
   - "Pytest: Enabled" 应为 `true`
   - "Pytest: Path" 应为 `${workspaceFolder}/.venv/bin/pytest`

### 方法 B: 使用绝对路径（临时）

如果 `${workspaceFolder}` 变量未正确解析，可以临时使用绝对路径：

编辑 `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo/.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.pytestPath": "/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo/.venv/bin/pytest",
    "python.testing.cwd": "/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo",
    "python.analysis.extraPaths": [
        "/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo"
    ]
}
```

然后重新加载窗口。

### 方法 C: 检查工作区设置优先级

1. 按 `Cmd+Shift+P` → `Preferences: Open Workspace Settings (JSON)`
2. 确保工作区设置包含 pytest 配置
3. 检查用户设置（`Preferences: Open User Settings (JSON)`）是否覆盖了工作区设置

### 方法 D: 检查 .cursorignore 影响

`.vscode/` 目录在 `.cursorignore` 中，但这不应该影响 IDE 读取配置。如果怀疑有问题：

1. 临时注释 `.cursorignore` 中的 `.vscode/` 行
2. 重新加载窗口
3. 如果有效，可以保持注释状态

### 方法 E: 查看开发者工具日志

1. 按 `Cmd+Shift+P` → `Developer: Toggle Developer Tools`
2. 打开 Console 标签页
3. 在 Test Explorer 中点击刷新
4. 查看是否有错误信息

## 当前配置参考

**工作目录**: `/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo`

**Python 解释器**: `${workspaceFolder}/.venv/bin/python`
- 实际路径: `/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo/.venv/bin/python`

**Pytest 路径**: `${workspaceFolder}/.venv/bin/pytest`
- 实际路径: `/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo/.venv/bin/pytest`

**测试路径**: `tests/`

**Pytest 配置**: `pytest.ini`

**测试数量**: 1012 个测试（4 个被取消选择）

## 验证命令

```bash
# 1. 检查 Python 解释器
.venv/bin/python --version
# 应该显示: Python 3.13.1

# 2. 检查 pytest
.venv/bin/pytest --version
# 应该显示: pytest 9.0.1

# 3. 测试发现
.venv/bin/pytest --collect-only -q | tail -1
# 应该显示测试收集结果

# 4. 运行一个简单测试验证
.venv/bin/pytest tests/contract/test_error_envelope.py::TestErrorEnvelopeStructure::test_error_envelope_has_required_fields -v
```

## 常见错误信息及解决方案

### "No tests found"

**可能原因**:
- IDE 使用了错误的 Python 解释器
- pytest 路径配置错误
- 工作目录不正确

**解决方案**: 按照步骤 1-3 检查配置

### "ModuleNotFoundError"

**可能原因**:
- IDE 使用了系统 Python 而不是虚拟环境
- `PYTHONPATH` 未正确设置

**解决方案**: 确保选择 `.venv/bin/python` 作为解释器

### "pytest not found"

**可能原因**:
- pytest 未安装在虚拟环境中
- pytest 路径配置错误

**解决方案**: 
```bash
# 安装 pytest（如果缺失）
.venv/bin/pip install pytest
```

## 联系支持

如果以上方法都无法解决问题，请提供以下信息：

1. IDE 版本和 Python 扩展版本
2. Test Explorer 的完整错误信息（从 Output → Python Test Log）
3. 开发者工具 Console 中的错误信息
4. `pytest.ini` 内容
5. `.vscode/settings.json` 内容
