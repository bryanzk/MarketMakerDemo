"""
Pytest configuration for unit tests
单元测试配置

Provides unified Exchange Provider Mock fixtures that implement the ExchangeClient interface.
提供统一的 Exchange Provider Mock fixtures，实现 ExchangeClient 接口。

This ensures tests are not dependent on specific implementations (BinanceClient, HyperliquidClient),
but rather depend on the ExchangeClient interface contract.
这确保测试不依赖于具体实现（BinanceClient、HyperliquidClient），而是依赖于 ExchangeClient 接口契约。
"""

from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_exchange_client():
    """
    Create a unified Exchange Provider Mock that implements the ExchangeClient interface.
    创建统一的 Exchange Provider Mock，实现 ExchangeClient 接口。
    
    This mock implements all methods defined in contracts/trading.json#ExchangeClient.
    此 mock 实现 contracts/trading.json#ExchangeClient 中定义的所有方法。
    
    Returns:
        Mock: A mock exchange client with all ExchangeClient interface methods
    """
    exchange = Mock()
    
    # Connection & Configuration / 连接与配置
    exchange.symbol = "ETH/USDT:USDT"
    exchange.set_symbol = Mock(return_value=True)
    exchange.get_leverage = Mock(return_value=5)
    exchange.set_leverage = Mock(return_value=True)
    exchange.get_max_leverage = Mock(return_value=125)
    exchange.get_symbol_limits = Mock(
        return_value={
            "minQty": 0.001,
            "maxQty": 100.0,
            "stepSize": 0.001,
            "minNotional": 5.0,
        }
    )
    
    # Market Data / 市场数据
    exchange.fetch_market_data = Mock(
        return_value={
            "best_bid": 1999.0,
            "best_ask": 2001.0,
            "mid_price": 2000.0,
            "timestamp": 1000000000000,
            "tick_size": 0.01,
            "step_size": 0.001,
        }
    )
    exchange.fetch_funding_rate = Mock(return_value=0.0001)
    exchange.fetch_funding_rate_for_symbol = Mock(return_value=0.0001)
    exchange.fetch_bulk_funding_rates = Mock(return_value={"ETH/USDT:USDT": 0.0001})
    exchange.fetch_ticker_stats = Mock(
        return_value={"percentage": 2.5, "quoteVolume": 1000000.0}
    )
    
    # Account & Position / 账户与仓位
    exchange.fetch_account_data = Mock(
        return_value={
            "position_amt": 0.0,
            "entry_price": 0.0,
            "balance": 1000.0,
            "available_balance": 1000.0,
            "liquidation_price": 0.0,
        }
    )
    exchange.fetch_account_balance = Mock(
        return_value={
            "total": 1000.0,
            "available": 1000.0,
            "margin_used": 0.0,
            "margin_available": 1000.0,
            "margin_ratio": 0.0,
            "liquidation_price": 0.0,
        }
    )
    exchange.fetch_positions = Mock(return_value=[])
    exchange.fetch_position = Mock(
        return_value={
            "symbol": "ETH/USDT:USDT",
            "side": "NONE",
            "size": 0.0,
            "entry_price": 0.0,
            "mark_price": 2000.0,
            "unrealized_pnl": 0.0,
            "liquidation_price": 0.0,
            "timestamp": 1000000000000,
        }
    )
    exchange.fetch_position_history = Mock(return_value=[])
    
    # Order Management / 订单管理
    exchange.fetch_open_orders = Mock(return_value=[])
    exchange.fetch_order = Mock(
        return_value={
            "order_id": "test_order_1",
            "symbol": "ETH/USDT:USDT",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": 0.01,
            "price": 1999.0,
            "status": "open",
            "filled_qty": 0.0,
            "timestamp": 1000000000000,
        }
    )
    exchange.fetch_orders_history = Mock(return_value=[])
    exchange.place_orders = Mock(return_value=[{"id": "ord1", "side": "buy"}])
    exchange.cancel_orders = Mock(return_value=True)
    exchange.cancel_all_orders = Mock(return_value=True)
    
    # PnL & Fees / 盈亏与费用
    exchange.fetch_realized_pnl = Mock(return_value=0.0)
    exchange.fetch_commission = Mock(return_value=0.0)
    exchange.fetch_pnl_and_fees = Mock(
        return_value={"realized_pnl": 0.0, "commission": 0.0, "net_pnl": 0.0}
    )
    
    # Error tracking / 错误跟踪
    exchange.last_order_error = None
    
    # Connection status / 连接状态
    exchange.is_connected = True
    
    return exchange

