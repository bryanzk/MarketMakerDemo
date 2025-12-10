#!/bin/bash
# Server Environment Verification Script / 服务器环境验证脚本
# Verifies that server startup environment is consistent / 验证服务器启动环境的一致性
# Owner: Agent ARCH

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Server Environment Verification / 服务器环境验证 ==="
echo ""

# Check 1: Project root / 检查 1：项目根目录
echo "1. Project Root / 项目根目录:"
if [ -f "$PROJECT_ROOT/server.py" ]; then
    echo "   ✓ server.py found / 找到 server.py"
else
    echo "   ✗ server.py not found / 未找到 server.py"
    exit 1
fi

# Check 2: Virtual environment / 检查 2：虚拟环境
echo ""
echo "2. Virtual Environment / 虚拟环境:"
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "   ✓ .venv directory exists / .venv 目录存在"
    if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
        echo "   ✓ activate script exists / activate 脚本存在"
    else
        echo "   ✗ activate script not found / 未找到 activate 脚本"
        exit 1
    fi
else
    echo "   ✗ .venv directory not found / 未找到 .venv 目录"
    exit 1
fi

# Check 3: Python interpreter / 检查 3：Python 解释器
echo ""
echo "3. Python Interpreter / Python 解释器:"
source "$PROJECT_ROOT/.venv/bin/activate"
PYTHON_INTERPRETER=$(which python)
PYTHON_VERSION=$(python --version)
echo "   Location / 位置: $PYTHON_INTERPRETER"
echo "   Version / 版本: $PYTHON_VERSION"
if [[ "$PYTHON_INTERPRETER" == *".venv"* ]]; then
    echo "   ✓ Using venv Python / 使用 venv Python"
else
    echo "   ⚠ Warning: Not using venv Python / 警告：未使用 venv Python"
fi

# Check 4: Required packages / 检查 4：必需的包
echo ""
echo "4. Required Packages / 必需的包:"
# Check packages with their import names / 使用导入名检查包
check_package() {
    local package_name=$1
    local import_name=$2
    if python -c "import ${import_name}" 2>/dev/null; then
        echo "   ✓ $package_name installed / $package_name 已安装"
        return 0
    else
        echo "   ✗ $package_name not found / 未找到 $package_name"
        return 1
    fi
}

check_package "uvicorn" "uvicorn" || exit 1
check_package "fastapi" "fastapi" || exit 1
check_package "python-dotenv" "dotenv" || exit 1

# Check 5: Environment file / 检查 5：环境文件
echo ""
echo "5. Environment File / 环境文件:"
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "   ✓ .env file exists / .env 文件存在"
    # Check for critical variables (without exposing values) / 检查关键变量（不暴露值）
    if grep -q "GEMINI_API_KEY\|OPENAI_API_KEY\|ANTHROPIC_API_KEY" "$PROJECT_ROOT/.env" 2>/dev/null; then
        echo "   ✓ LLM API keys configured / LLM API 密钥已配置"
    else
        echo "   ⚠ No LLM API keys found in .env / 在 .env 中未找到 LLM API 密钥"
    fi
else
    echo "   ⚠ .env file not found (optional) / 未找到 .env 文件（可选）"
fi

# Check 6: PYTHONPATH / 检查 6：PYTHONPATH
echo ""
echo "6. PYTHONPATH:"
if [ -n "$PYTHONPATH" ]; then
    echo "   Current / 当前: $PYTHONPATH"
else
    echo "   ⚠ PYTHONPATH not set / PYTHONPATH 未设置"
fi

# Check 7: Working directory / 检查 7：工作目录
echo ""
echo "7. Working Directory / 工作目录:"
CURRENT_DIR=$(pwd)
echo "   Current / 当前: $CURRENT_DIR"
if [ "$CURRENT_DIR" == "$PROJECT_ROOT" ]; then
    echo "   ✓ In project root / 在项目根目录"
else
    echo "   ⚠ Not in project root / 不在项目根目录"
    echo "   Expected / 期望: $PROJECT_ROOT"
fi

echo ""
echo "=== Verification Complete / 验证完成 ==="
echo "All checks passed / 所有检查通过 ✓"

