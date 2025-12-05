"""
Logger Module / 日志模块

Provides JSON-formatted logging for structured log output with trace_id support.
提供支持 trace_id 的 JSON 格式结构化日志输出。

Owner: Agent ARCH
"""

import json
import logging
import sys
from datetime import datetime
from typing import Optional

# Import tracing utilities / 导入追踪工具
try:
    from src.shared.tracing import get_trace_id
except ImportError:
    # Fallback if tracing module not available / 如果追踪模块不可用则回退
    def get_trace_id() -> Optional[str]:
        return None


class JsonFormatter(logging.Formatter):
    """
    JSON log formatter for structured logging with trace_id support.
    支持 trace_id 的结构化日志 JSON 格式化器。
    """

    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add trace_id from context / 从上下文添加 trace_id
        trace_id = get_trace_id()
        if trace_id:
            log_record["trace_id"] = trace_id

        # Add extra fields if available / 如果可用则添加额外字段
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        # Add any extra fields from record / 从记录添加任何额外字段
        # (e.g., from logger.info("message", extra={"key": "value"}))
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "extra_data",
            ]:
                log_record[key] = value

        return json.dumps(log_record)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with JSON formatting.

    Args:
        name: Logger name
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    return logger
