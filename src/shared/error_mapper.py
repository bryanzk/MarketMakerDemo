"""
Error Mapper Module / 错误映射器模块

Maps exceptions to standardized error responses with bilingual support.
将异常映射为标准化错误响应，支持双语。

Owner: Agent ARCH
"""

import logging
import traceback
import uuid
from typing import Any, Dict, Optional, Tuple, Type

from src.shared.errors import ErrorSeverity, ErrorType, StandardErrorResponse

logger = logging.getLogger(__name__)

# Import exchange-specific exceptions
try:
    from src.trading.hyperliquid_client import (
        AuthenticationError as HyperliquidAuthenticationError,
    )
    from src.trading.hyperliquid_client import (
        ConnectionError as HyperliquidConnectionError,
    )
    from src.trading.hyperliquid_client import (
        InsufficientBalanceError,
        InvalidOrderError,
        OrderNotFoundError,
    )
except ImportError:
    # Fallback if module not available
    HyperliquidAuthenticationError = None
    HyperliquidConnectionError = None
    InsufficientBalanceError = None
    InvalidOrderError = None
    OrderNotFoundError = None

try:
    from ccxt import AuthenticationError as CCXTAuthenticationError
    from ccxt import (
        ExchangeError,
        InsufficientFunds,
        InvalidOrder,
        NetworkError,
        OrderNotFound,
        RateLimitExceeded,
    )
except ImportError:
    # Fallback if CCXT not available
    CCXTAuthenticationError = None
    ExchangeError = None
    InsufficientFunds = None
    InvalidOrder = None
    NetworkError = None
    OrderNotFound = None
    RateLimitExceeded = None


