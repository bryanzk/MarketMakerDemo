"""
Standalone smoke test for volatility calculation / 波动率计算独立冒烟测试

Can run without full project dependencies.
可以在没有完整项目依赖的情况下运行。

Owner: Agent QA
"""

import sys
import os

# Add src to path / 将 src 添加到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "src"))

# Direct import to avoid __init__ dependencies / 直接导入以避免 __init__ 依赖
from trading.volatility import (
    calculate_returns,
    calculate_volatility,
    VolatilityCalculator,
)


def test_basic_calculation():
    """Test basic volatility calculation / 测试基本波动率计算"""
    prices = [100.0, 101.0, 102.0, 101.5, 103.0, 102.5]
    returns = calculate_returns(prices)
    volatility = calculate_volatility(returns)
    
    assert len(returns) > 0
    assert volatility >= 0
    assert volatility < 1.0
    
    print(f"✅ Basic calculation: volatility = {volatility:.4%}")


def test_calculator():
    """Test VolatilityCalculator / 测试 VolatilityCalculator"""
    calculator = VolatilityCalculator()
    prices = [100.0, 101.0, 102.0, 101.5, 103.0]
    volatility = calculator.calculate_from_prices(prices)
    
    assert volatility >= 0
    assert volatility < 1.0
    
    print(f"✅ Calculator: volatility = {volatility:.4%}")


if __name__ == "__main__":
    print("Running standalone volatility smoke tests...")
    print("运行独立波动率冒烟测试...\n")
    
    try:
        test_basic_calculation()
        test_calculator()
        print("\n✅ All smoke tests passed!")
        print("✅ 所有冒烟测试通过！")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

