"""
Direct smoke test for volatility calculation / 波动率计算直接冒烟测试

Directly imports and tests the volatility module.
直接导入并测试波动率模块。

Owner: Agent QA
"""

import sys
import os
import math

# Add project root to path / 将项目根目录添加到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Direct file import / 直接文件导入
import importlib.util
spec = importlib.util.spec_from_file_location(
    "volatility", 
    os.path.join(project_root, "src", "trading", "volatility.py")
)
volatility_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(volatility_module)

calculate_returns = volatility_module.calculate_returns
calculate_volatility = volatility_module.calculate_volatility
VolatilityCalculator = volatility_module.VolatilityCalculator


def test_basic_calculation():
    """Test basic volatility calculation / 测试基本波动率计算"""
    prices = [100.0, 101.0, 102.0, 101.5, 103.0, 102.5]
    returns = calculate_returns(prices)
    volatility = calculate_volatility(returns)
    
    assert len(returns) > 0, "Should have returns"
    assert volatility >= 0, "Volatility should be non-negative"
    assert volatility < 1.0, "Volatility should be reasonable"
    
    print(f"✅ Basic calculation: volatility = {volatility:.4%}")


def test_calculator():
    """Test VolatilityCalculator / 测试 VolatilityCalculator"""
    calculator = VolatilityCalculator()
    prices = [100.0, 101.0, 102.0, 101.5, 103.0]
    volatility = calculator.calculate_from_prices(prices)
    
    assert volatility >= 0, "Volatility should be non-negative"
    assert volatility < 1.0, "Volatility should be reasonable"
    
    print(f"✅ Calculator: volatility = {volatility:.4%}")


def test_returns_calculation():
    """Test returns calculation / 测试收益率计算"""
    prices = [100.0, 101.0, 102.0]
    returns = calculate_returns(prices)
    
    assert len(returns) == 2, "Should have 2 returns for 3 prices"
    assert abs(returns[0] - 0.01) < 0.0001, "First return should be 1%"
    assert abs(returns[1] - 0.0099) < 0.0001, "Second return should be ~0.99%"
    
    print(f"✅ Returns calculation: {returns}")


if __name__ == "__main__":
    print("Running direct volatility smoke tests...")
    print("运行直接波动率冒烟测试...\n")
    
    try:
        test_returns_calculation()
        test_basic_calculation()
        test_calculator()
        print("\n✅ All smoke tests passed!")
        print("✅ 所有冒烟测试通过！")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


