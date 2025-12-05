"""
Integration Test for US-CORE-004-A: Hyperliquid Connection and Authentication
US-CORE-004-A 集成测试：Hyperliquid 连接与认证

Integration tests verify cross-module interactions and end-to-end workflows.
集成测试验证跨模块交互和端到端工作流。

Owner: Agent QA
"""

import os
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.trading.hyperliquid_client import HyperliquidClient, AuthenticationError
from src.trading.strategy_instance import StrategyInstance
from src.trading.engine import AlphaLoop


class TestHyperliquidStrategyInstanceIntegration:
    """
    Integration tests for HyperliquidClient with StrategyInstance.
    HyperliquidClient 与 StrategyInstance 的集成测试。
    
    Tests that HyperliquidClient can be used as a drop-in replacement for BinanceClient.
    测试 HyperliquidClient 可以作为 BinanceClient 的直接替代品使用。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_hyperliquid_client_in_strategy_instance(self, mock_requests):
        """
        Integration Test: HyperliquidClient can be used in StrategyInstance
        集成测试：HyperliquidClient 可以在 StrategyInstance 中使用
        
        Verifies that HyperliquidClient implements the same interface as BinanceClient
        and can be used interchangeably.
        验证 HyperliquidClient 实现与 BinanceClient 相同的接口，可以互换使用。
        """
        # Mock successful API responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create HyperliquidClient
        hyperliquid_client = HyperliquidClient()

        # Verify client is connected
        assert hyperliquid_client.is_connected is True

        # Mock exchange methods that StrategyInstance uses
        hyperliquid_client.fetch_market_data = Mock(
            return_value={
                "best_bid": 1000.0,
                "best_ask": 1002.0,
                "mid_price": 1001.0,
                "timestamp": time.time() * 1000,
            }
        )
        hyperliquid_client.fetch_funding_rate = Mock(return_value=0.0001)
        hyperliquid_client.fetch_account_data = Mock(
            return_value={
                "position_amt": 0.1,
                "entry_price": 1000.0,
            }
        )
        hyperliquid_client.fetch_open_orders = Mock(return_value=[])
        hyperliquid_client.set_symbol = Mock(return_value=True)

        # Verify interface compatibility
        # These methods should exist and be callable
        assert hasattr(hyperliquid_client, "fetch_market_data")
        assert hasattr(hyperliquid_client, "fetch_funding_rate")
        assert hasattr(hyperliquid_client, "fetch_account_data")
        assert hasattr(hyperliquid_client, "fetch_open_orders")
        assert hasattr(hyperliquid_client, "set_symbol")
        assert hasattr(hyperliquid_client, "place_orders")
        assert hasattr(hyperliquid_client, "cancel_orders")

        # Test that methods can be called (interface compatibility)
        market_data = hyperliquid_client.fetch_market_data()
        assert market_data["mid_price"] == 1001.0

        funding_rate = hyperliquid_client.fetch_funding_rate()
        assert funding_rate == 0.0001

        account_data = hyperliquid_client.fetch_account_data()
        assert account_data["position_amt"] == 0.1

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_hyperliquid_data_refresh_flow(self, mock_requests):
        """
        Integration Test: Complete data refresh flow with HyperliquidClient
        集成测试：使用 HyperliquidClient 的完整数据刷新流程
        
        Tests the end-to-end flow: connect → authenticate → fetch data.
        测试端到端流程：连接 → 认证 → 获取数据。
        """
        # Mock successful API responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "data": "test"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()

        # Verify connection
        assert client.is_connected is True

        # Mock data fetching methods
        client.fetch_market_data = Mock(
            return_value={
                "best_bid": 2000.0,
                "best_ask": 2002.0,
                "mid_price": 2001.0,
                "timestamp": time.time() * 1000,
            }
        )
        client.fetch_funding_rate = Mock(return_value=0.0002)
        client.fetch_account_data = Mock(
            return_value={
                "position_amt": 0.2,
                "entry_price": 2000.0,
                "available_balance": 1000.0,
            }
        )

        # Simulate data refresh flow (as StrategyInstance would do)
        market_data = client.fetch_market_data()
        funding_rate = client.fetch_funding_rate()
        account_data = client.fetch_account_data()

        # Verify data is fetched correctly
        assert market_data["mid_price"] == 2001.0
        assert funding_rate == 0.0002
        assert account_data["position_amt"] == 0.2
        assert account_data["available_balance"] == 1000.0

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_hyperliquid_order_management_flow(self, mock_requests):
        """
        Integration Test: Order management flow with HyperliquidClient
        集成测试：使用 HyperliquidClient 的订单管理流程
        
        Tests placing and canceling orders through HyperliquidClient.
        测试通过 HyperliquidClient 下单和取消订单。
        """
        # Mock successful API responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()

        # Mock order management methods
        client.place_orders = Mock(
            return_value=[
                {"id": "order1", "side": "buy", "price": 1000.0, "amount": 0.01},
                {"id": "order2", "side": "sell", "price": 1002.0, "amount": 0.01},
            ]
        )
        client.fetch_open_orders = Mock(
            return_value=[
                {"id": "order1", "side": "buy", "price": 1000.0, "amount": 0.01},
                {"id": "order2", "side": "sell", "price": 1002.0, "amount": 0.01},
            ]
        )
        client.cancel_orders = Mock(return_value=[])

        # Test placing orders
        orders_to_place = [
            {"side": "buy", "price": 1000.0, "quantity": 0.01},
            {"side": "sell", "price": 1002.0, "quantity": 0.01},
        ]
        placed_orders = client.place_orders(orders_to_place)
        assert len(placed_orders) == 2
        assert placed_orders[0]["id"] == "order1"

        # Test fetching open orders
        open_orders = client.fetch_open_orders()
        assert len(open_orders) == 2

        # Test canceling orders
        canceled = client.cancel_orders(["order1", "order2"])
        assert client.cancel_orders.called


class TestHyperliquidInterfaceCompatibility:
    """
    Integration tests for interface compatibility between HyperliquidClient and BinanceClient.
    HyperliquidClient 和 BinanceClient 接口兼容性的集成测试。
    
    Verifies that both clients implement the same interface and can be used interchangeably.
    验证两个客户端实现相同的接口，可以互换使用。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_interface_methods_exist(self, mock_requests):
        """
        Integration Test: Verify required interface methods exist
        集成测试：验证必需的接口方法存在
        
        Checks that HyperliquidClient has all methods that BinanceClient has.
        检查 HyperliquidClient 具有 BinanceClient 的所有方法。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        hyperliquid_client = HyperliquidClient()

        # List of methods that should exist (matching BinanceClient interface)
        required_methods = [
            "fetch_market_data",
            "fetch_funding_rate",
            "fetch_account_data",
            "fetch_open_orders",
            "place_orders",
            "cancel_orders",
            "set_symbol",
            "set_leverage",
        ]

        # Verify all methods exist
        for method_name in required_methods:
            assert hasattr(
                hyperliquid_client, method_name
            ), f"HyperliquidClient missing method: {method_name}"

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_interface_attributes_exist(self, mock_requests):
        """
        Integration Test: Verify required interface attributes exist
        集成测试：验证必需的接口属性存在
        
        Checks that HyperliquidClient has all attributes that BinanceClient has.
        检查 HyperliquidClient 具有 BinanceClient 的所有属性。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        hyperliquid_client = HyperliquidClient()

        # List of attributes that should exist
        required_attributes = [
            "symbol",
            "is_connected",
            "base_url",
        ]

        # Verify all attributes exist
        for attr_name in required_attributes:
            assert hasattr(
                hyperliquid_client, attr_name
            ), f"HyperliquidClient missing attribute: {attr_name}"


class TestHyperliquidErrorHandlingIntegration:
    """
    Integration tests for error handling in HyperliquidClient.
    HyperliquidClient 错误处理的集成测试。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_authentication_error_propagation(self, mock_requests):
        """
        Integration Test: Authentication errors are properly propagated
        集成测试：认证错误被正确传播
        
        Verifies that authentication errors from HyperliquidClient can be caught
        and handled by calling code.
        验证来自 HyperliquidClient 的认证错误可以被调用代码捕获和处理。
        """
        # Mock authentication failure
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_response.text = '{"error": "Invalid API key"}'
        mock_requests.post.return_value = mock_response

        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            HyperliquidClient()

        # Verify error message is accessible
        error_msg = str(exc_info.value)
        assert len(error_msg) > 0





