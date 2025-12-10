"""
Portfolio API Tests / 组合 API 测试

基于用户故事编写的测试用例，用于驱动 Portfolio Overview 和策略对比表功能的开发。
测试遵循 TDD 原则：先写测试，再实现功能。

对应用户故事文档：docs/user_guide/user_stories_portfolio.md
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.portfolio.manager import StrategyStatus

# ============================================================================
# Epic 1: Portfolio Overview Tests
# ============================================================================


class TestPortfolioOverview:
    """US-1.x: 组合概览相关测试"""

    # ------------------------------------------------------------------------
    # US-1.1: 查看组合总盈亏
    # ------------------------------------------------------------------------

    def test_get_portfolio_success(self, client):
        """
        US-1.1: 成功获取组合数据
        Given: 系统有运行中的策略
        When: 调用 GET /api/portfolio
        Then: 返回 200 和完整的组合数据
        """
        response = client.get("/api/portfolio")
        assert response.status_code == 200
        data = response.json()

        # 验证必需字段存在
        assert "total_pnl" in data
        assert "commission" in data
        assert "net_pnl" in data
        assert "available_balance" in data
        assert "portfolio_sharpe" in data
        assert "active_count" in data
        assert "total_count" in data
        assert "risk_level" in data
        assert "strategies" in data

    def test_portfolio_commission_included(self, client, mock_bot_with_commission):
        """
        US-1.1: Portfolio 应包含交易费用
        Given: 交易所返回 commission = 5.0
        When: 调用 GET /api/portfolio
        Then: commission = 5.0, net_pnl = total_pnl - commission
        """
        response = client.get("/api/portfolio")
        data = response.json()

        assert data["commission"] == pytest.approx(5.0, rel=0.01)
        assert data["net_pnl"] == pytest.approx(data["total_pnl"] - 5.0, rel=0.01)

    def test_portfolio_commission_fallback(self, client, mock_bot_commission_error):
        """
        US-1.1: 当获取交易费用失败时应回退为0
        Given: 交易所获取 commission 抛出异常
        When: 调用 GET /api/portfolio
        Then: commission = 0, net_pnl = total_pnl
        """
        response = client.get("/api/portfolio")
        data = response.json()

        assert data["commission"] == 0.0
        assert data["net_pnl"] == pytest.approx(data["total_pnl"], rel=0.01)

    def test_portfolio_available_balance(self, client, mock_bot_with_available_balance):
        """
        US-1.1: Portfolio 应包含可用余额
        Given: 交易所返回 wallet_balance = 5000, available_balance = 4500
        When: 调用 GET /api/portfolio
        Then: available_balance = 4500
        """
        response = client.get("/api/portfolio")
        data = response.json()

        assert data["available_balance"] == pytest.approx(4500.0, rel=0.01)

    def test_portfolio_total_pnl_calculation(self, client, mock_bot_with_strategies):
        """
        US-1.1: Total PnL 应等于所有策略 PnL 之和
        Given: 策略A PnL = 100, 策略B PnL = 50
        When: 调用 GET /api/portfolio
        Then: total_pnl = 150
        """
        response = client.get("/api/portfolio")
        data = response.json()

        # Total PnL = sum of all strategy PnLs
        expected_total = sum(s["pnl"] for s in data["strategies"])
        assert data["total_pnl"] == pytest.approx(expected_total, rel=0.01)

    def test_portfolio_total_pnl_with_negative(self, client, mock_bot_mixed_pnl):
        """
        US-1.1: Total PnL 正确处理正负混合情况
        Given: 策略A PnL = 100, 策略B PnL = -30
        When: 调用 GET /api/portfolio
        Then: total_pnl = 70
        """
        response = client.get("/api/portfolio")
        data = response.json()

        # 验证正负混合计算正确
        assert data["total_pnl"] == pytest.approx(70.0, rel=0.01)

    # ------------------------------------------------------------------------
    # US-1.2: 查看组合夏普比率
    # ------------------------------------------------------------------------

    def test_portfolio_sharpe_calculation(self, client, mock_bot_with_trades):
        """
        US-1.2: Portfolio Sharpe 基于组合整体收益率计算
        Given: 有足够的交易历史数据
        When: 调用 GET /api/portfolio
        Then: 返回有效的 Sharpe 值
        """
        response = client.get("/api/portfolio")
        data = response.json()

        # Sharpe 应该是一个合理的数值
        assert data["portfolio_sharpe"] is not None
        assert isinstance(data["portfolio_sharpe"], (int, float))

    def test_portfolio_sharpe_insufficient_data(self, client, mock_bot_no_trades):
        """
        US-1.2: 交易数少于 10 时返回 None
        Given: 没有足够的交易数据
        When: 调用 GET /api/portfolio
        Then: portfolio_sharpe = None 或 0
        """
        response = client.get("/api/portfolio")
        data = response.json()

        # 数据不足时返回 None 或 0
        assert data["portfolio_sharpe"] is None or data["portfolio_sharpe"] == 0

    # ------------------------------------------------------------------------
    # US-1.3: 查看活跃策略数量
    # ------------------------------------------------------------------------

    def test_portfolio_active_count_only_live(self, client, mock_bot_mixed_status):
        """
        US-1.3: 只计算 status=live 的策略
        Given: 2 个 live 策略, 1 个 paused 策略
        When: 调用 GET /api/portfolio
        Then: active_count = 2
        """
        response = client.get("/api/portfolio")
        data = response.json()

        # 只有 live 状态的策略计入 active
        assert data["active_count"] == 2
        assert data["total_count"] == 3

    def test_portfolio_active_count_format(self, client):
        """
        US-1.3: 验证 active_count 和 total_count 为整数
        """
        response = client.get("/api/portfolio")
        data = response.json()

        assert isinstance(data["active_count"], int)
        assert isinstance(data["total_count"], int)
        assert data["active_count"] <= data["total_count"]

    # ------------------------------------------------------------------------
    # US-1.4: 查看组合风险等级
    # ------------------------------------------------------------------------

    def test_portfolio_risk_level_low(self, client, mock_bot_healthy):
        """
        US-1.4: 所有指标正常时返回 Low
        Given: 所有策略健康，无回撤
        When: 调用 GET /api/portfolio
        Then: risk_level = "low"
        """
        response = client.get("/api/portfolio")
        data = response.json()

        assert data["risk_level"] == "low"

    def test_portfolio_risk_level_high_drawdown(self, client, mock_bot_high_drawdown):
        """
        US-1.4: Max Drawdown > 10% 时返回 High
        Given: 组合回撤超过 10%
        When: 调用 GET /api/portfolio
        Then: risk_level = "high"
        """
        response = client.get("/api/portfolio")
        data = response.json()

        assert data["risk_level"] == "high"

    def test_portfolio_risk_level_medium_health(self, client, mock_bot_low_health):
        """
        US-1.4: 任一策略健康度 < 40 时返回 Medium
        Given: 某策略健康度 = 35
        When: 调用 GET /api/portfolio
        Then: risk_level = "medium"
        """
        response = client.get("/api/portfolio")
        data = response.json()

        assert data["risk_level"] == "medium"

    def test_portfolio_risk_level_values(self, client):
        """
        US-1.4: 风险等级只能是预定义的值
        """
        response = client.get("/api/portfolio")
        data = response.json()

        valid_levels = ["low", "medium", "high", "critical"]
        assert data["risk_level"] in valid_levels


# ============================================================================
# Epic 2: Strategy Comparison Table Tests
# ============================================================================


class TestStrategyComparisonTable:
    """US-2.x: 策略对比表相关测试"""

    # ------------------------------------------------------------------------
    # US-2.1: 查看策略列表
    # ------------------------------------------------------------------------

    def test_strategy_list_contains_required_fields(self, client):
        """
        US-2.1: API 返回包含所有必需字段
        Given: 有配置的策略
        When: 调用 GET /api/portfolio
        Then: 每个策略包含所有必需字段
        """
        response = client.get("/api/portfolio")
        data = response.json()

        required_fields = [
            "id",
            "name",
            "status",
            "pnl",
            "sharpe",
            "health",
            "allocation",
            "roi",
        ]

        for strategy in data["strategies"]:
            for field in required_fields:
                assert field in strategy, f"策略缺少字段: {field}"

    def test_strategy_list_sorted_by_pnl_default(
        self, client, mock_bot_with_strategies
    ):
        """
        US-2.1: 默认按 PnL 降序排列
        Given: 多个策略有不同的 PnL
        When: 调用 GET /api/portfolio
        Then: 策略按 PnL 从高到低排列
        """
        response = client.get("/api/portfolio")
        data = response.json()

        pnls = [s["pnl"] for s in data["strategies"]]
        assert pnls == sorted(pnls, reverse=True), "策略应按 PnL 降序排列"

    # ------------------------------------------------------------------------
    # US-2.2: 查看策略状态
    # ------------------------------------------------------------------------

    def test_strategy_status_valid_values(self, client):
        """
        US-2.2: 状态只能是 live/paper/paused/stopped
        """
        response = client.get("/api/portfolio")
        data = response.json()

        valid_statuses = ["live", "paper", "paused", "stopped"]
        for strategy in data["strategies"]:
            assert (
                strategy["status"] in valid_statuses
            ), f"无效状态: {strategy['status']}"

    # ------------------------------------------------------------------------
    # US-2.3: 查看策略健康度
    # ------------------------------------------------------------------------

    def test_strategy_health_score_range(self, client):
        """
        US-2.3: 健康度在 0-100 范围内
        """
        response = client.get("/api/portfolio")
        data = response.json()

        for strategy in data["strategies"]:
            assert (
                0 <= strategy["health"] <= 100
            ), f"健康度超出范围: {strategy['health']}"

    def test_strategy_health_score_calculation(self):
        """
        US-2.3: 健康度计算公式验证
        Given: 已知的指标值
        When: 计算健康度
        Then: 结果符合公式
        """
        from src.portfolio.health import calculate_strategy_health

        metrics = {
            "pnl": 100,  # 盈利 100
            "sharpe": 2.0,  # Sharpe = 2.0
            "fill_rate": 0.85,  # 85% 成交率
            "slippage": 2.0,  # 2 bps 滑点
            "max_drawdown": 0.02,  # 2% 回撤
        }

        health = calculate_strategy_health(metrics)

        # 手动计算预期值:
        # 盈利能力: min(100, max(0, 50 + 100/100)) = 51 * 0.4 = 20.4
        # 风险调整: min(100, 2.0 * 40) = 80 * 0.3 = 24
        # 执行质量: (0.85 * 100 - 2 * 10) = 65 * 0.2 = 13
        # 稳定性: max(0, 100 - 0.02 * 1000) = 80 * 0.1 = 8
        # 总计: 20.4 + 24 + 13 + 8 = 65.4

        assert 60 <= health <= 70, f"健康度计算错误: {health}"

    def test_strategy_health_weights(self):
        """
        US-2.3: 各因素权重正确（40% + 30% + 20% + 10% = 100%）
        """
        from src.portfolio.health import HEALTH_WEIGHTS

        total_weight = sum(HEALTH_WEIGHTS.values())
        assert total_weight == pytest.approx(1.0, rel=0.01)

    # ------------------------------------------------------------------------
    # US-2.4: 查看策略资金分配
    # ------------------------------------------------------------------------

    def test_strategy_allocation_sum_100(self, client):
        """
        US-2.4: 所有策略分配之和为 100%
        """
        response = client.get("/api/portfolio")
        data = response.json()

        total_allocation = sum(s["allocation"] for s in data["strategies"])
        assert total_allocation == pytest.approx(
            1.0, rel=0.01
        ), f"分配之和不为 100%: {total_allocation * 100}%"

    def test_strategy_allocation_range(self, client):
        """
        US-2.4: 每个策略分配在 0-1 范围内
        """
        response = client.get("/api/portfolio")
        data = response.json()

        for strategy in data["strategies"]:
            assert (
                0 <= strategy["allocation"] <= 1
            ), f"分配超出范围: {strategy['allocation']}"

    # ------------------------------------------------------------------------
    # US-2.5: 查看策略 ROI
    # ------------------------------------------------------------------------

    def test_strategy_roi_calculation(self, client, mock_bot_with_capital):
        """
        US-2.5: ROI = PnL / Allocated Capital
        Given: 策略 PnL = 100, 分配资金 = 5000
        When: 调用 GET /api/portfolio
        Then: ROI = 0.02 (2%)
        """
        response = client.get("/api/portfolio")
        data = response.json()

        for strategy in data["strategies"]:
            if strategy["allocation"] > 0 and strategy["pnl"] != 0:
                # ROI 应该合理
                assert isinstance(strategy["roi"], (int, float))

    # ------------------------------------------------------------------------
    # US-2.6: 暂停策略
    # ------------------------------------------------------------------------

    def test_pause_strategy_success(self, client, mock_bot_with_strategies):
        """
        US-2.6: 暂停策略后状态变为 paused
        Given: 策略状态为 live
        When: POST /api/strategy/fixed_spread/pause
        Then: 策略状态变为 paused
        """
        response = client.post("/api/strategy/fixed_spread/pause")
        assert response.status_code == 200

        # 验证状态已更新
        portfolio_response = client.get("/api/portfolio")
        data = portfolio_response.json()

        strategy = next(
            (s for s in data["strategies"] if s["id"] == "fixed_spread"), None
        )
        assert strategy is not None
        assert strategy["status"] == "paused"

    def test_pause_strategy_idempotent(self, client, mock_bot_paused_strategy):
        """
        US-2.6: 暂停已暂停的策略不应报错
        Given: 策略状态为 paused
        When: POST /api/strategy/fixed_spread/pause
        Then: 返回成功，状态仍为 paused
        """
        response = client.post("/api/strategy/fixed_spread/pause")
        assert response.status_code == 200

    def test_resume_strategy(self, client, mock_bot_paused_strategy):
        """
        US-2.6: 恢复暂停的策略
        Given: 策略状态为 paused
        When: POST /api/strategy/fixed_spread/resume
        Then: 策略状态变为 live
        """
        response = client.post("/api/strategy/fixed_spread/resume")
        assert response.status_code == 200

        # 验证状态已更新
        portfolio_response = client.get("/api/portfolio")
        data = portfolio_response.json()

        strategy = next(
            (s for s in data["strategies"] if s["id"] == "fixed_spread"), None
        )
        assert strategy is not None
        assert strategy["status"] == "live"


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def client():
    """创建测试客户端"""
    from server import app

    return TestClient(app)


@pytest.fixture
def mock_bot_with_strategies(monkeypatch):
    """Mock 有两个策略的 bot"""
    mock_engine = MagicMock()
    mock_engine.get_portfolio_data.return_value = {
        "total_pnl": 150.0,
        "portfolio_sharpe": 2.0,
        "active_count": 2,
        "total_count": 2,
        "risk_level": "low",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 100.0,
                "sharpe": 2.1,
                "health": 85,
                "allocation": 0.6,
                "roi": 0.02,
            },
            {
                "id": "funding_rate",
                "name": "Funding Rate",
                "status": "live",
                "pnl": 50.0,
                "sharpe": 2.5,
                "health": 88,
                "allocation": 0.4,
                "roi": 0.0125,
            },
        ],
    }
    return mock_engine


@pytest.fixture
def mock_bot_mixed_pnl(monkeypatch):
    """Mock 有正负混合 PnL 的 bot"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 70.0,  # 100 + (-30)
        "portfolio_sharpe": 1.5,
        "active_count": 2,
        "total_count": 2,
        "risk_level": "low",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 100.0,
                "sharpe": 2.0,
                "health": 80,
                "allocation": 0.5,
                "roi": 0.02,
            },
            {
                "id": "funding_rate",
                "name": "Funding Rate",
                "status": "live",
                "pnl": -30.0,
                "sharpe": 0.5,
                "health": 60,
                "allocation": 0.5,
                "roi": -0.006,
            },
        ],
    }
    monkeypatch.setattr(server, "portfolio_manager", mock_pm)


