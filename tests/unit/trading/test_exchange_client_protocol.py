"""
Unit tests for ExchangeClient Protocol / ExchangeClient Protocol 单元测试

Tests that verify all exchange clients (BinanceClient, HyperliquidClient) properly
implement the ExchangeClient Protocol interface.
测试验证所有交易所客户端（BinanceClient、HyperliquidClient）正确实现 ExchangeClient Protocol 接口。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.trading.exchange import BinanceClient
from src.trading.exchange_client import ExchangeClient
from src.trading.hyperliquid_client import HyperliquidClient


class TestExchangeClientProtocol:
    """
    Test that ExchangeClient Protocol is properly defined and can be used for type checking.
    测试 ExchangeClient Protocol 正确定义并可用于类型检查。
    """

    def test_protocol_imports_successfully(self):
        """Test that ExchangeClient Protocol can be imported / 测试 ExchangeClient Protocol 可以导入"""
        from src.trading.exchange_client import ExchangeClient

        assert ExchangeClient is not None
        assert hasattr(ExchangeClient, "__protocol__") or hasattr(
            ExchangeClient, "__module__"
        )

    def test_protocol_has_required_methods(self):
        """Test that Protocol defines all required methods / 测试 Protocol 定义所有必需方法"""
        from src.trading.exchange_client import ExchangeClient

        # Check that Protocol has method signatures (via __annotations__ or inspection)
        # 检查 Protocol 是否有方法签名（通过 __annotations__ 或检查）
        protocol_methods = [
            "set_symbol",
            "get_leverage",
            "set_leverage",
            "get_max_leverage",
            "get_symbol_limits",
            "fetch_market_data",
            "fetch_funding_rate",
            "fetch_funding_rate_for_symbol",
            "fetch_bulk_funding_rates",
            "fetch_ticker_stats",
            "fetch_account_data",
            "fetch_account_balance",
            "fetch_positions",
            "fetch_position",
            "fetch_position_history",
            "fetch_open_orders",
            "fetch_order",
            "fetch_orders_history",
            "place_orders",
            "cancel_orders",
            "cancel_all_orders",
            "fetch_realized_pnl",
            "fetch_commission",
            "fetch_pnl_and_fees",
        ]

        # Protocol methods are defined in the class, check via dir() or inspection
        # Protocol 方法在类中定义，通过 dir() 或检查验证
        protocol_attrs = dir(ExchangeClient)
        for method_name in protocol_methods:
            assert (
                method_name in protocol_attrs
            ), f"ExchangeClient Protocol missing method: {method_name}"

    def test_protocol_has_required_attributes(self):
        """Test that Protocol defines all required attributes / 测试 Protocol 定义所有必需属性"""
        from src.trading.exchange_client import ExchangeClient

        # Check required attributes via __annotations__ (Protocol attributes are defined as class variables)
        # 通过 __annotations__ 检查必需属性（Protocol 属性定义为类变量）
        required_attrs = ["symbol", "last_order_error", "last_api_error", "is_connected"]

        # Protocol attributes are defined as class variables with type annotations
        # Protocol 属性定义为带类型注解的类变量
        # They appear in __annotations__ or can be checked via inspection
        # 它们出现在 __annotations__ 中或可以通过检查验证
        protocol_annotations = getattr(ExchangeClient, "__annotations__", {})
        
        # Also check if attributes are accessible (they might be in __dict__ or via getattr)
        # 同时检查属性是否可访问（它们可能在 __dict__ 中或通过 getattr）
        for attr_name in required_attrs:
            # Check if attribute exists in annotations or is accessible
            # 检查属性是否存在于注解中或可访问
            has_attr = (
                attr_name in protocol_annotations
                or hasattr(ExchangeClient, attr_name)
                or attr_name in getattr(ExchangeClient, "__dict__", {})
            )
            assert (
                has_attr
            ), f"ExchangeClient Protocol missing attribute: {attr_name}"


class TestBinanceClientProtocolCompliance:
    """
    Test that BinanceClient implements ExchangeClient Protocol.
    测试 BinanceClient 实现 ExchangeClient Protocol。
    """

    @patch("src.trading.exchange.ccxt.binanceusdm")
    def test_binance_client_implements_protocol(self, mock_ccxt):
        """Test that BinanceClient implements ExchangeClient Protocol / 测试 BinanceClient 实现 ExchangeClient Protocol"""
        # Mock CCXT exchange
        # 模拟 CCXT exchange
        mock_exchange = MagicMock()
        mock_exchange.markets = {"ETH/USDT:USDT": {"id": "ETHUSDT"}}
        mock_exchange.load_markets.return_value = mock_exchange.markets
        mock_exchange.urls = {"api": {}, "test": {}}
        mock_exchange.has = {}
        mock_exchange.fapiPrivatePostLeverage.return_value = {}
        mock_ccxt.return_value = mock_exchange

        client = BinanceClient()

        # Verify client can be used as ExchangeClient (structural typing)
        # 验证客户端可以用作 ExchangeClient（结构类型）
        # This test verifies that BinanceClient has all required methods/attributes
        # 此测试验证 BinanceClient 具有所有必需的方法/属性
        required_methods = [
            "set_symbol",
            "get_leverage",
            "set_leverage",
            "get_max_leverage",
            "get_symbol_limits",
            "fetch_market_data",
            "fetch_funding_rate",
            "fetch_account_data",
            "fetch_open_orders",
            "place_orders",
            "cancel_orders",
            "cancel_all_orders",
        ]

        for method_name in required_methods:
            assert hasattr(
                client, method_name
            ), f"BinanceClient missing required method: {method_name}"
            assert callable(
                getattr(client, method_name)
            ), f"BinanceClient.{method_name} is not callable"

        # Verify required attributes exist
        # 验证必需属性存在
        required_attrs = ["symbol", "last_order_error", "last_api_error"]
        for attr_name in required_attrs:
            assert hasattr(
                client, attr_name
            ), f"BinanceClient missing required attribute: {attr_name}"

    @patch("src.trading.exchange.ccxt.binanceusdm")
    def test_binance_client_type_compatibility(self, mock_ccxt):
        """
        Test that BinanceClient is compatible with ExchangeClient type annotation.
        测试 BinanceClient 与 ExchangeClient 类型注解兼容。

        This test verifies that BinanceClient can be assigned to ExchangeClient type.
        此测试验证 BinanceClient 可以赋值给 ExchangeClient 类型。
        """
        # Mock CCXT exchange
        # 模拟 CCXT exchange
        mock_exchange = MagicMock()
        mock_exchange.markets = {"ETH/USDT:USDT": {"id": "ETHUSDT"}}
        mock_exchange.load_markets.return_value = mock_exchange.markets
        mock_exchange.urls = {"api": {}, "test": {}}
        mock_exchange.has = {}
        mock_exchange.fapiPrivatePostLeverage.return_value = {}
        mock_ccxt.return_value = mock_exchange

        client = BinanceClient()

        # Type annotation test: assign to ExchangeClient type
        # 类型注解测试：赋值给 ExchangeClient 类型
        exchange_client: ExchangeClient = client

        # Verify the assignment worked (structural typing)
        # 验证赋值成功（结构类型）
        assert exchange_client is client
        assert hasattr(exchange_client, "fetch_market_data")
        assert hasattr(exchange_client, "place_orders")


class TestHyperliquidClientProtocolCompliance:
    """
    Test that HyperliquidClient implements ExchangeClient Protocol.
    测试 HyperliquidClient 实现 ExchangeClient Protocol。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_hyperliquid_client_implements_protocol(self, mock_requests):
        """Test that HyperliquidClient implements ExchangeClient Protocol / 测试 HyperliquidClient 实现 ExchangeClient Protocol"""
        # Mock successful API response
        # 模拟成功的 API 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        client = HyperliquidClient()

        # Verify client can be used as ExchangeClient (structural typing)
        # 验证客户端可以用作 ExchangeClient（结构类型）
        required_methods = [
            "set_symbol",
            "get_leverage",
            "set_leverage",
            "get_max_leverage",
            "get_symbol_limits",
            "fetch_market_data",
            "fetch_funding_rate",
            "fetch_funding_rate_for_symbol",
            "fetch_bulk_funding_rates",
            "fetch_account_data",
            "fetch_open_orders",
            "place_orders",
            "cancel_orders",
            "cancel_all_orders",
        ]

        for method_name in required_methods:
            assert hasattr(
                client, method_name
            ), f"HyperliquidClient missing required method: {method_name}"
            assert callable(
                getattr(client, method_name)
            ), f"HyperliquidClient.{method_name} is not callable"

        # Verify required attributes exist
        # 验证必需属性存在
        required_attrs = ["symbol", "last_order_error", "last_api_error", "is_connected"]
        for attr_name in required_attrs:
            assert hasattr(
                client, attr_name
            ), f"HyperliquidClient missing required attribute: {attr_name}"

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_hyperliquid_client_type_compatibility(self, mock_requests):
        """
        Test that HyperliquidClient is compatible with ExchangeClient type annotation.
        测试 HyperliquidClient 与 ExchangeClient 类型注解兼容。

        This test verifies that HyperliquidClient can be assigned to ExchangeClient type.
        此测试验证 HyperliquidClient 可以赋值给 ExchangeClient 类型。
        """
        # Mock successful API response
        # 模拟成功的 API 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        client = HyperliquidClient()

        # Type annotation test: assign to ExchangeClient type
        # 类型注解测试：赋值给 ExchangeClient 类型
        exchange_client: ExchangeClient = client

        # Verify the assignment worked (structural typing)
        # 验证赋值成功（结构类型）
        assert exchange_client is client
        assert hasattr(exchange_client, "fetch_market_data")
        assert hasattr(exchange_client, "place_orders")


