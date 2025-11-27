"""
Portfolio Manager / 组合管理器

基于用户故事 US-1.x 和 US-2.x 实现组合管理功能：
- 计算组合总盈亏
- 计算组合夏普比率
- 统计活跃策略数
- 评估组合风险等级
- 管理策略状态
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

from alphaloop.portfolio.health import calculate_strategy_health


class StrategyStatus(Enum):
    """策略状态枚举"""

    LIVE = "live"
    PAPER = "paper"
    PAUSED = "paused"
    STOPPED = "stopped"


class RiskLevel(Enum):
    """风险等级枚举"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class StrategyInfo:
    """策略信息数据类"""

    id: str
    name: str
    status: StrategyStatus = StrategyStatus.STOPPED
    pnl: float = 0.0
    sharpe: Optional[float] = None
    health: int = 0
    allocation: float = 0.0
    roi: float = 0.0

    # 执行指标
    fill_rate: float = 0.85
    slippage: float = 0.0
    max_drawdown: float = 0.0
    total_trades: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "pnl": round(self.pnl, 4),
            "sharpe": round(self.sharpe, 2) if self.sharpe else None,
            "health": self.health,
            "allocation": round(self.allocation, 4),
            "roi": round(self.roi, 4),
        }


class PortfolioManager:
    """
    组合管理器

    管理多个交易策略的组合，提供：
    - 组合级别的指标汇总
    - 策略间的对比分析
    - 风险等级评估
    - 策略状态管理
    - 动态资金分配
    """

    def __init__(
        self,
        total_capital: float = 10000.0,
        min_allocation: float = 0.1,
        max_allocation: float = 0.7,
        auto_rebalance: bool = False,
    ):
        """
        初始化组合管理器

        Args:
            total_capital: 总资金 (USDT)
            min_allocation: 最小分配比例 (0-1)
            max_allocation: 最大分配比例 (0-1)
            auto_rebalance: 是否自动再平衡（更新指标时自动调整分配）
        """
        self.total_capital = total_capital
        self.strategies: Dict[str, StrategyInfo] = {}
        self.pnl_history: List[float] = []  # 用于计算组合 Sharpe
        self.min_allocation = min_allocation
        self.max_allocation = max_allocation
        self.auto_rebalance = auto_rebalance

    def register_strategy(
        self,
        strategy_id: str,
        name: str,
        allocation: float = 0.5,
        status: StrategyStatus = StrategyStatus.STOPPED,
    ) -> None:
        """
        注册新策略

        Args:
            strategy_id: 策略唯一标识
            name: 策略名称
            allocation: 资金分配比例 (0-1)
            status: 初始状态
        """
        self.strategies[strategy_id] = StrategyInfo(
            id=strategy_id,
            name=name,
            status=status,
            allocation=allocation,
        )
        self._normalize_allocations()

    def _normalize_allocations(self) -> None:
        """
        归一化资金分配，确保总和为 100%
        """
        total = sum(s.allocation for s in self.strategies.values())
        if total > 0:
            for strategy in self.strategies.values():
                strategy.allocation = strategy.allocation / total

    def update_strategy_metrics(
        self,
        strategy_id: str,
        pnl: float = None,
        sharpe: float = None,
        fill_rate: float = None,
        slippage: float = None,
        max_drawdown: float = None,
        total_trades: int = None,
    ) -> None:
        """
        更新策略指标

        Args:
            strategy_id: 策略标识
            pnl: 净盈亏
            sharpe: 夏普比率
            fill_rate: 成交率
            slippage: 滑点 (bps)
            max_drawdown: 最大回撤
            total_trades: 总交易数
        """
        if strategy_id not in self.strategies:
            return

        strategy = self.strategies[strategy_id]

        if pnl is not None:
            strategy.pnl = pnl
        if sharpe is not None:
            strategy.sharpe = sharpe
        if fill_rate is not None:
            strategy.fill_rate = fill_rate
        if slippage is not None:
            strategy.slippage = slippage
        if max_drawdown is not None:
            strategy.max_drawdown = max_drawdown
        if total_trades is not None:
            strategy.total_trades = total_trades

        # 重新计算健康度
        strategy.health = int(
            calculate_strategy_health(
                {
                    "pnl": strategy.pnl,
                    "sharpe": strategy.sharpe or 0,
                    "fill_rate": strategy.fill_rate,
                    "slippage": strategy.slippage,
                    "max_drawdown": strategy.max_drawdown,
                }
            )
        )

        # 计算 ROI
        allocated_capital = self.total_capital * strategy.allocation
        if allocated_capital > 0:
            strategy.roi = strategy.pnl / allocated_capital

        # Auto-rebalance if enabled
        if self.auto_rebalance:
            self.rebalance_allocations(method="composite")

    def set_strategy_status(self, strategy_id: str, status: StrategyStatus) -> bool:
        """
        设置策略状态

        Args:
            strategy_id: 策略标识
            status: 新状态

        Returns:
            bool: 是否成功
        """
        if strategy_id not in self.strategies:
            return False

        self.strategies[strategy_id].status = status
        return True

    def pause_strategy(self, strategy_id: str) -> bool:
        """暂停策略"""
        return self.set_strategy_status(strategy_id, StrategyStatus.PAUSED)

    def resume_strategy(self, strategy_id: str) -> bool:
        """恢复策略"""
        return self.set_strategy_status(strategy_id, StrategyStatus.LIVE)

    def get_total_pnl(self) -> float:
        """
        获取组合总盈亏

        Returns:
            float: 所有策略 PnL 之和
        """
        return sum(s.pnl for s in self.strategies.values())

    def get_active_count(self) -> int:
        """
        获取活跃策略数量

        Returns:
            int: status = LIVE 的策略数
        """
        return sum(
            1 for s in self.strategies.values() if s.status == StrategyStatus.LIVE
        )

    def get_portfolio_sharpe(self) -> Optional[float]:
        """
        计算组合夏普比率

        基于组合整体收益率计算，而非各策略 Sharpe 的简单平均。

        Returns:
            Optional[float]: 组合夏普比率，数据不足时返回 None
        """
        if len(self.pnl_history) < 10:
            return None

        returns = np.diff(self.pnl_history)
        if len(returns) == 0 or np.std(returns) == 0:
            return None

        # 年化夏普比率 (假设每分钟一个数据点)
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(365 * 24 * 60)
        return round(float(sharpe), 2)

    def get_risk_level(self) -> RiskLevel:
        """
        评估组合风险等级

        规则：
        - 任一策略 max_drawdown > 10% → HIGH
        - 任一策略健康度 < 40 → MEDIUM
        - 所有策略正常 → LOW

        Returns:
            RiskLevel: 风险等级
        """
        for strategy in self.strategies.values():
            # 高回撤 → 高风险
            if strategy.max_drawdown > 0.1:
                return RiskLevel.HIGH

        for strategy in self.strategies.values():
            # 低健康度 → 中风险
            if strategy.health < 40:
                return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def get_portfolio_data(self) -> Dict[str, Any]:
        """
        获取组合完整数据

        用于 /api/portfolio 端点响应。

        Returns:
            Dict: 包含组合概览和策略列表的字典
        """
        # 按 PnL 降序排列策略
        sorted_strategies = sorted(
            self.strategies.values(), key=lambda s: s.pnl, reverse=True
        )

        return {
            "total_pnl": round(self.get_total_pnl(), 4),
            "portfolio_sharpe": self.get_portfolio_sharpe(),
            "active_count": self.get_active_count(),
            "total_count": len(self.strategies),
            "risk_level": self.get_risk_level().value,
            "total_capital": self.total_capital,
            "strategies": [s.to_dict() for s in sorted_strategies],
        }

    def record_pnl_snapshot(self) -> None:
        """
        记录当前 PnL 快照

        用于计算组合 Sharpe 比率。
        """
        total_pnl = self.get_total_pnl()
        self.pnl_history.append(total_pnl)

        # 只保留最近 1000 个数据点
        if len(self.pnl_history) > 1000:
            self.pnl_history = self.pnl_history[-1000:]

    def set_allocation_limits(
        self, min_allocation: float = None, max_allocation: float = None
    ) -> None:
        """
        设置资金分配限制

        Args:
            min_allocation: 最小分配比例 (0-1)
            max_allocation: 最大分配比例 (0-1)
        """
        if min_allocation is not None:
            self.min_allocation = max(0.0, min(1.0, min_allocation))
        if max_allocation is not None:
            self.max_allocation = max(0.0, min(1.0, max_allocation))

    def get_allocation_for_strategy(self, strategy_id: str) -> float:
        """
        获取策略的当前资金分配

        Args:
            strategy_id: 策略标识

        Returns:
            float: 分配比例 (0-1)，策略不存在时返回 0.0
        """
        if strategy_id not in self.strategies:
            return 0.0
        return self.strategies[strategy_id].allocation

    def rebalance_allocations(
        self,
        method: str = "equal",
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """
        重新平衡资金分配

        支持多种分配策略：
        - "equal": 等权重分配
        - "sharpe": 基于夏普比率加权
        - "health": 基于健康度加权
        - "roi": 基于 ROI 加权
        - "composite": 综合评分（Sharpe + ROI + Health）
        - "risk_adjusted": 风险调整分配（基于最大回撤）

        Args:
            method: 分配方法
            weights: 综合评分时的权重（仅用于 composite 方法）
                    格式: {"sharpe": 0.4, "roi": 0.3, "health": 0.3}

        Returns:
            Dict[str, float]: 新的分配比例字典
        """
        if not self.strategies:
            return {}

        # Filter active strategies only
        active_strategies = {
            sid: s
            for sid, s in self.strategies.items()
            if s.status == StrategyStatus.LIVE
        }

        if not active_strategies:
            # If no active strategies, use all strategies
            active_strategies = self.strategies

        if method == "equal":
            # Equal allocation
            allocation = 1.0 / len(active_strategies)
            new_allocations = {sid: allocation for sid in active_strategies.keys()}

        elif method == "sharpe":
            # Sharpe ratio weighted
            sharpe_values = {
                sid: max(0.0, s.sharpe or 0.0) for sid, s in active_strategies.items()
            }
            total_sharpe = sum(sharpe_values.values())
            if total_sharpe > 0:
                new_allocations = {
                    sid: sharpe / total_sharpe
                    for sid, sharpe in sharpe_values.items()
                }
            else:
                # Fallback to equal if no Sharpe data
                allocation = 1.0 / len(active_strategies)
                new_allocations = {sid: allocation for sid in active_strategies.keys()}

        elif method == "health":
            # Health score weighted
            health_values = {
                sid: max(0.0, s.health) for sid, s in active_strategies.items()
            }
            total_health = sum(health_values.values())
            if total_health > 0:
                new_allocations = {
                    sid: health / total_health
                    for sid, health in health_values.items()
                }
            else:
                # Fallback to equal
                allocation = 1.0 / len(active_strategies)
                new_allocations = {sid: allocation for sid in active_strategies.keys()}

        elif method == "roi":
            # ROI weighted (normalize to positive values first)
            roi_values = {
                sid: max(0.0, s.roi + 1.0)  # Shift to positive
                for sid, s in active_strategies.items()
            }
            total_roi = sum(roi_values.values())
            if total_roi > 0:
                new_allocations = {
                    sid: roi / total_roi for sid, roi in roi_values.items()
                }
            else:
                # Fallback to equal
                allocation = 1.0 / len(active_strategies)
                new_allocations = {sid: allocation for sid in active_strategies.keys()}

        elif method == "composite":
            # Composite score: weighted combination of Sharpe, ROI, Health
            default_weights = {"sharpe": 0.4, "roi": 0.3, "health": 0.3}
            if weights is None:
                weights = default_weights

            # Normalize inputs
            sharpe_values = [
                max(0.0, s.sharpe or 0.0) for s in active_strategies.values()
            ]
            roi_values = [max(0.0, s.roi + 1.0) for s in active_strategies.values()]
            health_values = [max(0.0, s.health) for s in active_strategies.values()]

            # Normalize to 0-1 range
            def normalize(values):
                if not values or max(values) == min(values):
                    return [1.0 / len(values)] * len(values)
                max_val = max(values)
                min_val = min(values)
                if max_val == min_val:
                    return [1.0 / len(values)] * len(values)
                return [(v - min_val) / (max_val - min_val) for v in values]

            norm_sharpe = normalize(sharpe_values)
            norm_roi = normalize(roi_values)
            norm_health = normalize(health_values)

            # Calculate composite scores
            composite_scores = {}
            for i, (sid, strategy) in enumerate(active_strategies.items()):
                score = (
                    weights.get("sharpe", 0.4) * norm_sharpe[i]
                    + weights.get("roi", 0.3) * norm_roi[i]
                    + weights.get("health", 0.3) * norm_health[i]
                )
                composite_scores[sid] = max(0.0, score)

            total_score = sum(composite_scores.values())
            if total_score > 0:
                new_allocations = {
                    sid: score / total_score
                    for sid, score in composite_scores.items()
                }
            else:
                # Fallback to equal
                allocation = 1.0 / len(active_strategies)
                new_allocations = {sid: allocation for sid in active_strategies.keys()}

        elif method == "risk_adjusted":
            # Inverse risk weighted (lower risk → more allocation)
            risk_scores = {}
            for sid, strategy in active_strategies.items():
                # Risk = max_drawdown + normalized position risk
                risk = max(0.01, strategy.max_drawdown)  # Avoid division by zero
                risk_scores[sid] = risk

            # Inverse risk (lower risk → higher allocation)
            inverse_risk = {sid: 1.0 / risk for sid, risk in risk_scores.items()}
            total_inverse = sum(inverse_risk.values())
            if total_inverse > 0:
                new_allocations = {
                    sid: inv_risk / total_inverse
                    for sid, inv_risk in inverse_risk.items()
                }
            else:
                # Fallback to equal
                allocation = 1.0 / len(active_strategies)
                new_allocations = {sid: allocation for sid in active_strategies.keys()}

        else:
            # Unknown method, fallback to equal
            allocation = 1.0 / len(active_strategies)
            new_allocations = {sid: allocation for sid in active_strategies.keys()}

        # Apply min/max constraints
        constrained_allocations = {}
        for sid, alloc in new_allocations.items():
            constrained_alloc = max(
                self.min_allocation, min(self.max_allocation, alloc)
            )
            constrained_allocations[sid] = constrained_alloc

        # Renormalize to ensure sum = 1.0
        total_constrained = sum(constrained_allocations.values())
        if total_constrained > 0:
            for sid in constrained_allocations:
                constrained_allocations[sid] /= total_constrained

        # Update allocations
        for sid, new_alloc in constrained_allocations.items():
            if sid in self.strategies:
                self.strategies[sid].allocation = new_alloc

        # Update inactive strategies to 0 (or keep their current allocation)
        for sid, strategy in self.strategies.items():
            if sid not in constrained_allocations:
                # Optionally set inactive strategies to 0
                # strategy.allocation = 0.0
                pass

        return constrained_allocations
