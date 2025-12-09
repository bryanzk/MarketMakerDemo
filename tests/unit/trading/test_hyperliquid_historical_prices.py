"""
Unit tests for Hyperliquid historical price fetching / Hyperliquid 历史价格获取单元测试

Tests the fetch_historical_prices method using official REST API.
测试使用官方 REST API 的 fetch_historical_prices 方法。

Owner: Agent QA
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List

# Import the module / 导入模块
from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquidHistoricalPrices:
    """Test historical price fetching from Hyperliquid / 测试从 Hyperliquid 获取历史价格"""

    def test_interval_mapping(self):
        """Test interval mapping to official format / 测试间隔映射到官方格式"""
        # This will be tested through fetch_historical_prices
        # 这将通过 fetch_historical_prices 进行测试
        pass

    @patch('src.trading.hyperliquid_client.HyperliquidClient._make_request')
    def test_fetch_historical_prices_rest_api_success(self, mock_make_request):
        """Test successful REST API call for historical candles / 测试成功调用 REST API 获取历史 K 线"""
        # Mock REST API response / 模拟 REST API 响应
        # Response format: [[timestamp, open, high, low, close, volume], ...]
        # 响应格式: [[时间戳, 开盘, 最高, 最低, 收盘, 成交量], ...]
        mock_candles = [
            [1000000, 100.0, 101.0, 99.0, 100.5, 1000.0],
            [1000060, 100.5, 102.0, 100.0, 101.5, 1100.0],
            [1000120, 101.5, 103.0, 101.0, 102.5, 1200.0],
        ]
        mock_make_request.return_value = mock_candles
        
        client = HyperliquidClient("ETH/USDC:USDC")
        client._info = None  # Disable SDK to test REST API
        
        prices = client.fetch_historical_prices("ETH/USDC:USDC", hours=1, interval_minutes=1)
        
        # Verify REST API was called with correct payload / 验证 REST API 使用正确的负载调用
        assert mock_make_request.called
        call_args = mock_make_request.call_args
        assert call_args[1]['endpoint'] == '/info'
        assert call_args[1]['data']['type'] == 'candleSnapshot'
        assert call_args[1]['data']['req']['coin'] == 'ETH'
        assert call_args[1]['data']['req']['interval'] == '1m'
        assert call_args[1]['data']['req']['n'] <= 5000  # Max limit
        
        # Verify prices extracted correctly / 验证价格提取正确
        assert len(prices) == 3
        assert prices[0] == 100.5
        assert prices[1] == 101.5
        assert prices[2] == 102.5

    @patch('src.trading.hyperliquid_client.HyperliquidClient._make_request')
    def test_fetch_historical_prices_interval_mapping(self, mock_make_request):
        """Test interval mapping to official format / 测试间隔映射到官方格式"""
        mock_candles = [
            [1000000, 100.0, 101.0, 99.0, 100.5, 1000.0],
        ]
        mock_make_request.return_value = mock_candles
        
        client = HyperliquidClient("ETH/USDC:USDC")
        client._info = None
        
        # Test different intervals / 测试不同间隔
        test_cases = [
            (1, "1m"),
            (3, "3m"),
            (5, "5m"),
            (15, "15m"),
            (30, "30m"),
            (60, "1h"),
            (120, "2h"),
            (240, "4h"),
            (480, "8h"),
            (720, "12h"),
            (1440, "1d"),
        ]
        
        for interval_minutes, expected_interval in test_cases:
            client.fetch_historical_prices("ETH/USDC:USDC", hours=1, interval_minutes=interval_minutes)
            
            # Check last call / 检查最后一次调用
            if mock_make_request.called:
                call_args = mock_make_request.call_args
                actual_interval = call_args[1]['data']['req']['interval']
                assert actual_interval == expected_interval, \
                    f"Interval {interval_minutes}m should map to {expected_interval}, got {actual_interval}"

    @patch('src.trading.hyperliquid_client.HyperliquidClient._make_request')
    def test_fetch_historical_prices_max_candles_limit(self, mock_make_request):
        """Test 5000 candle limit enforcement / 测试 5000 根 K 线限制"""
        # Mock response with many candles / 模拟包含许多 K 线的响应
        mock_candles = [[1000000 + i*60000, 100.0, 101.0, 99.0, 100.5, 1000.0] for i in range(5000)]
        mock_make_request.return_value = mock_candles
        
        client = HyperliquidClient("ETH/USDC:USDC")
        client._info = None
        
        # Request more than 5000 candles / 请求超过 5000 根 K 线
        prices = client.fetch_historical_prices("ETH/USDC:USDC", hours=100, interval_minutes=1)
        
        # Verify request was limited to 5000 / 验证请求被限制为 5000
        call_args = mock_make_request.call_args
        assert call_args[1]['data']['req']['n'] == 5000

    @patch('src.trading.hyperliquid_client.HyperliquidClient._make_request')
    def test_fetch_historical_prices_extract_close_prices(self, mock_make_request):
        """Test close price extraction from different candle formats / 测试从不同 K 线格式提取收盘价"""
        client = HyperliquidClient("ETH/USDC:USDC")
        
        # Test format 1: [timestamp, open, high, low, close, volume] / 测试格式 1
        candles1 = [
            [1000000, 100.0, 101.0, 99.0, 100.5, 1000.0],
            [1000060, 100.5, 102.0, 100.0, 101.5, 1100.0],
        ]
        prices1 = client._extract_close_prices_from_candles(candles1)
        assert prices1 == [100.5, 101.5]
        
        # Test format 2: [open, high, low, close, volume] / 测试格式 2
        candles2 = [
            [100.0, 101.0, 99.0, 100.5, 1000.0],
            [100.5, 102.0, 100.0, 101.5, 1100.0],
        ]
        prices2 = client._extract_close_prices_from_candles(candles2)
        assert prices2 == [100.5, 101.5]
        
        # Test format 3: dict format / 测试格式 3
        candles3 = [
            {"close": 100.5, "open": 100.0, "high": 101.0, "low": 99.0, "volume": 1000.0},
            {"c": 101.5, "o": 100.5, "h": 102.0, "l": 100.0, "v": 1100.0},
        ]
        prices3 = client._extract_close_prices_from_candles(candles3)
        assert prices3 == [100.5, 101.5]

    @patch('src.trading.hyperliquid_client.HyperliquidClient._make_request')
    def test_fetch_historical_prices_fallback_to_allmids(self, mock_make_request):
        """Test fallback to allMids when candleSnapshot fails / 测试当 candleSnapshot 失败时回退到 allMids"""
        # First call fails (candleSnapshot) / 第一次调用失败（candleSnapshot）
        # Second call succeeds (allMids) / 第二次调用成功（allMids）
        def side_effect(*args, **kwargs):
            if kwargs.get('data', {}).get('type') == 'candleSnapshot':
                return None  # Fail
            elif kwargs.get('data', {}).get('type') == 'allMids':
                return {"mid_prices": {"ETH": 3000.0}}
            return None
        
        mock_make_request.side_effect = side_effect
        
        client = HyperliquidClient("ETH/USDC:USDC")
        client._info = None
        
        prices = client.fetch_historical_prices("ETH/USDC:USDC", hours=1, interval_minutes=1)
        
        # Should use allMids fallback / 应该使用 allMids 回退
        assert len(prices) > 0
        assert all(p == 3000.0 for p in prices)  # All prices should be current price


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