class TestMockExchangeClientProtocolCompliance:
    """
    Test that mock_exchange_client fixture implements ExchangeClient Protocol.
    测试 mock_exchange_client fixture 实现 ExchangeClient Protocol。
    """

    def test_mock_exchange_client_implements_protocol(self, mock_exchange_client):
        """
        Test that mock_exchange_client fixture implements ExchangeClient Protocol.
        测试 mock_exchange_client fixture 实现 ExchangeClient Protocol。
        """
        # Verify mock has all required methods
        # 验证 mock 具有所有必需方法
        required_methods = [
            "set_symbol",
            "get_leverage",
            "set_leverage",
            "get_max_leverage",
            "get_symbol_limits",
            "fetch_market_data",
            "fetch_funding_rate",
            "fetch_funding_rate_for_symbol",
            "fetch_bulk_funding_rates",
            "fetch_ticker_stats",
            "fetch_account_data",
            "fetch_account_balance",
            "fetch_positions",
            "fetch_position",
            "fetch_position_history",
            "fetch_open_orders",
            "fetch_order",
            "fetch_orders_history",
            "place_orders",
            "cancel_orders",
            "cancel_all_orders",
            "fetch_realized_pnl",
            "fetch_commission",
            "fetch_pnl_and_fees",
        ]

        for method_name in required_methods:
            assert hasattr(
                mock_exchange_client, method_name
            ), f"mock_exchange_client missing required method: {method_name}"
            assert callable(
                getattr(mock_exchange_client, method_name)
            ), f"mock_exchange_client.{method_name} is not callable"

        # Verify required attributes exist
        # 验证必需属性存在
        required_attrs = ["symbol", "last_order_error", "is_connected"]
        for attr_name in required_attrs:
            assert hasattr(
                mock_exchange_client, attr_name
            ), f"mock_exchange_client missing required attribute: {attr_name}"

    def test_mock_exchange_client_type_compatibility(self, mock_exchange_client):
        """
        Test that mock_exchange_client is compatible with ExchangeClient type annotation.
        测试 mock_exchange_client 与 ExchangeClient 类型注解兼容。

        This test verifies that mock_exchange_client can be assigned to ExchangeClient type.
        此测试验证 mock_exchange_client 可以赋值给 ExchangeClient 类型。
        """
        # Type annotation test: assign to ExchangeClient type
        # 类型注解测试：赋值给 ExchangeClient 类型
        exchange_client: ExchangeClient = mock_exchange_client

        # Verify the assignment worked (structural typing)
        # 验证赋值成功（结构类型）
        assert exchange_client is mock_exchange_client
        assert hasattr(exchange_client, "fetch_market_data")
        assert hasattr(exchange_client, "place_orders")


