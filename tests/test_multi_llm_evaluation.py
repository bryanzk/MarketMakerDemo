"""
多 LLM 策略评估系统测试用例
Test Cases for Multi-LLM Strategy Evaluation System

基于用户故事 (user_stories_multi_llm.md) 编写
测试用例编号对应用户故事编号 US-ML-XXX
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import time


# ============================================================================
# US-ML-001: 交易员获取多模型策略建议
# ============================================================================


class TestUSML001_GetMultiModelSuggestions:
    """US-ML-001: 交易员获取多模型策略建议"""

    @pytest.fixture
    def sample_market_context(self):
        """创建示例市场上下文"""
        from alphaloop.evaluation.schemas import MarketContext

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

    @pytest.fixture
    def mock_three_providers(self):
        """创建三个 Mock Provider"""
        gemini = Mock()
        gemini.name = "Gemini (gemini-1.5-pro)"
        gemini.generate.return_value = '{"recommended_strategy": "FundingRate", "spread": 0.012, "skew_factor": 120, "confidence": 0.85, "reasoning": "Positive funding rate"}'

        openai = Mock()
        openai.name = "OpenAI (gpt-4o)"
        openai.generate.return_value = '{"recommended_strategy": "FixedSpread", "spread": 0.015, "skew_factor": 100, "confidence": 0.78, "reasoning": "High volatility"}'

        claude = Mock()
        claude.name = "Claude (claude-sonnet-4-20250514)"
        claude.generate.return_value = '{"recommended_strategy": "FundingRate", "spread": 0.010, "skew_factor": 150, "confidence": 0.92, "reasoning": "Strong funding opportunity"}'

        return [gemini, openai, claude]

    def test_AC1_should_receive_3_evaluation_results(
        self, mock_three_providers, sample_market_context
    ):
        """
        验收标准: 我应该收到 3 个评估结果
        AC: 调用 evaluate() 后返回 3 个结果
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        evaluator = MultiLLMEvaluator(providers=mock_three_providers)
        results = evaluator.evaluate(sample_market_context)

        assert len(results) == 3, "应该返回 3 个评估结果"

    def test_AC2_each_result_contains_strategy_and_parameters(
        self, mock_three_providers, sample_market_context
    ):
        """
        验收标准: 每个结果包含策略类型、参数建议、置信度
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        evaluator = MultiLLMEvaluator(providers=mock_three_providers)
        results = evaluator.evaluate(sample_market_context)

        for result in results:
            assert result.proposal.recommended_strategy in [
                "FixedSpread",
                "FundingRate",
            ], "策略类型应该是 FixedSpread 或 FundingRate"
            assert (
                0.005 <= result.proposal.spread <= 0.03
            ), "spread 应该在合理范围内"
            assert (
                0 <= result.proposal.confidence <= 1
            ), "置信度应该在 0-1 之间"

    def test_AC3_each_result_contains_provider_name(
        self, mock_three_providers, sample_market_context
    ):
        """
        验收标准: 每个结果包含模型名称标识
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        evaluator = MultiLLMEvaluator(providers=mock_three_providers)
        results = evaluator.evaluate(sample_market_context)

        provider_names = [r.provider_name for r in results]
        assert any("Gemini" in name for name in provider_names)
        assert any("OpenAI" in name for name in provider_names)
        assert any("Claude" in name for name in provider_names)

    def test_AC4_partial_failure_still_returns_valid_results(
        self, sample_market_context
    ):
        """
        验收标准: 部分模型 API 失败时仍返回可用结果
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        # 创建一个会失败的 Provider
        failing_provider = Mock()
        failing_provider.name = "FailingLLM"
        failing_provider.generate.side_effect = RuntimeError("API Error")

        working_provider = Mock()
        working_provider.name = "WorkingLLM"
        working_provider.generate.return_value = (
            '{"recommended_strategy": "FixedSpread", "spread": 0.01, "confidence": 0.8}'
        )

        evaluator = MultiLLMEvaluator(providers=[failing_provider, working_provider])
        results = evaluator.evaluate(sample_market_context)

        assert len(results) == 2, "应该返回 2 个结果（包括失败的）"

        # 验证失败的结果被正确标记
        failed = next(r for r in results if r.provider_name == "FailingLLM")
        assert failed.proposal.parse_success is False

        # 验证成功的结果
        success = next(r for r in results if r.provider_name == "WorkingLLM")
        assert success.proposal.parse_success is True

    def test_AC5_parse_json_with_markdown_code_block(self, sample_market_context):
        """
        验收标准: 正确解析带有 markdown 代码块的 JSON
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        provider = Mock()
        provider.name = "TestLLM"
        provider.generate.return_value = """
        ```json
        {
            "recommended_strategy": "FundingRate",
            "spread": 0.012,
            "skew_factor": 120,
            "confidence": 0.85
        }
        ```
        """

        evaluator = MultiLLMEvaluator(providers=[provider])
        results = evaluator.evaluate(sample_market_context)

        assert results[0].proposal.parse_success is True
        assert results[0].proposal.spread == 0.012
        assert results[0].proposal.skew_factor == 120

    def test_AC6_invalid_json_uses_default_values(self, sample_market_context):
        """
        验收标准: JSON 格式错误时使用默认值并标记解析失败
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        provider = Mock()
        provider.name = "TestLLM"
        provider.generate.return_value = "This is not valid JSON!!!"

        evaluator = MultiLLMEvaluator(providers=[provider])
        results = evaluator.evaluate(sample_market_context)

        assert results[0].proposal.parse_success is False
        assert results[0].proposal.spread == 0.01  # 默认值


# ============================================================================
# US-ML-002: 交易员比较模型建议的模拟表现
# ============================================================================


class TestUSML002_SimulationComparison:
    """US-ML-002: 交易员比较模型建议的模拟表现"""

    @pytest.fixture
    def sample_market_context(self):
        from alphaloop.evaluation.schemas import MarketContext

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
        )

    @pytest.fixture
    def mock_providers(self):
        providers = []
        for name, spread in [("Gemini", 0.012), ("OpenAI", 0.015), ("Claude", 0.010)]:
            p = Mock()
            p.name = name
            p.generate.return_value = f'{{"recommended_strategy": "FixedSpread", "spread": {spread}, "confidence": 0.8}}'
            providers.append(p)
        return providers

    def test_AC1_each_suggestion_has_simulation_result(
        self, mock_providers, sample_market_context
    ):
        """
        验收标准: 每个建议都应该有对应的模拟结果
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        evaluator = MultiLLMEvaluator(providers=mock_providers, simulation_steps=100)
        results = evaluator.evaluate(sample_market_context)

        for result in results:
            assert result.simulation is not None
            assert hasattr(result.simulation, "realized_pnl")
            assert hasattr(result.simulation, "win_rate")
            assert hasattr(result.simulation, "sharpe_ratio")

    def test_AC2_simulation_result_contains_required_metrics(
        self, mock_providers, sample_market_context
    ):
        """
        验收标准: 模拟结果包含 PnL、胜率、夏普比率
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        evaluator = MultiLLMEvaluator(providers=mock_providers, simulation_steps=100)
        results = evaluator.evaluate(sample_market_context)

        for result in results:
            # PnL 可以是正或负
            assert isinstance(result.simulation.realized_pnl, (int, float))
            # 胜率在 0-1 之间
            assert 0 <= result.simulation.win_rate <= 1
            # 夏普比率是数值
            assert isinstance(result.simulation.sharpe_ratio, (int, float))

    def test_AC3_simulation_uses_suggested_parameters(self, sample_market_context):
        """
        验收标准: 模拟使用建议的参数
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        # Gemini 建议 spread=0.012
        gemini = Mock()
        gemini.name = "Gemini"
        gemini.generate.return_value = '{"recommended_strategy": "FixedSpread", "spread": 0.012, "skew_factor": 120, "confidence": 0.85}'

        evaluator = MultiLLMEvaluator(providers=[gemini], simulation_steps=100)
        results = evaluator.evaluate(sample_market_context)

        # 验证解析的参数
        assert results[0].proposal.spread == 0.012
        assert results[0].proposal.skew_factor == 120

    def test_AC4_configurable_simulation_steps(self, mock_providers, sample_market_context):
        """
        验收标准: 可配置模拟步数
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        evaluator = MultiLLMEvaluator(providers=mock_providers, simulation_steps=1000)
        results = evaluator.evaluate(sample_market_context)

        for result in results:
            assert result.simulation.simulation_steps == 1000


# ============================================================================
# US-ML-003: 交易员获取排名结果
# ============================================================================


class TestUSML003_RankedResults:
    """US-ML-003: 交易员获取排名结果"""

    @pytest.fixture
    def sample_market_context(self):
        from alphaloop.evaluation.schemas import MarketContext

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
        )

    def test_AC1_results_sorted_by_score_descending(self, sample_market_context):
        """
        验收标准: 结果应该按 score 降序排列
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        providers = []
        for name in ["ModelA", "ModelB", "ModelC"]:
            p = Mock()
            p.name = name
            p.generate.return_value = '{"recommended_strategy": "FixedSpread", "spread": 0.01, "confidence": 0.8}'
            providers.append(p)

        evaluator = MultiLLMEvaluator(providers=providers)
        results = evaluator.evaluate(sample_market_context)

        # 验证按 score 降序
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_AC2_ranks_are_sequential(self, sample_market_context):
        """
        验收标准: 第一名的 rank=1，第二名的 rank=2，依此类推
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        providers = []
        for name in ["ModelA", "ModelB", "ModelC"]:
            p = Mock()
            p.name = name
            p.generate.return_value = '{"recommended_strategy": "FixedSpread", "spread": 0.01, "confidence": 0.8}'
            providers.append(p)

        evaluator = MultiLLMEvaluator(providers=providers)
        results = evaluator.evaluate(sample_market_context)

        ranks = sorted([r.rank for r in results])
        assert ranks == [1, 2, 3]

    def test_AC3_get_best_proposal_returns_rank_1(self, sample_market_context):
        """
        验收标准: get_best_proposal 返回 rank=1 的结果
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        providers = []
        for name in ["ModelA", "ModelB", "ModelC"]:
            p = Mock()
            p.name = name
            p.generate.return_value = '{"recommended_strategy": "FixedSpread", "spread": 0.01, "confidence": 0.8}'
            providers.append(p)

        evaluator = MultiLLMEvaluator(providers=providers)
        results = evaluator.evaluate(sample_market_context)

        best = MultiLLMEvaluator.get_best_proposal(results)
        assert best.rank == 1

    def test_AC4_failed_parse_has_zero_score(self, sample_market_context):
        """
        验收标准: 解析失败的结果 score 应该为 0
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        failing = Mock()
        failing.name = "FailingModel"
        failing.generate.return_value = "invalid json"

        working = Mock()
        working.name = "WorkingModel"
        working.generate.return_value = '{"recommended_strategy": "FixedSpread", "spread": 0.01, "confidence": 0.8}'

        evaluator = MultiLLMEvaluator(providers=[failing, working])
        results = evaluator.evaluate(sample_market_context)

        failed = next(r for r in results if r.provider_name == "FailingModel")
        assert failed.score == 0
        assert failed.rank == 2  # 应该是最后一名


# ============================================================================
# US-ML-004: 交易员查看对比表格
# ============================================================================


class TestUSML004_ComparisonTable:
    """US-ML-004: 交易员查看对比表格"""

    def test_AC1_generate_formatted_table(self):
        """
        验收标准: 生成格式化的字符串表格
        """
        from alphaloop.evaluation.schemas import (
            EvaluationResult,
            StrategyProposal,
            SimulationResult,
        )
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        results = [
            EvaluationResult(
                provider_name="Gemini",
                proposal=StrategyProposal(
                    recommended_strategy="FundingRate",
                    spread=0.012,
                    skew_factor=120,
                    confidence=0.85,
                ),
                simulation=SimulationResult(
                    realized_pnl=180.0,
                    win_rate=0.58,
                    sharpe_ratio=2.1,
                    simulation_steps=500,
                ),
                score=85.0,
                rank=1,
                latency_ms=1250,
            ),
        ]

        table = MultiLLMEvaluator.generate_comparison_table(results)

        assert isinstance(table, str)
        assert len(table) > 0
        assert "Gemini" in table

    def test_AC2_table_contains_required_columns(self):
        """
        验收标准: 表格包含排名、模型名、策略、参数、PnL、胜率、夏普、评分
        """
        from alphaloop.evaluation.schemas import (
            EvaluationResult,
            StrategyProposal,
            SimulationResult,
        )
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        results = [
            EvaluationResult(
                provider_name="TestModel",
                proposal=StrategyProposal(
                    recommended_strategy="FixedSpread",
                    spread=0.015,
                    skew_factor=100,
                    confidence=0.78,
                ),
                simulation=SimulationResult(
                    realized_pnl=120.0,
                    win_rate=0.52,
                    sharpe_ratio=1.5,
                    simulation_steps=500,
                ),
                score=72.0,
                rank=1,
                latency_ms=980,
            ),
        ]

        table = MultiLLMEvaluator.generate_comparison_table(results)

        # 检查关键列是否存在
        assert "Rank" in table
        assert "Provider" in table
        assert "Strategy" in table
        assert "Spread" in table
        assert "PnL" in table or "pnl" in table.lower()

    def test_AC3_pnl_formatted_with_currency(self):
        """
        验收标准: PnL 显示为带货币符号的格式
        """
        from alphaloop.evaluation.schemas import (
            EvaluationResult,
            StrategyProposal,
            SimulationResult,
        )
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        results = [
            EvaluationResult(
                provider_name="TestModel",
                proposal=StrategyProposal(
                    recommended_strategy="FixedSpread",
                    spread=0.01,
                    confidence=0.8,
                ),
                simulation=SimulationResult(realized_pnl=200.0, win_rate=0.6),
                score=80.0,
                rank=1,
            ),
        ]

        table = MultiLLMEvaluator.generate_comparison_table(results)
        assert "$" in table or "200" in table

    def test_AC4_latency_displayed_in_milliseconds(self):
        """
        验收标准: 延迟显示为毫秒
        """
        from alphaloop.evaluation.schemas import (
            EvaluationResult,
            StrategyProposal,
            SimulationResult,
        )
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        results = [
            EvaluationResult(
                provider_name="TestModel",
                proposal=StrategyProposal(
                    recommended_strategy="FixedSpread",
                    spread=0.01,
                    confidence=0.8,
                ),
                simulation=SimulationResult(),
                score=80.0,
                rank=1,
                latency_ms=1250,
            ),
        ]

        table = MultiLLMEvaluator.generate_comparison_table(results)
        assert "1250" in table or "ms" in table


# ============================================================================
# US-ML-005: 交易员查看建议理由
# ============================================================================


class TestUSML005_SuggestionReasoning:
    """US-ML-005: 交易员查看建议理由"""

    @pytest.fixture
    def sample_market_context(self):
        from alphaloop.evaluation.schemas import MarketContext

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
        )

    def test_AC1_proposal_contains_reasoning(self, sample_market_context):
        """
        验收标准: StrategyProposal.reasoning 应该包含理由文本
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        provider = Mock()
        provider.name = "TestLLM"
        provider.generate.return_value = '{"recommended_strategy": "FundingRate", "spread": 0.01, "reasoning": "Positive funding rate detected, short bias recommended", "confidence": 0.9}'

        evaluator = MultiLLMEvaluator(providers=[provider])
        results = evaluator.evaluate(sample_market_context)

        assert "funding" in results[0].proposal.reasoning.lower()

    def test_AC2_proposal_contains_risk_level(self, sample_market_context):
        """
        验收标准: StrategyProposal.risk_level 应该是 low、medium 或 high
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        provider = Mock()
        provider.name = "TestLLM"
        provider.generate.return_value = '{"recommended_strategy": "FixedSpread", "spread": 0.01, "risk_level": "medium", "confidence": 0.8}'

        evaluator = MultiLLMEvaluator(providers=[provider])
        results = evaluator.evaluate(sample_market_context)

        assert results[0].proposal.risk_level in ["low", "medium", "high"]

    def test_AC3_proposal_contains_expected_return(self, sample_market_context):
        """
        验收标准: StrategyProposal.expected_return 应该是浮点数
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        provider = Mock()
        provider.name = "TestLLM"
        provider.generate.return_value = '{"recommended_strategy": "FixedSpread", "spread": 0.01, "expected_return": 0.05, "confidence": 0.8}'

        evaluator = MultiLLMEvaluator(providers=[provider])
        results = evaluator.evaluate(sample_market_context)

        assert isinstance(results[0].proposal.expected_return, float)
        assert results[0].proposal.expected_return == 0.05