@pytest.fixture
def mock_bot_with_trades(monkeypatch):
    """Mock 有交易历史的 bot"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 150.0,
        "portfolio_sharpe": 2.5,  # Valid Sharpe ratio
        "active_count": 2,
        "total_count": 2,
        "risk_level": "low",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 100.0,
                "sharpe": 2.1,
                "health": 85,
                "allocation": 0.6,
                "roi": 0.02,
            },
            {
                "id": "funding_rate",
                "name": "Funding Rate",
                "status": "live",
                "pnl": 50.0,
                "sharpe": 2.5,
                "health": 88,
                "allocation": 0.4,
                "roi": 0.0125,
            },
        ],
    }
    monkeypatch.setattr(server, "portfolio_manager", mock_pm)


@pytest.fixture
def mock_bot_no_trades(monkeypatch):
    """Mock 无交易历史的 bot"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 0.0,
        "portfolio_sharpe": None,  # No data for Sharpe
        "active_count": 0,
        "total_count": 2,
        "risk_level": "low",
        "strategies": [],
    }
    monkeypatch.setattr(server, "portfolio_manager", mock_pm)


@pytest.fixture
def mock_bot_mixed_status(monkeypatch):
    """Mock 有混合状态策略的 bot"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 100.0,
        "portfolio_sharpe": 1.8,
        "active_count": 2,  # Only live strategies count
        "total_count": 3,
        "risk_level": "low",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 80.0,
                "sharpe": 2.0,
                "health": 85,
                "allocation": 0.5,
                "roi": 0.016,
            },
            {
                "id": "funding_rate",
                "name": "Funding Rate",
                "status": "live",
                "pnl": 20.0,
                "sharpe": 1.5,
                "health": 75,
                "allocation": 0.3,
                "roi": 0.004,
            },
            {
                "id": "momentum",
                "name": "Momentum",
                "status": "stopped",
                "pnl": 0.0,
                "sharpe": 0.0,
                "health": 50,
                "allocation": 0.2,
                "roi": 0.0,
            },
        ],
    }
    monkeypatch.setattr(server, "portfolio_manager", mock_pm)


@pytest.fixture
def mock_bot_healthy(monkeypatch):
    """Mock 健康的 bot - low risk"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 200.0,
        "portfolio_sharpe": 3.0,
        "active_count": 2,
        "total_count": 2,
        "risk_level": "low",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 120.0,
                "sharpe": 3.2,
                "health": 95,
                "allocation": 0.6,
                "roi": 0.024,
            },
            {
                "id": "funding_rate",
                "name": "Funding Rate",
                "status": "live",
                "pnl": 80.0,
                "sharpe": 2.8,
                "health": 92,
                "allocation": 0.4,
                "roi": 0.016,
            },
        ],
    }
    monkeypatch.setattr(server, "portfolio_manager", mock_pm)


