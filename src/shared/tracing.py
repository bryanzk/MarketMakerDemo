"""
Request Tracing Utilities / 请求追踪工具

Provides trace_id generation and correlation across requests, logs, and responses.
提供跨请求、日志和响应的 trace_id 生成和关联。

Owner: Agent ARCH
"""

import hashlib
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

# Context variable for trace_id / 用于 trace_id 的上下文变量
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def generate_trace_id() -> str:
    """
    Generate a unique trace ID / 生成唯一的追踪ID

    Returns:
        Trace ID string (e.g., "req_abc123def456")
    """
    return f"req_{uuid.uuid4().hex[:12]}"


def get_trace_id() -> Optional[str]:
    """Get current trace ID from context / 从上下文获取当前追踪ID"""
    return trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    """Set trace ID in context / 在上下文中设置追踪ID"""
    trace_id_var.set(trace_id)


def create_request_context(
    endpoint: str,
    method: str = "GET",
    payload_hash: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create minimal request context for logging / 创建用于日志记录的最小请求上下文

    Args:
        endpoint: API endpoint path
        method: HTTP method
        payload_hash: Hash of request payload (for repro without secrets)

    Returns:
        Context dictionary
    """
    return {
        "endpoint": endpoint,
        "method": method,
        "payload_hash": payload_hash,
        "trace_id": get_trace_id(),
    }


def hash_payload(payload: Any) -> str:
    """
    Create a hash of request payload for logging (without secrets) / 为日志记录创建请求负载的哈希（不含密钥）

    Args:
        payload: Request payload (dict, list, etc.)

    Returns:
        Hash string
    """
    try:
        import json

        # Convert payload to JSON string / 将负载转换为 JSON 字符串
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        # Create hash / 创建哈希
        return hashlib.sha256(payload_str.encode()).hexdigest()[:16]
    except Exception:
        return "unknown"
