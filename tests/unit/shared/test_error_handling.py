#!/usr/bin/env python3
"""
Unit tests for error handling module / 错误处理模块单元测试

Tests error response format and trace_id handling in API endpoints.
测试 API 端点中的错误响应格式和 trace_id 处理。

Owner: Agent QA
"""

import pytest
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:3000"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/hyperliquid/status",
        "/api/status",
        "/api/hyperliquid/connection",
    ],
)
def test_error_response_format(endpoint: str):
    """
    Test error response follows standard format / 测试错误响应遵循标准格式
    
    Args:
        endpoint: API endpoint to test / 要测试的 API 端点
    """
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        data = response.json()
        
        # Check if it's an error response / 检查是否是错误响应
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
                not missing_fields
            ), f"{endpoint}: Missing fields / 缺少字段: {missing_fields}"
        else:
            # Success response should have trace_id / 成功响应应包含 trace_id
            assert (
                "trace_id" in data or "X-Trace-ID" in response.headers
            ), f"{endpoint}: Success response missing trace_id / 成功响应缺少 trace_id"
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Server not available / 服务器不可用: {e}")


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/hyperliquid/status",
        "/api/status",
        "/api/hyperliquid/connection",
    ],
)
def test_trace_id_in_header(endpoint: str):
    """
    Test trace_id in response header / 测试响应头中的 trace_id
    
    Args:
        endpoint: API endpoint to test / 要测试的 API 端点
    """
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        
        assert (
            "X-Trace-ID" in response.headers
        ), f"{endpoint}: X-Trace-ID header missing / X-Trace-ID 响应头缺失"
        
        trace_id = response.headers["X-Trace-ID"]
        assert trace_id, f"{endpoint}: X-Trace-ID header is empty / X-Trace-ID 响应头为空"
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Server not available / 服务器不可用: {e}")


def test_bot_status_errors():
    """Test bot status includes error information / 测试 bot 状态包含错误信息"""
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        data = response.json()
        
        assert (
            "errors" in data
        ), "/api/status: Error information missing / 错误信息缺失"
        
        errors = data["errors"]
        assert isinstance(
            errors, dict
        ), "/api/status: errors should be a dict / errors 应该是字典"
        
        # Verify errors structure / 验证 errors 结构
        assert (
            "global_alert" in errors
        ), "/api/status: errors should have global_alert field / errors 应该有 global_alert 字段"
        assert (
            "global_error_history" in errors
        ), "/api/status: errors should have global_error_history field / errors 应该有 global_error_history 字段"
        assert (
            "instance_errors" in errors
        ), "/api/status: errors should have instance_errors field / errors 应该有 instance_errors 字段"
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Server not available / 服务器不可用: {e}")


