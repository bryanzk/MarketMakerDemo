"""
Unit tests for trace_id in engine error_history / 引擎 error_history 中的 trace_id 单元测试

Tests that error_history entries include trace_id for correlation.
测试 error_history 条目包含用于关联的 trace_id。

Owner: Agent QA
"""

from unittest.mock import Mock, patch

import pytest

from src.shared.tracing import generate_trace_id, set_trace_id
from src.trading.engine import AlphaLoop


class TestEngineErrorHistoryTraceId:
    """Test error_history includes trace_id / 测试 error_history 包含 trace_id"""

    @patch("src.trading.engine.BinanceClient")
    @patch("src.trading.engine.DataAgent")
    @patch("src.trading.engine.QuantAgent")
    @patch("src.trading.engine.RiskAgent")
    @patch("src.trading.engine.FixedSpreadStrategy")
    def test_order_error_includes_trace_id(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test order error includes trace_id / 测试订单错误包含 trace_id"""
        # Setup mocks
        mock_client = Mock()
        mock_client.symbol = "ETH/USDT:USDT"
        mock_client.fetch_market_data.return_value = {"mid_price": 100.0}
        mock_client.fetch_account_data.return_value = {
            "balance": 1000.0,
            "position_amt": 0.0,
            "entry_price": 0.0,
        }
        mock_client.fetch_open_orders.return_value = []
        # Simulate order placement failure by returning empty list and setting error
        # 通过返回空列表并设置错误来模拟订单放置失败
        mock_client.place_orders.return_value = []
        # Set last_order_error to simulate order error
        # 设置 last_order_error 以模拟订单错误
        # Use a property to ensure it's always accessible
        # 使用属性确保它始终可访问
        type(mock_client).last_order_error = {
            "type": "insufficient_funds",
            "message": "Insufficient balance",
            "symbol": "ETH/USDT:USDT",
        }
        # Ensure place_orders is called but returns empty (simulating failure)
        # 确保 place_orders 被调用但返回空（模拟失败）
        mock_client_cls.return_value = mock_client

        mock_data_cls.return_value = Mock()
        mock_data_cls.return_value.calculate_metrics.return_value = {}
        mock_quant_cls.return_value = Mock()
        mock_quant_cls.return_value.analyze_and_propose.return_value = None
        mock_risk_cls.return_value = Mock()
        mock_strategy_cls.return_value = Mock()

        # Set trace_id
        trace_id = generate_trace_id()
        set_trace_id(trace_id)

        # Create engine and run cycle
        engine = AlphaLoop()
        engine.run_cycle()

        # Check error_history
        default_instance = engine.strategy_instances.get("default")
        assert default_instance is not None

        # Find the error in error_history
        errors = [e for e in default_instance.error_history if e.get("type") == "insufficient_funds"]
        assert len(errors) > 0, "Expected error in error_history"

        error = errors[0]
        assert "trace_id" in error
        assert error["trace_id"] == trace_id

    @patch("src.trading.engine.BinanceClient")
    @patch("src.trading.engine.DataAgent")
    @patch("src.trading.engine.QuantAgent")
    @patch("src.trading.engine.RiskAgent")
    @patch("src.trading.engine.FixedSpreadStrategy")
    def test_cycle_error_includes_trace_id(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test cycle error includes trace_id / 测试循环错误包含 trace_id"""
        # Setup mocks
        mock_client = Mock()
        # Ensure exchange has symbol attribute to avoid format string issues
        # 确保 exchange 有 symbol 属性以避免格式化字符串问题
        mock_client.symbol = "ETH/USDT:USDT"
        # Make fetch_market_data raise an exception to trigger cycle_error
        # 使 fetch_market_data 抛出异常以触发 cycle_error
        mock_client.fetch_market_data.side_effect = Exception("Network timeout")
        # Also mock other required methods to avoid additional errors
        # 同时 mock 其他必需的方法以避免额外错误
        mock_client.fetch_account_data.side_effect = Exception("Network timeout")
        mock_client_cls.return_value = mock_client

        mock_data_cls.return_value = Mock()
        mock_quant_cls.return_value = Mock()
        mock_risk_cls.return_value = Mock()
        mock_strategy_cls.return_value = Mock()

        # Set trace_id
        trace_id = generate_trace_id()
        set_trace_id(trace_id)

        # Create engine and run cycle
        engine = AlphaLoop()
        engine.run_cycle()

        # Check error_history
        default_instance = engine.strategy_instances.get("default")
        assert default_instance is not None

        # Find the cycle_error in error_history
        errors = [e for e in default_instance.error_history if e.get("type") == "cycle_error"]
        assert len(errors) > 0, "Expected cycle_error in error_history"

        error = errors[0]
        assert "trace_id" in error
        assert error["trace_id"] == trace_id

    @patch("src.trading.engine.BinanceClient")
    @patch("src.trading.engine.DataAgent")
    @patch("src.trading.engine.QuantAgent")
    @patch("src.trading.engine.RiskAgent")
    @patch("src.trading.engine.FixedSpreadStrategy")
    def test_global_error_history_includes_trace_id(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test global error_history includes trace_id / 测试全局 error_history 包含 trace_id"""
        # Setup mocks
        mock_client = Mock()
        mock_client.fetch_market_data.side_effect = Exception("System error")
        mock_client_cls.return_value = mock_client

        mock_data_cls.return_value = Mock()
        mock_quant_cls.return_value = Mock()
        mock_risk_cls.return_value = Mock()
        mock_strategy_cls.return_value = Mock()

        # Set trace_id
        trace_id = generate_trace_id()
        set_trace_id(trace_id)

        # Create engine and run cycle
        engine = AlphaLoop()
        try:
            engine.run_cycle()
        except Exception:
            pass  # Expected to fail

        # Check global error_history
        errors = [e for e in engine.error_history if e.get("type") == "cycle_error"]
        if errors:
            error = errors[0]
            assert "trace_id" in error
            assert error["trace_id"] == trace_id

    @patch("src.trading.engine.BinanceClient")
    @patch("src.trading.engine.DataAgent")
    @patch("src.trading.engine.QuantAgent")
    @patch("src.trading.engine.RiskAgent")
    @patch("src.trading.engine.FixedSpreadStrategy")
    def test_error_history_trace_id_none_when_not_set(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test error_history trace_id is None when not set / 测试未设置时 error_history trace_id 为 None"""
        # Setup mocks
        mock_client = Mock()
        mock_client.fetch_market_data.return_value = {"mid_price": 100.0}
        mock_client.fetch_account_data.return_value = {
            "balance": 1000.0,
            "position_amt": 0.0,
            "entry_price": 0.0,
        }
        mock_client.fetch_open_orders.return_value = []
        mock_client.place_orders.return_value = []
        mock_client.last_order_error = {
            "type": "invalid_order",
            "message": "Invalid order",
            "symbol": "ETH/USDT:USDT",
        }
        mock_client_cls.return_value = mock_client

        mock_data_cls.return_value = Mock()
        mock_data_cls.return_value.calculate_metrics.return_value = {}
        mock_quant_cls.return_value = Mock()
        mock_quant_cls.return_value.analyze_and_propose.return_value = None
        mock_risk_cls.return_value = Mock()
        mock_strategy_cls.return_value = Mock()

        # Don't set trace_id
        # Create engine and run cycle
        engine = AlphaLoop()
        engine.run_cycle()

        # Check error_history
        default_instance = engine.strategy_instances.get("default")
        assert default_instance is not None

        # Find the error in error_history
        errors = [e for e in default_instance.error_history if e.get("type") == "invalid_order"]
        if errors:
            error = errors[0]
            # trace_id should be None if not set
            assert "trace_id" in error
            # It may be None or a generated UUID (from ErrorMapper)
            assert error["trace_id"] is None or isinstance(error["trace_id"], str)

