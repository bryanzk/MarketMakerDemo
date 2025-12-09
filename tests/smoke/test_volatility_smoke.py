"""
Smoke tests for volatility calculation / 波动率计算冒烟测试

Quick tests to verify volatility calculation works end-to-end.
快速测试以验证波动率计算端到端工作。

Owner: Agent QA
"""

import os
import sys

# Add project root to path / 将项目根目录添加到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.trading.volatility import (
    calculate_returns,
    calculate_volatility,
    VolatilityCalculator,
    fetch_and_calculate_volatility,
)


def test_volatility_calculation_smoke():
    """Smoke test: Basic volatility calculation works / 冒烟测试：基本波动率计算工作"""
    # Simple price series / 简单价格序列
    prices = [100.0, 101.0, 102.0, 101.5, 103.0, 102.5]
    
    # Calculate returns / 计算收益率
    returns = calculate_returns(prices)
    assert len(returns) > 0, "Should have returns"
    
    # Calculate volatility / 计算波动率
    volatility = calculate_volatility(returns)
    assert volatility >= 0, "Volatility should be non-negative"
    assert volatility < 1.0, "Volatility should be reasonable (< 100%)"
    
    print(f"✅ Smoke test passed: Volatility = {volatility:.4%}")


def test_volatility_calculator_smoke():
    """Smoke test: VolatilityCalculator works / 冒烟测试：VolatilityCalculator 工作"""
    calculator = VolatilityCalculator()
    
    # Test with sample prices / 使用示例价格测试
    prices = [100.0, 101.0, 102.0, 101.5, 103.0]
    volatility = calculator.calculate_from_prices(prices)
    
    assert volatility >= 0, "Volatility should be non-negative"
    assert volatility < 1.0, "Volatility should be reasonable"
    
    print(f"✅ Smoke test passed: Calculator volatility = {volatility:.4%}")


def test_volatility_calculation_with_mock_exchange():
    """Smoke test: Volatility calculation with mock exchange / 冒烟测试：使用模拟交易所的波动率计算"""
    from unittest.mock import Mock
    
    # Create mock exchange / 创建模拟交易所
    mock_exchange = Mock()
    mock_prices = [100.0, 101.0, 102.0, 101.5, 103.0, 102.5, 104.0]
    mock_exchange.fetch_historical_prices = Mock(return_value=mock_prices)
    
    # Test volatility calculation / 测试波动率计算
    volatility = fetch_and_calculate_volatility(
        mock_exchange, "ETH/USDC:USDC", hours=1, default=0.02
    )
    
    assert volatility >= 0, "Volatility should be non-negative"
    assert volatility < 1.0, "Volatility should be reasonable"
    
    # Verify exchange method was called / 验证调用了交易所方法
    mock_exchange.fetch_historical_prices.assert_called_once()
    
    print(f"✅ Smoke test passed: Mock exchange volatility = {volatility:.4%}")


def test_volatility_calculation_insufficient_data():
    """Smoke test: Handles insufficient data gracefully / 冒烟测试：优雅处理数据不足"""
    from unittest.mock import Mock
    
    # Create mock exchange with insufficient data / 创建数据不足的模拟交易所
    mock_exchange = Mock()
    mock_exchange.fetch_historical_prices = Mock(return_value=[100.0])  # Only one price
    
    # Should return default when insufficient data / 数据不足时应返回默认值
    volatility = fetch_and_calculate_volatility(
        mock_exchange, "ETH/USDC:USDC", hours=1, default=0.02
    )
    
    assert volatility == 0.02, "Should return default when insufficient data"
    
    print(f"✅ Smoke test passed: Default volatility returned = {volatility:.4%}")


if __name__ == "__main__":
    print("Running volatility smoke tests...")
    print("运行波动率冒烟测试...")
    
    test_volatility_calculation_smoke()
    test_volatility_calculator_smoke()
    test_volatility_calculation_with_mock_exchange()
    test_volatility_calculation_insufficient_data()
    
    print("\n✅ All smoke tests passed!")
    print("✅ 所有冒烟测试通过！")

