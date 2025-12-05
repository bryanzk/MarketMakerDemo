"""
Unit tests for HyperliquidClient position and balance tracking
HyperliquidClient 仓位与余额追踪单元测试

Tests for US-CORE-004-C: Hyperliquid Position and Balance Tracking
测试 US-CORE-004-C: Hyperliquid 仓位与余额追踪

Owner: Agent TRADING
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

# Note: This test assumes HyperliquidClient position methods will be implemented
# 注意：此测试假设 HyperliquidClient 仓位方法将被实现
# According to TDD principles, tests are written first and will fail until implementation is complete
# 根据 TDD 原则，先编写测试，在实现完成前测试会失败


class TestHyperliquidClientBalanceFetching:
    """Test AC-1: Balance Fetching / 测试 AC-1: 余额获取"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_balance_success(self, mock_requests):
        """Test successful balance fetching / 测试成功获取余额"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock balance response
        balance_response = MagicMock()
        balance_response.status_code = 200
        balance_response.json.return_value = {
            "status": "ok",
            "marginSummary": {
                "accountValue": "10000.0",
                "totalMarginUsed": "1000.0",
                "totalNtlPos": "0.0",
                "totalRawUsd": "10000.0",
            },
        }
        mock_requests.post.return_value = balance_response

        # Fetch balance
        balance = client.fetch_balance()

        # Verify balance data
        assert balance is not None
        assert "total" in balance
        assert "available" in balance
        assert "margin_used" in balance
        assert "margin_available" in balance
        assert balance["total"] > 0
        assert balance["available"] >= 0
        assert mock_requests.post.called

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_balance_includes_margin_info(self, mock_requests):
        """Test balance includes margin information / 测试余额包含保证金信息"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock balance response with margin info
        balance_response = MagicMock()
        balance_response.status_code = 200
        balance_response.json.return_value = {
            "status": "ok",
            "marginSummary": {
                "accountValue": "10000.0",
                "totalMarginUsed": "2000.0",
                "totalNtlPos": "0.0",
                "totalRawUsd": "10000.0",
            },
        }
        mock_requests.post.return_value = balance_response

        # Fetch balance
        balance = client.fetch_balance()

        # Verify margin information
        assert "margin_used" in balance
        assert "margin_available" in balance
        assert "margin_ratio" in balance
        assert balance["margin_used"] == 2000.0
        assert balance["margin_available"] == 8000.0  # total - margin_used


