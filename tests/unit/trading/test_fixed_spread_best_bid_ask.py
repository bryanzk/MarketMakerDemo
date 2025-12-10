"""
Unit tests for FixedSpreadStrategy with best_bid/best_ask pricing / 基于 best_bid/best_ask 定价的固定点差策略单元测试

Owner: Agent QA
"""

import unittest
from unittest.mock import Mock

from src.trading.strategies.fixed_spread import FixedSpreadStrategy


class TestFixedSpreadBestBidAskPricing(unittest.TestCase):
    """Test FixedSpreadStrategy with best_bid/best_ask pricing / 测试基于 best_bid/best_ask 定价的固定点差策略"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.strategy = FixedSpreadStrategy()
        self.strategy.spread = 0.001  # 0.1% spread
        self.strategy.quantity = 0.1

    def test_calculate_target_orders_uses_best_bid_ask_when_available(self):
        """
        Test that strategy uses best_bid/best_ask for pricing when available.
        测试策略在可用时使用 best_bid/best_ask 进行定价。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        
        # Should have both buy and sell orders
        # 应该有买入和卖出订单
        self.assertEqual(len(orders), 2)
        
        buy_order = next((o for o in orders if o["side"] == "buy"), None)
        sell_order = next((o for o in orders if o["side"] == "sell"), None)
        
        self.assertIsNotNone(buy_order)
        self.assertIsNotNone(sell_order)
        
        # Buy price should be slightly above best_bid
        # 买入价应该略高于 best_bid
        self.assertGreater(buy_order["price"], market_data["best_bid"])
        self.assertLess(buy_order["price"], market_data["mid_price"])
        
        # Sell price should be slightly below best_ask
        # 卖出价应该略低于 best_ask
        self.assertLess(sell_order["price"], market_data["best_ask"])
        self.assertGreater(sell_order["price"], market_data["mid_price"])

    def test_buy_price_above_best_bid(self):
        """
        Test that buy price is positioned above best_bid.
        测试买入价位于 best_bid 之上。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        buy_order = next((o for o in orders if o["side"] == "buy"), None)
        
        self.assertIsNotNone(buy_order)
        # Buy price should be at least one tick above best_bid
        # 买入价应该至少比 best_bid 高一个 tick
        self.assertGreaterEqual(
            buy_order["price"],
            market_data["best_bid"] + market_data["tick_size"]
        )

    def test_sell_price_below_best_ask(self):
        """
        Test that sell price is positioned below best_ask.
        测试卖出价位于 best_ask 之下。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        sell_order = next((o for o in orders if o["side"] == "sell"), None)
        
        self.assertIsNotNone(sell_order)
        # Sell price should be at least one tick below best_ask
        # 卖出价应该至少比 best_ask 低一个 tick
        self.assertLessEqual(
            sell_order["price"],
            market_data["best_ask"] - market_data["tick_size"]
        )

    def test_fallback_to_mid_price_when_best_bid_ask_unavailable(self):
        """
        Test that strategy falls back to mid_price when best_bid/best_ask are not available.
        测试当 best_bid/best_ask 不可用时，策略回退到 mid_price。
        """
        market_data = {
            "mid_price": 3000.0,
            # No best_bid or best_ask
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        
        # Should still generate orders using mid_price
        # 应该仍然使用 mid_price 生成订单
        self.assertEqual(len(orders), 2)
        
        buy_order = next((o for o in orders if o["side"] == "buy"), None)
        sell_order = next((o for o in orders if o["side"] == "sell"), None)
        
        self.assertIsNotNone(buy_order)
        self.assertIsNotNone(sell_order)
        
        # Prices should be around mid_price with spread
        # 价格应该围绕 mid_price 加上价差
        self.assertLess(buy_order["price"], market_data["mid_price"])
        self.assertGreater(sell_order["price"], market_data["mid_price"])

    def test_buy_price_competitive_but_not_crossing(self):
        """
        Test that buy price is competitive (close to best_bid) but doesn't cross.
        测试买入价具有竞争力（接近 best_bid）但不会跨越。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        buy_order = next((o for o in orders if o["side"] == "buy"), None)
        
        self.assertIsNotNone(buy_order)
        # Buy price should be competitive (within reasonable range of best_bid)
        # 买入价应该具有竞争力（在 best_bid 的合理范围内）
        price_diff = buy_order["price"] - market_data["best_bid"]
        # Should be positive (above best_bid) but not too far
        # 应该是正数（高于 best_bid）但不要太远
        self.assertGreater(price_diff, 0)
        # Should be within 0.5% of best_bid for competitiveness
        # 应该在 best_bid 的 0.5% 以内以保持竞争力
        self.assertLess(price_diff, market_data["best_bid"] * 0.005)

    def test_sell_price_competitive_but_not_crossing(self):
        """
        Test that sell price is competitive (close to best_ask) but doesn't cross.
        测试卖出价具有竞争力（接近 best_ask）但不会跨越。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        sell_order = next((o for o in orders if o["side"] == "sell"), None)
        
        self.assertIsNotNone(sell_order)
        # Sell price should be competitive (within reasonable range of best_ask)
        # 卖出价应该具有竞争力（在 best_ask 的合理范围内）
        price_diff = market_data["best_ask"] - sell_order["price"]
        # Should be positive (below best_ask) but not too far
        # 应该是正数（低于 best_ask）但不要太远
        self.assertGreater(price_diff, 0)
        # Should be within 0.5% of best_ask for competitiveness
        # 应该在 best_ask 的 0.5% 以内以保持竞争力
        self.assertLess(price_diff, market_data["best_ask"] * 0.005)

    def test_handles_wide_spread(self):
        """
        Test that strategy handles wide market spread correctly.
        测试策略正确处理宽市场价差。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2990.0,  # Wide spread: 20 points
            "best_ask": 3010.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        
        self.assertEqual(len(orders), 2)
        
        buy_order = next((o for o in orders if o["side"] == "buy"), None)
        sell_order = next((o for o in orders if o["side"] == "sell"), None)
        
        # Buy price should still be above best_bid
        # 买入价应该仍然高于 best_bid
        self.assertGreater(buy_order["price"], market_data["best_bid"])
        # Sell price should still be below best_ask
        # 卖出价应该仍然低于 best_ask
        self.assertLess(sell_order["price"], market_data["best_ask"])

    def test_handles_narrow_spread(self):
        """
        Test that strategy handles narrow market spread correctly.
        测试策略正确处理窄市场价差。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.9,  # Narrow spread: 0.2 points
            "best_ask": 3000.1,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        
        self.assertEqual(len(orders), 2)
        
        buy_order = next((o for o in orders if o["side"] == "buy"), None)
        sell_order = next((o for o in orders if o["side"] == "sell"), None)
        
        # Buy price should still be above best_bid
        # 买入价应该仍然高于 best_bid
        self.assertGreater(buy_order["price"], market_data["best_bid"])
        # Sell price should still be below best_ask
        # 卖出价应该仍然低于 best_ask
        self.assertLess(sell_order["price"], market_data["best_ask"])

    def test_prices_rounded_to_tick_size(self):
        """
        Test that prices are properly rounded to tick_size.
        测试价格正确舍入到 tick_size。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        
        for order in orders:
            # Price should be divisible by tick_size (within floating point tolerance)
            # 价格应该能被 tick_size 整除（在浮点容差内）
            # Use Decimal for precise comparison to avoid floating point issues
            # 使用 Decimal 进行精确比较以避免浮点问题
            from decimal import Decimal
            price_decimal = Decimal(str(order["price"]))
            tick_size_decimal = Decimal(str(market_data["tick_size"]))
            remainder = float(price_decimal % tick_size_decimal)
            # Allow for small floating point errors (check if remainder is close to 0 or close to tick_size)
            # 允许小的浮点误差（检查余数是否接近 0 或接近 tick_size）
            remainder_normalized = min(remainder, market_data["tick_size"] - remainder)
            self.assertLess(remainder_normalized, 0.0001, 
                          f"Price {order['price']} not divisible by tick_size {market_data['tick_size']}, remainder: {remainder}")

    def test_quantity_rounded_to_step_size(self):
        """
        Test that quantity is properly rounded to step_size.
        测试数量正确舍入到 step_size。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        
        for order in orders:
            # Quantity should be divisible by step_size (within floating point tolerance)
            # 数量应该能被 step_size 整除（在浮点容差内）
            remainder = order["quantity"] % market_data["step_size"]
            self.assertLess(remainder, 0.0001)


if __name__ == "__main__":
    unittest.main()

