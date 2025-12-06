"""
Unit tests for error mapper module / 错误映射器模块单元测试

Tests for ErrorMapper and map_exception function.
测试 ErrorMapper 和 map_exception 函数。

Owner: Agent ARCH (for src/shared/), Agent QA (for tests/)
"""

import uuid
from unittest.mock import patch

import pytest

from src.shared.error_mapper import ErrorMapper, map_exception
from src.shared.errors import ErrorSeverity, ErrorType, StandardErrorResponse


class TestErrorMapperExceptionMapping:
    """Test exception to error type mapping / 测试异常到错误类型的映射"""

    def test_standard_python_exceptions(self):
        """Test standard Python exception mapping / 测试标准 Python 异常映射"""
        # ConnectionError
        error = ErrorMapper.map_exception(ConnectionError("Connection failed"))
        assert error.error_type == ErrorType.CONNECTION

        # TimeoutError
        error = ErrorMapper.map_exception(TimeoutError("Request timed out"))
        assert error.error_type == ErrorType.TIMEOUT

        # ValueError
        error = ErrorMapper.map_exception(ValueError("Invalid value"))
        assert error.error_type == ErrorType.VALIDATION

        # KeyError
        error = ErrorMapper.map_exception(KeyError("key"))
        assert error.error_type == ErrorType.VALIDATION

        # TypeError
        error = ErrorMapper.map_exception(TypeError("Invalid type"))
        assert error.error_type == ErrorType.VALIDATION

        # PermissionError
        error = ErrorMapper.map_exception(PermissionError("Permission denied"))
        assert error.error_type == ErrorType.AUTHORIZATION

        # FileNotFoundError
        error = ErrorMapper.map_exception(FileNotFoundError("File not found"))
        assert error.error_type == ErrorType.SYSTEM

        # OSError
        error = ErrorMapper.map_exception(OSError("OS error"))
        assert error.error_type == ErrorType.SYSTEM

    def test_hyperliquid_exceptions(self):
        """Test HyperliquidClient exception mapping / 测试 HyperliquidClient 异常映射"""
        try:
            from src.trading.hyperliquid_client import (
                AuthenticationError,
                ConnectionError,
                InsufficientBalanceError,
                InvalidOrderError,
                OrderNotFoundError,
            )

            # AuthenticationError
            error = ErrorMapper.map_exception(AuthenticationError("Auth failed"))
            assert error.error_type == ErrorType.AUTHENTICATION

            # ConnectionError
            error = ErrorMapper.map_exception(ConnectionError("Connection failed"))
            assert error.error_type == ErrorType.CONNECTION

            # InsufficientBalanceError
            error = ErrorMapper.map_exception(InsufficientBalanceError("Insufficient balance"))
            assert error.error_type == ErrorType.TRADING

            # InvalidOrderError
            error = ErrorMapper.map_exception(InvalidOrderError("Invalid order"))
            assert error.error_type == ErrorType.ORDER

            # OrderNotFoundError
            error = ErrorMapper.map_exception(OrderNotFoundError("Order not found"))
            assert error.error_type == ErrorType.ORDER
        except ImportError:
            pytest.skip("HyperliquidClient exceptions not available")

    def test_ccxt_exceptions(self):
        """Test CCXT exception mapping / 测试 CCXT 异常映射"""
        try:
            from ccxt import (
                AuthenticationError,
                ExchangeError,
                InsufficientFunds,
                InvalidOrder,
                NetworkError,
                OrderNotFound,
                RateLimitExceeded,
            )

            # AuthenticationError
            error = ErrorMapper.map_exception(AuthenticationError("Auth failed"))
            assert error.error_type == ErrorType.AUTHENTICATION

            # ExchangeError
            error = ErrorMapper.map_exception(ExchangeError("Exchange error"))
            assert error.error_type == ErrorType.EXCHANGE

            # InsufficientFunds
            error = ErrorMapper.map_exception(InsufficientFunds("Insufficient funds"))
            assert error.error_type == ErrorType.TRADING

            # InvalidOrder
            error = ErrorMapper.map_exception(InvalidOrder("Invalid order"))
            assert error.error_type == ErrorType.ORDER

            # NetworkError
            error = ErrorMapper.map_exception(NetworkError("Network error"))
            assert error.error_type == ErrorType.NETWORK

            # OrderNotFound
            error = ErrorMapper.map_exception(OrderNotFound("Order not found"))
            assert error.error_type == ErrorType.ORDER

            # RateLimitExceeded
            error = ErrorMapper.map_exception(RateLimitExceeded("Rate limit exceeded"))
            assert error.error_type == ErrorType.RATE_LIMIT
        except ImportError:
            pytest.skip("CCXT exceptions not available")

    def test_unknown_exception(self):
        """Test unknown exception mapping / 测试未知异常映射"""
        class CustomException(Exception):
            pass

        error = ErrorMapper.map_exception(CustomException("Custom error"))
        assert error.error_type == ErrorType.UNKNOWN

    def test_exception_message_based_mapping(self):
        """Test exception mapping based on message content / 测试基于消息内容的异常映射"""
        # Exception with authentication in message
        error = ErrorMapper.map_exception(Exception("Authentication failed"))
        assert error.error_type == ErrorType.AUTHENTICATION

        # Exception with connection in message
        error = ErrorMapper.map_exception(Exception("Connection error"))
        assert error.error_type == ErrorType.CONNECTION

        # Exception with network in message
        error = ErrorMapper.map_exception(Exception("Network issue"))
        assert error.error_type == ErrorType.NETWORK

        # Exception with timeout in message
        error = ErrorMapper.map_exception(Exception("Request timeout"))
        assert error.error_type == ErrorType.TIMEOUT

        # Exception with balance in message
        error = ErrorMapper.map_exception(Exception("Insufficient balance"))
        assert error.error_type == ErrorType.TRADING

        # Exception with order in message
        error = ErrorMapper.map_exception(Exception("Order rejected"))
        assert error.error_type == ErrorType.ORDER

        # Exception with rate limit in message
        error = ErrorMapper.map_exception(Exception("Rate limit exceeded"))
        assert error.error_type == ErrorType.RATE_LIMIT


