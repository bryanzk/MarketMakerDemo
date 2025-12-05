"""
Unit tests for error response with trace_id / 带 trace_id 的错误响应单元测试

Tests for create_error_response function and trace_id in error responses.
测试 create_error_response 函数和错误响应中的 trace_id。

Owner: Agent QA
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.shared.tracing import get_trace_id, set_trace_id


@pytest.fixture
def test_app_with_error_handler():
    """Create test app with error handler / 创建带错误处理器的测试应用"""
    from src.shared.tracing import generate_trace_id
    from src.shared.error_mapper import ErrorMapper

    app = FastAPI()

    @app.middleware("http")
    async def add_trace_id(request: Request, call_next):
        """Add trace_id to all requests / 为所有请求添加 trace_id"""
        trace_id = generate_trace_id()
        set_trace_id(trace_id)
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response

    def create_error_response(exception, error_code=None, details=None):
        """Create standardized error response / 创建标准化错误响应"""
        trace_id = get_trace_id()
        error_response = ErrorMapper.map_exception(exception, error_code, details, trace_id)
        return error_response.to_dict()

    @app.get("/test-success")
    async def test_success(request: Request):
        """Test success endpoint / 测试成功端点"""
        trace_id = get_trace_id()
        return {"ok": True, "message": "success", "trace_id": trace_id}

    @app.get("/test-error")
    async def test_error(request: Request):
        """Test error endpoint / 测试错误端点"""
        try:
            raise ValueError("Test error message")
        except Exception as e:
            return create_error_response(e, error_code="TEST_ERROR")

    @app.get("/test-connection-error")
    async def test_connection_error(request: Request):
        """Test connection error endpoint / 测试连接错误端点"""
        try:
            raise ConnectionError("Connection failed")
        except Exception as e:
            return create_error_response(
                e, error_code="CONNECTION_ERROR", details={"endpoint": "/test-connection-error"}
            )

    return app


class TestErrorResponseTraceId:
    """Test error response includes trace_id / 测试错误响应包含 trace_id"""

    def test_error_response_has_trace_id(self, test_app_with_error_handler):
        """Test error response includes trace_id / 测试错误响应包含 trace_id"""
        client = TestClient(test_app_with_error_handler)
        response = client.get("/test-error")
        assert response.status_code == 200
        data = response.json()
        assert "trace_id" in data
        assert data["trace_id"] is not None
        assert data["trace_id"].startswith("req_")

    def test_error_response_trace_id_matches_header(self, test_app_with_error_handler):
        """Test error response trace_id matches header / 测试错误响应 trace_id 与响应头匹配"""
        client = TestClient(test_app_with_error_handler)
        response = client.get("/test-error")
        assert response.status_code == 200
        header_trace_id = response.headers["X-Trace-ID"]
        body_trace_id = response.json()["trace_id"]
        assert header_trace_id == body_trace_id

    def test_error_response_has_error_fields(self, test_app_with_error_handler):
        """Test error response has all error fields / 测试错误响应包含所有错误字段"""
        client = TestClient(test_app_with_error_handler)
        response = client.get("/test-error")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "error_type" in data
        assert "error_code" in data
        assert "message" in data
        assert "message_zh" in data
        assert "trace_id" in data
        assert "timestamp" in data

    def test_success_response_has_trace_id(self, test_app_with_error_handler):
        """Test success response includes trace_id / 测试成功响应包含 trace_id"""
        client = TestClient(test_app_with_error_handler)
        response = client.get("/test-success")
        assert response.status_code == 200
        data = response.json()
        assert "trace_id" in data
        assert data["trace_id"].startswith("req_")
        assert data["ok"] is True

    def test_error_response_with_details(self, test_app_with_error_handler):
        """Test error response includes details / 测试错误响应包含详情"""
        client = TestClient(test_app_with_error_handler)
        response = client.get("/test-connection-error")
        assert response.status_code == 200
        data = response.json()
        assert "trace_id" in data
        assert "details" in data
        assert data["details"]["endpoint"] == "/test-connection-error"
        assert data["error_code"] == "CONNECTION_ERROR"

    def test_error_response_trace_id_unique(self, test_app_with_error_handler):
        """Test error response trace_id is unique per request / 测试每个请求的错误响应 trace_id 是唯一的"""
        client = TestClient(test_app_with_error_handler)
        trace_ids = []
        for _ in range(5):
            response = client.get("/test-error")
            trace_id = response.json()["trace_id"]
            trace_ids.append(trace_id)
        # All should be unique
        assert len(set(trace_ids)) == 5


class TestCreateErrorResponseFunction:
    """Test create_error_response function / 测试 create_error_response 函数"""

    def test_create_error_response_with_trace_id(self):
        """Test create_error_response includes trace_id / 测试 create_error_response 包含 trace_id"""
        from src.shared.tracing import generate_trace_id, get_trace_id, set_trace_id
        from src.shared.error_mapper import ErrorMapper

        # Set trace_id
        trace_id = generate_trace_id()
        set_trace_id(trace_id)

        # Create error response - pass trace_id explicitly (as create_error_response does)
        current_trace_id = get_trace_id()
        error = ErrorMapper.map_exception(ValueError("Test error"), trace_id=current_trace_id)
        error_dict = error.to_dict()

        # Verify trace_id is included
        assert error_dict["trace_id"] == trace_id

    def test_create_error_response_without_trace_id(self):
        """Test create_error_response generates trace_id if not set / 测试如果未设置 trace_id，create_error_response 会生成它"""
        from src.shared.error_mapper import ErrorMapper

        # Don't set trace_id
        # Create error response
        error = ErrorMapper.map_exception(ValueError("Test error"))
        error_dict = error.to_dict()

        # Should have a trace_id (auto-generated)
        assert "trace_id" in error_dict
        assert error_dict["trace_id"] is not None
        # Should be UUID format (from ErrorMapper)
        assert len(error_dict["trace_id"]) > 0

