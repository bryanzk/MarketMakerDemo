#!/bin/bash
# Start server script / 启动服务器脚本
# Handles both venv Python and system Python with PYTHONPATH
# 处理虚拟环境 Python 和带 PYTHONPATH 的系统 Python

cd "$(dirname "$0")"

# Find site-packages directory in venv
# 在虚拟环境中查找 site-packages 目录
VENV_SITE_PACKAGES=$(find .venv/lib -name "site-packages" -type d 2>/dev/null | head -1)

if [ -n "$VENV_SITE_PACKAGES" ]; then
    # Use system Python with PYTHONPATH pointing to venv site-packages
    # 使用系统 Python，PYTHONPATH 指向虚拟环境的 site-packages
    export PYTHONPATH="${VENV_SITE_PACKAGES}:${PWD}:${PYTHONPATH}"
    python3 server.py
else
    echo "Error: Cannot find virtual environment site-packages / 错误：无法找到虚拟环境 site-packages"
    echo "Please ensure virtual environment is properly set up / 请确保虚拟环境已正确设置"
    exit 1
fi

