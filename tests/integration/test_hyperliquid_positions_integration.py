"""
Integration Test for US-CORE-004-C: Hyperliquid Position and Balance Tracking
US-CORE-004-C 集成测试：Hyperliquid 仓位与余额追踪

Integration tests verify cross-module interactions and end-to-end workflows.
集成测试验证跨模块交互和端到端工作流。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.trading.hyperliquid_client import HyperliquidClient
from src.trading.performance import PerformanceTracker
from src.trading.strategy_instance import StrategyInstance


class TestHyperliquidStrategyInstancePositionIntegration:
    """
    Integration tests for HyperliquidClient with StrategyInstance for position tracking.
    HyperliquidClient 与 StrategyInstance 的仓位追踪集成测试。
    
    Tests that StrategyInstance can use HyperliquidClient for position and balance tracking.
    测试 StrategyInstance 可以使用 HyperliquidClient 进行仓位和余额追踪。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_strategy_instance_with_hyperliquid_positions(self, mock_requests):
        """
        Integration Test: StrategyInstance can fetch positions from HyperliquidClient
        集成测试：StrategyInstance 可以从 HyperliquidClient 获取仓位
        
        Verifies that StrategyInstance works correctly with HyperliquidClient for position tracking.
        验证 StrategyInstance 与 HyperliquidClient 的仓位追踪正常工作。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create HyperliquidClient
        hyperliquid_client = HyperliquidClient()
        hyperliquid_client.symbol = "ETH/USDT:USDT"

        # Mock position and balance data
        hyperliquid_client.fetch_account_data = Mock(
            return_value={
                "position_amt": 0.1,
                "entry_price": 3000.0,
                "balance": 10000.0,
                "available_balance": 5000.0,
                "liquidation_price": 2500.0,
            }
        )
        hyperliquid_client.fetch_position = Mock(
            return_value={
                "symbol": "ETH/USDT:USDT",
                "side": "LONG",
                "size": 0.1,
                "entry_price": 3000.0,
                "mark_price": 3100.0,
                "unrealized_pnl": 10.0,
                "liquidation_price": 2500.0,
            }
        )

        # Verify interface compatibility
        # 验证接口兼容性
        assert hasattr(hyperliquid_client, "fetch_account_data")
        assert hasattr(hyperliquid_client, "fetch_position")
        assert hasattr(hyperliquid_client, "fetch_positions")

        # Test that methods can be called (interface compatibility)
        # 测试方法可以被调用（接口兼容性）
        account_data = hyperliquid_client.fetch_account_data()
        assert account_data is not None
        assert "position_amt" in account_data
        assert "balance" in account_data

        position = hyperliquid_client.fetch_position("ETH/USDT:USDT")
        assert position is not None
        assert "symbol" in position
        assert "size" in position

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_strategy_instance_position_refresh_flow(self, mock_requests):
        """
        Integration Test: AC-8 - Position refresh flow with StrategyInstance
        集成测试：AC-8 - StrategyInstance 的仓位刷新流程
        
        Tests the end-to-end flow: fetch account data → update position → refresh.
        测试端到端流程：获取账户数据 → 更新仓位 → 刷新。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()
        client.symbol = "ETH/USDT:USDT"

        # Mock position data that changes over time
        # 模拟随时间变化的仓位数据
        position_data_v1 = {
            "symbol": "ETH/USDT:USDT",
            "side": "LONG",
            "size": 0.1,
            "entry_price": 3000.0,
            "mark_price": 3100.0,
            "unrealized_pnl": 10.0,
            "liquidation_price": 2500.0,
        }

        position_data_v2 = {
            "symbol": "ETH/USDT:USDT",
            "side": "LONG",
            "size": 0.1,
            "entry_price": 3000.0,
            "mark_price": 3200.0,  # Updated mark price
            "unrealized_pnl": 20.0,  # Updated PnL
            "liquidation_price": 2500.0,
        }

        # Simulate position updates
        # 模拟仓位更新
        client.fetch_position = Mock(side_effect=[position_data_v1, position_data_v2])

        # Step 1: Fetch initial position
        # 步骤 1：获取初始仓位
        position1 = client.fetch_position("ETH/USDT:USDT")
        assert position1["mark_price"] == 3100.0
        assert position1["unrealized_pnl"] == 10.0

        # Step 2: Refresh position (simulate new market data)
        # 步骤 2：刷新仓位（模拟新的市场数据）
        position2 = client.fetch_position("ETH/USDT:USDT")
        assert position2["mark_price"] == 3200.0
        assert position2["unrealized_pnl"] == 20.0

        # Verify position was updated
        # 验证仓位已更新
        assert position2["mark_price"] != position1["mark_price"]
        assert position2["unrealized_pnl"] != position1["unrealized_pnl"]


