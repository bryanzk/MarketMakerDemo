# Logging Management / 日志管理

## Overview / 概述

This document explains how server logs are handled after startup.
本文档说明服务器启动后日志的处理方式。

**Owner / 负责人**: Agent ARCH

## Current Logging Status / 当前日志状态

### Log Output Locations / 日志输出位置

Currently, logs are output to **stdout/stderr** and may be captured in log files if manually redirected.
当前，日志输出到 **stdout/stderr**，如果手动重定向，可能会被捕获到日志文件中。

**Existing log files / 现有日志文件**:
- `server.log` - May contain previous server output / 可能包含之前的服务器输出
- `server_output.log` - May contain previous server output / 可能包含之前的服务器输出

### Logging Configuration / 日志配置

1. **Python Logging / Python 日志**:
   - `server.py` uses standard Python `logging` module
   - `server.py` 使用标准 Python `logging` 模块
   - No file handler configured / 未配置文件处理器
   - Logs output to stdout/stderr / 日志输出到 stdout/stderr

2. **Uvicorn Logging / Uvicorn 日志**:
   - Uses default uvicorn logging configuration
   - 使用默认的 uvicorn 日志配置
   - Outputs to stdout/stderr / 输出到 stdout/stderr
   - No custom log configuration / 无自定义日志配置

3. **Structured Logging / 结构化日志**:
   - `src/shared/logger.py` provides `JsonFormatter` for JSON-formatted logs
   - `src/shared/logger.py` 提供 `JsonFormatter` 用于 JSON 格式日志
   - Currently only used by modules that explicitly use `setup_logger()`
   - 当前仅由显式使用 `setup_logger()` 的模块使用
   - `server.py` does not use structured logging / `server.py` 未使用结构化日志

## Log Flow / 日志流程

```
┌─────────────────┐
│  start_server.sh │
│  (启动脚本)      │
└────────┬────────┘
         │
         │ exec python server.py
         ▼
┌─────────────────┐
│   server.py      │
│  (服务器代码)     │
└────────┬────────┘
         │
         ├─► Python logging ──► stdout/stderr
         │   (Python 日志)
         │
         └─► Uvicorn logging ──► stdout/stderr
             (Uvicorn 日志)
```

**Current behavior / 当前行为**:
- All logs go to stdout/stderr / 所有日志都输出到 stdout/stderr
- No automatic file logging / 没有自动文件日志
- Log files exist but may be from manual redirection / 日志文件存在但可能来自手动重定向

## Issues / 问题

### 1. No Centralized Log Management / 没有集中式日志管理

**Problem / 问题**:
- Logs are scattered across stdout/stderr and potentially log files
- 日志分散在 stdout/stderr 和潜在的日志文件中
- No single source of truth for logs / 没有单一的日志来源

**Impact / 影响**:
- Difficult to debug issues / 难以调试问题
- Hard to track server activity / 难以跟踪服务器活动
- No log retention policy / 没有日志保留策略

### 2. No Log Rotation / 没有日志轮转

**Problem / 问题**:
- Log files can grow indefinitely / 日志文件可能无限增长
- No automatic cleanup / 没有自动清理
- Risk of disk space issues / 磁盘空间问题风险

**Impact / 影响**:
- Disk space consumption / 磁盘空间消耗
- Performance degradation / 性能下降
- Difficult to find recent logs / 难以找到最近的日志

### 3. Inconsistent Log Format / 不一致的日志格式

**Problem / 问题**:
- Some modules use JSON formatting / 某些模块使用 JSON 格式
- Some modules use plain text / 某些模块使用纯文本
- Uvicorn uses its own format / Uvicorn 使用自己的格式

**Impact / 影响**:
- Difficult to parse logs / 难以解析日志
- Hard to integrate with log aggregation tools / 难以与日志聚合工具集成
- Inconsistent debugging experience / 不一致的调试体验

### 4. No Log Level Configuration / 没有日志级别配置

**Problem / 问题**:
- Log level is hardcoded or uses defaults / 日志级别是硬编码的或使用默认值
- Cannot adjust verbosity without code changes / 无法在不更改代码的情况下调整详细程度
- No environment-based log level / 没有基于环境的日志级别

**Impact / 影响**:
- Too verbose in production / 生产环境过于详细
- Too quiet during development / 开发期间过于安静
- Difficult to filter important messages / 难以过滤重要消息

## Recommended Solution / 推荐解决方案

### 1. Centralized Logging Configuration / 集中式日志配置

Create a unified logging configuration that:
创建统一的日志配置，包括：

- **File handler** for persistent logs / 用于持久日志的文件处理器
- **Console handler** for development / 用于开发的控制台处理器
- **Log rotation** to prevent disk space issues / 日志轮转以防止磁盘空间问题
- **Structured format** (JSON) for all logs / 所有日志的结构化格式（JSON）
- **Configurable log level** via environment variable / 通过环境变量可配置的日志级别

### 2. Update Start Script / 更新启动脚本

Modify `start_server.sh` to:
修改 `start_server.sh` 以：

- Optionally redirect logs to file / 可选地将日志重定向到文件
- Support log rotation / 支持日志轮转
- Provide log viewing commands / 提供日志查看命令

### 3. Environment-Based Configuration / 基于环境的配置

Support different log configurations for:
支持不同环境的日志配置：

- **Development / 开发**: Verbose, console output / 详细，控制台输出
- **Production / 生产**: Info level, file output only / 信息级别，仅文件输出
- **Testing / 测试**: Debug level, minimal output / 调试级别，最小输出

## Implementation Plan / 实施计划

### Phase 1: Logging Configuration Module / 阶段 1：日志配置模块

1. Create `src/shared/logging_config.py`:
   - Centralized logging configuration / 集中式日志配置
   - File handler with rotation / 带轮转的文件处理器
   - Console handler / 控制台处理器
   - JSON formatter / JSON 格式化器

2. Update `server.py`:
   - Import and use centralized logging config / 导入并使用集中式日志配置
   - Configure uvicorn logging / 配置 uvicorn 日志

### Phase 2: Start Script Enhancement / 阶段 2：启动脚本增强

1. Update `start_server.sh`:
   - Add log file option / 添加日志文件选项
   - Support log rotation / 支持日志轮转
   - Add log viewing helpers / 添加日志查看助手

### Phase 3: Environment Configuration / 阶段 3：环境配置

1. Add environment variables:
   - `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
   - `LOG_FILE` - Log file path (optional)
   - `LOG_ROTATION_SIZE` - Max log file size before rotation
   - `LOG_RETENTION_DAYS` - Days to keep old log files

## Usage Examples / 使用示例

### Current Usage / 当前使用

```bash
# Start server (logs to stdout/stderr) / 启动服务器（日志输出到 stdout/stderr）
./start_server.sh

# Manually redirect logs / 手动重定向日志
./start_server.sh > server.log 2>&1
```

### Recommended Usage (After Implementation) / 推荐使用（实施后）

```bash
# Development: Console output / 开发：控制台输出
LOG_LEVEL=DEBUG ./start_server.sh

# Production: File output with rotation / 生产：带轮转的文件输出
LOG_LEVEL=INFO LOG_FILE=logs/server.log ./start_server.sh

# View recent logs / 查看最近的日志
tail -f logs/server.log

# Search logs / 搜索日志
grep "ERROR" logs/server.log
```

## Related Documents / 相关文档

- [Environment Consistency Guide](environment_consistency.md) - Server startup environment / 服务器启动环境
- [Development Protocol](../development_protocol.md) - Development workflow / 开发工作流
- [Agent Documentation](../agents/README.md) - Agent responsibilities / Agent 职责