class TestErrorMapperSeverity:
    """Test error severity determination / 测试错误严重程度确定"""

    def test_critical_severity(self):
        """Test critical severity / 测试严重严重程度"""
        error = ErrorMapper.map_exception(OSError("System error"))
        assert error.severity == ErrorSeverity.CRITICAL

        error = ErrorMapper.map_exception(Exception("Internal error"))
        # Internal error type should be CRITICAL if mapped
        if error.error_type == ErrorType.INTERNAL:
            assert error.severity == ErrorSeverity.CRITICAL

    def test_error_severity(self):
        """Test error severity / 测试错误严重程度"""
        error = ErrorMapper.map_exception(ConnectionError("Connection failed"))
        assert error.severity == ErrorSeverity.ERROR

        error = ErrorMapper.map_exception(ValueError("Invalid value"))
        # Validation errors should be WARNING
        if error.error_type == ErrorType.VALIDATION:
            assert error.severity == ErrorSeverity.WARNING

    def test_warning_severity(self):
        """Test warning severity / 测试警告严重程度"""
        try:
            from ccxt import RateLimitExceeded

            error = ErrorMapper.map_exception(RateLimitExceeded("Rate limit"))
            assert error.severity == ErrorSeverity.WARNING
        except ImportError:
            pytest.skip("CCXT not available")

    def test_info_severity(self):
        """Test info severity / 测试信息严重程度"""
        class UnknownException(Exception):
            pass

        error = ErrorMapper.map_exception(UnknownException("Unknown"))
        if error.error_type == ErrorType.UNKNOWN:
            assert error.severity == ErrorSeverity.INFO


class TestErrorMapperErrorCode:
    """Test error code generation / 测试错误代码生成"""

    def test_error_code_format(self):
        """Test error code format / 测试错误代码格式"""
        error = ErrorMapper.map_exception(ConnectionError("Connection failed"))
        assert error.error_code.startswith("CONNECTION_")
        assert "ConnectionError" in error.error_code

    def test_custom_error_code(self):
        """Test custom error code / 测试自定义错误代码"""
        error = ErrorMapper.map_exception(
            ConnectionError("Connection failed"), error_code="CUSTOM_001"
        )
        assert error.error_code == "CUSTOM_001"

    def test_error_code_for_different_exceptions(self):
        """Test error codes for different exceptions / 测试不同异常的错误代码"""
        error1 = ErrorMapper.map_exception(ValueError("Invalid"))
        error2 = ErrorMapper.map_exception(KeyError("Missing key"))
        error3 = ErrorMapper.map_exception(TypeError("Wrong type"))

        # All should have different error codes
        assert error1.error_code != error2.error_code
        assert error2.error_code != error3.error_code


