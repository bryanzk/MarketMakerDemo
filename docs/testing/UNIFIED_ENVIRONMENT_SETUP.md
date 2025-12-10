# 统一环境配置指南 / Unified Environment Setup Guide

## 问题 / Problem

不同的工具（终端、IDE、pytest）可能使用不同的 Python 环境，导致：
- 依赖包版本不一致
- 测试发现失败
- 导入错误

Different tools (terminal, IDE, pytest) may use different Python environments, causing:
- Inconsistent package versions
- Test discovery failures
- Import errors

## 解决方案：使用虚拟环境 / Solution: Use Virtual Environment

### 步骤 1：创建/激活虚拟环境

```bash
# 如果 .venv 不存在，创建它
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 验证
which python
# 应该显示: /path/to/MarketMakerDemo/.venv/bin/python
```

### 步骤 2：安装所有依赖

```bash
# 确保在虚拟环境中
source .venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装所有依赖
pip install -r requirements.txt
```

### 步骤 3：配置 IDE 使用虚拟环境

#### VS Code / Cursor 配置

1. **选择虚拟环境的 Python 解释器**
   - 按 `Cmd+Shift+P`
   - 输入：`Python: Select Interpreter`
   - 选择：`.venv/bin/python` 或 `./.venv/bin/python`

2. **更新 `.vscode/settings.json`**

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": ["tests"],
  "python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest",
  "python.testing.cwd": "${workspaceFolder}",
  "python.analysis.extraPaths": ["${workspaceFolder}"]
}
```

**关键点**：
- 使用 `${workspaceFolder}/.venv/bin/python` 而不是绝对路径
- 使用 `${workspaceFolder}/.venv/bin/pytest` 确保使用虚拟环境中的 pytest
- 这样配置在不同机器上都能工作

### 步骤 4：验证配置

#### 验证 1：检查 Python 解释器

```bash
# 在终端中
source .venv/bin/activate
which python
python --version
# 应该显示 .venv 中的 Python
```

#### 验证 2：检查 pytest

```bash
# 在虚拟环境中
which pytest
pytest --version
# 应该显示 .venv/bin/pytest
```

#### 验证 3：检查依赖

```bash
# 在虚拟环境中
python -c "import pytest, uvicorn, fastapi; print('✓ All dependencies available')"
```

#### 验证 4：IDE 测试发现

1. 在 IDE 中按 `Cmd+Shift+P` → `Python: Select Interpreter`
2. 选择 `.venv/bin/python`
3. 重新加载窗口：`Cmd+Shift+P` → `Developer: Reload Window`
4. 打开 Test Explorer，应该能看到所有测试

## 统一环境的最佳实践 / Best Practices

### 1. 始终使用虚拟环境

```bash
# 启动服务器
source .venv/bin/activate
./start_server.sh

# 运行测试
source .venv/bin/activate
pytest tests/ -v

# 安装新包
source .venv/bin/activate
pip install new-package
pip freeze > requirements.txt  # 更新依赖列表
```

### 2. IDE 配置使用相对路径

使用 `${workspaceFolder}` 而不是绝对路径，这样：
- 在不同机器上都能工作
- 团队成员可以共享配置
- 更容易维护

### 3. 创建环境验证脚本

创建 `scripts/verify_environment.sh`：

```bash
#!/bin/bash
echo "=== 环境验证 ==="
echo ""

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo "✓ .venv 存在"
    source .venv/bin/activate
    echo "Python: $(which python)"
    echo "版本: $(python --version)"
else
    echo "✗ .venv 不存在"
    exit 1
fi

# 检查关键依赖
echo ""
echo "检查依赖:"
python -c "import pytest; print('  ✓ pytest')" || echo "  ✗ pytest"
python -c "import uvicorn; print('  ✓ uvicorn')" || echo "  ✗ uvicorn"
python -c "import fastapi; print('  ✓ fastapi')" || echo "  ✗ fastapi"

# 检查 pytest
echo ""
echo "Pytest:"
which pytest || echo "  ✗ pytest 未找到"
pytest --version || echo "  ✗ pytest 版本检查失败"
```

### 4. 在 README 中明确说明

在项目 README 中明确说明：
- 必须使用虚拟环境
- 如何创建和激活虚拟环境
- IDE 如何配置

### 5. 使用 .python-version 文件（可选）

如果使用 pyenv，创建 `.python-version` 文件：

```
3.11.6
```

## 当前项目配置

### 推荐的统一配置

1. **虚拟环境路径**: `.venv/`
2. **Python 解释器**: `${workspaceFolder}/.venv/bin/python`
3. **Pytest 路径**: `${workspaceFolder}/.venv/bin/pytest`
4. **依赖文件**: `requirements.txt`

### 迁移步骤

如果您当前使用的是系统 Python，迁移到虚拟环境：

```bash
# 1. 创建虚拟环境
python3 -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 4. 验证
python -c "import pytest, uvicorn; print('✓ Setup complete')"

# 5. 更新 IDE 配置（见上面）
```

## 故障排除 / Troubleshooting

### 问题：IDE 仍然找不到测试

1. **检查 Python 解释器**
   - 状态栏右下角应该显示 `.venv` 或虚拟环境路径
   - 如果不是，选择正确的解释器

2. **检查 pytest 路径**
   ```bash
   # 在虚拟环境中
   which pytest
   # 应该显示: /path/to/.venv/bin/pytest
   ```

3. **清除缓存并重新加载**
   ```bash
   rm -rf .pytest_cache
   # 然后在 IDE 中重新加载窗口
   ```

### 问题：终端和 IDE 使用不同的环境

**解决方案**：
- 确保 IDE 配置使用 `${workspaceFolder}/.venv/bin/python`
- 确保终端激活了虚拟环境：`source .venv/bin/activate`
- 使用 `which python` 验证两者使用相同的 Python

### 问题：依赖缺失

**解决方案**：
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 验证清单 / Verification Checklist

- [ ] `.venv` 目录存在
- [ ] 虚拟环境已激活（终端中 `which python` 显示 `.venv/bin/python`）
- [ ] 所有依赖已安装（`pip list` 显示 requirements.txt 中的包）
- [ ] IDE 配置使用 `${workspaceFolder}/.venv/bin/python`
- [ ] IDE 配置使用 `${workspaceFolder}/.venv/bin/pytest`
- [ ] 终端可以运行测试：`pytest tests/ -v`
- [ ] IDE Test Explorer 可以发现测试
- [ ] 服务器可以启动：`./start_server.sh`

## 相关文档 / Related Documentation

- `docs/project/environment_consistency.md` - 环境一致性指南
- `docs/testing/IDE_PYTEST_SETUP.md` - IDE Pytest 配置
- `docs/testing/IDE_TROUBLESHOOTING.md` - 故障排除指南

