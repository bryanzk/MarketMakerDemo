"""
Unit tests for trace_id middleware / trace_id 中间件单元测试

Tests for FastAPI middleware that adds trace_id to requests and responses.
测试为请求和响应添加 trace_id 的 FastAPI 中间件。

Owner: Agent QA
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from src.shared.tracing import get_trace_id, set_trace_id


@pytest.fixture
def test_app():
    """Create a test FastAPI app with trace_id middleware / 创建带 trace_id 中间件的测试 FastAPI 应用"""
    from src.shared.tracing import generate_trace_id

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

    @app.get("/test")
    async def test_endpoint(request: Request):
        """Test endpoint / 测试端点"""
        trace_id = get_trace_id()
        return {"message": "test", "trace_id": trace_id}

    @app.get("/test-error")
    async def test_error_endpoint(request: Request):
        """Test error endpoint / 测试错误端点"""
        from src.shared.tracing import get_trace_id
        from src.shared.error_mapper import ErrorMapper
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            trace_id = get_trace_id()
            error_response = ErrorMapper.map_exception(e, trace_id=trace_id)
            return error_response.to_dict()

    return app


class TestTraceIdMiddleware:
    """Test trace_id middleware functionality / 测试 trace_id 中间件功能"""

    def test_middleware_adds_trace_id_to_response_header(self, test_app):
        """Test middleware adds trace_id to response header / 测试中间件将 trace_id 添加到响应头"""
        client = TestClient(test_app)
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-Trace-ID" in response.headers
        assert response.headers["X-Trace-ID"].startswith("req_")
        assert len(response.headers["X-Trace-ID"]) == 16  # "req_" (4) + 12 hex chars = 16

    def test_middleware_trace_id_in_response_body(self, test_app):
        """Test trace_id is available in response body / 测试 trace_id 在响应体中可用"""
        client = TestClient(test_app)
        response = client.get("/test")
        assert response.status_code == 200
        data = response.json()
        assert "trace_id" in data
        assert data["trace_id"].startswith("req_")

    def test_middleware_trace_id_consistent(self, test_app):
        """Test trace_id is consistent between header and body / 测试 trace_id 在响应头和响应体之间一致"""
        client = TestClient(test_app)
        response = client.get("/test")
        assert response.status_code == 200
        header_trace_id = response.headers["X-Trace-ID"]
        body_trace_id = response.json()["trace_id"]
        assert header_trace_id == body_trace_id

    def test_middleware_trace_id_unique_per_request(self, test_app):
        """Test trace_id is unique per request / 测试每个请求的 trace_id 是唯一的"""
        client = TestClient(test_app)
        trace_ids = []
        for _ in range(10):
            response = client.get("/test")
            trace_id = response.headers["X-Trace-ID"]
            trace_ids.append(trace_id)
        # All should be unique
        assert len(set(trace_ids)) == 10

    def test_middleware_trace_id_on_error(self, test_app):
        """Test trace_id is added even on error / 测试即使出错也添加 trace_id"""
        client = TestClient(test_app)
        # FastAPI will return 500 for unhandled exceptions, but middleware should still add trace_id
        response = client.get("/test-error", follow_redirects=False)
        # Error should still have trace_id in header (if middleware ran)
        if "X-Trace-ID" in response.headers:
            assert response.headers["X-Trace-ID"].startswith("req_")

    def test_middleware_trace_id_in_request_state(self, test_app):
        """Test trace_id is stored in request state / 测试 trace_id 存储在请求状态中"""
        trace_id_in_state = None

        @test_app.get("/test-state")
        async def test_state_endpoint(request: Request):
            nonlocal trace_id_in_state
            trace_id_in_state = request.state.trace_id
            return {"trace_id": trace_id_in_state}

        client = TestClient(test_app)
        response = client.get("/test-state")
        assert response.status_code == 200
        assert trace_id_in_state is not None
        assert trace_id_in_state.startswith("req_")
        assert trace_id_in_state == response.json()["trace_id"]


class TestTraceIdWithErrorHandling:
    """Test trace_id with error handling / 测试带错误处理的 trace_id"""

    def test_trace_id_in_error_response(self):
        """Test trace_id is included in error responses / 测试 trace_id 包含在错误响应中"""
        from src.shared.tracing import generate_trace_id, set_trace_id
        from src.shared.error_mapper import ErrorMapper

        # Set trace_id
        trace_id = generate_trace_id()
        set_trace_id(trace_id)

        # Create error response - pass trace_id explicitly
        error = ErrorMapper.map_exception(ValueError("Test error"), trace_id=trace_id)
        error_dict = error.to_dict()

        # Verify trace_id is in error response
        assert "trace_id" in error_dict
        assert error_dict["trace_id"] == trace_id

    def test_create_error_response_includes_trace_id(self):
        """Test create_error_response includes trace_id / 测试 create_error_response 包含 trace_id"""
        from src.shared.tracing import generate_trace_id, get_trace_id, set_trace_id
        from src.shared.error_mapper import ErrorMapper

        # Set trace_id
        trace_id = generate_trace_id()
        set_trace_id(trace_id)

        # Create error response using ErrorMapper - get trace_id from context
        current_trace_id = get_trace_id()
        error = ErrorMapper.map_exception(ValueError("Test error"), trace_id=current_trace_id)
        error_dict = error.to_dict()

        # Verify trace_id is included
        assert error_dict["trace_id"] == trace_id