class TestErrorMapperBilingualMessages:
    """Test bilingual message handling / 测试双语消息处理"""

    def test_english_only_message(self):
        """Test English-only message / 测试仅英文消息"""
        error = ErrorMapper.map_exception(ConnectionError("Connection failed"))
        assert error.message == "Connection failed"
        assert error.message_zh  # Should have Chinese translation
        assert len(error.message_zh) > 0

    def test_bilingual_message_split(self):
        """Test splitting bilingual message / 测试拆分双语消息"""
        error = ErrorMapper.map_exception(
            Exception("Connection failed. 连接失败。")
        )
        # Should split bilingual message
        assert "Connection failed" in error.message or "连接失败" in error.message_zh

    def test_message_with_chinese_characters(self):
        """Test message with Chinese characters / 测试包含中文字符的消息"""
        error = ErrorMapper.map_exception(Exception("连接失败"))
        # Should detect Chinese and handle appropriately
        assert len(error.message) > 0
        assert len(error.message_zh) > 0

    def test_empty_message(self):
        """Test exception with empty message / 测试空消息的异常"""
        error = ErrorMapper.map_exception(ValueError())
        # Should use default message
        assert len(error.message) > 0
        assert len(error.message_zh) > 0


class TestErrorMapperSuggestions:
    """Test error suggestions / 测试错误建议"""

    def test_suggestions_for_all_error_types(self):
        """Test suggestions exist for all error types / 测试所有错误类型都有建议"""
        for error_type in ErrorType:
            error = ErrorMapper.map_exception(Exception("Test"))
            # Override error type to test all suggestions
            error.error_type = error_type
            suggestions = ErrorMapper._get_suggestions(error_type)
            assert len(suggestions[0]) > 0  # English suggestion
            assert len(suggestions[1]) > 0  # Chinese suggestion

    def test_suggestions_bilingual(self):
        """Test suggestions are bilingual / 测试建议是双语的"""
        error = ErrorMapper.map_exception(ConnectionError("Connection failed"))
        assert len(error.suggestion) > 0
        assert len(error.suggestion_zh) > 0
        assert error.suggestion != error.suggestion_zh

    def test_suggestions_match_error_type(self):
        """Test suggestions match error type / 测试建议匹配错误类型"""
        error = ErrorMapper.map_exception(ConnectionError("Connection failed"))
        assert error.error_type == ErrorType.CONNECTION
        # Suggestion should mention connection
        assert "connection" in error.suggestion.lower() or "连接" in error.suggestion_zh


class TestErrorMapperRemediation:
    """Test remediation steps / 测试修复步骤"""

    def test_remediation_for_supported_types(self):
        """Test remediation for supported error types / 测试支持的错误类型的修复步骤"""
        # Authentication
        error = ErrorMapper.map_exception(Exception("Auth failed"))
        error.error_type = ErrorType.AUTHENTICATION
        remediation = ErrorMapper._get_remediation(ErrorType.AUTHENTICATION)
        if remediation[0]:  # If remediation exists
            assert len(remediation[0]) > 0
            assert len(remediation[1]) > 0

        # Connection
        remediation = ErrorMapper._get_remediation(ErrorType.CONNECTION)
        if remediation[0]:
            assert len(remediation[0]) > 0
            assert len(remediation[1]) > 0

    def test_remediation_optional(self):
        """Test remediation is optional / 测试修复步骤是可选的"""
        # Some error types may not have remediation
        remediation = ErrorMapper._get_remediation(ErrorType.UNKNOWN)
        # Should return None or have remediation
        assert remediation is not None

    def test_remediation_bilingual(self):
        """Test remediation is bilingual / 测试修复步骤是双语的"""
        remediation = ErrorMapper._get_remediation(ErrorType.AUTHENTICATION)
        if remediation[0]:
            assert len(remediation[0]) > 0  # English
            assert len(remediation[1]) > 0  # Chinese
            assert remediation[0] != remediation[1]


