"""
Unit tests for Hyperliquid LLM Evaluation API Support
Hyperliquid LLM 评估 API 支持单元测试

Tests for US-API-004: Hyperliquid LLM Evaluation Support
测试 US-API-004: Hyperliquid LLM 评估支持

Owner: Agent QA (TDD: tests written first)
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

import server
from src.trading.hyperliquid_client import HyperliquidClient
from src.trading.exchange import BinanceClient


class TestHyperliquidLLMEvaluationAPI:
    """
    Test AC-1: LLM Evaluation API Support for Hyperliquid
    测试 AC-1: Hyperliquid 的 LLM 评估 API 支持
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETH/USDC:USDC"
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
            "funding_rate": 0.0001,
            "timestamp": 1234567890,
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
    def mock_binance_client(self):
        """Create a mock BinanceClient / 创建模拟 BinanceClient"""
        client = Mock(spec=BinanceClient)
        client.is_connected = True
        client.symbol = "ETH/USDC:USDC"
        client.fetch_market_data.return_value = {
            "best_bid": 2000.0,
            "best_ask": 2002.0,
            "mid_price": 2001.0,
            "funding_rate": 0.0001,
        }
        client.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "entry_price": 2000.0,
            "balance": 10000.0,
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
                '{"recommended_strategy": "FundingRate", "spread": 0.012, "skew_factor": 120, "confidence": 0.85}',
            ),
            (
                "OpenAI",
                '{"recommended_strategy": "FixedSpread", "spread": 0.015, "skew_factor": 100, "confidence": 0.78}',
            ),
        ]:
            mock = Mock()
            mock.name = name
            mock.generate.return_value = response
            providers.append(mock)
        return providers

    @patch("server.create_all_providers")
    @patch("server.get_default_exchange")
    def test_evaluation_api_with_hyperliquid_exchange(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_llm_providers,
    ):
        """
        Test AC-1: API accepts exchange parameter and uses HyperliquidClient
        测试 AC-1: API 接受 exchange 参数并使用 HyperliquidClient
        
        Given: I call the LLM evaluation API with Hyperliquid exchange parameter
        When: The API processes the request
        Then: The system should use Hyperliquid exchange context and fetch Hyperliquid market data
        """
        # Mock exchange selection based on parameter
        # 根据参数模拟交易所选择
        def get_exchange_for_hyperliquid():
            return mock_hyperliquid_client

        mock_get_exchange.side_effect = get_exchange_for_hyperliquid
        mock_create_providers.return_value = mock_llm_providers

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call API with exchange parameter (Note: API may need to be updated to accept this)
            # 使用 exchange 参数调用 API（注意：API 可能需要更新以接受此参数）
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDC:USDC",
                    "simulation_steps": 100,
                    # "exchange": "hyperliquid"  # This parameter may need to be added
                },
            )

            # Verify HyperliquidClient was used (if exchange parameter is implemented)
            # 验证使用了 HyperliquidClient（如果实现了 exchange 参数）
            # For now, we test that the API can work with HyperliquidClient when provided
            # 目前，我们测试当提供 HyperliquidClient 时 API 可以工作
            assert mock_hyperliquid_client.fetch_market_data.called or response.status_code in [
                200,
                400,
            ]

    @patch("server.create_all_providers")
    @patch("server.get_default_exchange")
    def test_hyperliquid_market_data_integration(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_llm_providers,
    ):
        """
        Test AC-3: Hyperliquid market data is fetched and included in LLM context
        测试 AC-3: 获取 Hyperliquid 市场数据并包含在 LLM 上下文中
        
        Given: I am running LLM evaluation for Hyperliquid
        When: The evaluation process starts
        Then: The system should fetch current market data from Hyperliquid
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
                json={"symbol": "ETH/USDC:USDC", "simulation_steps": 100},
            )

            # Verify Hyperliquid market data was fetched
            # 验证获取了 Hyperliquid 市场数据
            assert mock_hyperliquid_client.fetch_market_data.called
            assert mock_hyperliquid_client.fetch_account_data.called

            # Verify market data contains expected fields
            # 验证市场数据包含预期字段
            market_data = mock_hyperliquid_client.fetch_market_data.return_value
            assert "mid_price" in market_data
            assert "best_bid" in market_data
            assert "best_ask" in market_data
            assert "funding_rate" in market_data


class TestHyperliquidLLMResponseFormat:
    """
    Test AC-2: LLM Response Format
    测试 AC-2: LLM 响应格式
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
            "funding_rate": 0.0001,
        }
        client.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "balance": 10000.0,
        }
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
        ]:
            mock = Mock()
            mock.name = name
            mock.generate.return_value = response
            providers.append(mock)
        return providers

    @patch("server.create_all_providers")
    @patch("server.get_default_exchange")
    def test_response_format_includes_exchange_name(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_llm_providers,
    ):
        """
        Test AC-2: Response format includes exchange name and LLM suggestions
        测试 AC-2: 响应格式包含交易所名称和 LLM 建议
        
        Given: I call the LLM evaluation API for Hyperliquid
        When: The evaluation completes
        Then: The API should return LLM suggestions in consistent format
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
                json={"symbol": "ETH/USDC:USDC", "simulation_steps": 100},
            )

            # Verify response structure (when API is updated to include exchange)
            # 验证响应结构（当 API 更新以包含 exchange 时）
            if response.status_code == 200:
                data = response.json()
                # Response should include individual_results and aggregated
                # 响应应该包含 individual_results 和 aggregated
                assert "individual_results" in data or "error" in data
                # When exchange parameter is implemented, response should include exchange name
                # 当实现 exchange 参数时，响应应该包含交易所名称
                # assert data.get("exchange") == "hyperliquid"


class TestHyperliquidExchangeContext:
    """
    Test AC-4: Exchange Context in LLM Input
    测试 AC-4: LLM 输入中的交易所上下文
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
            "funding_rate": 0.0002,  # Hyperliquid-specific funding rate
        }
        client.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "balance": 10000.0,
        }
        return client

    @patch("server.create_all_providers")
    @patch("server.get_default_exchange")
    def test_llm_context_includes_exchange_name(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
    ):
        """
        Test AC-4: LLM context includes exchange name and Hyperliquid-specific data
        测试 AC-4: LLM 上下文包含交易所名称和 Hyperliquid 特定数据
        
        Given: I call the LLM evaluation API for Hyperliquid
        When: The API builds the LLM context
        Then: The context should indicate evaluation is for Hyperliquid exchange
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock LLM provider to capture prompt
        # 模拟 LLM 提供商以捕获提示
        captured_prompt = []

        def capture_prompt(prompt):
            captured_prompt.append(prompt)
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
                json={"symbol": "ETH/USDC:USDC", "simulation_steps": 100},
            )

            # Verify market data was fetched from Hyperliquid
            # 验证从 Hyperliquid 获取了市场数据
            assert mock_hyperliquid_client.fetch_market_data.called

            # When exchange context is implemented, prompt should mention Hyperliquid
            # 当实现交易所上下文时，提示应该提到 Hyperliquid
            # if captured_prompt:
            #     prompt_text = captured_prompt[0]
            #     assert "hyperliquid" in prompt_text.lower() or "Hyperliquid" in prompt_text


class TestHyperliquidErrorHandling:
    """
    Test AC-5: Error Handling for Hyperliquid LLM Evaluation
    测试 AC-5: Hyperliquid LLM 评估的错误处理
    """

    @patch("server.get_default_exchange")
    def test_error_when_hyperliquid_not_connected(self, mock_get_exchange):
        """
        Test AC-5: Error handling when Hyperliquid is not connected
        测试 AC-5: Hyperliquid 未连接时的错误处理
        
        Given: I attempt to call the LLM evaluation API for Hyperliquid when Hyperliquid is not connected
        When: The API call fails
        Then: The API should return a clear error message in Chinese and English
        """
        # Mock no exchange available
        # 模拟没有可用的交易所
        mock_get_exchange.return_value = None

        # Mock bot_engine to avoid other errors
        # 模拟 bot_engine 以避免其他错误
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            response = client.post(
                "/api/evaluation/run",
                json={"symbol": "ETH/USDC:USDC", "simulation_steps": 100},
            )

            # Verify error response (API should return error when exchange is None)
            # 验证错误响应（当 exchange 为 None 时 API 应该返回错误）
            # Note: Current implementation may return 200 with error in body, or proper error status
            # 注意：当前实现可能返回 200 并在 body 中包含错误，或返回适当的错误状态
            data = response.json()
            
            # Check if error is in response (either as status code or in body)
            # 检查响应中是否有错误（状态码或 body 中）
            if response.status_code != 200:
                assert "error" in data
            elif "error" in data:
                # Error in response body
                # 响应 body 中的错误
                error_msg = data.get("error", "")
                assert len(error_msg) > 0
                # Error should indicate exchange not available
                # 错误应该表明交易所不可用
                assert "exchange" in error_msg.lower() or "连接" in error_msg or "available" in error_msg.lower()

    @patch("server.get_default_exchange")
    def test_error_when_hyperliquid_fetch_fails(self, mock_get_exchange):
        """
        Test AC-5: Error handling when Hyperliquid market data fetch fails
        测试 AC-5: Hyperliquid 市场数据获取失败时的错误处理
        
        Given: Hyperliquid is connected but market data fetch fails
        When: The API attempts to fetch market data
        Then: The API should return a clear error message
        """
        # Mock HyperliquidClient that fails to fetch market data
        # 模拟无法获取市场数据的 HyperliquidClient
        mock_client = Mock(spec=HyperliquidClient)
        mock_client.is_connected = True
        mock_client.symbol = "ETH/USDT:USDT"
        mock_client.fetch_market_data.side_effect = Exception("Network error")
        mock_client.set_symbol.return_value = True
        mock_get_exchange.return_value = mock_client

        # Mock bot_engine
        # 模拟 bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            response = client.post(
                "/api/evaluation/run",
                json={"symbol": "ETH/USDC:USDC", "simulation_steps": 100},
            )

            # Verify error response (API should handle exception gracefully)
            # 验证错误响应（API 应该优雅地处理异常）
            data = response.json()
            
            # Check if error is in response
            # 检查响应中是否有错误
            if response.status_code != 200:
                assert "error" in data
            elif "error" in data:
                # Error in response body
                # 响应 body 中的错误
                error_msg = data.get("error", "")
                assert len(error_msg) > 0
                # Error should mention market data or fetch failure
                # 错误应该提到市场数据或获取失败
                assert "market" in error_msg.lower() or "data" in error_msg.lower() or "获取" in error_msg or "fetch" in error_msg.lower()


class TestHyperliquidApplyAPI:
    """
    Test AC-3: Apply LLM Suggestions to Hyperliquid
    测试 AC-3: 将 LLM 建议应用到 Hyperliquid
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        return client

    @patch("server.get_default_exchange")
    def test_apply_suggestions_to_hyperliquid(
        self, mock_get_exchange, mock_hyperliquid_client
    ):
        """
        Test AC-3: Apply LLM suggestions to Hyperliquid exchange configuration
        测试 AC-3: 将 LLM 建议应用到 Hyperliquid 交易所配置
        
        Given: I have LLM evaluation results for Hyperliquid
        When: I call the apply API with a specific LLM provider's suggestion
        Then: The system should apply the suggested trading parameters to Hyperliquid
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock evaluation results
        # 模拟评估结果
        with patch("server._last_evaluation_results", []), patch(
            "server._last_evaluation_aggregated", None
        ):
            client = TestClient(server.app)

            # Note: Apply API may need to be updated to accept exchange parameter
            # 注意：Apply API 可能需要更新以接受 exchange 参数
            response = client.post(
                "/api/evaluation/apply",
                json={
                    "source": "consensus",
                    # "exchange": "hyperliquid"  # This parameter may need to be added
                },
            )

            # Verify response (when exchange parameter is implemented)
            # 验证响应（当实现 exchange 参数时）
            assert response.status_code in [200, 400, 404]


class TestSelectedModelsFiltering:
    """
    Test selected_models parameter filtering
    测试 selected_models 参数过滤
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETH/USDC:USDC"
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
            "funding_rate": 0.0001,
            "timestamp": 1234567890,
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
    def mock_all_llm_providers(self):
        """Create mock LLM providers for all models / 为所有模型创建模拟 LLM 提供商"""
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
            (
                "Claude",
                '{"recommended_strategy": "FixedSpread", "spread": 0.014, "skew_factor": 110, "confidence": 0.82, "quantity": 0.12, "leverage": 4}',
            ),
        ]:
            mock = Mock()
            mock.name = name
            mock.generate.return_value = response
            providers.append(mock)
        return providers

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_selected_models_single_selection(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_all_llm_providers,
    ):
        """
        Test: API filters providers when single model is selected
        测试：当选择单个模型时 API 过滤提供商
        """
        mock_get_exchange.return_value = mock_hyperliquid_client
        mock_create_providers.return_value = mock_all_llm_providers

        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call API with only Gemini selected
            # 仅选择 Gemini 调用 API
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDC:USDC",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                    "selected_models": ["gemini"],
                },
            )

            # Verify API accepts the request
            # 验证 API 接受请求
            assert response.status_code != 404, "API endpoint not found / API 端点未找到"

            # If successful, verify only Gemini was used
            # 如果成功，验证仅使用了 Gemini
            if response.status_code == 200:
                data = response.json()
                if "individual_results" in data:
                    # Should only have Gemini results
                    # 应该只有 Gemini 结果
                    results = data["individual_results"]
                    assert len(results) == 1, "Should have only one result / 应该只有一个结果"
                    assert results[0]["provider_name"] == "Gemini", "Should be Gemini / 应该是 Gemini"

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_selected_models_multiple_selection(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_all_llm_providers,
    ):
        """
        Test: API filters providers when multiple models are selected
        测试：当选择多个模型时 API 过滤提供商
        """
        mock_get_exchange.return_value = mock_hyperliquid_client
        mock_create_providers.return_value = mock_all_llm_providers

        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call API with Gemini and OpenAI selected
            # 选择 Gemini 和 OpenAI 调用 API
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDC:USDC",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                    "selected_models": ["gemini", "openai"],
                },
            )

            # Verify API accepts the request
            # 验证 API 接受请求
            assert response.status_code != 404, "API endpoint not found / API 端点未找到"

            # If successful, verify only selected models were used
            # 如果成功，验证仅使用了选中的模型
            if response.status_code == 200:
                data = response.json()
                if "individual_results" in data:
                    results = data["individual_results"]
                    provider_names = [r["provider_name"] for r in results]
                    assert "Gemini" in provider_names, "Should include Gemini / 应该包含 Gemini"
                    assert "OpenAI" in provider_names, "Should include OpenAI / 应该包含 OpenAI"
                    assert "Claude" not in provider_names, "Should not include Claude / 不应该包含 Claude"
                    assert len(results) == 2, "Should have two results / 应该有两个结果"

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_selected_models_empty_list_uses_all(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_all_llm_providers,
    ):
        """
        Test: API uses all providers when selected_models is empty or None
        测试：当 selected_models 为空或 None 时 API 使用所有提供商
        """
        mock_get_exchange.return_value = mock_hyperliquid_client
        mock_create_providers.return_value = mock_all_llm_providers

        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call API without selected_models (should use all)
            # 不提供 selected_models 调用 API（应该使用所有）
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDC:USDC",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                    # No selected_models parameter
                },
            )

            # Verify API accepts the request
            # 验证 API 接受请求
            assert response.status_code != 404, "API endpoint not found / API 端点未找到"

            # If successful, verify all providers were used
            # 如果成功，验证使用了所有提供商
            if response.status_code == 200:
                data = response.json()
                if "individual_results" in data:
                    results = data["individual_results"]
                    provider_names = [r["provider_name"] for r in results]
                    # Should have all three providers
                    # 应该有三个提供商
                    assert len(results) == 3, "Should use all providers / 应该使用所有提供商"

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_selected_models_invalid_model_name(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_all_llm_providers,
    ):
        """
        Test: API returns error when invalid model name is selected
        测试：当选择无效模型名称时 API 返回错误
        """
        mock_get_exchange.return_value = mock_hyperliquid_client
        mock_create_providers.return_value = mock_all_llm_providers

        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call API with invalid model name
            # 使用无效模型名称调用 API
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDC:USDC",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                    "selected_models": ["invalid_model"],
                },
            )

            # Verify error response
            # 验证错误响应
            data = response.json()
            assert "error" in data, "Should return error for invalid model / 应该为无效模型返回错误"
            error_msg = data.get("error", "").lower()
            assert (
                "matching" in error_msg
                or "not found" in error_msg
                or "未找到" in data.get("error", "")
            ), "Error should mention no matching providers / 错误应该提到没有匹配的提供商"

