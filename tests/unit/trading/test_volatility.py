"""
Unit tests for volatility calculation module / 波动率计算模块单元测试

Tests volatility calculation from historical price data.
测试从历史价格数据计算波动率。

Owner: Agent QA
"""

import pytest
import math
from typing import List, Dict
from unittest.mock import Mock, patch

# Import the module we'll create
# 导入我们将创建的模块
from src.trading.volatility import (
    calculate_volatility,
    calculate_returns,
    fetch_and_calculate_volatility,
    VolatilityCalculator,
)


class TestVolatilityCalculation:
    """Test volatility calculation functions / 测试波动率计算函数"""

    def test_calculate_returns_basic(self):
        """Test basic return calculation / 测试基本收益率计算"""
        prices = [100.0, 101.0, 102.0, 101.5, 103.0]
        returns = calculate_returns(prices)
        
        assert len(returns) == 4
        assert returns[0] == pytest.approx(0.01, abs=0.0001)  # (101-100)/100
        assert returns[1] == pytest.approx(0.0099, abs=0.0001)  # (102-101)/101
        assert returns[2] == pytest.approx(-0.0049, abs=0.0001)  # (101.5-102)/102
        assert returns[3] == pytest.approx(0.0148, abs=0.0001)  # (103-101.5)/101.5

    def test_calculate_returns_empty(self):
        """Test return calculation with empty prices / 测试空价格列表的收益率计算"""
        prices = []
        returns = calculate_returns(prices)
        assert returns == []

    def test_calculate_returns_single_price(self):
        """Test return calculation with single price / 测试单个价格的收益率计算"""
        prices = [100.0]
        returns = calculate_returns(prices)
        assert returns == []

    def test_calculate_volatility_basic(self):
        """Test basic volatility calculation / 测试基本波动率计算"""
        # Simple test case: constant returns should give low volatility
        # 简单测试用例：恒定收益率应该给出低波动率
        returns = [0.01, 0.01, 0.01, 0.01, 0.01]
        volatility = calculate_volatility(returns)
        
        # With constant returns, volatility should be near zero
        # 恒定收益率时，波动率应该接近零
        assert volatility == pytest.approx(0.0, abs=0.0001)

    def test_calculate_volatility_variable_returns(self):
        """Test volatility with variable returns / 测试可变收益率的波动率"""
        # Returns with standard deviation of ~0.01
        # 标准差约为 0.01 的收益率
        returns = [0.01, -0.01, 0.02, -0.02, 0.01]
        volatility = calculate_volatility(returns)
        
        # Should be positive and reasonable
        # 应该是正数且合理
        assert volatility > 0
        assert volatility < 0.1  # Should be less than 10%
        # Expected volatility ≈ 0.0141 (std dev of returns)
        assert volatility == pytest.approx(0.0141, abs=0.001)

    def test_calculate_volatility_annualized(self):
        """Test annualized volatility calculation / 测试年化波动率计算"""
        # Daily returns with 1% daily volatility
        # 日收益率为 1% 的日波动率
        daily_returns = [0.01, -0.01, 0.01, -0.01, 0.01]
        daily_vol = calculate_volatility(daily_returns, annualized=False)
        
        # Annualized (assuming 365 days)
        # 年化（假设 365 天）
        annualized_vol = calculate_volatility(daily_returns, annualized=True, periods_per_year=365)
        
        assert annualized_vol > daily_vol
        # Annualized should be approximately daily * sqrt(365)
        # 年化应该约为日波动率 * sqrt(365)
        expected_annualized = daily_vol * math.sqrt(365)
        assert annualized_vol == pytest.approx(expected_annualized, abs=0.01)

    def test_calculate_volatility_insufficient_data(self):
        """Test volatility with insufficient data / 测试数据不足时的波动率"""
        returns = [0.01]  # Need at least 2 returns
        volatility = calculate_volatility(returns)
        assert volatility == 0.0

    def test_calculate_volatility_empty_returns(self):
        """Test volatility with empty returns / 测试空收益率列表的波动率"""
        returns = []
        volatility = calculate_volatility(returns)
        assert volatility == 0.0


