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
    AggregatedResult,
    EvaluationResult,
    MarketContext,
    ParameterStatistics,
    SimulationResult,
    StrategyConsensus,
    StrategyProposal,
)
from alphaloop.market.performance import PerformanceTracker
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

    def _parse_response(
        self, raw_response: str, provider_name: str
    ) -> StrategyProposal:
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

        Note: Only FixedSpread strategy is supported in simulation.
        注意：模拟中仅支持 FixedSpread 策略。

        Args:
            proposal: 策略建议
            context: 市场上下文

        Returns:
            模拟结果
        """
        # Only use FixedSpread strategy for simulation
        # 模拟中仅使用 FixedSpread 策略
        strategy = FixedSpreadStrategy()

        # 应用建议的参数
        strategy.spread = proposal.spread
        strategy.quantity = proposal.quantity
        strategy.leverage = proposal.leverage
        # Note: skew_factor is not used for FixedSpread strategy
        # 注意：FixedSpread 策略不使用 skew_factor

        # 运行模拟
        simulator = StrategySimulator(
            strategy=strategy,
            initial_price=context.mid_price,
            volatility=context.volatility_1h,
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

    def _calculate_sharpe(
        self, pnl_history: list, risk_free_rate: float = 0.0
    ) -> float:
        """计算夏普比率"""
        if len(pnl_history) < 2:
            return 0.0

        # 提取 PnL 值
        pnls = [p[1] if isinstance(p, list) else p for p in pnl_history]

        # 计算收益率
        returns = []
        for i in range(1, len(pnls)):
            if pnls[i - 1] != 0:
                ret = (
                    (pnls[i] - pnls[i - 1]) / abs(pnls[i - 1])
                    if pnls[i - 1] != 0
                    else 0
                )
                returns.append(ret)

        if not returns:
            return 0.0

        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - risk_free_rate) / std_return
        return round(float(sharpe), 2)

    def _score_and_rank(
        self, results: List[EvaluationResult]
    ) -> List[EvaluationResult]:
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
            pnl_score = (
                min(max(result.simulation.realized_pnl / 100.0, -1), 1) * 50 + 50
            )
            sharpe_score = (
                min(max(result.simulation.sharpe_ratio / 3.0, -1), 1) * 50 + 50
            )
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

    @staticmethod
    def get_strategy_consensus(results: List[EvaluationResult]) -> StrategyConsensus:
        """
        分析策略共识

        Analyze strategy consensus across all models.
        统计所有模型的策略投票，确定共识策略。

        Args:
            results: 评估结果列表

        Returns:
            StrategyConsensus 对象
        """
        # Filter successful results / 过滤成功的结果
        valid_results = [r for r in results if r.proposal.parse_success]
        total_models = len(valid_results)

        if total_models == 0:
            return StrategyConsensus(
                consensus_strategy="",
                consensus_count=0,
                total_models=0,
                consensus_level="none",
                consensus_ratio=0.0,
            )

        # Count votes for each strategy / 统计每个策略的投票
        strategy_votes: dict = {}
        providers_by_strategy: dict = {}

        for result in valid_results:
            strategy = result.proposal.recommended_strategy
            strategy_votes[strategy] = strategy_votes.get(strategy, 0) + 1

            if strategy not in providers_by_strategy:
                providers_by_strategy[strategy] = []
            providers_by_strategy[strategy].append(result.provider_name)

        # Calculate percentages / 计算百分比
        strategy_percentages = {
            s: count / total_models for s, count in strategy_votes.items()
        }

        # Find consensus strategy (most voted) / 找到共识策略（票数最多）
        consensus_strategy = max(strategy_votes, key=strategy_votes.get)
        consensus_count = strategy_votes[consensus_strategy]
        consensus_ratio = consensus_count / total_models

        # Determine consensus level / 确定共识程度
        if consensus_ratio == 1.0:
            consensus_level = "full"
        elif consensus_ratio > 0.5:
            consensus_level = "majority"
        elif consensus_ratio > 0.0:
            consensus_level = "split"
        else:
            consensus_level = "none"

        return StrategyConsensus(
            consensus_strategy=consensus_strategy,
            consensus_count=consensus_count,
            total_models=total_models,
            strategy_votes=strategy_votes,
            strategy_percentages=strategy_percentages,
            consensus_level=consensus_level,
            consensus_ratio=consensus_ratio,
            providers_by_strategy=providers_by_strategy,
        )

    @staticmethod
    def get_parameter_statistics(
        results: List[EvaluationResult],
    ) -> ParameterStatistics:
        """
        计算参数统计

        Calculate parameter statistics across all models.
        计算所有模型参数的统计数据（均值、中位数、范围等）。

        Args:
            results: 评估结果列表

        Returns:
            ParameterStatistics 对象
        """
        # Filter successful results / 过滤成功的结果
        valid_results = [r for r in results if r.proposal.parse_success]

        if not valid_results:
            return ParameterStatistics()

        # Extract parameters / 提取参数
        spreads = [r.proposal.spread for r in valid_results]
        skews = [r.proposal.skew_factor for r in valid_results]
        quantities = [r.proposal.quantity for r in valid_results]
        leverages = [r.proposal.leverage for r in valid_results]
        confidences = [r.proposal.confidence for r in valid_results]

        # Calculate statistics / 计算统计数据
        return ParameterStatistics(
            # Spread
            spread_mean=float(np.mean(spreads)),
            spread_median=float(np.median(spreads)),
            spread_min=float(np.min(spreads)),
            spread_max=float(np.max(spreads)),
            spread_std=float(np.std(spreads)) if len(spreads) > 1 else 0.0,
            # Skew
            skew_mean=float(np.mean(skews)),
            skew_median=float(np.median(skews)),
            # Quantity
            quantity_mean=float(np.mean(quantities)),
            quantity_median=float(np.median(quantities)),
            # Leverage
            leverage_mean=float(np.mean(leverages)),
            leverage_median=float(np.median(leverages)),
            # Confidence
            confidence_mean=float(np.mean(confidences)),
            confidence_min=float(np.min(confidences)),
            confidence_max=float(np.max(confidences)),
        )

    @staticmethod
    def calculate_consensus_confidence(
        results: List[EvaluationResult],
        strategy_consensus: StrategyConsensus,
    ) -> tuple:
        """
        计算共识置信度

        Calculate consensus confidence based on model agreement and individual confidences.
        基于模型共识程度和个体置信度计算综合共识置信度。

        Formula / 公式:
        consensus_confidence = agreement_factor * weighted_confidence

        - agreement_factor: Based on how many models agree (1.0 if all, 0.8 if majority, 0.5 if split)
        - weighted_confidence: Average of confidences from agreeing models, weighted by simulation score

        Args:
            results: 评估结果列表
            strategy_consensus: 策略共识分析结果

        Returns:
            (consensus_confidence, confidence_breakdown) 元组
        """
        valid_results = [r for r in results if r.proposal.parse_success]

        if not valid_results or not strategy_consensus.consensus_strategy:
            return 0.0, {}

        # Calculate agreement factor / 计算共识因子
        if strategy_consensus.consensus_level == "full":
            agreement_factor = 1.0
        elif strategy_consensus.consensus_level == "majority":
            agreement_factor = 0.8
        elif strategy_consensus.consensus_level == "split":
            agreement_factor = 0.5
        else:
            agreement_factor = 0.0

        # Get agreeing models / 获取同意的模型
        agreeing_providers = strategy_consensus.providers_by_strategy.get(
            strategy_consensus.consensus_strategy, []
        )
        agreeing_results = [
            r for r in valid_results if r.provider_name in agreeing_providers
        ]

        if not agreeing_results:
            return 0.0, {"agreement_factor": agreement_factor}

        # Calculate weighted confidence / 计算加权置信度
        # Weight by simulation score
        total_weight = sum(max(r.score, 1) for r in agreeing_results)
        if total_weight == 0:
            weighted_confidence = np.mean(
                [r.proposal.confidence for r in agreeing_results]
            )
        else:
            weighted_confidence = (
                sum(r.proposal.confidence * max(r.score, 1) for r in agreeing_results)
                / total_weight
            )

        # Calculate consensus confidence / 计算共识置信度
        consensus_confidence = float(agreement_factor * weighted_confidence)

        # Build breakdown / 构建分解
        breakdown = {
            "agreement_factor": agreement_factor,
            "weighted_confidence": float(weighted_confidence),
            "agreeing_models": len(agreeing_results),
            "total_models": len(valid_results),
            "individual_confidences": {
                r.provider_name: r.proposal.confidence for r in valid_results
            },
        }

        return consensus_confidence, breakdown

    def aggregate_results(self, results: List[EvaluationResult]) -> AggregatedResult:
        """
        聚合所有评估结果

        Aggregate all evaluation results into a comprehensive summary.
        将所有评估结果聚合为综合摘要，包括共识分析、参数统计和共识建议。

        Args:
            results: 评估结果列表

        Returns:
            AggregatedResult 对象
        """
        if not results:
            return AggregatedResult()

        # Get consensus analysis / 获取共识分析
        strategy_consensus = self.get_strategy_consensus(results)
        parameter_stats = self.get_parameter_statistics(results)

        # Calculate consensus confidence / 计算共识置信度
        consensus_confidence, confidence_breakdown = (
            self.calculate_consensus_confidence(results, strategy_consensus)
        )

        # Count successful/failed evaluations / 统计成功/失败数量
        successful = [r for r in results if r.proposal.parse_success]
        failed = [r for r in results if not r.proposal.parse_success]

        # Calculate performance averages / 计算性能平均值
        if successful:
            avg_pnl = float(np.mean([r.simulation.realized_pnl for r in successful]))
            avg_sharpe = float(np.mean([r.simulation.sharpe_ratio for r in successful]))
            avg_win_rate = float(np.mean([r.simulation.win_rate for r in successful]))
            avg_latency = float(np.mean([r.latency_ms for r in successful]))
        else:
            avg_pnl = avg_sharpe = avg_win_rate = avg_latency = 0.0

        # Generate consensus proposal / 生成共识建议
        consensus_proposal = self._generate_consensus_proposal(
            results, strategy_consensus, parameter_stats, consensus_confidence
        )

        return AggregatedResult(
            strategy_consensus=strategy_consensus,
            parameter_stats=parameter_stats,
            consensus_confidence=consensus_confidence,
            confidence_breakdown=confidence_breakdown,
            consensus_proposal=consensus_proposal,
            individual_results=results,
            successful_evaluations=len(successful),
            failed_evaluations=len(failed),
            avg_pnl=avg_pnl,
            avg_sharpe=avg_sharpe,
            avg_win_rate=avg_win_rate,
            avg_latency_ms=avg_latency,
        )

    def _generate_consensus_proposal(
        self,
        results: List[EvaluationResult],
        strategy_consensus: StrategyConsensus,
        parameter_stats: ParameterStatistics,
        consensus_confidence: float,
    ) -> StrategyProposal:
        """
        生成共识策略建议

        Generate a consensus-based strategy proposal using complete parameter set
        from the best-performing model among agreeing models.
        使用同意模型中最佳模型的完整参数集生成基于共识的策略建议。

        This ensures parameter coherence - parameters work together as an atomic unit.
        这确保了参数一致性 - 参数作为一个原子单位协同工作。

        Args:
            results: 评估结果列表
            strategy_consensus: 策略共识
            parameter_stats: 参数统计（用于回退情况）
            consensus_confidence: 共识置信度

        Returns:
            StrategyProposal 共识建议
        """
        if not strategy_consensus.consensus_strategy:
            return StrategyProposal(
                recommended_strategy="FixedSpread",
                spread=0.01,
                provider_name="Consensus",
                parse_success=False,
                parse_error="No valid results to generate consensus",
            )

        # Get agreeing results for reasoning / 获取同意的结果用于生成理由
        agreeing_providers = strategy_consensus.providers_by_strategy.get(
            strategy_consensus.consensus_strategy, []
        )
        valid_results = [r for r in results if r.proposal.parse_success]
        agreeing_results = [
            r for r in valid_results if r.provider_name in agreeing_providers
        ]

        # Combine reasoning from agreeing models / 合并同意模型的理由
        combined_reasoning = (
            f"Consensus from {len(agreeing_results)}/{len(valid_results)} models. "
        )
        if agreeing_results:
            reasons = [
                r.proposal.reasoning for r in agreeing_results if r.proposal.reasoning
            ]
            if reasons:
                combined_reasoning += " | ".join(reasons[:3])  # Limit to first 3

        # Determine risk level by majority / 多数决定风险等级
        risk_levels = [r.proposal.risk_level for r in agreeing_results]
        if risk_levels:
            risk_counts = {}
            for rl in risk_levels:
                risk_counts[rl] = risk_counts.get(rl, 0) + 1
            consensus_risk = max(risk_counts, key=risk_counts.get)
        else:
            consensus_risk = "medium"

        # Calculate expected return (average of agreeing models) / 计算预期收益
        expected_returns = [r.proposal.expected_return for r in agreeing_results]
        avg_expected_return = (
            float(np.mean(expected_returns)) if expected_returns else 0.0
        )

        # FIXED: Use complete parameter set from best-performing model instead of independent medians
        # 修复：使用最佳模型的完整参数集，而不是独立的中位数
        # This ensures parameter coherence - parameters work together as an atomic unit
        # 这确保了参数一致性 - 参数作为一个原子单位协同工作
        if agreeing_results:
            # Sort by score (highest first) and take the best model's complete parameter set
            # 按得分排序（最高优先），使用最佳模型的完整参数集
            sorted_agreeing = sorted(agreeing_results, key=lambda r: r.score, reverse=True)
            best_result = sorted_agreeing[0]
            best_proposal = best_result.proposal
            
            logger.info(
                f"Consensus using complete parameter set from best model: {best_result.provider_name} "
                f"(score: {best_result.score:.2f})"
            )
            
            return StrategyProposal(
                recommended_strategy=strategy_consensus.consensus_strategy,
                spread=best_proposal.spread,
                skew_factor=best_proposal.skew_factor,
                quantity=best_proposal.quantity,
                leverage=best_proposal.leverage,
                reasoning=combined_reasoning,
                confidence=consensus_confidence,
                risk_level=consensus_risk,
                expected_return=avg_expected_return,
                provider_name="Consensus",
                raw_response="",
                parse_success=True,
            )
        else:
            # Fallback to median if no agreeing results (should not happen)
            # 如果没有同意的结果，回退到中位数（不应该发生）
            logger.warning("No agreeing results found, using median parameters as fallback")
            return StrategyProposal(
                recommended_strategy=strategy_consensus.consensus_strategy,
                spread=parameter_stats.spread_median,
                skew_factor=parameter_stats.skew_median,
                quantity=parameter_stats.quantity_median,
                leverage=parameter_stats.leverage_median,
                reasoning=combined_reasoning,
                confidence=consensus_confidence,
                risk_level=consensus_risk,
                expected_return=avg_expected_return,
                provider_name="Consensus",
                raw_response="",
                parse_success=True,
            )

    @staticmethod
    def generate_consensus_summary(aggregated: AggregatedResult) -> str:
        """
        生成共识摘要报告

        Generate a formatted summary of the aggregated results.
        生成聚合结果的格式化摘要报告。

        Args:
            aggregated: 聚合结果

        Returns:
            格式化的摘要字符串
        """
        lines = []
        separator = "=" * 80

        lines.append(separator)
        lines.append("MULTI-LLM CONSENSUS REPORT / 多 LLM 共识报告")
        lines.append(separator)
        lines.append("")

        # Consensus Summary / 共识摘要
        sc = aggregated.strategy_consensus
        lines.append("【Strategy Consensus / 策略共识】")
        lines.append(f"  Consensus Strategy / 共识策略: {sc.consensus_strategy}")
        lines.append(f"  Consensus Level / 共识程度: {sc.consensus_level.upper()}")
        lines.append(f"  Agreement Ratio / 共识比例: {sc.consensus_ratio:.1%}")
        lines.append(
            f"  Models Agreeing / 同意模型数: {sc.consensus_count}/{sc.total_models}"
        )
        lines.append("")

        # Vote Distribution / 投票分布
        lines.append("【Vote Distribution / 投票分布】")
        for strategy, votes in sc.strategy_votes.items():
            pct = sc.strategy_percentages.get(strategy, 0)
            providers = sc.providers_by_strategy.get(strategy, [])
            lines.append(
                f"  {strategy}: {votes} votes ({pct:.0%}) - {', '.join(providers)}"
            )
        lines.append("")

        # Consensus Confidence / 共识置信度
        lines.append("【Consensus Confidence / 共识置信度】")
        lines.append(
            f"  Overall Confidence / 综合置信度: {aggregated.consensus_confidence:.1%}"
        )
        lines.append(
            f"  Recommendation Strength / 推荐强度: {aggregated.get_recommendation_strength().upper()}"
        )
        lines.append("")

        # Parameter Statistics / 参数统计
        ps = aggregated.parameter_stats
        lines.append("【Parameter Statistics / 参数统计】")
        lines.append(f"  Spread / 价差:")
        lines.append(f"    Mean: {ps.spread_mean:.4f}, Median: {ps.spread_median:.4f}")
        lines.append(f"    Range: [{ps.spread_min:.4f}, {ps.spread_max:.4f}]")
        lines.append(
            f"  Skew Factor / 倾斜因子: Mean {ps.skew_mean:.1f}, Median {ps.skew_median:.1f}"
        )
        lines.append(
            f"  Confidence / 置信度: {ps.confidence_mean:.1%} (min: {ps.confidence_min:.1%}, max: {ps.confidence_max:.1%})"
        )
        lines.append("")

        # Performance Summary / 性能摘要
        lines.append("【Performance Summary / 性能摘要】")
        lines.append(f"  Avg PnL / 平均盈亏: ${aggregated.avg_pnl:,.2f}")
        lines.append(f"  Avg Sharpe / 平均夏普: {aggregated.avg_sharpe:.2f}")
        lines.append(f"  Avg Win Rate / 平均胜率: {aggregated.avg_win_rate:.1%}")
        lines.append(f"  Avg Latency / 平均延迟: {aggregated.avg_latency_ms:.0f}ms")
        lines.append("")

        # Consensus Proposal / 共识建议
        if aggregated.consensus_proposal:
            cp = aggregated.consensus_proposal
            lines.append("【Consensus Proposal / 共识建议】")
            lines.append(f"  Strategy / 策略: {cp.recommended_strategy}")
            lines.append(f"  Spread / 价差: {cp.spread:.4f}")
            lines.append(f"  Skew Factor / 倾斜因子: {cp.skew_factor:.1f}")
            lines.append(f"  Quantity / 数量: {cp.quantity:.3f}")
            lines.append(f"  Leverage / 杠杆: {cp.leverage:.1f}x")
            lines.append(f"  Risk Level / 风险等级: {cp.risk_level}")
            lines.append(f"  Expected Return / 预期收益: {cp.expected_return:.2%}")
            lines.append("")
            if cp.reasoning:
                lines.append(f"  Reasoning / 理由: {cp.reasoning[:200]}...")

        lines.append("")
        lines.append(separator)

        return "\n".join(lines)


class StrategySimulator:
    """
    策略模拟器 - 用于测试策略参数

    基于 MarketSimulator，但允许自定义参数
    
    Note: Only supports FixedSpread strategy in simulation.
    注意：模拟中仅支持 FixedSpread 策略。
    """

    def __init__(
        self,
        strategy,
        initial_price: float = 2000.0,
        volatility: float = 0.02,
    ):
        self.strategy = strategy
        self.current_price = initial_price
        self.volatility = volatility
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
            # Get target orders (FixedSpread strategy only)
            # 获取目标订单（仅支持 FixedSpread 策略）
            if hasattr(self.strategy, "calculate_target_orders"):
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