@pytest.fixture
def mock_bot_high_drawdown(monkeypatch):
    """Mock 高回撤的 bot - high risk"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": -100.0,
        "portfolio_sharpe": -0.5,
        "active_count": 2,
        "total_count": 2,
        "risk_level": "high",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": -60.0,
                "sharpe": -0.3,
                "health": 30,
                "allocation": 0.6,
                "roi": -0.012,
            },
            {
                "id": "funding_rate",
                "name": "Funding Rate",
                "status": "live",
                "pnl": -40.0,
                "sharpe": -0.7,
                "health": 25,
                "allocation": 0.4,
                "roi": -0.008,
            },
        ],
    }
    monkeypatch.setattr(server, "portfolio_manager", mock_pm)


@pytest.fixture
def mock_bot_low_health(monkeypatch):
    """Mock 低健康度策略的 bot"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 50.0,
        "portfolio_sharpe": 0.8,
        "active_count": 2,
        "total_count": 2,
        "risk_level": "medium",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 30.0,
                "sharpe": 1.0,
                "health": 45,
                "allocation": 0.5,
                "roi": 0.006,
            },
            {
                "id": "funding_rate",
                "name": "Funding Rate",
                "status": "live",
                "pnl": 20.0,
                "sharpe": 0.6,
                "health": 40,
                "allocation": 0.5,
                "roi": 0.004,
            },
        ],
    }
    monkeypatch.setattr(server, "portfolio_manager", mock_pm)


