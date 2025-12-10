# Environment Consistency Guide / 环境一致性指南

## Overview / 概述

This document explains how to ensure consistent server startup environment across all agents.
本文档说明如何确保所有 agent 的服务器启动环境一致。

**Owner / 负责人**: Agent ARCH

## Problem Statement / 问题陈述

Different agents may start the server from different contexts, leading to:
不同的 agent 可能从不同的上下文启动服务器，导致：

1. **Inconsistent working directory / 不一致的工作目录**
   - Agent may start from subdirectories / Agent 可能从子目录启动
   - Relative paths break / 相对路径失效

2. **Different Python interpreters / 不同的 Python 解释器**
   - System Python vs venv Python / 系统 Python vs venv Python
   - Different package versions / 不同的包版本

3. **Environment variable loading issues / 环境变量加载问题**
   - `.env` file path resolution / `.env` 文件路径解析
   - Missing or incorrect variables / 缺少或错误的变量

4. **PYTHONPATH misconfiguration / PYTHONPATH 配置错误**
   - Missing project root / 缺少项目根目录
   - Incorrect site-packages path / 错误的 site-packages 路径

## Solution: Standardized Startup Script / 解决方案：标准化启动脚本

### `start_server.sh` Features / 功能

The standardized startup script (`start_server.sh`) ensures:
标准化启动脚本（`start_server.sh`）确保：

1. **Absolute path resolution / 绝对路径解析**
   ```bash
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   cd "$SCRIPT_DIR"
   ```

2. **Virtual environment activation / 虚拟环境激活**
   ```bash
   source "$SCRIPT_DIR/.venv/bin/activate"
   ```

3. **Python interpreter verification / Python 解释器验证**
   ```bash
   PYTHON_INTERPRETER=$(which python)
   # Verifies it's from .venv / 验证它来自 .venv
   ```

4. **Explicit PYTHONPATH / 明确的 PYTHONPATH**
   ```bash
   export PYTHONPATH="${SCRIPT_DIR}:${VENV_SITE_PACKAGES}:${PYTHONPATH}"
   ```

5. **Environment file verification / 环境文件验证**
   ```bash
   if [ ! -f "$SCRIPT_DIR/.env" ]; then
       echo "Warning: .env file not found"
   fi
   ```

6. **Environment logging / 环境日志**
   - Logs all critical environment variables / 记录所有关键环境变量
   - Helps debug startup issues / 帮助调试启动问题

### Usage / 使用方法

**Always use the standardized script / 始终使用标准化脚本：**

```bash
./start_server.sh
```

**Never start manually unless absolutely necessary / 除非绝对必要，否则不要手动启动：**

```bash
# ❌ Don't do this / 不要这样做
python server.py

# ❌ Don't do this / 不要这样做
cd src && python ../server.py
```

## Environment Verification / 环境验证

### Verification Script / 验证脚本

Before starting the server, verify your environment:
在启动服务器之前，验证您的环境：

```bash
./scripts/verify_server_env.sh
```

### What It Checks / 检查内容

1. ✓ Project root / 项目根目录
2. ✓ Virtual environment / 虚拟环境
3. ✓ Python interpreter / Python 解释器
4. ✓ Required packages / 必需的包
5. ✓ Environment file / 环境文件
6. ✓ PYTHONPATH / PYTHONPATH
7. ✓ Working directory / 工作目录

### Expected Output / 预期输出

```
=== Server Environment Verification / 服务器环境验证 ===

1. Project Root / 项目根目录:
   ✓ server.py found / 找到 server.py

2. Virtual Environment / 虚拟环境:
   ✓ .venv directory exists / .venv 目录存在
   ✓ activate script exists / activate 脚本存在

3. Python Interpreter / Python 解释器:
   Location / 位置: /path/to/.venv/bin/python
   Version / 版本: Python 3.x.x
   ✓ Using venv Python / 使用 venv Python

4. Required Packages / 必需的包:
   ✓ uvicorn installed / uvicorn 已安装
   ✓ fastapi installed / fastapi 已安装
   ✓ python-dotenv installed / python-dotenv 已安装

5. Environment File / 环境文件:
   ✓ .env file exists / .env 文件存在
   ✓ LLM API keys configured / LLM API 密钥已配置

6. PYTHONPATH:
   Current / 当前: /path/to/project:/path/to/.venv/lib/.../site-packages

7. Working Directory / 工作目录:
   Current / 当前: /path/to/project
   ✓ In project root / 在项目根目录

=== Verification Complete / 验证完成 ===
All checks passed / 所有检查通过 ✓
```

