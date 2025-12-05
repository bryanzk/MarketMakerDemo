"""
Unit tests for standard error response module / 标准错误响应模块单元测试

Tests for ErrorSeverity, ErrorType, and StandardErrorResponse.
测试 ErrorSeverity、ErrorType 和 StandardErrorResponse。

Owner: Agent ARCH (for src/shared/), Agent QA (for tests/)
"""

import time
from datetime import datetime

import pytest

from src.shared.errors import ErrorSeverity, ErrorType, StandardErrorResponse


class TestErrorSeverity:
    """Test ErrorSeverity enum / 测试 ErrorSeverity 枚举"""

    def test_error_severity_values(self):
        """Test ErrorSeverity enum values / 测试 ErrorSeverity 枚举值"""
        assert ErrorSeverity.INFO.value == "info"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.CRITICAL.value == "critical"

    def test_error_severity_all_values(self):
        """Test all ErrorSeverity values exist / 测试所有 ErrorSeverity 值存在"""
        values = [severity.value for severity in ErrorSeverity]
        assert "info" in values
        assert "warning" in values
        assert "error" in values
        assert "critical" in values
        assert len(values) == 4


class TestErrorType:
    """Test ErrorType enum / 测试 ErrorType 枚举"""

    def test_error_type_authentication(self):
        """Test authentication error types / 测试认证错误类型"""
        assert ErrorType.AUTHENTICATION.value == "authentication"
        assert ErrorType.AUTHORIZATION.value == "authorization"

    def test_error_type_connection(self):
        """Test connection error types / 测试连接错误类型"""
        assert ErrorType.CONNECTION.value == "connection"
        assert ErrorType.NETWORK.value == "network"
        assert ErrorType.TIMEOUT.value == "timeout"

    def test_error_type_trading(self):
        """Test trading error types / 测试交易错误类型"""
        assert ErrorType.TRADING.value == "trading"
        assert ErrorType.ORDER.value == "order"
        assert ErrorType.POSITION.value == "position"
        assert ErrorType.BALANCE.value == "balance"

    def test_error_type_exchange(self):
        """Test exchange error types / 测试交易所错误类型"""
        assert ErrorType.EXCHANGE.value == "exchange"
        assert ErrorType.RATE_LIMIT.value == "rate_limit"
        assert ErrorType.MAINTENANCE.value == "maintenance"

    def test_error_type_strategy(self):
        """Test strategy error types / 测试策略错误类型"""
        assert ErrorType.STRATEGY.value == "strategy"
        assert ErrorType.CONFIG.value == "config"
        assert ErrorType.VALIDATION.value == "validation"

    def test_error_type_system(self):
        """Test system error types / 测试系统错误类型"""
        assert ErrorType.SYSTEM.value == "system"
        assert ErrorType.INTERNAL.value == "internal"
        assert ErrorType.UNKNOWN.value == "unknown"

    def test_error_type_all_categories(self):
        """Test all error type categories exist / 测试所有错误类型分类存在"""
        categories = [error_type.value for error_type in ErrorType]
        assert len(categories) == 18  # Total number of error types