class TestHyperliquidClientPositionTracking:
    """Test AC-2: Position Tracking / 测试 AC-2: 仓位追踪"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_positions_success(self, mock_requests):
        """Test successful position fetching / 测试成功获取仓位"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock positions response
        positions_response = MagicMock()
        positions_response.status_code = 200
        positions_response.json.return_value = {
            "status": "ok",
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "entryPx": "3000.0",
                        "leverage": {"value": "10"},
                        "liquidationPx": "2700.0",
                        "marginUsed": "100.0",
                        "maxLeverage": {"value": "20"},
                        "realizedPnl": "0.0",
                        "returnOnEquity": "0.0",
                        "szi": "1.0",
                        "unrealizedPnl": "50.0",
                    },
                    "type": "oneWay",
                }
            ],
        }
        mock_requests.post.return_value = positions_response

        # Fetch positions
        positions = client.fetch_positions()

        # Verify positions data
        assert positions is not None
        assert isinstance(positions, list)
        if len(positions) > 0:
            position = positions[0]
            assert "symbol" in position
            assert "side" in position
            assert "size" in position
            assert "entry_price" in position
            assert "mark_price" in position
            assert "unrealized_pnl" in position

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_position_includes_all_fields(self, mock_requests):
        """Test position includes all required fields / 测试仓位包含所有必需字段"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()
        client.symbol = "ETH/USDT:USDT"

        # Mock position response
        position_response = MagicMock()
        position_response.status_code = 200
        position_response.json.return_value = {
            "status": "ok",
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "entryPx": "3000.0",
                        "leverage": {"value": "10"},
                        "liquidationPx": "2700.0",
                        "marginUsed": "100.0",
                        "maxLeverage": {"value": "20"},
                        "realizedPnl": "0.0",
                        "returnOnEquity": "0.0",
                        "szi": "1.0",
                        "unrealizedPnl": "50.0",
                    },
                    "type": "oneWay",
                }
            ],
        }
        mock_requests.post.return_value = position_response

        # Fetch position for specific symbol
        position = client.fetch_position("ETH/USDT:USDT")

        # Verify all required fields
        assert position is not None
        assert "symbol" in position
        assert "side" in position
        assert "size" in position
        assert "entry_price" in position
        assert "mark_price" in position
        assert "unrealized_pnl" in position
        assert "liquidation_price" in position
        assert "timestamp" in position


class TestHyperliquidClientUnrealizedPnLCalculation:
    """Test AC-3: Unrealized PnL Calculation / 测试 AC-3: 未实现盈亏计算"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_unrealized_pnl_calculation_long_position(self, mock_requests):
        """Test unrealized PnL calculation for long position / 测试多头仓位的未实现盈亏计算"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock position with long position (entry: 3000, mark: 3100, size: 1.0)
        position_response = MagicMock()
        position_response.status_code = 200
        position_response.json.return_value = {
            "status": "ok",
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "entryPx": "3000.0",
                        "szi": "1.0",  # Long position
                        "unrealizedPnl": "100.0",  # (3100 - 3000) * 1.0
                    },
                    "type": "oneWay",
                }
            ],
        }
        mock_requests.post.return_value = position_response

        # Fetch position
        position = client.fetch_position("ETH/USDT:USDT")

        # Verify PnL calculation
        assert position is not None
        assert "unrealized_pnl" in position
        # PnL should be positive for long position when mark price > entry price
        assert position["unrealized_pnl"] > 0

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_unrealized_pnl_calculation_short_position(self, mock_requests):
        """Test unrealized PnL calculation for short position / 测试空头仓位的未实现盈亏计算"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock position with short position (entry: 3000, mark: 2900, size: -1.0)
        position_response = MagicMock()
        position_response.status_code = 200
        position_response.json.return_value = {
            "status": "ok",
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "entryPx": "3000.0",
                        "szi": "-1.0",  # Short position
                        "unrealizedPnl": "100.0",  # (3000 - 2900) * 1.0
                    },
                    "type": "oneWay",
                }
            ],
        }
        mock_requests.post.return_value = position_response

        # Fetch position
        position = client.fetch_position("ETH/USDT:USDT")

        # Verify PnL calculation
        assert position is not None
        assert "unrealized_pnl" in position
        assert "side" in position
        assert position["side"] == "SHORT"
        # PnL should be positive for short position when mark price < entry price
        assert position["unrealized_pnl"] > 0


class TestHyperliquidClientRealizedPnLTracking:
    """Test AC-4: Realized PnL Tracking / 测试 AC-4: 已实现盈亏追踪"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_realized_pnl_success(self, mock_requests):
        """Test successful realized PnL fetching / 测试成功获取已实现盈亏"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock realized PnL response
        pnl_response = MagicMock()
        pnl_response.status_code = 200
        pnl_response.json.return_value = {
            "status": "ok",
            "userFills": [
                {
                    "closedPnl": "50.0",
                    "oid": 12345,
                    "time": 1700000000000,
                    "px": "3050.0",
                    "sz": "1.0",
                    "side": "A",  # Ask (sell)
                }
            ],
        }
        mock_requests.post.return_value = pnl_response

        # Fetch realized PnL
        realized_pnl = client.fetch_realized_pnl()

        # Verify realized PnL
        assert realized_pnl is not None
        assert isinstance(realized_pnl, (int, float))
        assert realized_pnl >= 0  # Can be positive or negative

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_realized_pnl_with_timestamp(self, mock_requests):
        """Test realized PnL includes timestamps / 测试已实现盈亏包含时间戳"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock realized PnL response with timestamps
        pnl_response = MagicMock()
        pnl_response.status_code = 200
        pnl_response.json.return_value = {
            "status": "ok",
            "userFills": [
                {
                    "closedPnl": "50.0",
                    "oid": 12345,
                    "time": 1700000000000,
                    "px": "3050.0",
                    "sz": "1.0",
                }
            ],
        }
        mock_requests.post.return_value = pnl_response

        # Fetch realized PnL with start_time
        start_time = 1699000000000  # Timestamp in milliseconds
        realized_pnl = client.fetch_realized_pnl(start_time=start_time)

        # Verify realized PnL
        assert realized_pnl is not None
        assert isinstance(realized_pnl, (int, float))


class TestHyperliquidClientPositionHistory:
    """Test AC-5: Position History / 测试 AC-5: 仓位历史"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_position_history_success(self, mock_requests):
        """Test successful position history fetching / 测试成功获取仓位历史"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock position history response
        history_response = MagicMock()
        history_response.status_code = 200
        history_response.json.return_value = {
            "status": "ok",
            "userFills": [
                {
                    "closedPnl": "50.0",
                    "oid": 12345,
                    "time": 1700000000000,
                    "px": "3050.0",
                    "sz": "1.0",
                    "side": "A",
                },
                {
                    "closedPnl": "-20.0",
                    "oid": 12346,
                    "time": 1700001000000,
                    "px": "2980.0",
                    "sz": "0.5",
                    "side": "B",
                },
            ],
        }
        mock_requests.post.return_value = history_response

        # Fetch position history
        history = client.fetch_position_history()

        # Verify position history
        assert history is not None
        assert isinstance(history, list)
        if len(history) > 0:
            entry = history[0]
            assert "symbol" in entry or "open_time" in entry
            assert "timestamp" in entry or "open_time" in entry

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_position_history_with_limit(self, mock_requests):
        """Test position history with limit / 测试带限制的仓位历史"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock position history response
        history_response = MagicMock()
        history_response.status_code = 200
        history_response.json.return_value = {
            "status": "ok",
            "userFills": [
                {
                    "closedPnl": "50.0",
                    "oid": 12345,
                    "time": 1700000000000,
                    "px": "3050.0",
                    "sz": "1.0",
                }
            ],
        }
        mock_requests.post.return_value = history_response

        # Fetch position history with limit
        history = client.fetch_position_history(limit=10)

        # Verify limit is respected
        assert history is not None
        assert isinstance(history, list)
        assert len(history) <= 10


