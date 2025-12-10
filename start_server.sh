#!/bin/bash
# Standardized Server Startup Script / 标准化服务器启动脚本
# Ensures consistent environment across all agents / 确保所有 agent 使用一致的环境
# Owner: Agent ARCH

set -e  # Exit on error / 遇到错误立即退出

# Get absolute path to script directory / 获取脚本目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verify we're in the project root / 验证我们在项目根目录
if [ ! -f "server.py" ]; then
    echo "Error: server.py not found. Please run this script from the project root." >&2
    echo "错误：未找到 server.py。请从项目根目录运行此脚本。" >&2
    exit 1
fi

# Check for virtual environment / 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment .venv not found." >&2
    echo "错误：未找到虚拟环境 .venv。" >&2
    echo "Please create it with: python3 -m venv .venv" >&2
    echo "请使用以下命令创建：python3 -m venv .venv" >&2
    exit 1
fi

# Activate virtual environment / 激活虚拟环境
# Use absolute path to ensure consistency / 使用绝对路径确保一致性
source "$SCRIPT_DIR/.venv/bin/activate"

# Verify Python interpreter / 验证 Python 解释器
PYTHON_INTERPRETER=$(which python)
if [[ ! "$PYTHON_INTERPRETER" == *".venv"* ]]; then
    echo "Warning: Python interpreter is not from .venv" >&2
    echo "警告：Python 解释器不是来自 .venv" >&2
    echo "Using: $PYTHON_INTERPRETER" >&2
    echo "使用：$PYTHON_INTERPRETER" >&2
fi

# Set PYTHONPATH explicitly / 明确设置 PYTHONPATH
# Include project root and venv site-packages / 包含项目根目录和 venv site-packages
VENV_SITE_PACKAGES=$(find "$SCRIPT_DIR/.venv/lib" -name "site-packages" -type d 2>/dev/null | head -1)
if [ -n "$VENV_SITE_PACKAGES" ]; then
    export PYTHONPATH="${SCRIPT_DIR}:${VENV_SITE_PACKAGES}:${PYTHONPATH}"
else
    echo "Warning: Cannot find venv site-packages, using default PYTHONPATH" >&2
    echo "警告：无法找到 venv site-packages，使用默认 PYTHONPATH" >&2
    export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
fi

# Verify .env file exists / 验证 .env 文件存在
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "Warning: .env file not found at $SCRIPT_DIR/.env" >&2
    echo "警告：未找到 .env 文件：$SCRIPT_DIR/.env" >&2
    echo "Server will use system environment variables only." >&2
    echo "服务器将仅使用系统环境变量。" >&2
fi

# Set explicit environment variables for consistency / 设置明确的环境变量以确保一致性
export PROJECT_ROOT="$SCRIPT_DIR"
export ENV_FILE="$SCRIPT_DIR/.env"

# Log environment info for debugging / 记录环境信息用于调试
echo "=== Server Startup Environment / 服务器启动环境 ===" >&2
echo "Project Root / 项目根目录: $PROJECT_ROOT" >&2
echo "Python Interpreter / Python 解释器: $PYTHON_INTERPRETER" >&2
echo "Python Version / Python 版本: $(python --version)" >&2
echo "PYTHONPATH: $PYTHONPATH" >&2
echo "Working Directory / 工作目录: $(pwd)" >&2
echo "================================================" >&2

# Create logs directory if it doesn't exist / 如果日志目录不存在则创建
LOGS_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOGS_DIR"

# Log file path / 日志文件路径
LOG_FILE="$LOGS_DIR/server.log"

# Start server / 启动服务器
# Use absolute path to server.py / 使用 server.py 的绝对路径
# Redirect both stdout and stderr to log file / 将 stdout 和 stderr 重定向到日志文件
# Append to log file to preserve previous logs / 追加到日志文件以保留之前的日志
exec python "$SCRIPT_DIR/server.py" >> "$LOG_FILE" 2>&1
