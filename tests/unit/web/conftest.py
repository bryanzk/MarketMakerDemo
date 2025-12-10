"""
Pytest configuration for unit/web tests
单元测试配置

This conftest.py ensures that Mocks are applied BEFORE any test modules are imported.
这确保 Mock 在任何测试模块导入之前应用。

Using pytest_configure hook to apply Mocks before test collection.
使用 pytest_configure hook 在测试收集之前应用 Mock。
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Global patches that persist for the entire test session
# 在整个测试会话中持续存在的全局 patches
_volatility_patch = None
_simulation_patch = None


def pytest_configure(config):
    """
    Pytest configuration hook that runs BEFORE any test modules are imported.
    This is the earliest point where we can apply Mocks.
    
    Pytest 配置 hook，在任何测试模块导入之前运行。
    这是我们可以应用 Mock 的最早时间点。
    """
    global _volatility_patch, _simulation_patch
    
    # Mock volatility calculation to speed up tests / Mock 波动率计算以加快测试
    def mock_volatility_calc(exchange, symbol, calculator=None):
        """Return default volatility values quickly / 快速返回默认波动率值"""
        return (0.01, 0.03)  # (1h, 24h)
    
    _volatility_patch = patch("src.trading.volatility.calculate_volatility_1h_24h", mock_volatility_calc)
    _volatility_patch.start()
    
    # Mock StrategySimulator.run() to avoid slow simulation runs in tests
    # Mock StrategySimulator.run() 以避免测试中的慢速模拟运行
    def mock_simulator_run(self, steps: int = 500) -> dict:
        """Return mock simulation stats quickly / 快速返回模拟统计数据"""
        return {
            "realized_pnl": 10.0,
            "total_trades": 5,
            "winning_trades": 3,
            "win_rate": 60.0,  # Percentage, not decimal / 百分比，不是小数
            "sharpe_ratio": 1.5,
            "pnl_history": [[0, 0.0], [1, 5.0], [2, 10.0]],
        }
    
    _simulation_patch = patch("src.ai.evaluation.evaluator.StrategySimulator.run", mock_simulator_run)
    _simulation_patch.start()


def pytest_unconfigure(config):
    """
    Pytest unconfiguration hook that runs AFTER all tests are complete.
    Clean up patches here.
    
    Pytest 取消配置 hook，在所有测试完成后运行。
    在这里清理 patches。
    """
    global _volatility_patch, _simulation_patch
    
    if _volatility_patch:
        _volatility_patch.stop()
    if _simulation_patch:
        _simulation_patch.stop()


@pytest.fixture(scope="session")
def mock_bot_engine_before_import():
    """
    Mock bot_engine initialization before server module is imported.
    This prevents expensive AlphaLoop() initialization during tests.
    
    在导入服务器模块之前 mock bot_engine 初始化。
    这防止测试期间昂贵的 AlphaLoop() 初始化。
    """
    # Mock AlphaLoop before importing server to avoid expensive initialization
    # 在导入 server 之前 mock AlphaLoop 以避免昂贵的初始化
    with patch("src.trading.engine.AlphaLoop", return_value=MagicMock()):
        yield


@pytest.fixture(scope="session")
def test_client(mock_bot_engine_before_import):
    """
    Shared TestClient fixture to avoid repeated server module imports.
    Session-scoped to cache the client across all tests in the session.
    
    共享 TestClient fixture 以避免重复导入服务器模块。
    会话作用域，以便在会话中的所有测试之间缓存客户端。
    """
    # Import server after mocks are in place
    # 在 mock 就位后导入 server
    import server
    
    # Ensure bot_engine is mocked even if it was already initialized
    # 确保 bot_engine 被 mock，即使它已经被初始化
    if not isinstance(server.bot_engine, MagicMock):
        server.bot_engine = MagicMock()
    
    return TestClient(server.app)