class ErrorMapper:
    """
    Maps exceptions to standardized error responses / 将异常映射为标准化错误响应

    Provides consistent error handling across all modules with bilingual support.
    为所有模块提供一致的错误处理，支持双语。
    """

    # Exception to ErrorType mapping / 异常到错误类型的映射
    EXCEPTION_TO_ERROR_TYPE: Dict[Type[Exception], ErrorType] = {}

    # Initialize exception mappings / 初始化异常映射
    if HyperliquidAuthenticationError:
        EXCEPTION_TO_ERROR_TYPE[HyperliquidAuthenticationError] = (
            ErrorType.AUTHENTICATION
        )
    if HyperliquidConnectionError:
        EXCEPTION_TO_ERROR_TYPE[HyperliquidConnectionError] = ErrorType.CONNECTION
    if InsufficientBalanceError:
        EXCEPTION_TO_ERROR_TYPE[InsufficientBalanceError] = ErrorType.TRADING
    if InvalidOrderError:
        EXCEPTION_TO_ERROR_TYPE[InvalidOrderError] = ErrorType.ORDER
    if OrderNotFoundError:
        EXCEPTION_TO_ERROR_TYPE[OrderNotFoundError] = ErrorType.ORDER

    if CCXTAuthenticationError:
        EXCEPTION_TO_ERROR_TYPE[CCXTAuthenticationError] = ErrorType.AUTHENTICATION
    if ExchangeError:
        EXCEPTION_TO_ERROR_TYPE[ExchangeError] = ErrorType.EXCHANGE
    if InsufficientFunds:
        EXCEPTION_TO_ERROR_TYPE[InsufficientFunds] = ErrorType.TRADING
    if InvalidOrder:
        EXCEPTION_TO_ERROR_TYPE[InvalidOrder] = ErrorType.ORDER
    if NetworkError:
        EXCEPTION_TO_ERROR_TYPE[NetworkError] = ErrorType.NETWORK
    if OrderNotFound:
        EXCEPTION_TO_ERROR_TYPE[OrderNotFound] = ErrorType.ORDER
    if RateLimitExceeded:
        EXCEPTION_TO_ERROR_TYPE[RateLimitExceeded] = ErrorType.RATE_LIMIT

    # Standard Python exceptions / 标准 Python 异常
    EXCEPTION_TO_ERROR_TYPE[ConnectionError] = ErrorType.CONNECTION
    EXCEPTION_TO_ERROR_TYPE[TimeoutError] = ErrorType.TIMEOUT
    EXCEPTION_TO_ERROR_TYPE[ValueError] = ErrorType.VALIDATION
    EXCEPTION_TO_ERROR_TYPE[KeyError] = ErrorType.VALIDATION
    EXCEPTION_TO_ERROR_TYPE[TypeError] = ErrorType.VALIDATION
    EXCEPTION_TO_ERROR_TYPE[PermissionError] = ErrorType.AUTHORIZATION
    EXCEPTION_TO_ERROR_TYPE[FileNotFoundError] = ErrorType.SYSTEM
    EXCEPTION_TO_ERROR_TYPE[OSError] = ErrorType.SYSTEM

    # Bilingual error suggestions dictionary / 双语错误建议字典
    ERROR_SUGGESTIONS: Dict[ErrorType, Dict[str, str]] = {
        ErrorType.AUTHENTICATION: {
            "en": "Check your API credentials (API key and secret). Ensure they are correctly set in environment variables or configuration.",
            "zh": "检查您的 API 凭证（API 密钥和密钥）。确保它们在环境变量或配置中正确设置。",
        },
        ErrorType.AUTHORIZATION: {
            "en": "Verify that your API key has the necessary permissions for the requested operation.",
            "zh": "验证您的 API 密钥是否具有执行请求操作所需的权限。",
        },
        ErrorType.CONNECTION: {
            "en": "Check your internet connection and try again. If the problem persists, the exchange may be temporarily unavailable.",
            "zh": "检查您的互联网连接并重试。如果问题持续存在，交易所可能暂时不可用。",
        },
        ErrorType.NETWORK: {
            "en": "Network error occurred. Check your connection and try again. If the issue persists, contact support.",
            "zh": "发生网络错误。检查您的连接并重试。如果问题持续存在，请联系支持。",
        },
        ErrorType.TIMEOUT: {
            "en": "Request timed out. The operation took too long to complete. Try again with a longer timeout or check network conditions.",
            "zh": "请求超时。操作完成时间过长。使用更长的超时时间重试或检查网络状况。",
        },
        ErrorType.TRADING: {
            "en": "Trading operation failed. Check your account balance, position limits, and order parameters.",
            "zh": "交易操作失败。检查您的账户余额、仓位限制和订单参数。",
        },
        ErrorType.ORDER: {
            "en": "Order operation failed. Verify order parameters (symbol, side, type, price, quantity) and try again.",
            "zh": "订单操作失败。验证订单参数（交易对、方向、类型、价格、数量）并重试。",
        },
        ErrorType.POSITION: {
            "en": "Position operation failed. Check your current positions and position limits.",
            "zh": "仓位操作失败。检查您当前的仓位和仓位限制。",
        },
        ErrorType.BALANCE: {
            "en": "Balance operation failed. Check your account balance and available margin.",
            "zh": "余额操作失败。检查您的账户余额和可用保证金。",
        },
        ErrorType.EXCHANGE: {
            "en": "Exchange API error occurred. The exchange may be experiencing issues. Check exchange status and try again later.",
            "zh": "发生交易所 API 错误。交易所可能遇到问题。检查交易所状态并稍后重试。",
        },
        ErrorType.RATE_LIMIT: {
            "en": "Rate limit exceeded. Too many requests in a short time. Wait a moment and try again.",
            "zh": "超过速率限制。短时间内请求过多。等待片刻后重试。",
        },
        ErrorType.MAINTENANCE: {
            "en": "Exchange is under maintenance. Please wait for maintenance to complete and try again later.",
            "zh": "交易所正在维护中。请等待维护完成后再试。",
        },
        ErrorType.STRATEGY: {
            "en": "Strategy error occurred. Check strategy configuration and parameters.",
            "zh": "发生策略错误。检查策略配置和参数。",
        },
        ErrorType.CONFIG: {
            "en": "Configuration error. Check your configuration file and environment variables.",
            "zh": "配置错误。检查您的配置文件和环境变量。",
        },
        ErrorType.VALIDATION: {
            "en": "Validation error. Check input parameters and ensure they meet the required format and constraints.",
            "zh": "验证错误。检查输入参数并确保它们符合所需的格式和约束。",
        },
        ErrorType.SYSTEM: {
            "en": "System error occurred. This may be a temporary issue. Try again or contact support if the problem persists.",
            "zh": "发生系统错误。这可能是临时问题。重试或如果问题持续存在，请联系支持。",
        },
        ErrorType.INTERNAL: {
            "en": "Internal error occurred. Please report this issue to support with error details.",
            "zh": "发生内部错误。请将错误详情报告给支持。",
        },
        ErrorType.UNKNOWN: {
            "en": "An unexpected error occurred. Please check the error details and try again. If the problem persists, contact support.",
            "zh": "发生意外错误。请检查错误详情并重试。如果问题持续存在，请联系支持。",
        },
    }

    # Remediation steps dictionary / 修复步骤字典
    ERROR_REMEDIATION: Dict[ErrorType, Dict[str, str]] = {
        ErrorType.AUTHENTICATION: {
            "en": "1. Verify API credentials in environment variables (API_KEY, API_SECRET)\n2. Check if credentials are expired or revoked\n3. Regenerate API keys if necessary",
            "zh": "1. 验证环境变量中的 API 凭证（API_KEY, API_SECRET）\n2. 检查凭证是否已过期或已撤销\n3. 如有必要，重新生成 API 密钥",
        },
        ErrorType.CONNECTION: {
            "en": "1. Check internet connectivity\n2. Verify firewall/proxy settings\n3. Check exchange API status page\n4. Retry after a few moments",
            "zh": "1. 检查互联网连接\n2. 验证防火墙/代理设置\n3. 检查交易所 API 状态页面\n4. 等待片刻后重试",
        },
        ErrorType.TRADING: {
            "en": "1. Check account balance\n2. Verify position limits\n3. Review order parameters\n4. Check exchange trading rules",
            "zh": "1. 检查账户余额\n2. 验证仓位限制\n3. 审查订单参数\n4. 检查交易所交易规则",
        },
        ErrorType.RATE_LIMIT: {
            "en": "1. Reduce request frequency\n2. Implement exponential backoff\n3. Use rate limit headers to track remaining requests",
            "zh": "1. 降低请求频率\n2. 实现指数退避\n3. 使用速率限制标头跟踪剩余请求",
        },
    }

    @classmethod
    def map_exception(
        cls,
        exception: Exception,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> StandardErrorResponse:
        """
        Map an exception to a standardized error response / 将异常映射为标准化错误响应

        Args:
            exception: The exception to map / 要映射的异常
            error_code: Optional custom error code / 可选的自定义错误代码
            details: Optional additional error details / 可选的附加错误详情
            trace_id: Optional trace ID for error tracking / 可选的错误追踪 ID

        Returns:
            StandardErrorResponse object / StandardErrorResponse 对象
        """
        # Determine error type / 确定错误类型
        error_type = cls._determine_error_type(exception)

        # Determine severity / 确定严重程度
        severity = cls._determine_severity(exception, error_type)

        # Generate error code / 生成错误代码
        if error_code is None:
            error_code = cls._generate_error_code(exception, error_type)

        # Get error message / 获取错误消息
        error_message = str(exception)
        if not error_message or error_message == exception.__class__.__name__:
            error_message = cls._get_default_message(exception, error_type)

        # Get bilingual messages / 获取双语消息
        message_en, message_zh = cls._get_bilingual_messages(error_message, error_type)

        # Get suggestions / 获取建议
        suggestion_en, suggestion_zh = cls._get_suggestions(error_type)

        # Get remediation / 获取修复步骤
        remediation_en, remediation_zh = cls._get_remediation(error_type)

        # Generate trace ID if not provided / 如果未提供则生成追踪 ID
        if trace_id is None:
            trace_id = str(uuid.uuid4())

        # Add exception details if not provided / 如果未提供则添加异常详情
        if details is None:
            details = {}
        details["exception_type"] = exception.__class__.__name__
        details["exception_module"] = getattr(
            exception.__class__, "__module__", "unknown"
        )

        return StandardErrorResponse(
            error=exception.__class__.__name__,
            error_type=error_type,
            error_code=error_code,
            message=message_en,
            message_zh=message_zh,
            severity=severity,
            suggestion=suggestion_en,
            suggestion_zh=suggestion_zh,
            remediation=remediation_en,
            remediation_zh=remediation_zh,
            details=details,
            trace_id=trace_id,
        )

    @classmethod
    def _determine_error_type(cls, exception: Exception) -> ErrorType:
        """
        Determine error type from exception / 从异常确定错误类型

        Args:
            exception: The exception / 异常

        Returns:
            ErrorType enum value / ErrorType 枚举值
        """
        exception_type = type(exception)

        # Check direct mapping / 检查直接映射
        if exception_type in cls.EXCEPTION_TO_ERROR_TYPE:
            return cls.EXCEPTION_TO_ERROR_TYPE[exception_type]

        # Check parent classes / 检查父类
        for exc_type, error_type in cls.EXCEPTION_TO_ERROR_TYPE.items():
            if issubclass(exception_type, exc_type):
                return error_type

        # Check exception message for hints / 检查异常消息中的提示
        error_msg = str(exception).lower()
        if (
            "authentication" in error_msg
            or "auth" in error_msg
            or "credential" in error_msg
        ):
            return ErrorType.AUTHENTICATION
        if "connection" in error_msg or "connect" in error_msg:
            return ErrorType.CONNECTION
        if "network" in error_msg:
            return ErrorType.NETWORK
        if "timeout" in error_msg:
            return ErrorType.TIMEOUT
        if "balance" in error_msg or "insufficient" in error_msg or "fund" in error_msg:
            return ErrorType.TRADING
        if "order" in error_msg:
            return ErrorType.ORDER
        if "rate limit" in error_msg or "rate_limit" in error_msg:
            return ErrorType.RATE_LIMIT

        # Default to unknown / 默认为未知
        return ErrorType.UNKNOWN

    @classmethod
    def _determine_severity(
        cls, exception: Exception, error_type: ErrorType
    ) -> ErrorSeverity:
        """
        Determine error severity / 确定错误严重程度

        Args:
            exception: The exception / 异常
            error_type: The error type / 错误类型

        Returns:
            ErrorSeverity enum value / ErrorSeverity 枚举值
        """
        # Critical errors / 严重错误
        if error_type in (ErrorType.SYSTEM, ErrorType.INTERNAL):
            return ErrorSeverity.CRITICAL

        # Error level / 错误级别
        if error_type in (
            ErrorType.AUTHENTICATION,
            ErrorType.CONNECTION,
            ErrorType.NETWORK,
            ErrorType.TRADING,
            ErrorType.ORDER,
            ErrorType.EXCHANGE,
        ):
            return ErrorSeverity.ERROR

        # Warning level / 警告级别
        if error_type in (ErrorType.RATE_LIMIT, ErrorType.VALIDATION, ErrorType.CONFIG):
            return ErrorSeverity.WARNING

        # Info level / 信息级别
        if error_type == ErrorType.UNKNOWN:
            return ErrorSeverity.INFO

        # Default to error / 默认为错误
        return ErrorSeverity.ERROR

    @classmethod
    def _generate_error_code(cls, exception: Exception, error_type: ErrorType) -> str:
        """
        Generate error code / 生成错误代码

        Args:
            exception: The exception / 异常
            error_type: The error type / 错误类型

        Returns:
            Error code string / 错误代码字符串
        """
        exception_name = exception.__class__.__name__
        error_type_code = error_type.value.upper()
        return f"{error_type_code}_{exception_name}"

    @classmethod
    def _get_default_message(cls, exception: Exception, error_type: ErrorType) -> str:
        """
        Get default error message / 获取默认错误消息

        Args:
            exception: The exception / 异常
            error_type: The error type / 错误类型

        Returns:
            Default error message / 默认错误消息
        """
        messages = {
            ErrorType.AUTHENTICATION: "Authentication failed",
            ErrorType.CONNECTION: "Connection failed",
            ErrorType.NETWORK: "Network error occurred",
            ErrorType.TIMEOUT: "Request timed out",
            ErrorType.TRADING: "Trading operation failed",
            ErrorType.ORDER: "Order operation failed",
            ErrorType.EXCHANGE: "Exchange API error",
            ErrorType.RATE_LIMIT: "Rate limit exceeded",
            ErrorType.VALIDATION: "Validation error",
            ErrorType.SYSTEM: "System error occurred",
        }
        return messages.get(error_type, "An unexpected error occurred")

    @classmethod
    def _get_bilingual_messages(
        cls, error_message: str, error_type: ErrorType
    ) -> Tuple[str, str]:
        """
        Get bilingual error messages / 获取双语错误消息

        Args:
            error_message: Original error message / 原始错误消息
            error_type: The error type / 错误类型

        Returns:
            Tuple of (English message, Chinese message) / （英文消息，中文消息）元组
        """
        # For connection errors, extract concise message (details go in details field)
        # 对于连接错误，提取简洁消息（详细信息放在 details 字段中）
        if error_type == ErrorType.CONNECTION:
            # Extract core message before "Base URL" or similar details
            # 在 "Base URL" 或类似详细信息之前提取核心消息
            if "Base URL:" in error_message:
                message_en = error_message.split("Base URL:")[0].strip()
                # Remove trailing period if present / 如果存在则删除尾随句号
                if message_en.endswith("."):
                    message_en = message_en[:-1]
            elif "基础 URL:" in error_message:
                message_en = error_message.split("基础 URL:")[0].strip()
                if message_en.endswith("。"):
                    message_en = message_en[:-1]
            else:
                # If message is too long, use default / 如果消息过长，使用默认值
                if len(error_message) > 100:
                    message_en = "Connection failed"
                else:
                    message_en = error_message
            message_zh = cls._translate_message(message_en, error_type)
            return (message_en, message_zh)

        # If message already contains Chinese, try to extract / 如果消息已包含中文，尝试提取
        if any("\u4e00" <= char <= "\u9fff" for char in error_message):
            # Try to split bilingual message / 尝试拆分双语消息
            parts = error_message.split("。")
            if len(parts) >= 2:
                en_part = parts[0].strip()
                zh_part = parts[1].strip() if len(parts) > 1 else ""
                return (en_part, zh_part)

        # Default: use original message for English, translate for Chinese / 默认：英文使用原始消息，中文翻译
        message_en = error_message
        message_zh = cls._translate_message(error_message, error_type)

        return (message_en, message_zh)

    @classmethod
    def _translate_message(cls, message: str, error_type: ErrorType) -> str:
        """
        Translate error message to Chinese / 将错误消息翻译为中文

        Args:
            message: English error message / 英文错误消息
            error_type: The error type / 错误类型

        Returns:
            Chinese error message / 中文错误消息
        """
        # For connection errors, provide concise translation / 对于连接错误，提供简洁翻译
        if error_type == ErrorType.CONNECTION:
            if "Failed to connect" in message or "connection failed" in message.lower():
                return "连接失败"
            elif "after" in message.lower() and "attempts" in message.lower():
                return "连接失败，已重试多次"
            else:
                return "连接错误"

        # Simple keyword-based translation / 基于关键字的简单翻译
        translations = {
            "authentication failed": "认证失败",
            "connection failed": "连接失败",
            "network error": "网络错误",
            "timeout": "超时",
            "insufficient": "不足",
            "balance": "余额",
            "order": "订单",
            "invalid": "无效",
            "not found": "未找到",
            "rate limit": "速率限制",
            "validation": "验证",
            "system error": "系统错误",
        }

        message_lower = message.lower()
        for en_key, zh_value in translations.items():
            if en_key in message_lower:
                # Simple replacement / 简单替换
                return message.replace(en_key, zh_value)

        # Default: return original with type prefix / 默认：返回带类型前缀的原始消息
        type_translations = {
            ErrorType.AUTHENTICATION: "认证错误",
            ErrorType.CONNECTION: "连接错误",
            ErrorType.NETWORK: "网络错误",
            ErrorType.TRADING: "交易错误",
            ErrorType.ORDER: "订单错误",
            ErrorType.EXCHANGE: "交易所错误",
        }
        prefix = type_translations.get(error_type, "错误")
        return f"{prefix}: {message}"

    @classmethod
    def _get_suggestions(cls, error_type: ErrorType) -> Tuple[str, str]:
        """
        Get bilingual suggestions / 获取双语建议

        Args:
            error_type: The error type / 错误类型

        Returns:
            Tuple of (English suggestion, Chinese suggestion) / （英文建议，中文建议）元组
        """
        suggestions = cls.ERROR_SUGGESTIONS.get(
            error_type, cls.ERROR_SUGGESTIONS[ErrorType.UNKNOWN]
        )
        return (suggestions["en"], suggestions["zh"])

    @classmethod
    def _get_remediation(
        cls, error_type: ErrorType
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get bilingual remediation steps / 获取双语修复步骤

        Args:
            error_type: The error type / 错误类型

        Returns:
            Tuple of (English remediation, Chinese remediation) / （英文修复步骤，中文修复步骤）元组
        """
        remediation = cls.ERROR_REMEDIATION.get(error_type)
        if remediation:
            return (remediation["en"], remediation["zh"])
        return (None, None)


# Convenience function / 便利函数
def map_exception(
    exception: Exception,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
) -> StandardErrorResponse:
    """
    Map an exception to a standardized error response / 将异常映射为标准化错误响应

    Convenience function that uses ErrorMapper.map_exception().
    使用 ErrorMapper.map_exception() 的便利函数。

    Args:
        exception: The exception to map / 要映射的异常
        error_code: Optional custom error code / 可选的自定义错误代码
        details: Optional additional error details / 可选的附加错误详情
        trace_id: Optional trace ID for error tracking / 可选的错误追踪 ID

    Returns:
        StandardErrorResponse object / StandardErrorResponse 对象
    """
    return ErrorMapper.map_exception(exception, error_code, details, trace_id)