# ============================================================================
# US-ML-006: 系统测量 LLM 响应延迟
# ============================================================================


class TestUSML006_LatencyMeasurement:
    """US-ML-006: 系统测量 LLM 响应延迟"""

    @pytest.fixture
    def sample_market_context(self):
        from alphaloop.evaluation.schemas import MarketContext

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
        )

    def test_AC1_latency_recorded_in_milliseconds(self, sample_market_context):
        """
        验收标准: 延迟以毫秒为单位存储在 latency_ms 字段
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        def slow_generate(prompt):
            time.sleep(0.1)  # 模拟 100ms 延迟
            return '{"recommended_strategy": "FixedSpread", "spread": 0.01, "confidence": 0.8}'

        provider = Mock()
        provider.name = "SlowLLM"
        provider.generate.side_effect = slow_generate

        evaluator = MultiLLMEvaluator(providers=[provider])
        results = evaluator.evaluate(sample_market_context)

        # 延迟应该大于等于 100ms
        assert results[0].latency_ms >= 100

    def test_AC2_latency_included_in_result(self, sample_market_context):
        """
        验收标准: 延迟包含在 EvaluationResult 中
        """
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        provider = Mock()
        provider.name = "TestLLM"
        provider.generate.return_value = '{"recommended_strategy": "FixedSpread", "spread": 0.01, "confidence": 0.8}'

        evaluator = MultiLLMEvaluator(providers=[provider])
        results = evaluator.evaluate(sample_market_context)

        assert hasattr(results[0], "latency_ms")
        assert results[0].latency_ms >= 0


# ============================================================================
# 数据模型测试 (Schema Tests)
# ============================================================================


class TestMarketContext:
    """测试市场上下文数据模型"""

    def test_create_with_required_fields(self):
        """应该能创建包含所有必要字段的市场上下文"""
        from alphaloop.evaluation.schemas import MarketContext

        ctx = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        assert ctx.symbol == "ETHUSDT"
        assert ctx.mid_price == 2500.0
        assert ctx.funding_rate == 0.0001

    def test_to_prompt_string_format(self):
        """应该能将上下文转换为 LLM Prompt 字符串"""
        from alphaloop.evaluation.schemas import MarketContext

        ctx = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = ctx.to_prompt_string()

        assert "ETHUSDT" in prompt
        assert "2,500.00" in prompt
        assert "rising" in prompt


class TestStrategyProposal:
    """测试策略建议数据模型"""

    def test_create_proposal(self):
        """应该能创建策略建议"""
        from alphaloop.evaluation.schemas import StrategyProposal

        proposal = StrategyProposal(
            recommended_strategy="FundingRate",
            spread=0.012,
            skew_factor=150.0,
            confidence=0.85,
            provider_name="Gemini",
        )

        assert proposal.recommended_strategy == "FundingRate"
        assert proposal.spread == 0.012
        assert proposal.confidence == 0.85


class TestEvaluationResult:
    """测试评估结果数据模型"""

    def test_to_summary(self):
        """应该能生成结果摘要"""
        from alphaloop.evaluation.schemas import (
            EvaluationResult,
            StrategyProposal,
            SimulationResult,
        )

        result = EvaluationResult(
            provider_name="OpenAI (gpt-4o)",
            proposal=StrategyProposal(
                recommended_strategy="FixedSpread",
                spread=0.01,
                confidence=0.8,
            ),
            simulation=SimulationResult(
                realized_pnl=150.0,
                win_rate=0.55,
                sharpe_ratio=1.8,
            ),
            score=78.5,
            rank=2,
            latency_ms=1250.0,
        )

        summary = result.to_summary()

        assert summary["provider"] == "OpenAI (gpt-4o)"
        assert summary["rank"] == 2


# ============================================================================
# LLM Provider 测试
# ============================================================================


class TestLLMProviders:
    """测试 LLM Provider"""

    def test_gemini_provider_has_name(self):
        """Gemini Provider 应该有 name 属性"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel"):
                    from alphaloop.core.llm import GeminiProvider

                    provider = GeminiProvider()
                    assert "Gemini" in provider.name

    def test_create_all_providers(self):
        """create_all_providers 应该返回所有可用的 Provider"""
        with patch.dict(
            "os.environ",
            {
                "GEMINI_API_KEY": "test-key",
                "OPENAI_API_KEY": "test-key",
                "ANTHROPIC_API_KEY": "test-key",
            },
        ):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel"):
                    # Mock OpenAI
                    mock_openai = MagicMock()
                    with patch.dict("sys.modules", {"openai": mock_openai}):
                        mock_openai.OpenAI = MagicMock()
                        
                        # Mock Anthropic
                        mock_anthropic = MagicMock()
                        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
                            mock_anthropic.Anthropic = MagicMock()
                            
                            from alphaloop.core.llm import create_all_providers
                            
                            providers = create_all_providers()
                            assert len(providers) >= 1  # At least Gemini should work


