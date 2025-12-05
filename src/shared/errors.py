"""
Standard Error Response Module / 标准错误响应模块

Defines standard error response format for consistent error handling across the application.
定义标准错误响应格式，用于应用程序中一致的错误处理。

Owner: Agent ARCH
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ErrorSeverity(Enum):
    """Error severity levels / 错误严重程度级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorType(Enum):
    """Error type categories / 错误类型分类"""

    # Authentication & Authorization / 认证与授权
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"

    # Connection & Network / 连接与网络
    CONNECTION = "connection"
    NETWORK = "network"
    TIMEOUT = "timeout"

    # Trading Operations / 交易操作
    TRADING = "trading"
    ORDER = "order"
    POSITION = "position"
    BALANCE = "balance"

    # Exchange Specific / 交易所特定
    EXCHANGE = "exchange"
    RATE_LIMIT = "rate_limit"
    MAINTENANCE = "maintenance"

    # Strategy & Configuration / 策略与配置
    STRATEGY = "strategy"
    CONFIG = "config"
    VALIDATION = "validation"

    # System & Internal / 系统与内部
    SYSTEM = "system"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


@dataclass
class StandardErrorResponse:
    """
    Standard error response data structure / 标准错误响应数据结构

    Provides a consistent format for error responses across all modules.
    为所有模块提供一致的错误响应格式。
    """

    error: str
    """Error identifier / 错误标识符"""

    error_type: ErrorType
    """Error type category / 错误类型分类"""

    error_code: str
    """Machine-readable error code / 机器可读的错误代码"""

    message: str
    """Error message in English / 英文错误消息"""

    message_zh: str
    """Error message in Chinese / 中文错误消息"""

    severity: ErrorSeverity
    """Error severity level / 错误严重程度级别"""

    suggestion: str
    """Suggestion for resolving the error in English / 英文错误解决建议"""

    suggestion_zh: str
    """Suggestion for resolving the error in Chinese / 中文错误解决建议"""

    remediation: Optional[str] = None
    """Remediation steps in English (optional) / 英文修复步骤（可选）"""

    remediation_zh: Optional[str] = None
    """Remediation steps in Chinese (optional) / 中文修复步骤（可选）"""

    details: Optional[Dict[str, Any]] = None
    """Additional error details (optional) / 附加错误详情（可选）"""

    timestamp: float = field(default_factory=time.time)
    """Error timestamp in seconds since epoch / 错误时间戳（自纪元以来的秒数）"""

    trace_id: Optional[str] = None
    """Trace ID for error tracking (optional) / 用于错误追踪的追踪 ID（可选）"""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error response to dictionary / 将错误响应转换为字典

        Returns:
            Dictionary representation of the error response
            错误响应的字典表示
        """
        result = {
            "error": self.error,
            "error_type": self.error_type.value,
            "error_code": self.error_code,
            "message": self.message,
            "message_zh": self.message_zh,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
            "suggestion_zh": self.suggestion_zh,
            "timestamp": self.timestamp,
        }

        if self.remediation is not None:
            result["remediation"] = self.remediation
        if self.remediation_zh is not None:
            result["remediation_zh"] = self.remediation_zh
        if self.details is not None:
            result["details"] = self.details
        if self.trace_id is not None:
            result["trace_id"] = self.trace_id

        return result

    def __str__(self) -> str:
        """String representation / 字符串表示"""
        return f"[{self.error_type.value}] {self.error_code}: {self.message}"

    def __repr__(self) -> str:
        """Representation / 表示"""
        return (
            f"StandardErrorResponse("
            f"error={self.error!r}, "
            f"error_type={self.error_type.value}, "
            f"error_code={self.error_code!r}, "
            f"severity={self.severity.value}"
            f")"
        )