## Agent-Specific Guidelines / Agent 特定指南

### For All Agents / 对所有 Agent

**Rule / 规则**: Always use `./start_server.sh` to start the server.
**规则**：始终使用 `./start_server.sh` 启动服务器。

### For Agent TRADING / 对于 Agent TRADING

When testing trading functionality:
测试交易功能时：

```bash
# ✅ Correct / 正确
cd /path/to/MarketMakerDemo
./start_server.sh

# ❌ Incorrect / 错误
cd /path/to/MarketMakerDemo/src/trading
python ../../server.py
```

### For Agent WEB / 对于 Agent WEB

When testing API endpoints:
测试 API 端点时：

```bash
# ✅ Correct / 正确
cd /path/to/MarketMakerDemo
./start_server.sh

# ❌ Incorrect / 错误
cd /path/to/MarketMakerDemo/templates
python ../server.py
```

### For Agent AI / 对于 Agent AI

When testing LLM evaluation:
测试 LLM 评估时：

```bash
# ✅ Correct / 正确
cd /path/to/MarketMakerDemo
./start_server.sh

# ❌ Incorrect / 错误
cd /path/to/MarketMakerDemo/src/ai
python ../../server.py
```

## Troubleshooting / 故障排除

### Issue: "Module not found" / 问题："找不到模块"

**Cause / 原因**: PYTHONPATH not set correctly / PYTHONPATH 未正确设置

**Solution / 解决方案**:
```bash
# Use standardized script / 使用标准化脚本
./start_server.sh
```

### Issue: "Environment variable not found" / 问题："找不到环境变量"

**Cause / 原因**: `.env` file not loaded / `.env` 文件未加载

**Solution / 解决方案**:
1. Verify `.env` file exists in project root / 验证 `.env` 文件存在于项目根目录
2. Use standardized script (it verifies .env path) / 使用标准化脚本（它验证 .env 路径）
3. Check server logs for environment loading messages / 检查服务器日志中的环境加载消息

### Issue: "Wrong Python version" / 问题："错误的 Python 版本"

**Cause / 原因**: Using system Python instead of venv Python / 使用系统 Python 而不是 venv Python

**Solution / 解决方案**:
```bash
# Verify virtual environment / 验证虚拟环境
./scripts/verify_server_env.sh

# Recreate venv if needed / 如需要，重新创建 venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Working directory error" / 问题："工作目录错误"

**Cause / 原因**: Starting from wrong directory / 从错误的目录启动

**Solution / 解决方案**:
```bash
# Always start from project root / 始终从项目根目录启动
cd /path/to/MarketMakerDemo
./start_server.sh
```

## Best Practices / 最佳实践

1. **Always use `./start_server.sh`** / **始终使用 `./start_server.sh`**
   - Never start manually / 不要手动启动
   - Ensures consistency / 确保一致性

2. **Verify environment before starting** / **启动前验证环境**
   ```bash
   ./scripts/verify_server_env.sh
   ```

3. **Check server logs for environment info** / **检查服务器日志中的环境信息**
   - Startup script logs environment variables / 启动脚本记录环境变量
   - Helps identify configuration issues / 帮助识别配置问题

4. **Document any environment-specific requirements** / **记录任何特定于环境的要求**
   - Update this guide if new requirements arise / 如有新要求，更新本指南
   - Share with all agents / 与所有 agent 分享

## Related Documents / 相关文档

- [README.md](../README.md) - Quick start guide / 快速开始指南
- [Development Protocol](../development_protocol.md) - Development workflow / 开发工作流
- [Agent Documentation](../agents/README.md) - Agent responsibilities / Agent 职责