@pytest.fixture
def mock_bot_with_capital(monkeypatch):
    """Mock 有资金分配的 bot"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 150.0,
        "portfolio_sharpe": 2.0,
        "active_count": 2,
        "total_count": 2,
        "risk_level": "low",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 100.0,
                "sharpe": 2.1,
                "health": 85,
                "allocation": 0.6,
                "roi": 0.02,
            },
            {
                "id": "funding_rate",
                "name": "Funding Rate",
                "status": "live",
                "pnl": 50.0,
                "sharpe": 2.5,
                "health": 88,
                "allocation": 0.4,
                "roi": 0.0125,
            },
        ],
    }
    monkeypatch.setattr(server, "portfolio_manager", mock_pm)


@pytest.fixture
def mock_bot_paused_strategy(monkeypatch):
    """Mock 有暂停策略的 bot"""
    import server

    # Create a stateful mock that tracks strategy status
    strategy_status = {"fixed_spread": "paused"}

    def get_portfolio_data():
        return {
            "total_pnl": 100.0,
            "portfolio_sharpe": 1.5,
            "active_count": 1 if strategy_status["fixed_spread"] == "live" else 0,
            "total_count": 1,
            "risk_level": "low",
            "strategies": [
                {
                    "id": "fixed_spread",
                    "name": "Fixed Spread",
                    "status": strategy_status["fixed_spread"],
                    "pnl": 100.0,
                    "sharpe": 2.0,
                    "health": 80,
                    "allocation": 1.0,
                    "roi": 0.02,
                },
            ],
        }

    def resume_strategy(strategy_id):
        if strategy_id in strategy_status:
            strategy_status[strategy_id] = "live"
            return True
        return False

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.side_effect = get_portfolio_data
    mock_pm.resume_strategy.side_effect = resume_strategy
    monkeypatch.setattr(server, "portfolio_manager", mock_pm)


@pytest.fixture
def mock_bot_with_commission(monkeypatch):
    """Mock 有交易费用的 bot"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 100.0,
        "portfolio_sharpe": 2.0,
        "active_count": 1,
        "total_count": 1,
        "risk_level": "low",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 100.0,
                "sharpe": 2.0,
                "health": 80,
                "allocation": 1.0,
                "roi": 0.02,
            },
        ],
    }

    # Mock exchange to return commission
    mock_exchange = MagicMock()
    mock_exchange.fetch_pnl_and_fees.return_value = {
        "realized_pnl": 100.0,
        "commission": 5.0,
        "net_pnl": 95.0,
    }
    mock_exchange.fetch_account_data.return_value = {"balance": 10000.0}

    mock_bot = MagicMock()

    monkeypatch.setattr(server, "portfolio_manager", mock_pm)
    monkeypatch.setattr(server, "bot_engine", mock_bot)
    monkeypatch.setattr(server, "get_default_exchange", lambda: mock_exchange)


