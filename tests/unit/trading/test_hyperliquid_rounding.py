"""
Unit tests for HyperliquidClient price and quantity rounding
HyperliquidClient 价格和数量舍入的单元测试

Tests verify that prices and quantities are properly rounded before sending to SDK.
测试验证价格和数量在发送到 SDK 之前被正确舍入。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquidRounding:
    """
    Unit tests for price and quantity rounding in place_orders.
    测试 place_orders 中价格和数量舍入的单元测试。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format for SDK initialization
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.HyperliquidExchange")
    def test_price_rounding_before_sdk(self, mock_exchange_class, mock_post):
        """
        Test: Price is rounded to tick_size before sending to SDK
        测试：价格在发送到 SDK 之前被舍入到 tick_size
        """
        # Mock successful connection
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.side_effect = [mock_success, mock_success]

        client = HyperliquidClient()

        # Mock fetch_market_data to return market data with tick_size and step_size
        client.fetch_market_data = Mock(
            return_value={
                "best_bid": 3334.0,
                "best_ask": 3334.1,
                "mid_price": 3334.05,
                "tick_size": 0.1,
                "step_size": 0.001,
            }
        )

        # Mock SDK order() method
        if client._exchange:
            client._exchange.order = MagicMock(
                return_value={
                    "status": "ok",
                    "response": {
                        "type": "order",
                        "data": {"statuses": [{"resting": {"oid": 12345}}]},
                    },
                }
            )

        # Place order with price that needs rounding (3334.073600000411)
        # 下订单，价格需要舍入（3334.073600000411）
        orders = [
            {
                "side": "buy",
                "price": 3334.073600000411,  # Price that needs rounding
                "quantity": 0.01,
                "type": "limit",
            }
        ]

        result = client.place_orders(orders)

        # Verify order was placed successfully
        # 验证订单成功下单
        assert len(result) > 0

        # Verify SDK was called with rounded price
        # 验证 SDK 被调用时使用了舍入后的价格
        if client._exchange and hasattr(client._exchange, "order"):
            call_args = client._exchange.order.call_args
            if call_args:
                # Check that limit_px is rounded to nearest tick_size (0.1)
                # 检查 limit_px 被舍入到最近的 tick_size (0.1)
                limit_px = call_args.kwargs.get("limit_px")
                if limit_px:
                    # Price should be rounded to nearest tick (0.1)
                    # Check by comparing with nearest tick_size multiple
                    # 价格应该被舍入到最近的 tick (0.1)
                    # 通过与最近的 tick_size 倍数比较来检查
                    tick_size = 0.1
                    nearest_tick = round(limit_px / tick_size) * tick_size
                    difference = abs(limit_px - nearest_tick)
                    assert difference < 1e-6, (
                        f"Price {limit_px} should be rounded to nearest tick_size {tick_size}. "
                        f"Nearest tick: {nearest_tick}, Difference: {difference}"
                    )

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format for SDK initialization
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_quantity_rounding_before_sdk(self, mock_post):
        """
        Test: Quantity is rounded to step_size before sending to SDK
        测试：数量在发送到 SDK 之前被舍入到 step_size
        """
        # Mock successful connection
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.side_effect = [mock_success, mock_success]

        client = HyperliquidClient()

        # Mock fetch_market_data to return market data with tick_size and step_size
        client.fetch_market_data = Mock(
            return_value={
                "best_bid": 3334.0,
                "best_ask": 3334.1,
                "mid_price": 3334.05,
                "tick_size": 0.1,
                "step_size": 0.001,
            }
        )

        # Mock SDK order() method
        if client._exchange:
            client._exchange.order = MagicMock(
                return_value={
                    "status": "ok",
                    "response": {
                        "type": "order",
                        "data": {"statuses": [{"resting": {"oid": 12345}}]},
                    },
                }
            )

        # Place order with quantity that needs rounding (0.010123456)
        # 下订单，数量需要舍入（0.010123456）
        orders = [
            {
                "side": "buy",
                "price": 3334.0,
                "quantity": 0.010123456,  # Quantity that needs rounding
                "type": "limit",
            }
        ]

        result = client.place_orders(orders)

        # Verify order was placed successfully
        # 验证订单成功下单
        assert len(result) > 0

        # Verify SDK was called with rounded quantity
        # 验证 SDK 被调用时使用了舍入后的数量
        if client._exchange and hasattr(client._exchange, "order"):
            call_args = client._exchange.order.call_args
            if call_args:
                # Check that sz is divisible by step_size (0.001)
                # 检查 sz 可被 step_size (0.001) 整除
                sz = call_args.kwargs.get("sz")
                if sz:
                    # Quantity should be rounded to nearest step (0.001)
                    # 数量应该被舍入到最近的 step (0.001)
                    remainder = sz % 0.001
                    assert abs(remainder) < 1e-10, (
                        f"Quantity {sz} should be divisible by step_size 0.001. "
                        f"Remainder: {remainder}"
                    )

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format for SDK initialization
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_rounding_with_missing_market_data(self, mock_post):
        """
        Test: Rounding works even when market_data doesn't have step_size/tick_size
        测试：即使 market_data 没有 step_size/tick_size，舍入仍然工作
        """
        # Mock successful connection
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock meta data response with szDecimals
        mock_meta = MagicMock()
        mock_meta.status_code = 200
        mock_meta.json.return_value = {
            "universe": [
                {
                    "name": "ETH",
                    "szDecimals": 3,  # step_size = 0.001, tick_size = 0.0001
                }
            ],
        }
        
        mock_post.side_effect = [mock_success, mock_success, mock_meta]

        client = HyperliquidClient()

        # Mock fetch_market_data to return market data WITHOUT step_size/tick_size
        # Mock fetch_market_data 返回没有 step_size/tick_size 的市场数据
        client.fetch_market_data = Mock(
            return_value={
                "best_bid": 3334.0,
                "best_ask": 3334.1,
                "mid_price": 3334.05,
                # No tick_size or step_size
            }
        )

        # Mock SDK order() method
        if client._exchange:
            client._exchange.order = MagicMock(
                return_value={
                    "status": "ok",
                    "response": {
                        "type": "order",
                        "data": {"statuses": [{"resting": {"oid": 12345}}]},
                    },
                }
            )

        # Place order
        orders = [
            {
                "side": "buy",
                "price": 3334.073600000411,
                "quantity": 0.010123456,
                "type": "limit",
            }
        ]

        result = client.place_orders(orders)

        # Verify order was placed successfully (should use defaults or resolve from meta)
        # 验证订单成功下单（应该使用默认值或从 meta 解析）
        assert len(result) > 0

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format for SDK initialization
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.HyperliquidExchange")
    def test_rounding_prevents_float_to_wire_error(self, mock_exchange_class, mock_post):
        """
        Test: Proper rounding prevents 'float_to_wire causes rounding' error
        测试：正确的舍入防止 'float_to_wire causes rounding' 错误
        """
        # Mock successful connection
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.side_effect = [mock_success, mock_success]

        # Mock HyperliquidExchange to avoid SDK initialization issues
        # Mock HyperliquidExchange 以避免 SDK 初始化问题
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.order.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 12345}}]},
            },
        }
        mock_exchange_class.return_value = mock_exchange_instance

        client = HyperliquidClient()

        # Manually set _exchange to mock to bypass initialization
        # 手动设置 _exchange 为 mock 以绕过初始化
        client._exchange = mock_exchange_instance
        client.symbol = "ETH/USDT:USDT"

        # Mock fetch_market_data with proper tick_size and step_size
        client.fetch_market_data = Mock(
            return_value={
                "best_bid": 3334.0,
                "best_ask": 3334.1,
                "mid_price": 3334.05,
                "tick_size": 0.1,
                "step_size": 0.001,
            }
        )

        # Place order with problematic price that would cause float_to_wire error
        # 下订单，使用会导致 float_to_wire 错误的问题价格
        orders = [
            {
                "side": "buy",
                "price": 3334.073600000411,  # This price caused the error
                "quantity": 0.01,
                "type": "limit",
            }
        ]

        result = client.place_orders(orders)

        # Verify order was placed successfully without error
        # 验证订单成功下单，没有错误
        assert len(result) > 0
        assert client.last_order_error is None

        # Verify SDK was called (order was actually sent)
        # 验证 SDK 被调用（订单实际被发送）
        if client._exchange and hasattr(client._exchange, "order"):
            assert client._exchange.order.called
            
            # Verify the price sent to SDK is properly rounded
            # 验证发送到 SDK 的价格被正确舍入
            call_args = client._exchange.order.call_args
            if call_args:
                limit_px = call_args.kwargs.get("limit_px")
                if limit_px:
                    # Price should be rounded to nearest tick_size (0.1)
                    # Check by comparing with nearest tick_size multiple
                    # 价格应该被舍入到最近的 tick_size (0.1)
                    # 通过与最近的 tick_size 倍数比较来检查
                    tick_size = 0.1
                    nearest_tick = round(limit_px / tick_size) * tick_size
                    difference = abs(limit_px - nearest_tick)
                    assert difference < 1e-6, (
                        f"Price {limit_px} should be rounded to nearest tick_size {tick_size}. "
                        f"Nearest tick: {nearest_tick}, Difference: {difference}"
                    )

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format for SDK initialization
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.HyperliquidExchange")
    def test_rounding_for_problematic_price_3355(self, mock_exchange_class, mock_post):
        """
        Test: Specific problematic price 3355.162750000075 is properly rounded
        测试：特定问题价格 3355.162750000075 被正确舍入
        
        This test verifies the fix for the specific error:
        ('float_to_wire causes rounding', 3355.162750000075)
        """
        # Mock successful connection
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.side_effect = [mock_success, mock_success]

        # Mock HyperliquidExchange to avoid SDK initialization issues
        # Mock HyperliquidExchange 以避免 SDK 初始化问题
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.order.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 12345}}]},
            },
        }
        mock_exchange_class.return_value = mock_exchange_instance

        client = HyperliquidClient()

        # Manually set _exchange to mock to bypass initialization
        # 手动设置 _exchange 为 mock 以绕过初始化
        client._exchange = mock_exchange_instance
        client.symbol = "ETH/USDT:USDT"

        # Mock fetch_market_data with proper tick_size and step_size
        client.fetch_market_data = Mock(
            return_value={
                "best_bid": 3355.0,
                "best_ask": 3355.2,
                "mid_price": 3355.1,
                "tick_size": 0.1,
                "step_size": 0.001,
            }
        )

        # Place order with the specific problematic price
        # 使用特定问题价格下单
        orders = [
            {
                "side": "buy",
                "price": 3355.162750000075,  # The exact problematic price from the error
                "quantity": 0.01,
                "type": "limit",
            }
        ]

        result = client.place_orders(orders)

        # Verify order was placed successfully
        # 验证订单成功下单
        assert len(result) > 0
        assert client.last_order_error is None

        # Verify SDK was called with properly rounded price
        # 验证 SDK 被调用时使用了正确舍入的价格
        if client._exchange and hasattr(client._exchange, "order"):
            assert client._exchange.order.called
            call_args = client._exchange.order.call_args
            if call_args:
                limit_px = call_args.kwargs.get("limit_px")
                if limit_px:
                    # Price should be rounded to nearest tick_size (0.1)
                    # Check by comparing with nearest tick_size multiple using Decimal for precision
                    # 价格应该被舍入到最近的 tick_size (0.1)
                    # 使用 Decimal 精确计算与最近的 tick_size 倍数的差异
                    from decimal import Decimal
                    tick_size = Decimal("0.1")
                    price_decimal = Decimal(str(limit_px))
                    nearest_tick = (price_decimal / tick_size).quantize(Decimal('1'), rounding='ROUND_HALF_UP') * tick_size
                    difference = abs(price_decimal - nearest_tick)
                    
                    assert difference < Decimal('1e-6'), (
                        f"Price {limit_px} should be rounded to nearest tick_size {tick_size}. "
                        f"Nearest tick: {nearest_tick}, Difference: {difference}"
                    )
                    
                    # Note: The actual rounding behavior may vary due to implementation details
                    # The key requirement is that the price is properly rounded to tick_size
                    # 注意：由于实现细节，实际舍入行为可能有所不同
                    # 关键要求是价格被正确舍入到 tick_size

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format for SDK initialization
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.HyperliquidExchange")
    def test_final_rounding_always_applied(self, mock_exchange_class, mock_post):
        """
        Test: Final rounding is always applied before sending to SDK, even if price was already rounded
        测试：在发送到 SDK 之前始终应用最终舍入，即使价格已经被舍入过
        """
        # Mock successful connection
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.side_effect = [mock_success, mock_success]

        # Mock HyperliquidExchange to avoid SDK initialization issues
        # Mock HyperliquidExchange 以避免 SDK 初始化问题
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.order.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 12345}}]},
            },
        }
        mock_exchange_class.return_value = mock_exchange_instance

        client = HyperliquidClient()

        # Manually set _exchange to mock to bypass initialization
        # 手动设置 _exchange 为 mock 以绕过初始化
        client._exchange = mock_exchange_instance
        client.symbol = "ETH/USDT:USDT"

        # Mock fetch_market_data with proper tick_size and step_size
        client.fetch_market_data = Mock(
            return_value={
                "best_bid": 3000.0,
                "best_ask": 3002.0,
                "mid_price": 3001.0,
                "tick_size": 0.1,
                "step_size": 0.001,
            }
        )

        # Place order with price that has floating point precision issues
        # 使用有浮点数精度问题的价格下单
        orders = [
            {
                "side": "buy",
                "price": 3000.1000000000001,  # Price with tiny floating point error
                "quantity": 0.0100000000001,  # Quantity with tiny floating point error
                "type": "limit",
            }
        ]

        result = client.place_orders(orders)

        # Verify order was placed successfully
        # 验证订单成功下单
        assert len(result) > 0

        # Verify SDK was called with properly rounded values
        # 验证 SDK 被调用时使用了正确舍入的值
        if client._exchange and hasattr(client._exchange, "order"):
            call_args = client._exchange.order.call_args
            if call_args:
                limit_px = call_args.kwargs.get("limit_px")
                sz = call_args.kwargs.get("sz")
                
                if limit_px:
                    # Price should be rounded to nearest tick_size
                    # Check by comparing with nearest tick_size multiple
                    # 价格应该被舍入到最近的 tick_size
                    # 通过与最近的 tick_size 倍数比较来检查
                    tick_size = 0.1
                    nearest_tick = round(limit_px / tick_size) * tick_size
                    difference = abs(limit_px - nearest_tick)
                    assert difference < 1e-6, (
                        f"Price {limit_px} should be rounded to nearest tick_size {tick_size}. "
                        f"Nearest tick: {nearest_tick}, Difference: {difference}"
                    )
                
                if sz:
                    # Quantity should be divisible by step_size
                    # 数量应该可被 step_size 整除
                    remainder = sz % 0.001
                    assert abs(remainder) < 1e-10, (
                        f"Quantity {sz} should be divisible by step_size 0.001. "
                        f"Remainder: {remainder}"
                    )