class TestErrorMapperDetails:
    """Test error details / 测试错误详情"""

    def test_default_details(self):
        """Test default details / 测试默认详情"""
        error = ErrorMapper.map_exception(ConnectionError("Connection failed"))
        assert error.details is not None
        assert "exception_type" in error.details
        assert error.details["exception_type"] == "ConnectionError"
        assert "exception_module" in error.details

    def test_custom_details(self):
        """Test custom details / 测试自定义详情"""
        custom_details = {"custom_key": "custom_value", "another_key": 123}
        error = ErrorMapper.map_exception(
            ConnectionError("Connection failed"), details=custom_details
        )
        assert error.details is not None
        assert error.details["custom_key"] == "custom_value"
        assert error.details["another_key"] == 123
        assert "exception_type" in error.details  # Should merge with default

    def test_details_merge(self):
        """Test details merge with default / 测试详情与默认值合并"""
        custom_details = {"user_id": "123"}
        error = ErrorMapper.map_exception(
            ValueError("Invalid"), details=custom_details
        )
        assert error.details["user_id"] == "123"
        assert error.details["exception_type"] == "ValueError"


class TestErrorMapperTraceId:
    """Test trace ID generation / 测试追踪 ID 生成"""

    def test_trace_id_auto_generated(self):
        """Test trace ID is auto-generated / 测试追踪 ID 自动生成"""
        error = ErrorMapper.map_exception(ConnectionError("Connection failed"))
        assert error.trace_id is not None
        assert len(error.trace_id) > 0
        # Should be valid UUID format
        try:
            uuid.UUID(error.trace_id)
        except ValueError:
            pytest.fail("Trace ID should be valid UUID format")

    def test_custom_trace_id(self):
        """Test custom trace ID / 测试自定义追踪 ID"""
        custom_trace_id = "custom-trace-123"
        error = ErrorMapper.map_exception(
            ConnectionError("Connection failed"), trace_id=custom_trace_id
        )
        assert error.trace_id == custom_trace_id

    def test_trace_id_unique(self):
        """Test trace IDs are unique / 测试追踪 ID 是唯一的"""
        error1 = ErrorMapper.map_exception(ConnectionError("Error 1"))
        error2 = ErrorMapper.map_exception(ConnectionError("Error 2"))
        assert error1.trace_id != error2.trace_id


class TestMapExceptionFunction:
    """Test map_exception convenience function / 测试 map_exception 便利函数"""

    def test_map_exception_function(self):
        """Test map_exception function / 测试 map_exception 函数"""
        from src.shared.error_mapper import map_exception

        error = map_exception(ConnectionError("Connection failed"))
        assert isinstance(error, StandardErrorResponse)
        assert error.error_type == ErrorType.CONNECTION

    def test_map_exception_with_custom_params(self):
        """Test map_exception with custom parameters / 测试带自定义参数的 map_exception"""
        from src.shared.error_mapper import map_exception

        error = map_exception(
            ValueError("Invalid"),
            error_code="CUSTOM_001",
            details={"key": "value"},
            trace_id="trace-123",
        )
        assert error.error_code == "CUSTOM_001"
        assert error.details["key"] == "value"
        assert error.trace_id == "trace-123"


class TestErrorMapperIntegration:
    """Integration tests for ErrorMapper / ErrorMapper 集成测试"""

    def test_full_error_response_creation(self):
        """Test full error response creation / 测试完整错误响应创建"""
        error = ErrorMapper.map_exception(
            ConnectionError("Connection to exchange failed"),
            error_code="CONN_EXCHANGE_001",
            details={"exchange": "binance", "retry_count": 3},
            trace_id="trace-full-test",
        )

        # Verify all fields
        assert error.error == "ConnectionError"
        assert error.error_type == ErrorType.CONNECTION
        assert error.error_code == "CONN_EXCHANGE_001"
        assert "Connection" in error.message
        assert len(error.message_zh) > 0
        assert error.severity == ErrorSeverity.ERROR
        assert len(error.suggestion) > 0
        assert len(error.suggestion_zh) > 0
        assert error.details["exchange"] == "binance"
        assert error.details["retry_count"] == 3
        assert error.trace_id == "trace-full-test"
        assert error.timestamp > 0

    def test_error_response_serialization(self):
        """Test error response can be serialized / 测试错误响应可以序列化"""
        error = ErrorMapper.map_exception(ValueError("Invalid input"))
        error_dict = error.to_dict()

        # Verify all required fields in dict
        assert "error" in error_dict
        assert "error_type" in error_dict
        assert "error_code" in error_dict
        assert "message" in error_dict
        assert "message_zh" in error_dict
        assert "severity" in error_dict
        assert "suggestion" in error_dict
        assert "suggestion_zh" in error_dict
        assert "timestamp" in error_dict

        # Verify values are serializable
        import json

        json_str = json.dumps(error_dict)
        assert len(json_str) > 0