@pytest.fixture
def mock_bot_commission_error(monkeypatch):
    """Mock 获取交易费用时抛出异常的 bot"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 100.0,
        "portfolio_sharpe": 2.0,
        "active_count": 1,
        "total_count": 1,
        "risk_level": "low",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 100.0,
                "sharpe": 2.0,
                "health": 80,
                "allocation": 1.0,
                "roi": 0.02,
            },
        ],
    }

    # Mock exchange to raise exception
    mock_exchange = MagicMock()
    mock_exchange.fetch_pnl_and_fees.side_effect = Exception("API Error")
    mock_exchange.fetch_account_data.side_effect = Exception("API Error")

    mock_bot = MagicMock()

    monkeypatch.setattr(server, "portfolio_manager", mock_pm)
    monkeypatch.setattr(server, "bot_engine", mock_bot)
    monkeypatch.setattr(server, "get_default_exchange", lambda: mock_exchange)


@pytest.fixture
def mock_bot_with_available_balance(monkeypatch):
    """Mock 有可用余额数据的 bot"""
    import server

    mock_pm = MagicMock()
    mock_pm.get_portfolio_data.return_value = {
        "total_pnl": 100.0,
        "total_capital": 5000.0,
        "portfolio_sharpe": 2.0,
        "active_count": 1,
        "total_count": 1,
        "risk_level": "low",
        "strategies": [
            {
                "id": "fixed_spread",
                "name": "Fixed Spread",
                "status": "live",
                "pnl": 100.0,
                "sharpe": 2.0,
                "health": 80,
                "allocation": 1.0,
                "roi": 0.02,
            },
        ],
    }

    # Mock exchange to return account data with available_balance
    mock_exchange = MagicMock()
    mock_exchange.fetch_pnl_and_fees.return_value = {
        "realized_pnl": 100.0,
        "commission": 5.0,
        "net_pnl": 95.0,
    }
    mock_exchange.fetch_account_data.return_value = {
        "balance": 5000.0,
        "available_balance": 4500.0,
        "position_amt": 0.5,
        "entry_price": 2000.0,
    }

    mock_bot = MagicMock()
    
    monkeypatch.setattr(server, "get_default_exchange", lambda: mock_exchange)
    mock_bot.exchange = mock_exchange

    monkeypatch.setattr(server, "portfolio_manager", mock_pm)
    monkeypatch.setattr(server, "bot_engine", mock_bot)


# ============================================================================
# Capital Allocation API Tests / 资金分配 API 测试
# ============================================================================


class TestCapitalAllocation:
    """资金分配相关 API 测试"""

    def test_get_allocation_success(self, client):
        """
        测试获取资金分配信息
        """
        response = client.get("/api/portfolio/allocation")
        assert response.status_code == 200
        data = response.json()

        assert "total_capital" in data
        assert "min_allocation" in data
        assert "max_allocation" in data
        assert "auto_rebalance" in data
        assert "strategies" in data
        assert isinstance(data["strategies"], list)

    def test_rebalance_equal(self, client):
        """
        测试等权重再平衡
        """
        response = client.post(
            "/api/portfolio/rebalance",
            json={"method": "equal"},
        )
        assert response.status_code == 200
        data = response.json()

        assert "method" in data
        assert data["method"] == "equal"
        assert "new_allocations" in data
        assert "total_capital" in data

    def test_update_allocation_limits(self, client):
        """
        测试更新分配限制
        """
        response = client.put(
            "/api/portfolio/allocation/limits",
            json={"min_allocation": 0.15, "max_allocation": 0.65},
        )
        assert response.status_code == 200
        data = response.json()

        assert "min_allocation" in data
        assert "max_allocation" in data
        assert data["min_allocation"] == 0.15
        assert data["max_allocation"] == 0.65

    def test_update_strategy_allocation(self, client):
        """
        测试更新单个策略的分配
        """
        response = client.put(
            "/api/portfolio/strategy/fixed_spread/allocation",
            json={"allocation": 0.7},
        )
        assert response.status_code == 200
        data = response.json()

        assert "strategy_id" in data
        assert data["strategy_id"] == "fixed_spread"
        assert "new_allocation" in data
