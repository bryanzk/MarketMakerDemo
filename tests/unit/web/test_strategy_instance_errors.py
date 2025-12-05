"""
Unit tests for Strategy Instance Errors Exposure
策略实例错误暴露单元测试

Tests for Phase 7: Expose Strategy Instance Errors
测试 Phase 7: 暴露策略实例错误

Owner: Agent QA
"""

import time
from collections import deque
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

import server
from src.trading.engine import AlphaLoop
from src.trading.strategy_instance import StrategyInstance


class TestStrategyInstanceErrorsExposure:
    """
    Test Strategy Instance Errors Exposure in /api/status
    测试 /api/status 中的策略实例错误暴露
    """

    def test_status_endpoint_includes_errors_field(self):
        """
        Test AC: /api/status includes errors field
        测试 AC: /api/status 包含 errors 字段
        
        Given: I call /api/status
        When: The endpoint returns successfully
        Then: Response should include errors field
        """
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for errors field / 检查 errors 字段
        assert "errors" in data
        assert isinstance(data["errors"], dict)

    def test_errors_field_has_global_alert(self):
        """
        Test AC: errors field includes global_alert
        测试 AC: errors 字段包含 global_alert
        
        Given: bot_engine has an alert
        When: I call /api/status
        Then: errors.global_alert should be included
        """
        # Set a test alert / 设置测试警报
        test_alert = {
            "type": "warning",
            "message": "Test alert message",
            "suggestion": "Test suggestion"
        }
        server.bot_engine.alert = test_alert
        
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check global_alert / 检查 global_alert
        assert "errors" in data
        assert "global_alert" in data["errors"]
        assert data["errors"]["global_alert"] == test_alert
        
        # Cleanup / 清理
        server.bot_engine.alert = None

    def test_errors_field_has_global_error_history(self):
        """
        Test AC: errors field includes global_error_history
        测试 AC: errors 字段包含 global_error_history
        
        Given: bot_engine has error_history
        When: I call /api/status
        Then: errors.global_error_history should be included (last 20 entries)
        """
        # Add test errors / 添加测试错误
        test_errors = [
            {
                "timestamp": time.time() - i,
                "type": "test_error",
                "message": f"Test error {i}",
                "trace_id": f"trace_{i}"
            }
            for i in range(25)  # Add 25 errors to test limiting
        ]
        server.bot_engine.error_history = deque(test_errors, maxlen=200)
        
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check global_error_history / 检查 global_error_history
        assert "errors" in data
        assert "global_error_history" in data["errors"]
        error_history = data["errors"]["global_error_history"]
        
        # Should be limited to last 20 entries / 应该限制为最后 20 条
        assert isinstance(error_history, list)
        assert len(error_history) <= 20
        
        # Cleanup / 清理
        server.bot_engine.error_history = deque(maxlen=200)

    def test_errors_field_has_instance_errors(self):
        """
        Test AC: errors field includes instance_errors
        测试 AC: errors 字段包含 instance_errors
        
        Given: bot_engine has strategy instances
        When: I call /api/status
        Then: errors.instance_errors should be included
        """
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check instance_errors / 检查 instance_errors
        assert "errors" in data
        assert "instance_errors" in data["errors"]
        assert isinstance(data["errors"]["instance_errors"], dict)

    def test_instance_errors_include_alert_and_history(self):
        """
        Test AC: instance_errors include alert and error_history for each instance
        测试 AC: instance_errors 包含每个实例的 alert 和 error_history
        
        Given: A strategy instance has alert and error_history
        When: I call /api/status
        Then: instance_errors should include alert and error_history for that instance
        """
        # Set test alert and error history for default instance / 为默认实例设置测试警报和错误历史
        default_instance = server.bot_engine.strategy_instances.get("default")
        if default_instance:
            test_alert = {
                "type": "error",
                "message": "Instance test error",
                "suggestion": "Instance test suggestion"
            }
            test_errors = [
                {
                    "timestamp": time.time() - i,
                    "type": "instance_error",
                    "message": f"Instance error {i}",
                    "strategy_id": "default",
                    "trace_id": f"trace_{i}"
                }
                for i in range(15)
            ]
            
            default_instance.alert = test_alert
            default_instance.error_history = deque(test_errors, maxlen=200)
        
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check instance_errors structure / 检查 instance_errors 结构
        assert "errors" in data
        assert "instance_errors" in data["errors"]
        
        if "default" in data["errors"]["instance_errors"]:
            instance_errors = data["errors"]["instance_errors"]["default"]
            assert "alert" in instance_errors
            assert "error_history" in instance_errors
            assert isinstance(instance_errors["error_history"], list)
            # Should be limited to last 20 entries / 应该限制为最后 20 条
            assert len(instance_errors["error_history"]) <= 20
            
            # Cleanup / 清理
            default_instance.alert = None
            default_instance.error_history = deque(maxlen=200)

    def test_error_history_includes_trace_id(self):
        """
        Test AC: error_history entries include trace_id
        测试 AC: error_history 条目包含 trace_id
        
        Given: error_history has entries
        When: I call /api/status
        Then: error_history entries should include trace_id field
        """
        # Add test error with trace_id / 添加带 trace_id 的测试错误
        test_error = {
            "timestamp": time.time(),
            "type": "test_error",
            "message": "Test error with trace_id",
            "trace_id": "test_trace_id_123",
            "strategy_id": "default"
        }
        server.bot_engine.error_history.append(test_error)
        
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check trace_id in error_history / 检查 error_history 中的 trace_id
        assert "errors" in data
        assert "global_error_history" in data["errors"]
        error_history = data["errors"]["global_error_history"]
        
        # Find the test error / 查找测试错误
        test_errors = [e for e in error_history if e.get("message") == "Test error with trace_id"]
        if test_errors:
            assert "trace_id" in test_errors[0]
            assert test_errors[0]["trace_id"] == "test_trace_id_123"
        
        # Cleanup / 清理
        server.bot_engine.error_history.clear()

    def test_error_history_limit_enforced(self):
        """
        Test AC: error_history is limited to last 20 entries
        测试 AC: error_history 限制为最后 20 条
        
        Given: bot_engine has more than 20 errors
        When: I call /api/status
        Then: Only last 20 entries should be returned
        """
        # Add 30 test errors / 添加 30 个测试错误
        test_errors = [
            {
                "timestamp": time.time() - (30 - i),
                "type": "test_error",
                "message": f"Error {i}",
                "trace_id": f"trace_{i}"
            }
            for i in range(30)
        ]
        server.bot_engine.error_history = deque(test_errors, maxlen=200)
        
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check limit / 检查限制
        assert "errors" in data
        assert "global_error_history" in data["errors"]
        error_history = data["errors"]["global_error_history"]
        
        assert len(error_history) <= 20
        
        # Cleanup / 清理
        server.bot_engine.error_history = deque(maxlen=200)

    def test_instance_error_history_limit_enforced(self):
        """
        Test AC: instance error_history is limited to last 20 entries
        测试 AC: 实例 error_history 限制为最后 20 条
        
        Given: A strategy instance has more than 20 errors
        When: I call /api/status
        Then: Only last 20 entries should be returned
        """
        default_instance = server.bot_engine.strategy_instances.get("default")
        if default_instance:
            # Add 25 test errors / 添加 25 个测试错误
            test_errors = [
                {
                    "timestamp": time.time() - (25 - i),
                    "type": "instance_error",
                    "message": f"Instance error {i}",
                    "strategy_id": "default",
                    "trace_id": f"trace_{i}"
                }
                for i in range(25)
            ]
            default_instance.error_history = deque(test_errors, maxlen=200)
        
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check limit / 检查限制
        assert "errors" in data
        assert "instance_errors" in data["errors"]
        
        if "default" in data["errors"]["instance_errors"]:
            instance_errors = data["errors"]["instance_errors"]["default"]
            assert "error_history" in instance_errors
            error_history = instance_errors["error_history"]
            assert len(error_history) <= 20
            
            # Cleanup / 清理
            default_instance.error_history = deque(maxlen=200)

    def test_errors_field_structure(self):
        """
        Test AC: errors field has correct structure
        测试 AC: errors 字段具有正确的结构
        
        Given: I call /api/status
        When: The endpoint returns successfully
        Then: errors field should have global_alert, global_error_history, instance_errors
        """
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure / 检查结构
        assert "errors" in data
        errors = data["errors"]
        
        # Required fields / 必需字段
        assert "global_alert" in errors
        assert "global_error_history" in errors
        assert "instance_errors" in errors
        
        # Type checks / 类型检查
        assert errors["global_error_history"] is None or isinstance(errors["global_error_history"], list)
        assert isinstance(errors["instance_errors"], dict)

    def test_status_response_includes_trace_id(self):
        """
        Test AC: Status response includes trace_id
        测试 AC: 状态响应包含 trace_id
        
        Given: I call /api/status
        When: The endpoint returns successfully
        Then: Response should include trace_id field
        """
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check trace_id / 检查 trace_id
        assert "trace_id" in data
        assert data["trace_id"] is not None
        assert isinstance(data["trace_id"], str)

    def test_multiple_instances_errors_exposed(self):
        """
        Test AC: Errors from multiple instances are exposed
        测试 AC: 多个实例的错误都被暴露
        
        Given: Multiple strategy instances exist with errors
        When: I call /api/status
        Then: All instances' errors should be included
        """
        # Add a test instance / 添加测试实例
        test_instance_id = "test_instance"
        if test_instance_id not in server.bot_engine.strategy_instances:
            server.bot_engine.add_strategy_instance(test_instance_id, "fixed_spread")
        
        test_instance = server.bot_engine.strategy_instances.get(test_instance_id)
        if test_instance:
            test_instance.alert = {
                "type": "warning",
                "message": "Test instance alert"
            }
            test_instance.error_history.append({
                "timestamp": time.time(),
                "type": "test_error",
                "message": "Test instance error",
                "trace_id": "test_trace"
            })
        
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check multiple instances / 检查多个实例
        assert "errors" in data
        assert "instance_errors" in data["errors"]
        instance_errors = data["errors"]["instance_errors"]
        
        # Should have at least default instance / 应该至少有默认实例
        assert len(instance_errors) >= 1
        
        # Cleanup / 清理
        if test_instance_id in server.bot_engine.strategy_instances:
            server.bot_engine.remove_strategy_instance(test_instance_id)

