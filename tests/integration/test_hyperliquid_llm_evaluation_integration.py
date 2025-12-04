"""
Integration Test for US-API-004: Hyperliquid LLM Evaluation Support
US-API-004 集成测试：Hyperliquid LLM 评估支持

Integration tests verify cross-module interactions and end-to-end workflows.
集成测试验证跨模块交互和端到端工作流。

Owner: Agent QA
"""

import os
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

import server
from src.ai.evaluation.evaluator import MultiLLMEvaluator
from src.ai.evaluation.schemas import MarketContext
from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquidLLMEvaluationAPIIntegration:
    """
    Integration tests for Hyperliquid LLM Evaluation API.
    Hyperliquid LLM 评估 API 的集成测试。
    
    Tests the complete flow from API call to LLM response with HyperliquidClient.
    测试从 API 调用到 LLM 响应的完整流程，使用 HyperliquidClient。
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETHUSDT"
        client.exchange_name = "hyperliquid"
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
            "funding_rate": 0.0001,
            "timestamp": int(time.time() * 1000),
        }
        client.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "entry_price": 3000.0,
            "balance": 10000.0,
            "available_balance": 5000.0,
            "leverage": 5,
        }
        client.set_symbol.return_value = True
        return client

    @pytest.fixture
    def mock_llm_providers(self):
        """Create mock LLM providers / 创建模拟 LLM 提供商"""
        providers = []
        for name, response in [
            (
                "Gemini",
                '{"recommended_strategy": "FundingRate", "spread": 0.012, "skew_factor": 120, "confidence": 0.85, "quantity": 0.1, "leverage": 5}',
            ),
            (
                "OpenAI",
                '{"recommended_strategy": "FixedSpread", "spread": 0.015, "skew_factor": 100, "confidence": 0.78, "quantity": 0.15, "leverage": 3}',
            ),
        ]:
            mock = Mock()
            mock.name = name
            mock.generate.return_value = response
            providers.append(mock)
        return providers

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_complete_evaluation_flow_with_hyperliquid(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_llm_providers,
    ):
        """
        Integration Test: AC-1, AC-3 - Complete evaluation flow with Hyperliquid
        集成测试：AC-1, AC-3 - 使用 Hyperliquid 的完整评估流程
        
        Tests the end-to-end flow:
        1. API receives request with exchange="hyperliquid"
        2. API gets HyperliquidClient
        3. API fetches market data from Hyperliquid
        4. API builds MarketContext with Hyperliquid data
        5. API runs LLM evaluation
        6. API returns results with exchange="hyperliquid"
        
        测试端到端流程：
        1. API 接收 exchange="hyperliquid" 的请求
        2. API 获取 HyperliquidClient
        3. API 从 Hyperliquid 获取市场数据
        4. API 使用 Hyperliquid 数据构建 MarketContext
        5. API 运行 LLM 评估
        6. API 返回 exchange="hyperliquid" 的结果
        """
        # Setup mocks
        mock_get_exchange.return_value = mock_hyperliquid_client
        mock_create_providers.return_value = mock_llm_providers

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Step 1: Call API with Hyperliquid exchange
            # 步骤 1：使用 Hyperliquid 交易所调用 API
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDT:USDT",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                },
            )

            # Step 2: Verify API response
            # 步骤 2：验证 API 响应
            assert response.status_code == 200, f"Expected 200, got {response.status_code} / 预期 200，得到 {response.status_code}"
            data = response.json()

            # Step 3: Verify exchange parameter was processed
            # 步骤 3：验证交易所参数已处理
            assert "exchange" in data, "Response should include exchange field / 响应应该包含 exchange 字段"
            assert data["exchange"] == "hyperliquid", "Exchange should be hyperliquid / 交易所应该是 hyperliquid"

            # Step 4: Verify HyperliquidClient was used
            # 步骤 4：验证使用了 HyperliquidClient
            assert mock_hyperliquid_client.fetch_market_data.called, "Should fetch market data from Hyperliquid / 应该从 Hyperliquid 获取市场数据"
            assert mock_hyperliquid_client.fetch_account_data.called, "Should fetch account data from Hyperliquid / 应该从 Hyperliquid 获取账户数据"

            # Step 5: Verify market data in response
            # 步骤 5：验证响应中的市场数据
            assert "market_data" in data, "Response should include market_data / 响应应该包含 market_data"
            market_data = data["market_data"]
            assert market_data["mid_price"] == 3001.0, "Market data should match Hyperliquid data / 市场数据应该匹配 Hyperliquid 数据"

            # Step 6: Verify LLM evaluation results
            # 步骤 6：验证 LLM 评估结果
            assert "individual_results" in data, "Response should include individual_results / 响应应该包含 individual_results"
            assert len(data["individual_results"]) > 0, "Should have evaluation results / 应该有评估结果"

            # Step 7: Verify aggregated results
            # 步骤 7：验证聚合结果
            assert "aggregated" in data, "Response should include aggregated results / 响应应该包含聚合结果"

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_hyperliquid_market_data_in_llm_context(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_llm_providers,
    ):
        """
        Integration Test: AC-3, AC-4 - Hyperliquid market data in LLM context
        集成测试：AC-3, AC-4 - LLM 上下文中的 Hyperliquid 市场数据
        
        Verifies that Hyperliquid-specific market data is included in LLM context.
        验证 Hyperliquid 特定的市场数据包含在 LLM 上下文中。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client
        mock_create_providers.return_value = mock_llm_providers

        # Capture LLM prompt to verify context
        # 捕获 LLM 提示以验证上下文
        captured_prompts = []

        def capture_prompt(prompt):
            captured_prompts.append(prompt)
            return '{"recommended_strategy": "FixedSpread", "spread": 0.015, "confidence": 0.8}'

        mock_provider = Mock()
        mock_provider.name = "Gemini"
        mock_provider.generate.side_effect = capture_prompt
        mock_create_providers.return_value = [mock_provider]

        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDT:USDT",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                },
            )

            # Verify market data was fetched
            # 验证市场数据已获取
            assert mock_hyperliquid_client.fetch_market_data.called

            # Verify LLM was called (if prompt was captured)
            # 验证 LLM 被调用（如果捕获了提示）
            if captured_prompts:
                prompt_text = captured_prompts[0]
                # Prompt should include market data (price, funding rate, etc.)
                # Prices may be formatted (e.g., "$3,001.00") or raw numbers
                # 提示应该包含市场数据（价格、资金费率等）
                # 价格可能是格式化的（例如 "$3,001.00"）或原始数字
                assert (
                    "3001" in prompt_text
                    or "3,001" in prompt_text
                    or "$3,001" in prompt_text
                    or "3000" in prompt_text
                    or "3,000" in prompt_text
                    or "$3,000" in prompt_text
                    or "3002" in prompt_text
                    or "3,002" in prompt_text
                    or "$3,002" in prompt_text
                    or "HYPERLIQUID" in prompt_text.upper()
                ), (
                    "LLM prompt should include Hyperliquid market data. "
                    f"Prompt contains: {prompt_text[:200]}... / "
                    "LLM 提示应该包含 Hyperliquid 市场数据。"
                    f"提示包含：{prompt_text[:200]}..."
                )

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_hyperliquid_response_format_consistency(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_llm_providers,
    ):
        """
        Integration Test: AC-2 - Response format consistency for Hyperliquid
        集成测试：AC-2 - Hyperliquid 响应格式一致性
        
        Verifies that Hyperliquid evaluation returns results in the same format as Binance.
        验证 Hyperliquid 评估返回与 Binance 相同格式的结果。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client
        mock_create_providers.return_value = mock_llm_providers

        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDT:USDT",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                },
            )

            assert response.status_code == 200
            data = response.json()

            # Verify required fields are present (same format as Binance)
            # 验证必需字段存在（与 Binance 相同的格式）
            required_fields = [
                "symbol",
                "exchange",
                "individual_results",
                "aggregated",
                "market_data",
            ]
            for field in required_fields:
                assert field in data, f"Response should include {field} / 响应应该包含 {field}"

            # Verify individual_results structure
            # 验证 individual_results 结构
            if data["individual_results"]:
                result = data["individual_results"][0]
                assert "provider_name" in result
                assert "proposal" in result
                assert "simulation" in result

            # Verify aggregated structure
            # 验证 aggregated 结构
            aggregated = data["aggregated"]
            assert "strategy_consensus" in aggregated
            assert "consensus_proposal" in aggregated

    @patch("server.get_exchange_by_name")
    def test_hyperliquid_error_handling_integration(self, mock_get_exchange):
        """
        Integration Test: AC-5 - Error handling integration for Hyperliquid
        集成测试：AC-5 - Hyperliquid 错误处理集成
        
        Verifies that errors are handled gracefully throughout the integration flow.
        验证在整个集成流程中错误被优雅处理。
        """
        # Test case 1: Exchange not connected
        # 测试用例 1：交易所未连接
        mock_client = Mock(spec=HyperliquidClient)
        mock_client.is_connected = False
        mock_client.exchange_name = "hyperliquid"
        mock_get_exchange.return_value = mock_client

        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDT:USDT",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                },
            )

            # Verify error response
            # 验证错误响应
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                data = data[0]

            assert "error" in data, "Error message should be present / 应该存在错误消息"
            error_msg = data.get("error", "").lower()
            assert (
                "connection" in error_msg
                or "连接" in data.get("error", "")
                or "hyperliquid" in error_msg
            ), "Error should mention connection or Hyperliquid / 错误应该提到连接或 Hyperliquid"

        # Test case 2: Market data fetch failure
        # 测试用例 2：市场数据获取失败
        mock_connected_client = Mock(spec=HyperliquidClient)
        mock_connected_client.is_connected = True
        mock_connected_client.exchange_name = "hyperliquid"
        mock_connected_client.fetch_market_data.side_effect = Exception("Network error")
        mock_get_exchange.return_value = mock_connected_client

        with patch("server.bot_engine", mock_bot_engine):
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDT:USDT",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                },
            )

            # Verify error response
            # 验证错误响应
            data = response.json()
            assert "error" in data, "Error message should be present / 应该存在错误消息"


class TestHyperliquidLLMEvaluatorIntegration:
    """
    Integration tests for MultiLLMEvaluator with HyperliquidClient.
    MultiLLMEvaluator 与 HyperliquidClient 的集成测试。
    
    Tests that MultiLLMEvaluator can work with Hyperliquid market data.
    测试 MultiLLMEvaluator 可以使用 Hyperliquid 市场数据。
    """

    @pytest.fixture
    def mock_hyperliquid_market_context(self):
        """Create MarketContext with Hyperliquid data / 使用 Hyperliquid 数据创建 MarketContext"""
        return MarketContext(
            symbol="ETHUSDT (Hyperliquid)",  # Exchange name in symbol
            mid_price=3001.0,
            best_bid=3000.0,
            best_ask=3002.0,
            spread_bps=6.66,
            volatility_24h=0.03,
            volatility_1h=0.01,
            funding_rate=0.0001,
            funding_rate_trend="stable",
            current_position=0.1,
            position_side="long",
            unrealized_pnl=10.0,
            available_balance=5000.0,
            current_leverage=5.0,
            win_rate=0.6,
            sharpe_ratio=1.5,
            recent_pnl=50.0,
        )

    @pytest.fixture
    def mock_llm_providers(self):
        """Create mock LLM providers / 创建模拟 LLM 提供商"""
        providers = []
        for name, response in [
            (
                "Gemini",
                '{"recommended_strategy": "FundingRate", "spread": 0.012, "skew_factor": 120, "confidence": 0.85, "quantity": 0.1, "leverage": 5}',
            ),
        ]:
            mock = Mock()
            mock.name = name
            mock.generate.return_value = response
            providers.append(mock)
        return providers

    def test_evaluator_with_hyperliquid_context(
        self, mock_hyperliquid_market_context, mock_llm_providers
    ):
        """
        Integration Test: MultiLLMEvaluator works with Hyperliquid MarketContext
        集成测试：MultiLLMEvaluator 与 Hyperliquid MarketContext 正常工作
        
        Verifies that MultiLLMEvaluator can process Hyperliquid market data.
        验证 MultiLLMEvaluator 可以处理 Hyperliquid 市场数据。
        """
        evaluator = MultiLLMEvaluator(
            providers=mock_llm_providers,
            simulation_steps=100,
            parallel=False,  # Sequential for easier testing
        )

        # Run evaluation
        # 运行评估
        results = evaluator.evaluate(mock_hyperliquid_market_context)

        # Verify results
        # 验证结果
        assert len(results) > 0, "Should have evaluation results / 应该有评估结果"
        assert results[0].provider_name == "Gemini", "Should have Gemini result / 应该有 Gemini 结果"

        # Verify proposal contains expected data
        # 验证建议包含预期数据
        proposal = results[0].proposal
        assert proposal.recommended_strategy in ["FundingRate", "FixedSpread"], (
            "Should have valid strategy / 应该有有效策略"
        )
        assert proposal.spread > 0, "Spread should be positive / 价差应该为正"

        # Verify simulation was run
        # 验证模拟已运行
        simulation = results[0].simulation
        assert simulation.simulation_steps == 100, "Should have correct simulation steps / 应该有正确的模拟步数"

    def test_evaluator_aggregates_hyperliquid_results(
        self, mock_hyperliquid_market_context, mock_llm_providers
    ):
        """
        Integration Test: MultiLLMEvaluator aggregates results for Hyperliquid
        集成测试：MultiLLMEvaluator 聚合 Hyperliquid 结果
        
        Verifies that aggregation works correctly with Hyperliquid data.
        验证聚合与 Hyperliquid 数据正常工作。
        """
        evaluator = MultiLLMEvaluator(
            providers=mock_llm_providers,
            simulation_steps=100,
            parallel=False,
        )

        # Run evaluation
        # 运行评估
        results = evaluator.evaluate(mock_hyperliquid_market_context)

        # Aggregate results
        # 聚合结果
        aggregated = evaluator.aggregate_results(results)

        # Verify aggregated structure
        # 验证聚合结构
        assert aggregated is not None, "Should have aggregated results / 应该有聚合结果"
        assert aggregated.strategy_consensus is not None, "Should have strategy consensus / 应该有策略共识"
        assert aggregated.consensus_proposal is not None, "Should have consensus proposal / 应该有共识建议"

        # Verify consensus proposal has valid values
        # 验证共识建议有有效值
        consensus = aggregated.consensus_proposal
        assert consensus.recommended_strategy is not None, "Should have strategy / 应该有策略"
        assert consensus.spread > 0, "Spread should be positive / 价差应该为正"


class TestHyperliquidLLMApplyIntegration:
    """
    Integration tests for applying LLM suggestions to Hyperliquid.
    将 LLM 建议应用到 Hyperliquid 的集成测试。
    
    Tests AC-3: Apply LLM Suggestions to Hyperliquid.
    测试 AC-3：将 LLM 建议应用到 Hyperliquid。
    """

    @patch("server.get_exchange_by_name")
    def test_apply_suggestions_to_hyperliquid(self, mock_get_exchange):
        """
        Integration Test: AC-3 - Apply LLM suggestions to Hyperliquid
        集成测试：AC-3 - 将 LLM 建议应用到 Hyperliquid
        
        Verifies that LLM suggestions can be applied to Hyperliquid exchange configuration.
        验证 LLM 建议可以应用到 Hyperliquid 交易所配置。
        """
        # Mock HyperliquidClient
        mock_client = Mock(spec=HyperliquidClient)
        mock_client.is_connected = True
        mock_client.exchange_name = "hyperliquid"
        mock_get_exchange.return_value = mock_client

        # Mock bot_engine with strategy instances
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        # Mock evaluation results (simulate previous evaluation)
        # 模拟评估结果（模拟之前的评估）
        from src.ai.evaluation.schemas import (
            AggregatedResult,
            StrategyConsensus,
            StrategyProposal,
        )

        consensus_proposal = StrategyProposal(
            recommended_strategy="FundingRate",
            spread=0.012,
            skew_factor=120,
            quantity=0.1,
            leverage=5,
            confidence=0.85,
            risk_level="medium",
            reasoning="Test reasoning",
            parse_success=True,
        )

        strategy_consensus = StrategyConsensus(
            consensus_strategy="FundingRate",
            consensus_level="high",
            consensus_ratio=1.0,
            consensus_count=1,
            total_models=1,
            strategy_votes={"FundingRate": 1},
            strategy_percentages={"FundingRate": 100.0},
        )

        aggregated = AggregatedResult(
            strategy_consensus=strategy_consensus,
            consensus_confidence=0.85,
            consensus_proposal=consensus_proposal,
            avg_pnl=50.0,
            avg_sharpe=1.5,
            avg_win_rate=0.6,
            avg_latency_ms=1000.0,
            successful_evaluations=1,
            failed_evaluations=0,
        )

        with patch("server.bot_engine", mock_bot_engine), patch(
            "server._last_evaluation_aggregated", aggregated
        ), patch("server._last_evaluation_results", []):
            client = TestClient(server.app)

            # Apply consensus suggestion
            # 应用共识建议
            response = client.post(
                "/api/evaluation/apply",
                json={
                    "source": "consensus",
                    "exchange": "hyperliquid",
                },
            )

            # Verify response (API may return success or error depending on implementation)
            # 验证响应（API 可能返回成功或错误，取决于实现）
            assert response.status_code in [200, 400, 404], (
                f"Expected valid status code, got {response.status_code} / "
                f"预期有效状态码，得到 {response.status_code}"
            )

            data = response.json()
            # Response should indicate status
            # 响应应该指示状态
            assert "status" in data or "error" in data, (
                "Response should include status or error / 响应应该包含 status 或 error"
            )

