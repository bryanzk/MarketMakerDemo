"""
Contract tests to assert error envelopes per endpoint / 契约测试以断言每个端点的错误信封

Tests that all API endpoints return errors in the standard format.
测试所有 API 端点以标准格式返回错误。

Owner: Agent QA
"""

import pytest
from fastapi.testclient import TestClient

from server import app

client = TestClient(app)


class TestErrorEnvelopeStructure:
    """Test error response envelope structure / 测试错误响应信封结构"""

    def test_error_envelope_has_required_fields(self):
        """Test that error responses include all required fields / 测试错误响应包含所有必需字段"""
        # Try to trigger an error by accessing an invalid endpoint
        # 尝试通过访问无效端点来触发错误
        response = client.get("/api/nonexistent")
        
        # Should return 404, but if it returns JSON, check format
        # 应该返回 404，但如果返回 JSON，检查格式
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            if data.get("error") or not data.get("ok", True):
                required_fields = [
                    "error",
                    "error_type",
                    "message",
                    "message_zh",
                    "trace_id",
                    "timestamp",
                ]
                missing_fields = [field for field in required_fields if field not in data]
                assert (
                    len(missing_fields) == 0
                ), f"Missing required fields / 缺少必需字段: {missing_fields}"

    def test_success_envelope_includes_trace_id(self):
        """Test that success responses include trace_id / 测试成功响应包含 trace_id"""
        response = client.get("/api/bot/status")
        
        if response.status_code == 200:
            data = response.json()
            # Check if trace_id is in response body or header
            # 检查 trace_id 是否在响应体或响应头中
            has_trace_id = (
                "trace_id" in data or "X-Trace-ID" in response.headers
            )
            assert (
                has_trace_id
            ), "Success response should include trace_id / 成功响应应包含 trace_id"

    def test_error_response_has_trace_id_in_header(self):
        """Test that error responses include trace_id in header / 测试错误响应在响应头中包含 trace_id"""
        response = client.get("/api/nonexistent")
        
        # Check for X-Trace-ID header
        # 检查 X-Trace-ID 响应头
        assert (
            "X-Trace-ID" in response.headers
        ), "Response should include X-Trace-ID header / 响应应包含 X-Trace-ID 响应头"
        
        trace_id = response.headers["X-Trace-ID"]
        assert trace_id.startswith(
            "req_"
        ), f"Trace ID should start with 'req_': {trace_id} / Trace ID 应以 'req_' 开头: {trace_id}"

    def test_error_response_has_trace_id_in_body(self):
        """Test that error responses include trace_id in body / 测试错误响应在响应体中包含 trace_id"""
        # Try to trigger an error
        # 尝试触发错误
        response = client.get("/api/hyperliquid/status")
        
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            # If it's an error response, check for trace_id
            # 如果是错误响应，检查 trace_id
            if data.get("error") or not data.get("ok", True):
                assert (
                    "trace_id" in data
                ), "Error response should include trace_id in body / 错误响应应在响应体中包含 trace_id"
                assert (
                    data["trace_id"] is not None
                ), "Trace ID should not be None / Trace ID 不应为 None"

    def test_error_response_has_bilingual_messages(self):
        """Test that error responses include bilingual messages / 测试错误响应包含双语消息"""
        response = client.get("/api/nonexistent")
        
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            if data.get("error") or not data.get("ok", True):
                assert (
                    "message" in data
                ), "Error response should include 'message' field / 错误响应应包含 'message' 字段"
                assert (
                    "message_zh" in data
                ), "Error response should include 'message_zh' field / 错误响应应包含 'message_zh' 字段"

    def test_error_response_has_timestamp(self):
        """Test that error responses include timestamp / 测试错误响应包含时间戳"""
        response = client.get("/api/nonexistent")
        
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            if data.get("error") or not data.get("ok", True):
                assert (
                    "timestamp" in data
                ), "Error response should include 'timestamp' field / 错误响应应包含 'timestamp' 字段"
                assert (
                    isinstance(data["timestamp"], (int, float))
                ), "Timestamp should be numeric / 时间戳应为数字"

    def test_error_response_has_error_type(self):
        """Test that error responses include error_type / 测试错误响应包含 error_type"""
        response = client.get("/api/nonexistent")
        
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            if data.get("error") or not data.get("ok", True):
                assert (
                    "error_type" in data
                ), "Error response should include 'error_type' field / 错误响应应包含 'error_type' 字段"
                assert (
                    isinstance(data["error_type"], str)
                ), "Error type should be a string / 错误类型应为字符串"

    def test_hyperliquid_status_endpoint_format(self):
        """Test /api/hyperliquid/status endpoint response format / 测试 /api/hyperliquid/status 端点响应格式"""
        response = client.get("/api/hyperliquid/status")
        
        assert response.status_code in [
            200,
            500,
        ], f"Unexpected status code / 意外状态码: {response.status_code}"
        
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            
            # Check for trace_id
            # 检查 trace_id
            assert (
                "trace_id" in data or "X-Trace-ID" in response.headers
            ), "Response should include trace_id / 响应应包含 trace_id"
            
            # If error, check error format
            # 如果是错误，检查错误格式
            if data.get("error") or not data.get("ok", True):
                required_fields = [
                    "error",
                    "error_type",
                    "message",
                    "message_zh",
                    "trace_id",
                ]
                for field in required_fields:
                    assert (
                        field in data
                    ), f"Error response missing field / 错误响应缺少字段: {field}"

    def test_bot_status_endpoint_format(self):
        """Test /api/status endpoint response format / 测试 /api/status 端点响应格式"""
        # Use actual endpoint /api/status / 使用实际端点 /api/status
        response = client.get("/api/status")
        
        assert response.status_code == 200, f"Unexpected status code / 意外状态码: {response.status_code}"
        
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            
            # Check for trace_id
            # 检查 trace_id
            assert (
                "trace_id" in data or "X-Trace-ID" in response.headers
            ), "Response should include trace_id / 响应应包含 trace_id"
            
            # Check for errors field (if implemented)
            # 检查 errors 字段（如果已实现）
            if "errors" in data:
                errors = data["errors"]
                assert isinstance(
                    errors, dict
                ), "Errors field should be a dictionary / errors 字段应为字典"

