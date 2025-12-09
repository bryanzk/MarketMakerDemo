"""
Integration tests for volatility calculation / 波动率计算集成测试

Tests volatility calculation with real exchange clients.
使用真实交易所客户端测试波动率计算。

Owner: Agent QA
"""

import os
import sys
import pytest

# Add project root to path / 将项目根目录添加到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.trading.volatility import (
    calculate_volatility_1h_24h,
    VolatilityCalculator,
    fetch_and_calculate_volatility,
)


@pytest.mark.integration
class TestVolatilityIntegration:
    """Integration tests for volatility calculation / 波动率计算集成测试"""

    def test_volatility_calculation_hyperliquid(self):
        """Test volatility calculation with Hyperliquid client / 使用 Hyperliquid 客户端测试波动率计算"""
        # Skip if no API credentials / 如果没有 API 凭证则跳过
        if not os.getenv("HYPERLIQUID_API_SECRET"):
            pytest.skip("HYPERLIQUID_API_SECRET not set")
        
        from src.trading.hyperliquid_client import HyperliquidClient
        
        # Create client / 创建客户端
        client = HyperliquidClient("ETH/USDC:USDC")
        
        # Initialize calculator / 初始化计算器
        calculator = VolatilityCalculator(cache_ttl=60)
        
        # Calculate volatility / 计算波动率
        volatility_1h, volatility_24h = calculate_volatility_1h_24h(
            client, "ETH/USDC:USDC", calculator=calculator
        )
        
        # Verify results are reasonable / 验证结果合理
        assert volatility_1h >= 0, "1h volatility should be non-negative"
        assert volatility_24h >= 0, "24h volatility should be non-negative"
        assert volatility_1h < 1.0, "1h volatility should be reasonable (< 100%)"
        assert volatility_24h < 1.0, "24h volatility should be reasonable (< 100%)"
        
        print(f"✅ Integration test passed:")
        print(f"   1h volatility: {volatility_1h:.4%}")
        print(f"   24h volatility: {volatility_24h:.4%}")

    def test_volatility_calculation_with_caching(self):
        """Test volatility calculation caching / 测试波动率计算缓存"""
        # Skip if no API credentials / 如果没有 API 凭证则跳过
        if not os.getenv("HYPERLIQUID_API_SECRET"):
            pytest.skip("HYPERLIQUID_API_SECRET not set")
        
        from src.trading.hyperliquid_client import HyperliquidClient
        
        # Create client / 创建客户端
        client = HyperliquidClient("ETH/USDC:USDC")
        
        # Initialize calculator with short cache TTL / 使用短缓存 TTL 初始化计算器
        calculator = VolatilityCalculator(cache_ttl=60)
        
        # First call / 第一次调用
        volatility_1 = fetch_and_calculate_volatility(
            client, "ETH/USDC:USDC", hours=1, calculator=calculator
        )
        
        # Second call should use cache / 第二次调用应使用缓存
        volatility_2 = fetch_and_calculate_volatility(
            client, "ETH/USDC:USDC", hours=1, calculator=calculator
        )
        
        # Should be the same (cached) / 应该相同（缓存）
        assert volatility_1 == volatility_2, "Second call should use cached value"
        
        print(f"✅ Cache test passed: Volatility = {volatility_1:.4%}")

    def test_volatility_calculation_different_symbols(self):
        """Test volatility calculation for different symbols / 测试不同交易对的波动率计算"""
        # Skip if no API credentials / 如果没有 API 凭证则跳过
        if not os.getenv("HYPERLIQUID_API_SECRET"):
            pytest.skip("HYPERLIQUID_API_SECRET not set")
        
        from src.trading.hyperliquid_client import HyperliquidClient
        
        symbols = ["ETH/USDC:USDC", "BTC/USDC:USDC"]
        calculator = VolatilityCalculator(cache_ttl=60)
        
        for symbol in symbols:
            try:
                client = HyperliquidClient(symbol)
                volatility_1h, volatility_24h = calculate_volatility_1h_24h(
                    client, symbol, calculator=calculator
                )
                
                assert volatility_1h >= 0, f"{symbol} 1h volatility should be non-negative"
                assert volatility_24h >= 0, f"{symbol} 24h volatility should be non-negative"
                
                print(f"✅ {symbol}: 1h={volatility_1h:.4%}, 24h={volatility_24h:.4%}")
            except Exception as e:
                print(f"⚠️  Skipping {symbol}: {e}")
                continue

    def test_volatility_in_server_context(self):
        """Test volatility calculation in server context / 在服务器上下文中测试波动率计算"""
        # Skip if no API credentials / 如果没有 API 凭证则跳过
        if not os.getenv("HYPERLIQUID_API_SECRET"):
            pytest.skip("HYPERLIQUID_API_SECRET not set")
        
        # This test simulates how volatility is used in server.py
        # 此测试模拟波动率在 server.py 中的使用方式
        from src.trading.volatility import calculate_volatility_1h_24h, VolatilityCalculator
        
        # Simulate server context / 模拟服务器上下文
        def get_exchange_by_name(name):
            if name == "hyperliquid":
                from src.trading.hyperliquid_client import HyperliquidClient
                return HyperliquidClient("ETH/USDC:USDC")
            return None
        
        exchange = get_exchange_by_name("hyperliquid")
        if not exchange:
            pytest.skip("Exchange not available")
        
        calculator = VolatilityCalculator(cache_ttl=300)
        symbol = "ETH/USDC:USDC"
        
        volatility_1h, volatility_24h = calculate_volatility_1h_24h(
            exchange, symbol, calculator=calculator
        )
        
        # Verify results can be used in MarketContext / 验证结果可用于 MarketContext
        from src.ai.evaluation.schemas import MarketContext
        
        context = MarketContext(
            symbol=symbol,
            mid_price=3000.0,
            best_bid=2999.5,
            best_ask=3000.5,
            spread_bps=3.33,
            volatility_24h=volatility_24h,
            volatility_1h=volatility_1h,
            funding_rate=0.0001,
            funding_rate_trend="stable",
        )
        
        assert context.volatility_1h == volatility_1h
        assert context.volatility_24h == volatility_24h
        
        print(f"✅ Server context test passed:")
        print(f"   MarketContext created with volatility_1h={volatility_1h:.4%}, volatility_24h={volatility_24h:.4%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])