class TestStandardErrorResponse:
    """Test StandardErrorResponse dataclass / 测试 StandardErrorResponse 数据类"""

    def test_create_minimal_error_response(self):
        """Test creating minimal error response / 测试创建最小错误响应"""
        error = StandardErrorResponse(
            error="TestError",
            error_type=ErrorType.UNKNOWN,
            error_code="TEST_001",
            message="Test error message",
            message_zh="测试错误消息",
            severity=ErrorSeverity.ERROR,
            suggestion="Test suggestion",
            suggestion_zh="测试建议",
        )

        assert error.error == "TestError"
        assert error.error_type == ErrorType.UNKNOWN
        assert error.error_code == "TEST_001"
        assert error.message == "Test error message"
        assert error.message_zh == "测试错误消息"
        assert error.severity == ErrorSeverity.ERROR
        assert error.suggestion == "Test suggestion"
        assert error.suggestion_zh == "测试建议"
        assert error.remediation is None
        assert error.remediation_zh is None
        assert error.details is None
        assert error.timestamp > 0
        assert error.trace_id is None

    def test_create_full_error_response(self):
        """Test creating full error response with all fields / 测试创建包含所有字段的完整错误响应"""
        error = StandardErrorResponse(
            error="FullError",
            error_type=ErrorType.CONNECTION,
            error_code="CONN_001",
            message="Connection failed",
            message_zh="连接失败",
            severity=ErrorSeverity.ERROR,
            suggestion="Check connection",
            suggestion_zh="检查连接",
            remediation="1. Check network\n2. Retry",
            remediation_zh="1. 检查网络\n2. 重试",
            details={"host": "example.com", "port": 443},
            trace_id="trace-123",
        )

        assert error.error == "FullError"
        assert error.error_type == ErrorType.CONNECTION
        assert error.remediation == "1. Check network\n2. Retry"
        assert error.remediation_zh == "1. 检查网络\n2. 重试"
        assert error.details == {"host": "example.com", "port": 443}
        assert error.trace_id == "trace-123"

    def test_timestamp_auto_generated(self):
        """Test timestamp is auto-generated / 测试时间戳自动生成"""
        before = time.time()
        error = StandardErrorResponse(
            error="TestError",
            error_type=ErrorType.UNKNOWN,
            error_code="TEST_001",
            message="Test",
            message_zh="测试",
            severity=ErrorSeverity.ERROR,
            suggestion="Test",
            suggestion_zh="测试",
        )
        after = time.time()

        assert before <= error.timestamp <= after

    def test_to_dict_minimal(self):
        """Test to_dict() with minimal fields / 测试 to_dict() 最小字段"""
        error = StandardErrorResponse(
            error="TestError",
            error_type=ErrorType.VALIDATION,
            error_code="VAL_001",
            message="Validation error",
            message_zh="验证错误",
            severity=ErrorSeverity.WARNING,
            suggestion="Check input",
            suggestion_zh="检查输入",
        )

        result = error.to_dict()

        assert result["error"] == "TestError"
        assert result["error_type"] == "validation"
        assert result["error_code"] == "VAL_001"
        assert result["message"] == "Validation error"
        assert result["message_zh"] == "验证错误"
        assert result["severity"] == "warning"
        assert result["suggestion"] == "Check input"
        assert result["suggestion_zh"] == "检查输入"
        assert "timestamp" in result
        assert "remediation" not in result
        assert "remediation_zh" not in result
        assert "details" not in result
        assert "trace_id" not in result

    def test_to_dict_with_optional_fields(self):
        """Test to_dict() with optional fields / 测试 to_dict() 可选字段"""
        error = StandardErrorResponse(
            error="TestError",
            error_type=ErrorType.AUTHENTICATION,
            error_code="AUTH_001",
            message="Auth failed",
            message_zh="认证失败",
            severity=ErrorSeverity.ERROR,
            suggestion="Check credentials",
            suggestion_zh="检查凭证",
            remediation="Fix credentials",
            remediation_zh="修复凭证",
            details={"key": "value"},
            trace_id="trace-456",
        )

        result = error.to_dict()

        assert result["remediation"] == "Fix credentials"
        assert result["remediation_zh"] == "修复凭证"
        assert result["details"] == {"key": "value"}
        assert result["trace_id"] == "trace-456"

    def test_str_representation(self):
        """Test string representation / 测试字符串表示"""
        error = StandardErrorResponse(
            error="TestError",
            error_type=ErrorType.NETWORK,
            error_code="NET_001",
            message="Network error",
            message_zh="网络错误",
            severity=ErrorSeverity.ERROR,
            suggestion="Check network",
            suggestion_zh="检查网络",
        )

        str_repr = str(error)
        assert "[network]" in str_repr
        assert "NET_001" in str_repr
        assert "Network error" in str_repr

    def test_repr_representation(self):
        """Test representation / 测试表示"""
        error = StandardErrorResponse(
            error="TestError",
            error_type=ErrorType.ORDER,
            error_code="ORD_001",
            message="Order error",
            message_zh="订单错误",
            severity=ErrorSeverity.ERROR,
            suggestion="Check order",
            suggestion_zh="检查订单",
        )

        repr_str = repr(error)
        assert "StandardErrorResponse" in repr_str
        assert "TestError" in repr_str
        assert "order" in repr_str
        assert "ORD_001" in repr_str
        assert "error" in repr_str

    def test_all_severity_levels(self):
        """Test error response with all severity levels / 测试所有严重程度级别的错误响应"""
        for severity in ErrorSeverity:
            error = StandardErrorResponse(
                error="TestError",
                error_type=ErrorType.UNKNOWN,
                error_code="TEST_001",
                message="Test",
                message_zh="测试",
                severity=severity,
                suggestion="Test",
                suggestion_zh="测试",
            )
            assert error.severity == severity
            assert error.to_dict()["severity"] == severity.value

    def test_all_error_types(self):
        """Test error response with all error types / 测试所有错误类型的错误响应"""
        for error_type in ErrorType:
            error = StandardErrorResponse(
                error="TestError",
                error_type=error_type,
                error_code="TEST_001",
                message="Test",
                message_zh="测试",
                severity=ErrorSeverity.ERROR,
                suggestion="Test",
                suggestion_zh="测试",
            )
            assert error.error_type == error_type
            assert error.to_dict()["error_type"] == error_type.value