class TestVolatilityCalculator:
    """Test VolatilityCalculator class / 测试 VolatilityCalculator 类"""

    def test_calculator_init(self):
        """Test calculator initialization / 测试计算器初始化"""
        calculator = VolatilityCalculator()
        assert calculator is not None

    def test_calculator_calculate_from_prices(self):
        """Test calculating volatility from price list / 测试从价格列表计算波动率"""
        calculator = VolatilityCalculator()
        prices = [100.0, 101.0, 102.0, 101.5, 103.0, 102.5]
        volatility = calculator.calculate_from_prices(prices)
        
        assert volatility > 0
        assert volatility < 1.0  # Should be reasonable

    def test_calculator_calculate_from_prices_1h(self):
        """Test 1-hour volatility calculation / 测试 1 小时波动率计算"""
        calculator = VolatilityCalculator()
        # Simulate 1-hour price data (60 minutes)
        # 模拟 1 小时价格数据（60 分钟）
        base_price = 100.0
        prices = [base_price + (i * 0.1) for i in range(60)]
        volatility_1h = calculator.calculate_from_prices(prices, annualized=False)
        
        # Should be positive
        assert volatility_1h > 0

    def test_calculator_calculate_from_prices_24h(self):
        """Test 24-hour volatility calculation / 测试 24 小时波动率计算"""
        calculator = VolatilityCalculator()
        # Simulate 24-hour price data (1440 minutes)
        # 模拟 24 小时价格数据（1440 分钟）
        base_price = 100.0
        prices = [base_price + (i * 0.01) for i in range(1440)]
        volatility_24h = calculator.calculate_from_prices(prices, annualized=False)
        
        # Should be positive
        assert volatility_24h > 0


class TestFetchAndCalculateVolatility:
    """Test fetching and calculating volatility from exchange / 测试从交易所获取并计算波动率"""

    @patch('src.trading.volatility.fetch_historical_prices')
    def test_fetch_and_calculate_volatility_success(self, mock_fetch):
        """Test successful volatility calculation from exchange / 测试从交易所成功计算波动率"""
        # Mock historical prices / 模拟历史价格
        mock_prices = [100.0, 101.0, 102.0, 101.5, 103.0, 102.5, 104.0]
        mock_fetch.return_value = mock_prices
        
        exchange = Mock()
        symbol = "ETH/USDC:USDC"
        hours = 1
        
        volatility = fetch_and_calculate_volatility(exchange, symbol, hours)
        
        assert volatility > 0
        mock_fetch.assert_called_once_with(exchange, symbol, hours, 1)

    @patch('src.trading.volatility.fetch_historical_prices')
    def test_fetch_and_calculate_volatility_insufficient_data(self, mock_fetch):
        """Test volatility with insufficient data from exchange / 测试交易所数据不足时的波动率"""
        # Mock insufficient prices / 模拟数据不足
        mock_fetch.return_value = [100.0]  # Only one price
        
        exchange = Mock()
        symbol = "ETH/USDC:USDC"
        hours = 1
        
        volatility = fetch_and_calculate_volatility(exchange, symbol, hours, default=0.02)
        
        # Should return default when insufficient data
        # 数据不足时应返回默认值
        assert volatility == 0.02

    @patch('src.trading.volatility.fetch_historical_prices')
    def test_fetch_and_calculate_volatility_fetch_error(self, mock_fetch):
        """Test volatility calculation when fetch fails / 测试获取失败时的波动率计算"""
        # Mock fetch error / 模拟获取错误
        mock_fetch.side_effect = Exception("API Error")
        
        exchange = Mock()
        symbol = "ETH/USDC:USDC"
        hours = 1
        
        volatility = fetch_and_calculate_volatility(exchange, symbol, hours, default=0.02)
        
        # Should return default value on error
        # 错误时应返回默认值
        assert volatility == 0.02
        mock_fetch.assert_called_once_with(exchange, symbol, hours, 1)


class TestHistoricalPriceFetching:
    """Test historical price fetching from exchange / 测试从交易所获取历史价格"""

    def test_fetch_historical_prices_hyperliquid(self):
        """Test fetching historical prices from Hyperliquid / 测试从 Hyperliquid 获取历史价格"""
        # This will be tested with actual exchange client in integration tests
        # 这将在集成测试中使用实际交易所客户端进行测试
        pass

    def test_fetch_historical_prices_binance(self):
        """Test fetching historical prices from Binance / 测试从 Binance 获取历史价格"""
        # This will be tested with actual exchange client in integration tests
        # 这将在集成测试中使用实际交易所客户端进行测试
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

