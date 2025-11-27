"""
Portfolio Sync Tests / 组合同步测试

测试 _sync_portfolio_with_bot() 函数的多策略实例同步功能。
"""

from collections import deque
from unittest.mock import MagicMock, patch

import pytest

from alphaloop.portfolio.manager import PortfolioManager, StrategyStatus


class TestPortfolioSync:
    """测试组合同步功能"""

    @pytest.fixture
    def portfolio_manager(self):
        """创建 PortfolioManager 实例"""
        pm = PortfolioManager(total_capital=10000.0)
        pm.register_strategy("fixed_spread", "Fixed Spread", allocation=0.6)
        pm.register_strategy("funding_rate", "Funding Rate", allocation=0.4)
        return pm

    @pytest.fixture
    def mock_strategy_instance(self):
        """创建模拟的策略实例"""
        instance = MagicMock()
        instance.strategy_id = "fixed_spread"
        instance.strategy_type = "fixed_spread"
        instance.running = True
        instance.use_real_exchange = True
        instance.order_history = deque([
            {"id": "ord1", "status": "filled", "pnl": 10.0},
            {"id": "ord2", "status": "placed"},
        ])
        
        # Mock exchange
        instance.exchange = MagicMock()
        instance.exchange.fetch_pnl_and_fees.return_value = {
            "realized_pnl": 100.0,
            "commission": 5.0,
            "net_pnl": 95.0,
        }
        instance.exchange.fetch_account_data.return_value = {
            "balance": 10000.0,
            "position_amt": 0.5,
        }
        
        return instance

    @pytest.fixture
    def mock_bot_engine(self, mock_strategy_instance):
        """创建模拟的 bot_engine"""
        bot = MagicMock()
        bot.strategy_instances = {
            "fixed_spread": mock_strategy_instance,
        }
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = []
        bot.data.calculate_metrics.return_value = {
            "sharpe_ratio": 2.0,
            "fill_rate": 0.9,
            "slippage_bps": 1.0,
        }
        return bot

    def test_sync_single_strategy_instance(self, portfolio_manager, mock_bot_engine, mock_strategy_instance):
        """测试同步单个策略实例"""
        import server
        
        # Mock get_default_exchange
        with patch.object(server, "get_default_exchange", return_value=mock_strategy_instance.exchange):
            with patch.object(server, "bot_engine", mock_bot_engine):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            server._sync_portfolio_with_bot()
        
        # 验证策略状态已更新为 LIVE
        strategy = portfolio_manager.strategies["fixed_spread"]
        assert strategy.status == StrategyStatus.LIVE
        
        # 验证指标已更新
        assert strategy.pnl == 100.0  # 从 exchange 获取的 PnL

    def test_sync_multiple_strategy_instances(self, portfolio_manager):
        """测试同步多个策略实例"""
        import server
        
        # 创建两个策略实例
        instance1 = MagicMock()
        instance1.strategy_id = "fixed_spread"
        instance1.strategy_type = "fixed_spread"
        instance1.running = True
        instance1.use_real_exchange = True
        instance1.order_history = deque()
        instance1.exchange = MagicMock()
        instance1.exchange.fetch_pnl_and_fees.return_value = {
            "realized_pnl": 150.0,
            "commission": 5.0,
            "net_pnl": 145.0,
        }
        instance1.exchange.fetch_account_data.return_value = {"balance": 10000.0}
        
        instance2 = MagicMock()
        instance2.strategy_id = "funding_rate"
        instance2.strategy_type = "funding_rate"
        instance2.running = True
        instance2.use_real_exchange = True
        instance2.order_history = deque()
        instance2.exchange = MagicMock()
        instance2.exchange.fetch_pnl_and_fees.return_value = {
            "realized_pnl": 80.0,
            "commission": 3.0,
            "net_pnl": 77.0,
        }
        instance2.exchange.fetch_account_data.return_value = {"balance": 10000.0}
        
        bot = MagicMock()
        bot.strategy_instances = {
            "fixed_spread": instance1,
            "funding_rate": instance2,
        }
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = []
        
        with patch.object(server, "get_default_exchange", return_value=instance1.exchange):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            server._sync_portfolio_with_bot()
        
        # 验证两个策略的状态都已更新
        assert portfolio_manager.strategies["fixed_spread"].status == StrategyStatus.LIVE
        assert portfolio_manager.strategies["funding_rate"].status == StrategyStatus.LIVE
        
        # 验证两个策略的 PnL 都已更新
        assert portfolio_manager.strategies["fixed_spread"].pnl == 150.0
        assert portfolio_manager.strategies["funding_rate"].pnl == 80.0

    def test_sync_preserves_paused_status(self, portfolio_manager):
        """测试同步时保留 PAUSED 状态"""
        import server
        
        # 设置策略为 PAUSED
        portfolio_manager.strategies["fixed_spread"].status = StrategyStatus.PAUSED
        
        instance = MagicMock()
        instance.strategy_id = "fixed_spread"
        instance.strategy_type = "fixed_spread"
        instance.running = True  # 实例在运行
        instance.use_real_exchange = True
        instance.order_history = deque()
        instance.exchange = MagicMock()
        instance.exchange.fetch_pnl_and_fees.return_value = {"realized_pnl": 100.0}
        instance.exchange.fetch_account_data.return_value = {"balance": 10000.0}
        
        bot = MagicMock()
        bot.strategy_instances = {"fixed_spread": instance}
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = []
        
        with patch.object(server, "get_default_exchange", return_value=instance.exchange):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            server._sync_portfolio_with_bot()
        
        # 验证 PAUSED 状态被保留（不会因为 running=True 而变为 LIVE）
        assert portfolio_manager.strategies["fixed_spread"].status == StrategyStatus.PAUSED

    def test_sync_stopped_instance(self, portfolio_manager):
        """测试同步停止的实例"""
        import server
        
        instance = MagicMock()
        instance.strategy_id = "fixed_spread"
        instance.strategy_type = "fixed_spread"
        instance.running = False  # 实例未运行
        instance.use_real_exchange = True
        instance.order_history = deque()
        instance.exchange = MagicMock()
        instance.exchange.fetch_pnl_and_fees.return_value = {
            "realized_pnl": 0.0,
            "commission": 0.0,
            "net_pnl": 0.0,
        }
        instance.exchange.fetch_account_data.return_value = {
            "balance": 10000.0,
            "position_amt": 0.0,
        }
        
        bot = MagicMock()
        bot.strategy_instances = {"fixed_spread": instance}
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = []
        
        # 先设置为 LIVE
        portfolio_manager.strategies["fixed_spread"].status = StrategyStatus.LIVE
        
        with patch.object(server, "get_default_exchange", return_value=instance.exchange):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", False):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            server._sync_portfolio_with_bot()
        
        # 验证状态已更新为 STOPPED
        assert portfolio_manager.strategies["fixed_spread"].status == StrategyStatus.STOPPED

    def test_sync_fallback_to_shared_data(self, portfolio_manager):
        """测试当实例 exchange 不可用时回退到共享数据"""
        import server
        
        instance = MagicMock()
        instance.strategy_id = "fixed_spread"
        instance.strategy_type = "fixed_spread"
        instance.running = True
        instance.use_real_exchange = False  # 没有真实 exchange
        instance.order_history = deque()
        instance.exchange = None
        
        bot = MagicMock()
        bot.strategy_instances = {"fixed_spread": instance}
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = [
            {"pnl": 50.0, "strategy_id": "fixed_spread", "timestamp": 1000.0},
            {"pnl": 30.0, "strategy_id": "fixed_spread", "timestamp": 1100.0},
        ]
        bot.data.calculate_metrics.return_value = {
            "sharpe_ratio": 1.5,
            "fill_rate": 0.85,
            "slippage_bps": 2.0,
        }
        
        with patch.object(server, "get_default_exchange", return_value=None):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            server._sync_portfolio_with_bot()
        
        # 验证从共享数据获取了 PnL
        strategy = portfolio_manager.strategies["fixed_spread"]
        assert strategy.pnl == 80.0  # 50 + 30
        assert strategy.sharpe == 1.5
        assert strategy.fill_rate == 0.85

    def test_sync_calculates_metrics_from_order_history(self, portfolio_manager):
        """测试从订单历史计算指标"""
        import server
        
        instance = MagicMock()
        instance.strategy_id = "fixed_spread"
        instance.strategy_type = "fixed_spread"
        instance.running = True
        instance.use_real_exchange = True
        instance.order_history = deque([
            {"id": "ord1", "status": "filled"},
            {"id": "ord2", "status": "filled"},
            {"id": "ord3", "status": "placed"},
        ])
        instance.exchange = MagicMock()
        instance.exchange.fetch_pnl_and_fees.return_value = {"realized_pnl": 100.0}
        instance.exchange.fetch_account_data.return_value = {"balance": 10000.0}
        
        bot = MagicMock()
        bot.strategy_instances = {"fixed_spread": instance}
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = []
        
        with patch.object(server, "get_default_exchange", return_value=instance.exchange):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            server._sync_portfolio_with_bot()
        
        # 验证从订单历史计算了指标
        strategy = portfolio_manager.strategies["fixed_spread"]
        # fill_rate 应该是 2/3 = 0.67 (2 filled out of 3 placed)
        assert strategy.fill_rate == pytest.approx(0.67, rel=0.1)
        assert strategy.total_trades == 2  # 2 filled orders

    def test_sync_updates_total_capital(self, portfolio_manager):
        """测试同步更新总资金"""
        import server
        
        instance = MagicMock()
        instance.strategy_id = "fixed_spread"
        instance.strategy_type = "fixed_spread"
        instance.running = True
        instance.use_real_exchange = True
        instance.order_history = deque()
        instance.exchange = MagicMock()
        instance.exchange.fetch_pnl_and_fees.return_value = {"realized_pnl": 100.0}
        instance.exchange.fetch_account_data.return_value = {"balance": 15000.0}  # 新的余额
        
        bot = MagicMock()
        bot.strategy_instances = {"fixed_spread": instance}
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = []
        
        with patch.object(server, "get_default_exchange", return_value=instance.exchange):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            server._sync_portfolio_with_bot()
        
        # 验证总资金已更新
        assert portfolio_manager.total_capital == 15000.0

    def test_sync_handles_exchange_error_gracefully(self, portfolio_manager):
        """测试优雅处理 exchange 错误"""
        import server
        
        instance = MagicMock()
        instance.strategy_id = "fixed_spread"
        instance.strategy_type = "fixed_spread"
        instance.running = True
        instance.use_real_exchange = True
        instance.order_history = deque()
        instance.exchange = MagicMock()
        instance.exchange.fetch_pnl_and_fees.side_effect = Exception("Exchange error")
        instance.exchange.fetch_account_data.return_value = {"balance": 10000.0}
        
        bot = MagicMock()
        bot.strategy_instances = {"fixed_spread": instance}
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = [{"pnl": 50.0, "strategy_id": "fixed_spread"}]
        bot.data.calculate_metrics.return_value = {
            "sharpe_ratio": 1.0,
            "fill_rate": 0.8,
            "slippage_bps": 1.5,
        }
        
        with patch.object(server, "get_default_exchange", return_value=instance.exchange):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            # 不应该抛出异常
                            server._sync_portfolio_with_bot()
        
        # 验证回退到共享数据
        strategy = portfolio_manager.strategies["fixed_spread"]
        assert strategy.pnl == 50.0  # 从共享数据获取

    def test_sync_legacy_mode(self, portfolio_manager):
        """测试旧版单策略模式的向后兼容"""
        import server
        
        bot = MagicMock()
        bot.strategy_instances = {}  # 没有策略实例
        bot.strategy = MagicMock()
        bot.strategy.__class__.__name__ = "FixedSpreadStrategy"
        bot.data = MagicMock()
        bot.data.trade_history = [
            {"pnl": 100.0, "timestamp": 1000.0},
            {"pnl": 50.0, "timestamp": 1100.0},
        ]
        bot.data.calculate_metrics.return_value = {
            "sharpe_ratio": 2.0,
            "fill_rate": 0.9,
            "slippage_bps": 1.0,
        }
        
        with patch.object(server, "get_default_exchange", return_value=None):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            server._sync_portfolio_with_bot()
        
        # 验证旧版模式仍然工作
        strategy = portfolio_manager.strategies["fixed_spread"]
        assert strategy.pnl == 150.0  # 100 + 50
        assert strategy.sharpe == 2.0

    def test_sync_unknown_strategy_type(self, portfolio_manager):
        """测试未知策略类型的处理"""
        import server
        
        instance = MagicMock()
        instance.strategy_id = "unknown_strategy"
        instance.strategy_type = "unknown_type"  # 未知类型
        instance.running = True
        instance.use_real_exchange = True
        instance.order_history = deque()
        instance.exchange = MagicMock()
        
        bot = MagicMock()
        bot.strategy_instances = {"unknown_strategy": instance}
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = []
        
        with patch.object(server, "get_default_exchange", return_value=instance.exchange):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            # 不应该抛出异常，应该跳过未知类型
                            server._sync_portfolio_with_bot()
        
        # 验证现有策略未被错误修改
        assert "fixed_spread" in portfolio_manager.strategies
        assert "funding_rate" in portfolio_manager.strategies

    def test_sync_records_pnl_snapshot(self, portfolio_manager):
        """测试记录 PnL 快照用于组合 Sharpe 计算"""
        import server
        
        instance = MagicMock()
        instance.strategy_id = "fixed_spread"
        instance.strategy_type = "fixed_spread"
        instance.running = True
        instance.use_real_exchange = True
        instance.order_history = deque()
        instance.exchange = MagicMock()
        instance.exchange.fetch_pnl_and_fees.return_value = {"realized_pnl": 100.0}
        instance.exchange.fetch_account_data.return_value = {"balance": 10000.0}
        
        bot = MagicMock()
        bot.strategy_instances = {"fixed_spread": instance}
        bot.strategy = MagicMock()
        bot.data = MagicMock()
        bot.data.trade_history = []
        
        initial_snapshot_count = len(portfolio_manager.pnl_history)
        
        with patch.object(server, "get_default_exchange", return_value=instance.exchange):
            with patch.object(server, "bot_engine", bot):
                with patch.object(server, "portfolio_manager", portfolio_manager):
                    with patch.object(server, "is_running", True):
                        with patch.object(server, "get_session_start_time_ms", return_value=1000000):
                            server._sync_portfolio_with_bot()
        
        # 验证快照已记录
        assert len(portfolio_manager.pnl_history) == initial_snapshot_count + 1
        assert portfolio_manager.pnl_history[-1] == 100.0  # 总 PnL