# ============================================================================
# Prompt 生成测试
# ============================================================================


class TestPromptGeneration:
    """测试 Prompt 生成逻辑"""

    def test_strategy_advisor_prompt_includes_context(self):
        """策略顾问 Prompt 应该包含市场上下文"""
        from alphaloop.evaluation.prompts import StrategyAdvisorPrompt
        from alphaloop.evaluation.schemas import MarketContext

        ctx = MarketContext(
            symbol="BTCUSDT",
            mid_price=45000.0,
            best_bid=44990.0,
            best_ask=45010.0,
            spread_bps=4.4,
            volatility_24h=0.028,
            volatility_1h=0.008,
            funding_rate=0.0002,
            funding_rate_trend="stable",
        )

        prompt = StrategyAdvisorPrompt.generate(ctx)

        assert "BTCUSDT" in prompt
        assert "45,000.00" in prompt
        assert "JSON" in prompt

    def test_prompt_specifies_output_format(self):
        """Prompt 应该明确指定输出格式"""
        from alphaloop.evaluation.prompts import StrategyAdvisorPrompt
        from alphaloop.evaluation.schemas import MarketContext

        ctx = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = StrategyAdvisorPrompt.generate(ctx)

        assert "recommended_strategy" in prompt
        assert "spread" in prompt
        assert "confidence" in prompt