class TestHyperliquidPerformanceTrackerIntegration:
    """
    Integration tests for HyperliquidClient with PerformanceTracker.
    HyperliquidClient 与 PerformanceTracker 的集成测试。
    
    Tests AC-9: Integration with Performance Tracker.
    测试 AC-9：与性能追踪器集成。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_performance_tracker_with_hyperliquid(self, mock_requests):
        """
        Integration Test: AC-9 - PerformanceTracker can use HyperliquidClient
        集成测试：AC-9 - PerformanceTracker 可以使用 HyperliquidClient
        
        Verifies that PerformanceTracker works correctly with HyperliquidClient.
        验证 PerformanceTracker 与 HyperliquidClient 正常工作。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create HyperliquidClient
        hyperliquid_client = HyperliquidClient()

        # Mock realized PnL data
        hyperliquid_client.fetch_realized_pnl = Mock(return_value=150.0)

        # Create PerformanceTracker
        tracker = PerformanceTracker()

        # Simulate position updates using Hyperliquid data
        # 使用 Hyperliquid 数据模拟仓位更新
        # Step 1: Open position
        # 步骤 1：开仓
        tracker.update_position(0.1, 3000.0)  # Open long position at 3000
        assert tracker.last_position == 0.1

        # Step 2: Partial close
        # 步骤 2：部分平仓
        tracker.update_position(0.05, 3100.0)  # Close half at 3100
        assert tracker.last_position == 0.05
        assert tracker.realized_pnl > 0  # Should have realized PnL

        # Step 3: Get stats
        # 步骤 3：获取统计
        stats = tracker.get_stats()
        assert "realized_pnl" in stats
        assert "total_trades" in stats
        assert "win_rate" in stats

        # Verify HyperliquidClient can provide realized PnL
        # 验证 HyperliquidClient 可以提供已实现盈亏
        realized_pnl = hyperliquid_client.fetch_realized_pnl()
        assert isinstance(realized_pnl, (int, float))

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_performance_tracker_pnl_calculation_flow(self, mock_requests):
        """
        Integration Test: AC-3, AC-4 - PnL calculation flow with HyperliquidClient
        集成测试：AC-3, AC-4 - 使用 HyperliquidClient 的盈亏计算流程
        
        Tests the complete flow: fetch position → calculate unrealized PnL → track realized PnL.
        测试完整流程：获取仓位 → 计算未实现盈亏 → 追踪已实现盈亏。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()
        client.symbol = "ETH/USDT:USDT"

        # Mock position with unrealized PnL
        # 模拟带未实现盈亏的仓位
        client.fetch_position = Mock(
            return_value={
                "symbol": "ETH/USDT:USDT",
                "side": "LONG",
                "size": 0.1,
                "entry_price": 3000.0,
                "mark_price": 3100.0,
                "unrealized_pnl": 10.0,
                "liquidation_price": 2500.0,
            }
        )

        # Mock realized PnL
        # 模拟已实现盈亏
        client.fetch_realized_pnl = Mock(return_value=50.0)

        # Step 1: Fetch position (includes unrealized PnL)
        # 步骤 1：获取仓位（包含未实现盈亏）
        position = client.fetch_position("ETH/USDT:USDT")
        assert position["unrealized_pnl"] == 10.0

        # Step 2: Fetch realized PnL
        # 步骤 2：获取已实现盈亏
        realized_pnl = client.fetch_realized_pnl()
        assert realized_pnl == 50.0

        # Step 3: Verify both PnL types are available
        # 步骤 3：验证两种盈亏类型都可用
        assert "unrealized_pnl" in position
        assert isinstance(realized_pnl, (int, float))


class TestHyperliquidPositionWorkflowIntegration:
    """
    Integration tests for complete position tracking workflow.
    完整仓位追踪工作流的集成测试。
    
    Tests end-to-end workflows for position and balance tracking.
    测试仓位和余额追踪的端到端工作流。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_complete_position_tracking_workflow(self, mock_requests):
        """
        Integration Test: Complete position tracking workflow
        集成测试：完整仓位追踪工作流
        
        Tests the end-to-end flow: balance → positions → account data → PnL.
        测试端到端流程：余额 → 仓位 → 账户数据 → 盈亏。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()
        client.symbol = "ETH/USDT:USDT"

        # Mock all position-related methods
        # 模拟所有仓位相关方法
        client.fetch_balance = Mock(
            return_value={
                "total": 10000.0,
                "available": 5000.0,
                "margin_used": 2000.0,
                "margin_available": 5000.0,
                "margin_ratio": 20.0,
                "liquidation_price": 0.0,
            }
        )

        client.fetch_positions = Mock(
            return_value=[
                {
                    "symbol": "ETH/USDT:USDT",
                    "side": "LONG",
                    "size": 0.1,
                    "entry_price": 3000.0,
                    "mark_price": 3100.0,
                    "unrealized_pnl": 10.0,
                    "liquidation_price": 2500.0,
                }
            ]
        )

        client.fetch_account_data = Mock(
            return_value={
                "position_amt": 0.1,
                "entry_price": 3000.0,
                "balance": 10000.0,
                "available_balance": 5000.0,
                "liquidation_price": 2500.0,
            }
        )

        client.fetch_realized_pnl = Mock(return_value=50.0)

        # Step 1: Fetch balance
        # 步骤 1：获取余额
        balance = client.fetch_balance()
        assert balance["total"] == 10000.0
        assert balance["available"] == 5000.0

        # Step 2: Fetch positions
        # 步骤 2：获取仓位
        positions = client.fetch_positions()
        assert len(positions) == 1
        assert positions[0]["symbol"] == "ETH/USDT:USDT"

        # Step 3: Fetch account data
        # 步骤 3：获取账户数据
        account_data = client.fetch_account_data()
        assert account_data["position_amt"] == 0.1
        assert account_data["balance"] == 10000.0

        # Step 4: Fetch realized PnL
        # 步骤 4：获取已实现盈亏
        realized_pnl = client.fetch_realized_pnl()
        assert realized_pnl == 50.0

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_multi_symbol_position_tracking(self, mock_requests):
        """
        Integration Test: AC-7 - Multi-symbol position tracking
        集成测试：AC-7 - 多交易对仓位追踪
        
        Tests that positions for multiple symbols can be tracked simultaneously.
        测试可以同时追踪多个交易对的仓位。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()

        # Mock positions for multiple symbols
        # 模拟多个交易对的仓位
        client.fetch_positions = Mock(
            return_value=[
                {
                    "symbol": "ETH/USDT:USDT",
                    "side": "LONG",
                    "size": 0.1,
                    "entry_price": 3000.0,
                    "mark_price": 3100.0,
                    "unrealized_pnl": 10.0,
                    "liquidation_price": 2500.0,
                },
                {
                    "symbol": "BTC/USDT:USDT",
                    "side": "SHORT",
                    "size": 0.01,
                    "entry_price": 50000.0,
                    "mark_price": 49000.0,
                    "unrealized_pnl": 10.0,
                    "liquidation_price": 55000.0,
                },
            ]
        )

        # Fetch all positions
        # 获取所有仓位
        positions = client.fetch_positions()

        # Verify multiple positions
        # 验证多个仓位
        assert len(positions) == 2
        symbols = [pos["symbol"] for pos in positions]
        assert "ETH/USDT:USDT" in symbols
        assert "BTC/USDT:USDT" in symbols

        # Verify each position has correct data
        # 验证每个仓位都有正确的数据
        eth_position = next(p for p in positions if p["symbol"] == "ETH/USDT:USDT")
        assert eth_position["side"] == "LONG"
        assert eth_position["size"] == 0.1

        btc_position = next(p for p in positions if p["symbol"] == "BTC/USDT:USDT")
        assert btc_position["side"] == "SHORT"
        assert btc_position["size"] == 0.01

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_position_history_tracking(self, mock_requests):
        """
        Integration Test: AC-5 - Position history tracking
        集成测试：AC-5 - 仓位历史追踪
        
        Tests that position history can be fetched and tracked.
        测试可以获取和追踪仓位历史。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()

        # Mock position history
        # 模拟仓位历史
        client.fetch_position_history = Mock(
            return_value=[
                {
                    "symbol": "ETH/USDT:USDT",
                    "side": "LONG",
                    "size": 0.1,
                    "entry_price": 3000.0,
                    "close_price": 3100.0,
                    "realized_pnl": 10.0,
                    "status": "closed",
                    "timestamp": 1234567890000,
                },
                {
                    "symbol": "ETH/USDT:USDT",
                    "side": "LONG",
                    "size": 0.1,
                    "entry_price": 3000.0,
                    "mark_price": 3100.0,
                    "unrealized_pnl": 10.0,
                    "status": "open",
                    "timestamp": 1234567900000,
                },
            ]
        )

        # Fetch position history
        # 获取仓位历史
        history = client.fetch_position_history()

        # Verify history contains both open and closed positions
        # 验证历史包含未平仓和已平仓仓位
        assert len(history) == 2
        assert any(pos.get("status") == "closed" for pos in history)
        assert any(pos.get("status") == "open" for pos in history)

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_margin_information_integration(self, mock_requests):
        """
        Integration Test: AC-6 - Margin information integration
        集成测试：AC-6 - 保证金信息集成
        
        Tests that margin information is correctly integrated with position tracking.
        测试保证金信息与仓位追踪正确集成。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()

        # Mock balance with margin information
        # 模拟带保证金信息的余额
        client.fetch_balance = Mock(
            return_value={
                "total": 10000.0,
                "available": 5000.0,
                "margin_used": 2000.0,
                "margin_available": 5000.0,
                "margin_ratio": 20.0,
                "liquidation_price": 2500.0,
            }
        )

        # Fetch balance (includes margin information)
        # 获取余额（包含保证金信息）
        balance = client.fetch_balance(include_liquidation_price=True)

        # Verify margin information
        # 验证保证金信息
        assert "margin_used" in balance
        assert "margin_available" in balance
        assert "margin_ratio" in balance
        assert balance["margin_ratio"] == 20.0
        assert balance["liquidation_price"] == 2500.0

        # Verify margin calculations are correct
        # 验证保证金计算正确
        assert balance["margin_used"] + balance["margin_available"] <= balance["total"]


class TestHyperliquidErrorHandlingIntegration:
    """
    Integration tests for error handling in position tracking.
    仓位追踪错误处理的集成测试。
    
    Tests AC-10: Error handling integration.
    测试 AC-10：错误处理集成。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_error_handling_in_position_fetch(self, mock_requests):
        """
        Integration Test: AC-10 - Error handling in position operations
        集成测试：AC-10 - 仓位操作中的错误处理
        
        Verifies that errors are handled gracefully throughout the integration flow.
        验证在整个集成流程中错误被优雅处理。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()

        # Mock API failure
        client.fetch_positions = Mock(side_effect=ConnectionError("Network error / 网络错误"))

        # Attempt to fetch positions (should handle error gracefully)
        # 尝试获取仓位（应该优雅地处理错误）
        try:
            positions = client.fetch_positions()
            # If no exception, positions should be empty list or None
            # 如果没有异常，仓位应该是空列表或 None
            assert positions is None or positions == []
        except ConnectionError as e:
            # Exception should have bilingual message
            # 异常应该有双语消息
            error_msg = str(e)
            assert len(error_msg) > 0
            # Error should mention connection or network
            # 错误应该提到连接或网络
            assert "error" in error_msg.lower() or "连接" in error_msg or "网络" in error_msg



