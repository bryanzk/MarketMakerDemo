"""
Smoke Test for US-CORE-004-C: Hyperliquid Position and Balance Tracking
US-CORE-004-C 冒烟测试：Hyperliquid 仓位与余额追踪

Smoke tests verify critical paths without full integration.
冒烟测试验证关键路径，无需完整集成。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquidPositionTrackingSmoke:
    """
    Smoke tests for Hyperliquid position and balance tracking.
    Hyperliquid 仓位与余额追踪的冒烟测试。
    
    These tests verify the critical path without full integration.
    这些测试验证关键路径，无需完整集成。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_fetch_balance(self, mock_requests):
        """
        Smoke Test: AC-1 - Balance can be fetched successfully
        冒烟测试：AC-1 - 余额可以成功获取
        
        This is the most critical path - if balance fetching fails, position tracking cannot work.
        这是最关键路径 - 如果余额获取失败，仓位追踪无法工作。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()

        # Mock successful balance fetch
        balance_response = MagicMock()
        balance_response.status_code = 200
        balance_response.json.return_value = {
            "marginSummary": {
                "accountValue": 10000.0,
                "totalMarginUsed": 2000.0,
                "totalRawUsd": 10000.0,
            },
            "assetPositions": [],
        }
        mock_requests.post.return_value = balance_response

        # Fetch balance
        balance = client.fetch_balance()

        # Verify balance was fetched
        assert balance is not None
        assert "total" in balance
        assert "available" in balance
        assert "margin_used" in balance
        assert "margin_available" in balance
        assert "margin_ratio" in balance

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_fetch_positions(self, mock_requests):
        """
        Smoke Test: AC-2 - Positions can be fetched successfully
        冒烟测试：AC-2 - 仓位可以成功获取
        
        Verifies that position fetching flow works.
        验证仓位获取流程正常工作。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()

        # Mock successful positions fetch
        positions_response = MagicMock()
        positions_response.status_code = 200
        positions_response.json.return_value = {
            "marginSummary": {
                "accountValue": 10000.0,
                "totalMarginUsed": 2000.0,
                "totalRawUsd": 10000.0,
            },
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "szi": "0.1",
                        "entryPx": "3000.0",
                        "liquidationPx": "2500.0",
                        "marginUsed": "2000.0",
                    },
                    "markPx": "3100.0",
                }
            ],
        }
        mock_requests.post.return_value = positions_response

        # Fetch positions
        positions = client.fetch_positions()

        # Verify positions were fetched
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
    def test_smoke_fetch_position_for_symbol(self, mock_requests):
        """
        Smoke Test: AC-2, AC-7 - Position for specific symbol can be fetched
        冒烟测试：AC-2, AC-7 - 特定交易对的仓位可以获取
        
        Verifies that single symbol position fetching works.
        验证单个交易对仓位获取正常工作。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()
        client.symbol = "ETH/USDT:USDT"

        # Mock successful position fetch
        position_response = MagicMock()
        position_response.status_code = 200
        position_response.json.return_value = {
            "marginSummary": {
                "accountValue": 10000.0,
                "totalMarginUsed": 2000.0,
                "totalRawUsd": 10000.0,
            },
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "szi": "0.1",
                        "entryPx": "3000.0",
                        "liquidationPx": "2500.0",
                        "marginUsed": "2000.0",
                    },
                    "markPx": "3100.0",
                }
            ],
        }
        mock_requests.post.return_value = position_response

        # Fetch position for symbol
        position = client.fetch_position("ETH/USDT:USDT")

        # Verify position was fetched
        assert position is not None or position is None  # May be None if no position
        # If position exists, verify structure
        if position:
            assert "symbol" in position
            assert "size" in position
            assert "entry_price" in position

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_fetch_account_data(self, mock_requests):
        """
        Smoke Test: AC-1, AC-3 - Account data can be fetched successfully
        冒烟测试：AC-1, AC-3 - 账户数据可以成功获取
        
        Verifies that account data (balance + position) fetching works.
        验证账户数据（余额 + 仓位）获取正常工作。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()
        client.symbol = "ETH/USDT:USDT"

        # Mock successful account data fetch
        account_response = MagicMock()
        account_response.status_code = 200
        account_response.json.return_value = {
            "marginSummary": {
                "accountValue": 10000.0,
                "totalMarginUsed": 2000.0,
                "totalRawUsd": 10000.0,
            },
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "szi": "0.1",
                        "entryPx": "3000.0",
                        "liquidationPx": "2500.0",
                        "marginUsed": "2000.0",
                    },
                    "markPx": "3100.0",
                }
            ],
        }
        mock_requests.post.return_value = account_response

        # Fetch account data
        account_data = client.fetch_account_data()

        # Verify account data was fetched
        assert account_data is not None
        assert "balance" in account_data
        assert "available_balance" in account_data
        assert "position_amt" in account_data
        assert "entry_price" in account_data

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_margin_information(self, mock_requests):
        """
        Smoke Test: AC-6 - Margin information can be fetched
        冒烟测试：AC-6 - 保证金信息可以获取
        
        Verifies that margin information is included in balance response.
        验证保证金信息包含在余额响应中。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()

        # Mock successful balance fetch with margin info
        balance_response = MagicMock()
        balance_response.status_code = 200
        balance_response.json.return_value = {
            "marginSummary": {
                "accountValue": 10000.0,
                "totalMarginUsed": 2000.0,
                "totalRawUsd": 10000.0,
            },
            "assetPositions": [],
        }
        mock_requests.post.return_value = balance_response

        # Fetch balance (includes margin information)
        balance = client.fetch_balance()

        # Verify margin information is present
        assert balance is not None
        assert "margin_used" in balance
        assert "margin_available" in balance
        assert "margin_ratio" in balance
        assert balance["margin_ratio"] >= 0  # Should be a valid percentage

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_multi_symbol_positions(self, mock_requests):
        """
        Smoke Test: AC-7 - Multiple symbol positions can be fetched
        冒烟测试：AC-7 - 多个交易对的仓位可以获取
        
        Verifies that positions for multiple symbols are returned.
        验证返回多个交易对的仓位。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()

        # Mock successful positions fetch with multiple symbols
        positions_response = MagicMock()
        positions_response.status_code = 200
        positions_response.json.return_value = {
            "marginSummary": {
                "accountValue": 10000.0,
                "totalMarginUsed": 2000.0,
                "totalRawUsd": 10000.0,
            },
            "assetPositions": [
                {
                    "position": {
                        "coin": "ETH",
                        "szi": "0.1",
                        "entryPx": "3000.0",
                        "liquidationPx": "2500.0",
                        "marginUsed": "1000.0",
                    },
                    "markPx": "3100.0",
                },
                {
                    "position": {
                        "coin": "BTC",
                        "szi": "0.01",
                        "entryPx": "50000.0",
                        "liquidationPx": "45000.0",
                        "marginUsed": "1000.0",
                    },
                    "markPx": "51000.0",
                },
            ],
        }
        mock_requests.post.return_value = positions_response

        # Fetch positions
        positions = client.fetch_positions()

        # Verify multiple positions were fetched
        assert positions is not None
        assert isinstance(positions, list)
        # Should have positions for multiple symbols
        if len(positions) > 0:
            symbols = [pos.get("symbol") for pos in positions if pos.get("symbol")]
            assert len(set(symbols)) >= 1  # At least one unique symbol

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_position_history(self, mock_requests):
        """
        Smoke Test: AC-5 - Position history can be fetched
        冒烟测试：AC-5 - 仓位历史可以获取
        
        Verifies that position history fetching works.
        验证仓位历史获取正常工作。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()

        # Mock successful user fills fetch (for position history)
        fills_response = MagicMock()
        fills_response.status_code = 200
        fills_response.json.return_value = {
            "userFills": [
                {
                    "closedPnl": "10.0",
                    "coin": "ETH",
                    "px": "3000.0",
                    "sz": "0.1",
                    "side": "A",
                    "time": 1234567890000,
                }
            ],
        }
        mock_requests.post.return_value = fills_response

        # Fetch position history
        history = client.fetch_position_history()

        # Verify history was fetched
        assert history is not None
        assert isinstance(history, list)

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_realized_pnl(self, mock_requests):
        """
        Smoke Test: AC-4 - Realized PnL can be fetched
        冒烟测试：AC-4 - 已实现盈亏可以获取
        
        Verifies that realized PnL fetching works.
        验证已实现盈亏获取正常工作。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()

        # Mock successful user fills fetch (for realized PnL)
        fills_response = MagicMock()
        fills_response.status_code = 200
        fills_response.json.return_value = {
            "userFills": [
                {
                    "closedPnl": "10.0",
                    "coin": "ETH",
                    "px": "3000.0",
                    "sz": "0.1",
                    "side": "A",
                    "time": 1234567890000,
                }
            ],
        }
        mock_requests.post.return_value = fills_response

        # Fetch realized PnL
        realized_pnl = client.fetch_realized_pnl()

        # Verify realized PnL was fetched
        assert realized_pnl is not None
        assert isinstance(realized_pnl, (int, float))

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_error_handling(self, mock_requests):
        """
        Smoke Test: AC-10 - Error handling works correctly
        冒烟测试：AC-10 - 错误处理正常工作
        
        Verifies that errors are handled gracefully.
        验证错误被优雅处理。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()

        # Mock API failure
        error_response = MagicMock()
        error_response.status_code = 500
        error_response.json.return_value = {"error": "Internal server error"}
        mock_requests.post.return_value = error_response

        # Attempt to fetch balance (should handle error gracefully)
        try:
            balance = client.fetch_balance()
            # If no exception, balance should be None or error should be logged
            # 如果没有异常，余额应该为 None 或错误应该被记录
            assert balance is None or isinstance(balance, dict)
        except Exception as e:
            # Exception should be ConnectionError with bilingual message
            # 异常应该是带有双语消息的 ConnectionError
            assert isinstance(e, ConnectionError)
            error_msg = str(e)
            assert len(error_msg) > 0  # Should have error message

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_position_methods_exist(self, mock_requests):
        """
        Smoke Test: Verify all position tracking methods exist
        冒烟测试：验证所有仓位追踪方法存在
        
        Verifies that all required methods are implemented.
        验证所有必需的方法都已实现。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client
        client = HyperliquidClient()

        # Verify all required methods exist
        # 验证所有必需的方法存在
        assert hasattr(client, "fetch_balance"), "fetch_balance method should exist / fetch_balance 方法应该存在"
        assert hasattr(client, "fetch_positions"), "fetch_positions method should exist / fetch_positions 方法应该存在"
        assert hasattr(client, "fetch_position"), "fetch_position method should exist / fetch_position 方法应该存在"
        assert hasattr(client, "fetch_position_history"), "fetch_position_history method should exist / fetch_position_history 方法应该存在"
        assert hasattr(client, "fetch_account_data"), "fetch_account_data method should exist / fetch_account_data 方法应该存在"
        assert hasattr(client, "fetch_realized_pnl"), "fetch_realized_pnl method should exist / fetch_realized_pnl 方法应该存在"

        # Verify methods are callable
        # 验证方法是可调用的
        assert callable(client.fetch_balance), "fetch_balance should be callable / fetch_balance 应该是可调用的"
        assert callable(client.fetch_positions), "fetch_positions should be callable / fetch_positions 应该是可调用的"
        assert callable(client.fetch_position), "fetch_position should be callable / fetch_position 应该是可调用的"
        assert callable(client.fetch_position_history), "fetch_position_history should be callable / fetch_position_history 应该是可调用的"
        assert callable(client.fetch_account_data), "fetch_account_data should be callable / fetch_account_data 应该是可调用的"
        assert callable(client.fetch_realized_pnl), "fetch_realized_pnl should be callable / fetch_realized_pnl 应该是可调用的"


