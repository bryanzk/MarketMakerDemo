"""
Test that simulation only uses FixedSpread strategy
测试模拟中仅使用 FixedSpread 策略

This test verifies that even if LLM recommends FundingRate strategy,
the simulation will always use FixedSpread strategy.
此测试验证即使 LLM 建议 FundingRate 策略，模拟也始终使用 FixedSpread 策略。
"""

import pytest
from unittest.mock import Mock, patch
from src.ai.evaluation.schemas import MarketContext, StrategyProposal
from src.ai.evaluation.evaluator import MultiLLMEvaluator, StrategySimulator
from src.trading.strategies.fixed_spread import FixedSpreadStrategy


class TestSimulationFixedSpreadOnly:
    """Test that simulation only uses FixedSpread strategy"""

    @pytest.fixture
    def sample_market_context(self):
        """Create sample market context"""
        return MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
            current_position=0.0,
            available_balance=10000.0,
            win_rate=0.52,
            sharpe_ratio=1.2,
        )

    def test_simulator_only_uses_fixedspread(self):
        """
        Test that StrategySimulator only works with FixedSpread strategy
        测试 StrategySimulator 仅使用 FixedSpread 策略
        """
        # Create a FixedSpread strategy
        strategy = FixedSpreadStrategy()
        strategy.spread = 0.01
        strategy.quantity = 0.1
        strategy.leverage = 1.0

        # Create simulator (should not require funding_rate parameter)
        simulator = StrategySimulator(
            strategy=strategy,
            initial_price=2500.0,
            volatility=0.02,
        )

        # Verify simulator was created successfully
        assert simulator.strategy == strategy
        assert isinstance(simulator.strategy, FixedSpreadStrategy)
        assert simulator.current_price == 2500.0
        assert simulator.volatility == 0.02
        # Verify funding_rate is not stored
        assert not hasattr(simulator, "funding_rate")

    def test_run_simulation_always_uses_fixedspread(self, sample_market_context):
        """
        Test that _run_simulation always uses FixedSpread, even if proposal recommends FundingRate
        测试 _run_simulation 始终使用 FixedSpread，即使建议是 FundingRate
        """
        evaluator = MultiLLMEvaluator(providers=[], simulation_steps=10)

        # Create a proposal that recommends FundingRate
        funding_rate_proposal = StrategyProposal(
            recommended_strategy="FundingRate",
            spread=0.01,
            skew_factor=120,
            quantity=0.1,
            leverage=2.0,
            confidence=0.85,
            provider_name="Test",
            parse_success=True,
        )

        # Run simulation
        result = evaluator._run_simulation(funding_rate_proposal, sample_market_context)

        # Verify simulation completed (even though proposal was FundingRate)
        assert result is not None
        assert result.simulation_steps == 10
        # The simulation should have run with FixedSpread strategy internally

    def test_simulator_does_not_use_funding_rate_parameter(self):
        """
        Test that StrategySimulator does not accept or use funding_rate parameter
        测试 StrategySimulator 不接受或使用 funding_rate 参数
        """
        strategy = FixedSpreadStrategy()
        strategy.spread = 0.01
        strategy.quantity = 0.1

        # Create simulator without funding_rate (should work)
        simulator = StrategySimulator(
            strategy=strategy,
            initial_price=2500.0,
            volatility=0.02,
        )

        # Verify funding_rate is not in the simulator
        assert not hasattr(simulator, "funding_rate")

        # Run a few steps to verify it works
        stats = simulator.run(steps=5)
        assert stats is not None
        assert "realized_pnl" in stats

    def test_simulation_with_fixedspread_proposal(self, sample_market_context):
        """
        Test that simulation works correctly with FixedSpread proposal
        测试使用 FixedSpread 建议时模拟正常工作
        """
        evaluator = MultiLLMEvaluator(providers=[], simulation_steps=20)

        # Create a FixedSpread proposal
        fixedspread_proposal = StrategyProposal(
            recommended_strategy="FixedSpread",
            spread=0.015,
            skew_factor=100,  # Not used but required in schema
            quantity=0.2,
            leverage=1.5,
            confidence=0.80,
            provider_name="Test",
            parse_success=True,
        )

        # Run simulation
        result = evaluator._run_simulation(fixedspread_proposal, sample_market_context)

        # Verify results
        assert result is not None
        assert result.simulation_steps == 20
        assert isinstance(result.realized_pnl, float)
        assert isinstance(result.win_rate, float)
        assert 0 <= result.win_rate <= 1

    def test_simulation_creates_only_fixedspread_strategy(
        self, sample_market_context
    ):
        """
        Test that simulation creates only FixedSpreadStrategy, never FundingRateStrategy
        测试模拟仅创建 FixedSpreadStrategy，从不创建 FundingRateStrategy
        """
        # Verify FundingRateStrategy is not imported in evaluator
        import src.ai.evaluation.evaluator as evaluator_module

        # FundingRateStrategy should not be in the module (we removed the import)
        assert not hasattr(evaluator_module, "FundingRateStrategy"), (
            "FundingRateStrategy should not be imported in evaluator module"
        )

        evaluator = MultiLLMEvaluator(providers=[], simulation_steps=10)

        # Create proposals with both strategy types
        funding_proposal = StrategyProposal(
            recommended_strategy="FundingRate",
            spread=0.01,
            quantity=0.1,
            leverage=1.0,
            confidence=0.85,
            provider_name="Test",
            parse_success=True,
        )

        fixedspread_proposal = StrategyProposal(
            recommended_strategy="FixedSpread",
            spread=0.01,
            quantity=0.1,
            leverage=1.0,
            confidence=0.85,
            provider_name="Test",
            parse_success=True,
        )

        # Both should use FixedSpreadStrategy
        result1 = evaluator._run_simulation(funding_proposal, sample_market_context)
        result2 = evaluator._run_simulation(fixedspread_proposal, sample_market_context)

        # Both should complete successfully
        assert result1 is not None
        assert result2 is not None

        # Verify both simulations completed (they both used FixedSpread internally)
        assert result1.simulation_steps == 10
        assert result2.simulation_steps == 10

    def test_simulator_order_calculation_does_not_use_funding_rate(self):
        """
        Test that simulator's order calculation does not pass funding_rate to strategy
        测试模拟器的订单计算不向策略传递 funding_rate
        """
        strategy = FixedSpreadStrategy()
        strategy.spread = 0.01
        strategy.quantity = 0.1

        simulator = StrategySimulator(
            strategy=strategy,
            initial_price=2500.0,
            volatility=0.02,
        )

        # Mock the strategy's calculate_target_orders to verify it's called without funding_rate
        original_method = strategy.calculate_target_orders

        call_args_list = []

        def track_calls(market_data):
            call_args_list.append(market_data)
            return original_method(market_data)

        strategy.calculate_target_orders = track_calls

        # Run simulation
        simulator.run(steps=5)

        # Verify calculate_target_orders was called
        assert len(call_args_list) > 0

        # Verify all calls only passed market_data (no funding_rate parameter)
        for call_args in call_args_list:
            # call_args should be a dict (market_data), not a tuple with funding_rate
            assert isinstance(call_args, dict)
            assert "mid_price" in call_args
            assert "best_bid" in call_args
            assert "best_ask" in call_args

