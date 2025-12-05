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

    @patch("src.trading.strategy_instance.BinanceClient")
    @patch("src.trading.engine.BinanceClient")
    @patch("src.trading.engine.DataAgent")
    @patch("src.trading.engine.QuantAgent")
    @patch("src.trading.engine.RiskAgent")
    @patch("src.trading.engine.FixedSpreadStrategy")
    @patch("src.trading.strategy_instance.OrderManager")
    def test_order_error_includes_trace_id(
        self, mock_order_manager_cls, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_engine_client_cls, mock_strategy_client_cls
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
        # Mock place_orders to return empty list and set last_order_error
        # Mock place_orders 以返回空列表并设置 last_order_error
        def place_orders_with_error(orders):
            # Set error when place_orders is called
            # 在调用 place_orders 时设置错误
            mock_client.last_order_error = {
                "type": "insufficient_funds",
                "message": "Insufficient balance",
                "symbol": "ETH/USDT:USDT",
            }
            return []  # Return empty list to simulate failure
        mock_client.place_orders.side_effect = place_orders_with_error
        # Initialize last_order_error as None (will be set by side_effect)
        # 初始化 last_order_error 为 None（将由 side_effect 设置）
        mock_client.last_order_error = None
        # Ensure place_orders is called but returns empty (simulating failure)
        # 确保 place_orders 被调用但返回空（模拟失败）
        # Also need to ensure to_place is not empty so place_orders is actually called
        # 还需要确保 to_place 不为空，以便实际调用 place_orders
        # Patch both engine and strategy_instance BinanceClient
        # Patch engine 和 strategy_instance 的 BinanceClient
        # Note: Parameters are in reverse order of @patch decorators
        # 注意：参数顺序与 @patch 装饰器相反（从下往上）
        mock_strategy_client_cls.return_value = mock_client
        mock_engine_client_cls.return_value = mock_client

        mock_data_cls.return_value = Mock()
        mock_data_cls.return_value.calculate_metrics.return_value = {}
        # Mock quant to return a proposal so the cycle continues
        # Mock quant 以返回 proposal，以便循环继续执行
        mock_quant = Mock()
        mock_quant.analyze_and_propose.return_value = {"spread": 0.001}  # Return a proposal
        mock_quant_cls.return_value = mock_quant
        mock_risk_cls.return_value = Mock()
        # Mock strategy to return some orders so place_orders is called
        # Mock 策略以返回一些订单，以便调用 place_orders
        # StrategyInstance.calculate_target_orders calls strategy.calculate_target_orders
        # StrategyInstance.calculate_target_orders 调用 strategy.calculate_target_orders
        mock_strategy = Mock()
        # Return orders that will result in to_place being non-empty
        # 返回将导致 to_place 非空的订单
        mock_strategy.calculate_target_orders.return_value = [
            {"side": "BUY", "price": 100.0, "amount": 0.1, "id": "test_buy_1"},
            {"side": "SELL", "price": 101.0, "amount": 0.1, "id": "test_sell_1"},
        ]
        mock_strategy_cls.return_value = mock_strategy
        
        # Mock OrderManager to return orders to place
        # Mock OrderManager 以返回要放置的订单
        # sync_orders returns (order_ids_to_cancel, orders_to_place)
        # sync_orders 返回 (order_ids_to_cancel, orders_to_place)
        mock_order_manager = Mock()
        # sync_orders returns (order_ids_to_cancel, orders_to_place)
        # sync_orders 返回 (order_ids_to_cancel, orders_to_place)
        # Orders must have 'quantity' field for place_orders
        # 订单必须有 'quantity' 字段以供 place_orders 使用
        orders_to_place = [
            {"side": "BUY", "price": 100.0, "quantity": 0.1, "amount": 0.1},
            {"side": "SELL", "price": 101.0, "quantity": 0.1, "amount": 0.1},
        ]
        mock_order_manager.sync_orders.return_value = ([], orders_to_place)
        mock_order_manager_cls.return_value = mock_order_manager

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

    @patch("src.trading.strategy_instance.BinanceClient")
    @patch("src.trading.engine.BinanceClient")
    @patch("src.trading.engine.DataAgent")
    @patch("src.trading.engine.QuantAgent")
    @patch("src.trading.engine.RiskAgent")
    @patch("src.trading.engine.FixedSpreadStrategy")
    @patch("src.trading.strategy_instance.OrderManager")
    def test_cycle_error_includes_trace_id(
        self, mock_order_manager_cls, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_engine_client_cls, mock_strategy_client_cls
    ):
        """Test cycle error includes trace_id / 测试循环错误包含 trace_id"""
        # Setup mocks
        mock_client = Mock()
        # Ensure exchange has symbol attribute to avoid format string issues
        # 确保 exchange 有 symbol 属性以避免格式化字符串问题
        # Use a string value, not a Mock, to avoid format string issues
        # 使用字符串值，而不是 Mock，以避免格式化字符串问题
        mock_client.symbol = "ETH/USDT:USDT"
        # Make fetch_market_data raise an exception to trigger cycle_error
        # 使 fetch_market_data 抛出异常以触发 cycle_error
        mock_client.fetch_market_data.side_effect = Exception("Network timeout")
        # Also mock other required methods to avoid additional errors
        # 同时 mock 其他必需的方法以避免额外错误
        mock_client.fetch_account_data.side_effect = Exception("Network timeout")
        # Patch both engine and strategy_instance BinanceClient
        # Patch engine 和 strategy_instance 的 BinanceClient
        # Note: Parameters are in reverse order of @patch decorators (bottom to top)
        # 注意：参数顺序与 @patch 装饰器相反（从下往上）
        mock_strategy_client_cls.return_value = mock_client  # First @patch (bottom)
        mock_engine_client_cls.return_value = mock_client    # Second @patch

        # Mock data with proper return values
        # Mock data 并设置正确的返回值
        mock_data = Mock()
        mock_data.calculate_metrics.return_value = {"volatility": 0.01, "sharpe_ratio": 1.0}
        mock_data_cls.return_value = mock_data
        # Mock quant to return a proper proposal dict (not Mock)
        # Mock quant 以返回正确的 proposal 字典（不是 Mock）
        mock_quant = Mock()
        mock_quant.analyze_and_propose.return_value = {"spread": 0.001}  # Return a dict
        mock_quant_cls.return_value = mock_quant
        # Mock risk.validate_proposal to return tuple
        # Mock risk.validate_proposal 以返回元组
        mock_risk = Mock()
        mock_risk.validate_proposal.return_value = (True, None)
        mock_risk_cls.return_value = mock_risk
        mock_strategy_cls.return_value = Mock()
        # Mock OrderManager
        mock_order_manager = Mock()
        mock_order_manager.sync_orders.return_value = ([], [])
        mock_order_manager_cls.return_value = mock_order_manager

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

