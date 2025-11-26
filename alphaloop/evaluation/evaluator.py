"""
Multi-LLM Strategy Evaluator
多 LLM 策略评估器

同时使用多个 LLM 评估相同的市场数据，比较策略建议和模拟结果
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import numpy as np

from alphaloop.core.llm import LLMProvider
from alphaloop.core.logger import setup_logger
from alphaloop.evaluation.prompts import StrategyAdvisorPrompt
from alphaloop.evaluation.schemas import (
    EvaluationResult,
    MarketContext,
    SimulationResult,
    StrategyProposal,
)
from alphaloop.market.performance import PerformanceTracker
from alphaloop.strategies.funding import FundingRateStrategy
from alphaloop.strategies.strategy import FixedSpreadStrategy

logger = setup_logger("MultiLLMEvaluator")


class MultiLLMEvaluator:
    """
    多 LLM 策略评估器

    功能：
    1. 同时调用多个 LLM Provider
    2. 解析每个 LLM 的策略建议
    3. 为每个建议运行模拟交易
    4. 比较结果并排名

    用法：
        evaluator = MultiLLMEvaluator(providers=[gemini, openai, claude])
        results = evaluator.evaluate(market_context)
        best = MultiLLMEvaluator.get_best_proposal(results)
    """

    def __init__(
        self,
        providers: List[LLMProvider],
        simulation_steps: int = 500,
        parallel: bool = True,
    ):
        """
        初始化评估器

        Args:
            providers: LLM Provider 列表
            simulation_steps: 模拟交易步数
            parallel: 是否并行调用 LLM
        """
        self.providers = providers
        self.simulation_steps = simulation_steps
        self.parallel = parallel

    def evaluate(self, context: MarketContext) -> List[EvaluationResult]:
        """
        使用所有 Provider 评估市场数据

        Args:
            context: 市场上下文数据

        Returns:
            评估结果列表（按得分排名）
        """
        # 生成 Prompt
        prompt = StrategyAdvisorPrompt.generate(context)

        # 调用所有 LLM
        if self.parallel and len(self.providers) > 1:
            results = self._evaluate_parallel(prompt, context)
        else:
            results = self._evaluate_sequential(prompt, context)

        # 计算得分并排名
        results = self._score_and_rank(results)

        return results

    def _evaluate_parallel(
        self, prompt: str, context: MarketContext
    ) -> List[EvaluationResult]:
        """并行调用所有 LLM"""
        results = []

        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            futures = {
                executor.submit(
                    self._evaluate_single, provider, prompt, context
                ): provider
                for provider in self.providers
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    provider = futures[future]
                    logger.error(f"Parallel evaluation failed for {provider.name}: {e}")
                    results.append(self._create_error_result(provider.name, str(e)))

        return results

    def _evaluate_sequential(
        self, prompt: str, context: MarketContext
    ) -> List[EvaluationResult]:
        """顺序调用所有 LLM"""
        results = []

        for provider in self.providers:
            try:
                result = self._evaluate_single(provider, prompt, context)
                results.append(result)
            except Exception as e:
                logger.error(f"Sequential evaluation failed for {provider.name}: {e}")
                results.append(self._create_error_result(provider.name, str(e)))

        return results

    def _evaluate_single(
        self, provider: LLMProvider, prompt: str, context: MarketContext
    ) -> EvaluationResult:
        """
        使用单个 Provider 进行评估

        Args:
            provider: LLM Provider
            prompt: Prompt 字符串
            context: 市场上下文

        Returns:
            单个评估结果
        """
        provider_name = provider.name

        # 1. 调用 LLM 并测量延迟
        start_time = time.time()
        try:
            raw_response = provider.generate(prompt)
            latency_ms = (time.time() - start_time) * 1000
        except Exception as e:
            logger.error(f"LLM call failed for {provider_name}: {e}")
            return self._create_error_result(provider_name, str(e))

        # 2. 解析响应
        proposal = self._parse_response(raw_response, provider_name)

        # 3. 运行模拟
        simulation = self._run_simulation(proposal, context)

        # 4. 创建结果
        result = EvaluationResult(
            provider_name=provider_name,
            proposal=proposal,
            simulation=simulation,
            latency_ms=latency_ms,
        )

        logger.info(
            f"Evaluated {provider_name}",
            extra={
                "extra_data": {
                    "strategy": proposal.recommended_strategy,
                    "spread": proposal.spread,
                    "pnl": simulation.realized_pnl,
                }
            },
        )

        return result

    def _parse_response(self, raw_response: str, provider_name: str) -> StrategyProposal:
        """
        解析 LLM 响应为 StrategyProposal

        Args:
            raw_response: LLM 原始响应
            provider_name: Provider 名称

        Returns:
            解析后的策略建议
        """
        try:
            # 清理响应（移除 markdown 代码块）
            clean_response = raw_response.strip()
            
            # 检查是否包含 markdown 代码块
            if "```" in clean_response:
                # 移除 markdown 代码块
                lines = clean_response.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("```") and not in_json:
                        in_json = True
                        continue
                    if stripped.startswith("```") and in_json:
                        break
                    if in_json:
                        json_lines.append(line)
                clean_response = "\n".join(json_lines).strip()

            # 解析 JSON
            data = json.loads(clean_response)

            return StrategyProposal(
                recommended_strategy=data.get("recommended_strategy", "FixedSpread"),
                spread=float(data.get("spread", 0.01)),
                skew_factor=float(data.get("skew_factor", 100.0)),
                quantity=float(data.get("quantity", 0.1)),
                leverage=float(data.get("leverage", 1.0)),
                reasoning=data.get("reasoning", ""),
                confidence=float(data.get("confidence", 0.5)),
                risk_level=data.get("risk_level", "medium"),
                expected_return=float(data.get("expected_return", 0.0)),
                provider_name=provider_name,
                raw_response=raw_response,
                parse_success=True,
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse response from {provider_name}: {e}")
            return StrategyProposal(
                recommended_strategy="FixedSpread",
                spread=0.01,
                provider_name=provider_name,
                raw_response=raw_response,
                parse_success=False,
                parse_error=str(e),
            )

    def _run_simulation(
        self, proposal: StrategyProposal, context: MarketContext
    ) -> SimulationResult:
        """
        运行模拟交易

        Args:
            proposal: 策略建议
            context: 市场上下文

        Returns:
            模拟结果
        """
        # 根据建议创建策略
        if proposal.recommended_strategy == "FundingRate":
            strategy = FundingRateStrategy()
        else:
            strategy = FixedSpreadStrategy()

        # 应用建议的参数
        strategy.spread = proposal.spread
        strategy.quantity = proposal.quantity
        strategy.leverage = proposal.leverage
        if hasattr(strategy, "skew_factor"):
            strategy.skew_factor = proposal.skew_factor

        # 运行模拟
        simulator = StrategySimulator(
            strategy=strategy,
            initial_price=context.mid_price,
            volatility=context.volatility_1h,
            funding_rate=context.funding_rate,
        )

        stats = simulator.run(steps=self.simulation_steps)

        return SimulationResult(
            realized_pnl=stats.get("realized_pnl", 0.0),
            total_trades=stats.get("total_trades", 0),
            winning_trades=stats.get("winning_trades", 0),
            win_rate=stats.get("win_rate", 0.0) / 100.0,  # 转换为小数
            sharpe_ratio=self._calculate_sharpe(stats.get("pnl_history", [])),
            simulation_steps=self.simulation_steps,
            pnl_history=stats.get("pnl_history", []),
        )

    def _calculate_sharpe(self, pnl_history: list, risk_free_rate: float = 0.0) -> float:
        """计算夏普比率"""
        if len(pnl_history) < 2:
            return 0.0

        # 提取 PnL 值
        pnls = [p[1] if isinstance(p, list) else p for p in pnl_history]

        # 计算收益率
        returns = []
        for i in range(1, len(pnls)):
            if pnls[i - 1] != 0:
                ret = (pnls[i] - pnls[i - 1]) / abs(pnls[i - 1]) if pnls[i - 1] != 0 else 0
                returns.append(ret)

        if not returns:
            return 0.0

        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - risk_free_rate) / std_return
        return round(float(sharpe), 2)

    def _score_and_rank(self, results: List[EvaluationResult]) -> List[EvaluationResult]:
        """
        计算得分并排名

        评分公式：
        - PnL 权重: 40%
        - 夏普比率权重: 30%
        - 胜率权重: 20%
        - 置信度权重: 10%
        """
        for result in results:
            if not result.proposal.parse_success:
                result.score = 0.0
                continue

            # 归一化各指标
            pnl_score = min(max(result.simulation.realized_pnl / 100.0, -1), 1) * 50 + 50
            sharpe_score = min(max(result.simulation.sharpe_ratio / 3.0, -1), 1) * 50 + 50
            win_rate_score = result.simulation.win_rate * 100
            confidence_score = result.proposal.confidence * 100

            # 加权平均
            result.score = (
                pnl_score * 0.40
                + sharpe_score * 0.30
                + win_rate_score * 0.20
                + confidence_score * 0.10
            )

        # 按得分排名
        sorted_results = sorted(results, key=lambda r: r.score, reverse=True)
        for i, result in enumerate(sorted_results):
            result.rank = i + 1

        return sorted_results

    def _create_error_result(self, provider_name: str, error: str) -> EvaluationResult:
        """创建错误结果"""
        return EvaluationResult(
            provider_name=provider_name,
            proposal=StrategyProposal(
                recommended_strategy="FixedSpread",
                spread=0.01,
                provider_name=provider_name,
                parse_success=False,
                parse_error=error,
            ),
            simulation=SimulationResult(),
            score=0.0,
        )

    @staticmethod
    def generate_comparison_table(results: List[EvaluationResult]) -> str:
        """
        生成结果对比表格

        Args:
            results: 评估结果列表

        Returns:
            格式化的表格字符串
        """
        # 分隔线
        separator = "-" * 130

        # 构建表格
        lines = [separator]
        lines.append(
            f"{'Rank':^6} | {'Provider':^30} | {'Strategy':^12} | {'Spread':^8} | "
            f"{'Skew':^6} | {'Conf':^6} | {'PnL':^12} | {'WinRate':^8} | "
            f"{'Sharpe':^7} | {'Score':^6} | {'Latency':^10}"
        )
        lines.append(separator)

        for r in results:
            pnl_str = f"${r.simulation.realized_pnl:,.2f}"
            lines.append(
                f"{r.rank:^6} | {r.provider_name:^30} | {r.proposal.recommended_strategy:^12} | "
                f"{r.proposal.spread:^8.4f} | {r.proposal.skew_factor:^6.0f} | "
                f"{r.proposal.confidence:^6.1%} | {pnl_str:^12} | "
                f"{r.simulation.win_rate:^8.1%} | {r.simulation.sharpe_ratio:^7.2f} | "
                f"{r.score:^6.1f} | {r.latency_ms:^8.0f}ms"
            )

        lines.append(separator)

        return "\n".join(lines)

    @staticmethod
    def get_best_proposal(results: List[EvaluationResult]) -> EvaluationResult:
        """
        获取最佳建议

        Args:
            results: 评估结果列表

        Returns:
            排名第一的结果
        """
        return min(results, key=lambda r: r.rank)


class StrategySimulator:
    """
    策略模拟器 - 用于测试策略参数

    基于 MarketSimulator，但允许自定义参数
    """

    def __init__(
        self,
        strategy,
        initial_price: float = 2000.0,
        volatility: float = 0.02,
        funding_rate: float = 0.0001,
    ):
        self.strategy = strategy
        self.current_price = initial_price
        self.volatility = volatility
        self.funding_rate = funding_rate
        self.performance = PerformanceTracker()
        self.position = 0.0

    def generate_market_data(self):
        """生成模拟市场数据"""
        import random

        # 基于波动率的随机游走
        change = random.gauss(0, self.current_price * self.volatility)
        self.current_price += change

        # 确保价格为正
        self.current_price = max(self.current_price, 1.0)

        spread = self.current_price * 0.0002  # 2bps 市场价差
        best_bid = self.current_price - spread / 2
        best_ask = self.current_price + spread / 2

        return {
            "mid_price": self.current_price,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "tick_size": 0.01,
            "step_size": 0.001,
        }

    def run(self, steps: int = 500) -> dict:
        """运行模拟"""
        for _ in range(steps):
            market_data = self.generate_market_data()

            # 获取目标订单
            if hasattr(self.strategy, "calculate_target_orders"):
                # 检查是否需要 funding_rate 参数
                import inspect
                sig = inspect.signature(self.strategy.calculate_target_orders)
                if "funding_rate" in sig.parameters:
                    orders = self.strategy.calculate_target_orders(
                        market_data, funding_rate=self.funding_rate
                    )
                else:
                    orders = self.strategy.calculate_target_orders(market_data)
            else:
                orders = []

            # 简单成交逻辑
            for order in orders:
                if order["side"] == "buy":
                    if order["price"] >= market_data["best_bid"]:
                        self.position += order["quantity"]
                        self.performance.update_position(
                            self.position, market_data["mid_price"]
                        )
                elif order["side"] == "sell":
                    if order["price"] <= market_data["best_ask"]:
                        self.position -= order["quantity"]
                        self.performance.update_position(
                            self.position, market_data["mid_price"]
                        )

        return self.performance.get_stats()