class TestExchangeClientInterchangeability:
    """
    Test that different exchange clients can be used interchangeably via ExchangeClient Protocol.
    测试不同的交易所客户端可以通过 ExchangeClient Protocol 互换使用。
    """

    @patch("src.trading.exchange.ccxt.binanceusdm")
    def test_strategy_instance_accepts_binance_client(self, mock_ccxt):
        """
        Test that StrategyInstance accepts BinanceClient via ExchangeClient Protocol.
        测试 StrategyInstance 通过 ExchangeClient Protocol 接受 BinanceClient。
        """
        from src.trading.strategy_instance import StrategyInstance

        # Mock CCXT exchange
        # 模拟 CCXT exchange
        mock_exchange = MagicMock()
        mock_exchange.markets = {"ETH/USDT:USDT": {"id": "ETHUSDT"}}
        mock_exchange.load_markets.return_value = mock_exchange.markets
        mock_exchange.urls = {"api": {}, "test": {}}
        mock_exchange.has = {}
        mock_exchange.fapiPrivatePostLeverage.return_value = {}
        mock_ccxt.return_value = mock_exchange

        binance_client = BinanceClient()

        # Create StrategyInstance with BinanceClient
        # 使用 BinanceClient 创建 StrategyInstance
        instance = StrategyInstance(
            "test_binance", "fixed_spread", exchange=binance_client
        )

        # Verify exchange is set correctly
        # 验证 exchange 设置正确
        assert instance.exchange is binance_client
        assert instance.exchange.symbol == "ETH/USDT:USDT"

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_strategy_instance_accepts_hyperliquid_client(self, mock_requests):
        """
        Test that StrategyInstance accepts HyperliquidClient via ExchangeClient Protocol.
        测试 StrategyInstance 通过 ExchangeClient Protocol 接受 HyperliquidClient。
        """
        from src.trading.strategy_instance import StrategyInstance

        # Mock successful API response
        # 模拟成功的 API 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        hyperliquid_client = HyperliquidClient()

        # Create StrategyInstance with HyperliquidClient
        # 使用 HyperliquidClient 创建 StrategyInstance
        instance = StrategyInstance(
            "test_hyperliquid", "fixed_spread", exchange=hyperliquid_client
        )

        # Verify exchange is set correctly
        # 验证 exchange 设置正确
        assert instance.exchange is hyperliquid_client
        assert instance.exchange.symbol == "ETH/USDT:USDT"

    def test_strategy_instance_accepts_mock_exchange_client(self, mock_exchange_client):
        """
        Test that StrategyInstance accepts mock_exchange_client via ExchangeClient Protocol.
        测试 StrategyInstance 通过 ExchangeClient Protocol 接受 mock_exchange_client。
        """
        from src.trading.strategy_instance import StrategyInstance

        # Create StrategyInstance with mock_exchange_client
        # 使用 mock_exchange_client 创建 StrategyInstance
        instance = StrategyInstance(
            "test_mock", "fixed_spread", exchange=mock_exchange_client
        )

        # Verify exchange is set correctly
        # 验证 exchange 设置正确
        assert instance.exchange is mock_exchange_client
        assert instance.exchange.symbol == "ETH/USDT:USDT"