# ============================================================================
# 端到端集成测试
# ============================================================================


class TestEndToEndIntegration:
    """端到端集成测试"""

    def test_full_evaluation_workflow(self):
        """完整评估工作流测试"""
        from alphaloop.evaluation.schemas import MarketContext
        from alphaloop.evaluation.evaluator import MultiLLMEvaluator

        # 1. 准备市场数据
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        # 2. 创建 Mock Providers
        mock_providers = []
        for name, response in [
            ("Gemini", '{"recommended_strategy": "FundingRate", "spread": 0.012, "skew_factor": 120, "confidence": 0.85}'),
            ("OpenAI", '{"recommended_strategy": "FixedSpread", "spread": 0.015, "skew_factor": 100, "confidence": 0.78}'),
            ("Claude", '{"recommended_strategy": "FundingRate", "spread": 0.010, "skew_factor": 150, "confidence": 0.92}'),
        ]:
            mock = Mock()
            mock.name = name
            mock.generate.return_value = response
            mock_providers.append(mock)

        # 3. 运行评估
        evaluator = MultiLLMEvaluator(providers=mock_providers, simulation_steps=100)
        results = evaluator.evaluate(context)

        # 4. 验证结果数量
        assert len(results) == 3

        # 5. 验证排名
        ranks = [r.rank for r in results]
        assert sorted(ranks) == [1, 2, 3]

        # 6. 生成对比表格
        table = MultiLLMEvaluator.generate_comparison_table(results)
        assert len(table) > 0

        # 7. 获取最佳建议
        best = MultiLLMEvaluator.get_best_proposal(results)
        assert best.rank == 1

        # 8. 验证可以导出为 JSON
        summaries = [r.to_summary() for r in results]
        assert len(summaries) == 3
        assert all("provider" in s for s in summaries)