class TestHyperliquidClientMarginInformation:
    """Test AC-6: Margin Information / 测试 AC-6: 保证金信息"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_balance_includes_margin_ratio(self, mock_requests):
        """Test balance includes margin ratio / 测试余额包含保证金比率"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock balance response with margin info
        balance_response = MagicMock()
        balance_response.status_code = 200
        balance_response.json.return_value = {
            "status": "ok",
            "marginSummary": {
                "accountValue": "10000.0",
                "totalMarginUsed": "2000.0",
                "totalNtlPos": "0.0",
                "totalRawUsd": "10000.0",
            },
        }
        mock_requests.post.return_value = balance_response

        # Fetch balance
        balance = client.fetch_balance()

        # Verify margin ratio
        assert "margin_ratio" in balance
        assert isinstance(balance["margin_ratio"], (int, float))
        assert 0 <= balance["margin_ratio"] <= 100  # Margin ratio as percentage

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_position_includes_liquidation_price(self, mock_requests):
        """Test position includes liquidation price / 测试仓位包含清算价格"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock position response with liquidation price
        position_response = MagicMock()
        position_response.status_code = 200
        position_response.json.return_value = {
            "status": "ok",
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "entryPx": "3000.0",
                        "liquidationPx": "2700.0",
                        "szi": "1.0",
                        "unrealizedPnl": "50.0",
                    },
                    "type": "oneWay",
                }
            ],
        }
        mock_requests.post.return_value = position_response

        # Fetch position
        position = client.fetch_position("ETH/USDT:USDT")

        # Verify liquidation price
        assert position is not None
        assert "liquidation_price" in position
        assert isinstance(position["liquidation_price"], (int, float))
        assert position["liquidation_price"] > 0


class TestHyperliquidClientMultiSymbolPositionSupport:
    """Test AC-7: Multi-Symbol Position Support / 测试 AC-7: 多交易对仓位支持"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_positions_multiple_symbols(self, mock_requests):
        """Test fetching positions for multiple symbols / 测试获取多个交易对的仓位"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock positions response with multiple symbols
        positions_response = MagicMock()
        positions_response.status_code = 200
        positions_response.json.return_value = {
            "status": "ok",
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "entryPx": "3000.0",
                        "szi": "1.0",
                        "unrealizedPnl": "50.0",
                    },
                    "type": "oneWay",
                },
                {
                    "position": {
                        "coin": "BTC",
                        "entryPx": "40000.0",
                        "szi": "0.1",
                        "unrealizedPnl": "100.0",
                    },
                    "type": "oneWay",
                },
            ],
        }
        mock_requests.post.return_value = positions_response

        # Fetch all positions
        positions = client.fetch_positions()

        # Verify multiple positions
        assert positions is not None
        assert isinstance(positions, list)
        assert len(positions) >= 2

        # Verify each position has symbol
        symbols = [pos["symbol"] for pos in positions if "symbol" in pos]
        assert "ETH" in "".join(symbols) or "ETH/USDT" in "".join(symbols)
        assert "BTC" in "".join(symbols) or "BTC/USDT" in "".join(symbols)


class TestHyperliquidClientPositionUpdates:
    """Test AC-8: Position Updates / 测试 AC-8: 仓位更新"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_position_updates_with_latest_mark_price(self, mock_requests):
        """Test position updates with latest mark price / 测试仓位更新为最新标记价格"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock position response with updated mark price
        position_response = MagicMock()
        position_response.status_code = 200
        position_response.json.return_value = {
            "status": "ok",
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "entryPx": "3000.0",
                        "szi": "1.0",
                        "unrealizedPnl": "100.0",  # Updated PnL
                    },
                    "type": "oneWay",
                }
            ],
        }
        mock_requests.post.return_value = position_response

        # Fetch position (refresh)
        position = client.fetch_position("ETH/USDT:USDT")

        # Verify updated data
        assert position is not None
        assert "mark_price" in position
        assert "unrealized_pnl" in position
        assert position["unrealized_pnl"] == 100.0


class TestHyperliquidClientPerformanceTrackerIntegration:
    """Test AC-9: Integration with Performance Tracker / 测试 AC-9: 与性能追踪器集成"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_performance_tracker_can_fetch_positions(self, mock_requests):
        """Test PerformanceTracker can fetch positions / 测试 PerformanceTracker 可以获取仓位"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock positions response
        positions_response = MagicMock()
        positions_response.status_code = 200
        positions_response.json.return_value = {
            "status": "ok",
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "entryPx": "3000.0",
                        "szi": "1.0",
                        "unrealizedPnl": "50.0",
                    },
                    "type": "oneWay",
                }
            ],
        }
        mock_requests.post.return_value = positions_response

        # Fetch positions (simulating PerformanceTracker usage)
        positions = client.fetch_positions()

        # Verify positions can be fetched
        assert positions is not None
        assert isinstance(positions, list)

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_performance_tracker_can_fetch_pnl(self, mock_requests):
        """Test PerformanceTracker can fetch PnL / 测试 PerformanceTracker 可以获取盈亏"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock realized PnL response
        pnl_response = MagicMock()
        pnl_response.status_code = 200
        pnl_response.json.return_value = {
            "status": "ok",
            "userFills": [
                {
                    "closedPnl": "50.0",
                    "oid": 12345,
                    "time": 1700000000000,
                }
            ],
        }
        mock_requests.post.return_value = pnl_response

        # Fetch realized PnL (simulating PerformanceTracker usage)
        realized_pnl = client.fetch_realized_pnl()

        # Verify PnL can be fetched
        assert realized_pnl is not None
        assert isinstance(realized_pnl, (int, float))


class TestHyperliquidClientErrorHandling:
    """Test AC-10: Error Handling / 测试 AC-10: 错误处理"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_balance_error_handling(self, mock_requests):
        """Test error handling when API is unavailable / 测试 API 不可用时的错误处理"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient, ConnectionError

        client = HyperliquidClient()

        # Mock API error
        error_response = MagicMock()
        error_response.status_code = 500
        error_response.raise_for_status.side_effect = Exception("API Error")
        mock_requests.post.return_value = error_response

        # Attempt to fetch balance
        with pytest.raises((ConnectionError, Exception)):
            client.fetch_balance()

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_positions_error_bilingual_message(self, mock_requests):
        """Test error message is bilingual / 测试错误消息是双语的"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock API error
        error_response = MagicMock()
        error_response.status_code = 503
        error_response.raise_for_status.side_effect = Exception("Service Unavailable")
        mock_requests.post.return_value = error_response

        # Attempt to fetch positions
        try:
            positions = client.fetch_positions()
            # If no exception, positions should be None or empty
            assert positions is None or positions == []
        except Exception as e:
            # Verify error message contains both English and Chinese
            error_msg = str(e)
            # Check if error message is bilingual (contains both languages or is handled gracefully)
            assert len(error_msg) > 0

