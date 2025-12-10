#!/bin/bash
# 统一环境设置脚本 / Unified Environment Setup Script
# 确保所有工具使用相同的 Python 环境 / Ensure all tools use the same Python environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== 统一环境设置 / Unified Environment Setup ==="
echo ""

# 步骤 1: 检查/创建虚拟环境
echo "1. 检查虚拟环境 / Checking virtual environment..."
if [ ! -d ".venv" ]; then
    echo "   创建虚拟环境 / Creating virtual environment..."
    python3 -m venv .venv
    echo "   ✓ 虚拟环境已创建 / Virtual environment created"
else
    echo "   ✓ 虚拟环境已存在 / Virtual environment exists"
fi

# 步骤 2: 激活虚拟环境
echo ""
echo "2. 激活虚拟环境 / Activating virtual environment..."
source .venv/bin/activate

# 步骤 3: 升级 pip
echo ""
echo "3. 升级 pip / Upgrading pip..."
pip install --upgrade pip --quiet

# 步骤 4: 安装依赖
echo ""
echo "4. 安装依赖 / Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "   ✓ 依赖已安装 / Dependencies installed"
else
    echo "   ⚠ requirements.txt 不存在 / requirements.txt not found"
fi

# 步骤 5: 验证环境
echo ""
echo "5. 验证环境 / Verifying environment..."
PYTHON_PATH=$(which python)
PYTHON_VERSION=$(python --version)
PYTEST_PATH=$(which pytest)

echo "   Python 路径 / Python path: $PYTHON_PATH"
echo "   Python 版本 / Python version: $PYTHON_VERSION"
echo "   Pytest 路径 / Pytest path: $PYTEST_PATH"

# 验证关键依赖
echo ""
echo "6. 检查关键依赖 / Checking critical dependencies..."
python -c "import pytest; print('   ✓ pytest')" || echo "   ✗ pytest 缺失"
python -c "import uvicorn; print('   ✓ uvicorn')" || echo "   ✗ uvicorn 缺失"
python -c "import fastapi; print('   ✓ fastapi')" || echo "   ✗ fastapi 缺失"

# 步骤 7: 更新 IDE 配置
echo ""
echo "7. 更新 IDE 配置 / Updating IDE configuration..."
mkdir -p .vscode

cat > .vscode/settings.json << 'VSCODE_EOF'
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest",
    "python.testing.cwd": "${workspaceFolder}",
    "python.analysis.extraPaths": [
        "${workspaceFolder}"
    ]
}
VSCODE_EOF

echo "   ✓ IDE 配置已更新 / IDE configuration updated"

# 步骤 8: 验证测试发现
echo ""
echo "8. 验证测试发现 / Verifying test discovery..."
if pytest tests/unit/web/test_evaluation_cancellation.py --collect-only -q > /dev/null 2>&1; then
    TEST_COUNT=$(pytest tests/unit/web/test_evaluation_cancellation.py --collect-only -q 2>&1 | grep "collected" | grep -oE "[0-9]+" | head -1)
    echo "   ✓ 测试发现正常 / Test discovery working ($TEST_COUNT tests found)"
else
    echo "   ⚠ 测试发现可能有问题 / Test discovery may have issues"
fi

echo ""
echo "=== 设置完成 / Setup Complete ==="
echo ""
echo "下一步 / Next steps:"
echo "1. 在 IDE 中选择 Python 解释器: .venv/bin/python"
echo "   Select Python interpreter in IDE: .venv/bin/python"
echo "2. 重新加载 IDE 窗口 (Cmd+Shift+P → Developer: Reload Window)"
echo "   Reload IDE window (Cmd+Shift+P → Developer: Reload Window)"
echo "3. 验证测试发现 / Verify test discovery"
echo ""
echo "提示 / Tip: 始终在虚拟环境中工作"
echo "Always work within the virtual environment:"
echo "  source .venv/bin/activate"

