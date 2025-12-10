"""
Exchange Client Protocol / 交易所客户端协议

Defines the unified interface for all exchange clients (BinanceClient, HyperliquidClient, etc.).
定义所有交易所客户端（BinanceClient、HyperliquidClient 等）的统一接口。

This Protocol ensures type safety and interface consistency across all exchange implementations.
此 Protocol 确保所有交易所实现的类型安全和接口一致性。

Owner: Agent ARCH
"""

from typing import Dict, List, Optional, Protocol


class ExchangeClient(Protocol):
    """
    Unified interface for all exchange clients.
    所有交易所客户端的统一接口。

    All exchange clients (BinanceClient, HyperliquidClient, etc.) must implement
    all methods defined in this Protocol to ensure interface consistency.
    所有交易所客户端（BinanceClient、HyperliquidClient 等）必须实现此 Protocol 中定义的所有方法，
    以确保接口一致性。

    The interface is based on contracts/trading.json#ExchangeClient.
    接口基于 contracts/trading.json#ExchangeClient。
    """

    # Connection & Configuration / 连接与配置
    symbol: str
    """Current trading symbol / 当前交易符号"""

    def set_symbol(self, symbol: str) -> bool:
        """Update the trading symbol / 更新交易符号"""
        ...

    def get_leverage(self) -> int:
        """Get current leverage for the symbol / 获取当前杠杆"""
        ...

    def set_leverage(self, leverage: int) -> bool:
        """Set leverage for the symbol / 设置杠杆"""
        ...

    def get_max_leverage(self) -> int:
        """Get maximum leverage for the symbol / 获取最大杠杆"""
        ...

    def get_symbol_limits(self) -> Dict[str, float]:
        """Get trading limits for the symbol / 获取交易限制"""
        ...

    # Market Data / 市场数据
    def fetch_market_data(self) -> Optional[Dict]:
        """Fetch current market data (order book, mid price, tick/step sizes) / 获取当前市场数据"""
        ...

    def fetch_funding_rate(self) -> float:
        """Fetch funding rate for current symbol / 获取当前交易对的资金费率"""
        ...

    def fetch_funding_rate_for_symbol(self, symbol: str) -> float:
        """Fetch funding rate for specific symbol / 获取特定交易对的资金费率"""
        ...

    def fetch_bulk_funding_rates(self, symbols: List[str]) -> Dict[str, float]:
        """Fetch funding rates for multiple symbols / 获取多个交易对的资金费率"""
        ...

    def fetch_ticker_stats(self) -> Dict:
        """Fetch 24h ticker statistics / 获取 24 小时行情统计"""
        ...

    # Account & Position / 账户与仓位
    def fetch_account_data(self) -> Optional[Dict]:
        """Fetch position and balance data for current symbol / 获取当前交易对的仓位和余额数据"""
        ...

    def fetch_account_balance(self) -> Dict:
        """Fetch account balance and margin information / 获取账户余额和保证金信息"""
        ...

    def fetch_positions(self) -> List[Dict]:
        """Fetch all open positions across all symbols / 获取所有交易对的所有未平仓仓位"""
        ...

    def fetch_position(self, symbol: Optional[str] = None) -> Dict:
        """Fetch position for specific symbol / 获取特定交易对的仓位"""
        ...

    def fetch_position_history(
        self,
        limit: Optional[int] = None,
        start_time: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> List[Dict]:
        """Fetch position history / 获取仓位历史"""
        ...

    # Order Management / 订单管理
    def fetch_open_orders(self) -> List[Dict]:
        """Fetch all open orders for the symbol / 获取所有未成交订单"""
        ...

    def fetch_order(self, order_id: str) -> Dict:
        """Fetch order status by order ID / 根据订单 ID 获取订单状态"""
        ...

    def fetch_orders_history(
        self, limit: Optional[int] = None, start_time: Optional[int] = None
    ) -> List[Dict]:
        """Fetch order history / 获取订单历史"""
        ...

    def place_orders(self, orders: List[Dict]) -> List[Dict]:
        """Place batch of orders / 批量下单"""
        ...

    def cancel_orders(self, order_ids: List[str]) -> bool:
        """Cancel multiple orders / 取消多个订单"""
        ...

    def cancel_all_orders(self) -> bool:
        """Cancel all open orders / 取消所有未成交订单"""
        ...

    # PnL & Fees / 盈亏与费用
    def fetch_realized_pnl(self, start_time: int) -> float:
        """Get realized PnL / 获取已实现盈亏"""
        ...

    def fetch_commission(self, start_time: int) -> float:
        """Get trading commission / 获取交易手续费"""
        ...

    def fetch_pnl_and_fees(self, start_time: int) -> Dict:
        """Get both PnL and fees / 获取盈亏和手续费"""
        ...

    # Error tracking / 错误跟踪
    last_order_error: Optional[Dict]
    """Latest order error information / 最新订单错误信息"""

    last_api_error: Optional[Dict]
    """Latest API error information / 最新 API 错误信息"""

    # Connection status / 连接状态
    is_connected: bool
    """Whether the exchange client is connected / 交易所客户端是否已连接"""

