"""
Unit tests for market context volatility calculation
市场上下文波动率计算单元测试

Tests verify that _prepare_market_context_for_evaluation uses dynamic volatility calculation.
测试验证 _prepare_market_context_for_evaluation 使用动态波动率计算。

Owner: Agent QA
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import server
from src.ai.evaluation.schemas import MarketContext
from src.trading.hyperliquid_client import HyperliquidClient


class TestMarketContextVolatility:
    """Test market context volatility calculation / 测试市场上下文波动率计算"""

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    @patch("server._check_exchange_connection")
    @patch("src.trading.volatility.calculate_volatility_1h_24h")
    def test_prepare_market_context_uses_dynamic_volatility(
        self,
        mock_calculate_volatility,
        mock_check_connection,
        mock_bot_engine,
        mock_get_exchange,
    ):
        """
        Test that _prepare_market_context_for_evaluation uses dynamic volatility calculation
        测试 _prepare_market_context_for_evaluation 使用动态波动率计算
        """
        # Setup mocks / 设置模拟
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.is_connected = True
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 2500.0,
            "best_bid": 2499.5,
            "best_ask": 2500.5,
            "funding_rate": 0.0001,
            "timestamp": 1000000,
        }
        mock_exchange.fetch_account_data.return_value = {
            "balance": 10000.0,
            "position_amt": 0.0,
            "leverage": 1.0,
            "unrealizedProfit": 0.0,
        }
        mock_get_exchange.return_value = mock_exchange
        mock_check_connection.return_value = (True, None, None)

        # Mock volatility calculation to return specific values
        # 模拟波动率计算返回特定值
        mock_calculate_volatility.return_value = (0.015, 0.035)  # 1h=1.5%, 24h=3.5%

        # Mock bot_engine for historical metrics
        # 模拟 bot_engine 用于历史指标
        mock_bot_engine.data = MagicMock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.2}
        mock_bot_engine.data.trade_history = []

        # Call the function / 调用函数
        symbol = "ETH/USDC:USDC"
        exchange_name = "hyperliquid"
        trace_id = "test-trace-001"

        context, error, status_code = asyncio.run(
            server._prepare_market_context_for_evaluation(symbol, exchange_name, trace_id)
        )

        # Verify results / 验证结果
        assert context is not None, "Context should not be None"
        assert error is None, "Error should be None"
        assert status_code is None, "Status code should be None"

        # Verify volatility calculation was called / 验证波动率计算被调用
        mock_calculate_volatility.assert_called_once()
        call_args = mock_calculate_volatility.call_args
        assert call_args[0][0] == mock_exchange, "Exchange should be passed"
        assert call_args[0][1] == symbol, "Symbol should be passed"
        assert "calculator" in call_args[1], "Calculator should be passed"

        # Verify volatility values in context / 验证上下文中的波动率值
        assert context.volatility_1h == 0.015, "1h volatility should be 1.5%"
        assert context.volatility_24h == 0.035, "24h volatility should be 3.5%"

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    @patch("server._check_exchange_connection")
    @patch("src.trading.volatility.calculate_volatility_1h_24h")
    def test_prepare_market_context_fallback_to_default_volatility(
        self,
        mock_calculate_volatility,
        mock_check_connection,
        mock_bot_engine,
        mock_get_exchange,
    ):
        """
        Test that _prepare_market_context_for_evaluation uses default volatility when calculation fails
        测试当波动率计算失败时，_prepare_market_context_for_evaluation 使用默认波动率
        """
        # Setup mocks / 设置模拟
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.is_connected = True
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 2500.0,
            "best_bid": 2499.5,
            "best_ask": 2500.5,
            "funding_rate": 0.0001,
            "timestamp": 1000000,
        }
        mock_exchange.fetch_account_data.return_value = {
            "balance": 10000.0,
            "position_amt": 0.0,
            "leverage": 1.0,
            "unrealizedProfit": 0.0,
        }
        mock_get_exchange.return_value = mock_exchange
        mock_check_connection.return_value = (True, None, None)

        # Mock volatility calculation to raise exception
        # 模拟波动率计算抛出异常
        mock_calculate_volatility.side_effect = Exception("Volatility calculation failed")

        # Mock bot_engine for historical metrics
        # 模拟 bot_engine 用于历史指标
        mock_bot_engine.data = MagicMock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.2}
        mock_bot_engine.data.trade_history = []

        # Call the function / 调用函数
        symbol = "ETH/USDC:USDC"
        exchange_name = "hyperliquid"
        trace_id = "test-trace-002"

        context, error, status_code = asyncio.run(
            server._prepare_market_context_for_evaluation(symbol, exchange_name, trace_id)
        )

        # Verify results / 验证结果
        assert context is not None, "Context should not be None (should use defaults)"
        assert error is None, "Error should be None (exception should be caught)"
        assert status_code is None, "Status code should be None"

        # Verify default volatility values are used / 验证使用默认波动率值
        assert context.volatility_1h == 0.01, "1h volatility should be default 1%"
        assert context.volatility_24h == 0.03, "24h volatility should be default 3%"

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    @patch("server._check_exchange_connection")
    @patch("src.trading.volatility.calculate_volatility_1h_24h")
    def test_prepare_market_context_volatility_when_exchange_not_found(
        self,
        mock_calculate_volatility,
        mock_check_connection,
        mock_bot_engine,
        mock_get_exchange,
    ):
        """
        Test that _prepare_market_context_for_evaluation uses default volatility when exchange is not found
        测试当找不到 exchange 时，_prepare_market_context_for_evaluation 使用默认波动率
        """
        # Setup mocks / 设置模拟
        # Return None for exchange (exchange not found)
        # 返回 None 表示找不到 exchange
        mock_get_exchange.return_value = None
        mock_check_connection.return_value = (False, {"error": "Exchange not found"}, 404)

        # Call the function / 调用函数
        symbol = "ETH/USDC:USDC"
        exchange_name = "nonexistent"
        trace_id = "test-trace-003"

        context, error, status_code = asyncio.run(
            server._prepare_market_context_for_evaluation(symbol, exchange_name, trace_id)
        )

        # Should return error before volatility calculation
        # 应该在波动率计算之前返回错误
        assert context is None, "Context should be None when exchange not found"
        assert error is not None, "Error should be present when exchange not found"
        assert status_code == 404, "Status code should be 404"

        # Volatility calculation should not be called
        # 波动率计算不应该被调用
        mock_calculate_volatility.assert_not_called()

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    @patch("server._check_exchange_connection")
    @patch("src.trading.volatility.VolatilityCalculator")
    @patch("src.trading.volatility.calculate_volatility_1h_24h")
    def test_prepare_market_context_volatility_caching(
        self,
        mock_calculate_volatility,
        mock_volatility_calculator,
        mock_check_connection,
        mock_bot_engine,
        mock_get_exchange,
    ):
        """
        Test that _prepare_market_context_for_evaluation uses VolatilityCalculator with caching
        测试 _prepare_market_context_for_evaluation 使用带缓存的 VolatilityCalculator
        """
        # Setup mocks / 设置模拟
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.is_connected = True
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 2500.0,
            "best_bid": 2499.5,
            "best_ask": 2500.5,
            "funding_rate": 0.0001,
            "timestamp": 1000000,
        }
        mock_exchange.fetch_account_data.return_value = {
            "balance": 10000.0,
            "position_amt": 0.0,
            "leverage": 1.0,
            "unrealizedProfit": 0.0,
        }
        mock_get_exchange.return_value = mock_exchange
        mock_check_connection.return_value = (True, None, None)

        # Mock volatility calculation / 模拟波动率计算
        mock_calculate_volatility.return_value = (0.012, 0.032)
        mock_calculator_instance = MagicMock()
        mock_volatility_calculator.return_value = mock_calculator_instance

        # Mock bot_engine / 模拟 bot_engine
        mock_bot_engine.data = MagicMock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.2}
        mock_bot_engine.data.trade_history = []

        # Call the function / 调用函数
        symbol = "ETH/USDC:USDC"
        exchange_name = "hyperliquid"
        trace_id = "test-trace-004"

        context, error, status_code = asyncio.run(
            server._prepare_market_context_for_evaluation(symbol, exchange_name, trace_id)
        )

        # Verify VolatilityCalculator was instantiated with correct TTL
        # 验证 VolatilityCalculator 使用正确的 TTL 实例化
        mock_volatility_calculator.assert_called_once_with(cache_ttl=300)

        # Verify volatility calculation was called with calculator
        # 验证波动率计算使用计算器调用
        mock_calculate_volatility.assert_called_once()
        call_args = mock_calculate_volatility.call_args
        assert call_args[1]["calculator"] == mock_calculator_instance, "Calculator should be passed"

        # Verify context has correct volatility / 验证上下文有正确的波动率
        assert context.volatility_1h == 0.012, "1h volatility should match calculated value"
        assert context.volatility_24h == 0.032, "24h volatility should match calculated value"

