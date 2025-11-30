"""
Data schemas for Multi-LLM Strategy Evaluation
多 LLM 策略评估数据模型

Owner: Agent AI
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class MarketContext:
    """市场上下文数据 - 作为 LLM 输入"""

    symbol: str
    mid_price: float
    best_bid: float
    best_ask: float
    spread_bps: float

    volatility_24h: float
    volatility_1h: float

    funding_rate: float
    funding_rate_trend: str
    next_funding_time: Optional[datetime] = None

    current_position: float = 0.0
    position_side: str = "neutral"
    unrealized_pnl: float = 0.0

    available_balance: float = 10000.0
    current_leverage: float = 1.0

    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    recent_pnl: float = 0.0

    def to_prompt_string(self) -> str:
        """Convert to formatted string for LLM prompt"""
        return f"""
【市场数据 / Market Data】
- 交易对 Symbol: {self.symbol}
- 中间价 Mid Price: ${self.mid_price:,.2f}
- 最佳买价 Best Bid: ${self.best_bid:,.2f}
- 最佳卖价 Best Ask: ${self.best_ask:,.2f}
- 市场价差 Market Spread: {self.spread_bps:.2f} bps

【波动率 / Volatility】
- 24小时波动率: {self.volatility_24h:.2%}
- 1小时波动率: {self.volatility_1h:.2%}

【资金费率 / Funding Rate】
- 当前费率: {self.funding_rate:.4%}
- 费率趋势: {self.funding_rate_trend}

【当前持仓 / Current Position】
- 仓位: {self.current_position} ({self.position_side})
- 未实现盈亏: ${self.unrealized_pnl:,.2f}
- 杠杆倍数: {self.current_leverage}x

【账户状态 / Account Status】
- 可用余额: ${self.available_balance:,.2f}

【历史绩效 / Historical Performance】
- 胜率: {self.win_rate:.1%}
- 夏普比率: {self.sharpe_ratio:.2f}
- 近期盈亏: ${self.recent_pnl:,.2f}
"""


@dataclass
class StrategyProposal:
    """策略参数建议 - LLM 输出"""

    recommended_strategy: str
    spread: float
    skew_factor: float = 100.0
    quantity: float = 0.1
    leverage: float = 1.0

    reasoning: str = ""
    confidence: float = 0.0
    risk_level: str = "medium"
    expected_return: float = 0.0

    provider_name: str = ""
    raw_response: str = ""
    parse_success: bool = True
    parse_error: str = ""


@dataclass
class SimulationResult:
    """模拟交易结果"""

    realized_pnl: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    win_rate: float = 0.0
    max_drawdown: float = 0.0

    avg_slippage_bps: float = 0.0
    fill_rate: float = 0.0

    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    volatility: float = 0.0

    simulation_steps: int = 0
    pnl_history: list = field(default_factory=list)


@dataclass
class EvaluationResult:
    """完整的评估结果"""

    provider_name: str
    proposal: StrategyProposal
    simulation: SimulationResult

    score: float = 0.0
    rank: int = 0

    timestamp: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0.0

    def to_summary(self) -> dict:
        return {
            "provider": self.provider_name,
            "strategy": self.proposal.recommended_strategy,
            "spread": f"{self.proposal.spread:.4f}",
            "skew_factor": self.proposal.skew_factor,
            "confidence": f"{self.proposal.confidence:.1%}",
            "pnl": f"${self.simulation.realized_pnl:,.2f}",
            "win_rate": f"{self.simulation.win_rate:.1%}",
            "sharpe": f"{self.simulation.sharpe_ratio:.2f}",
            "score": f"{self.score:.1f}",
            "rank": self.rank,
            "latency_ms": f"{self.latency_ms:.0f}",
        }


@dataclass
class ParameterStatistics:
    """Parameter statistics across models"""

    spread_mean: float = 0.0
    spread_median: float = 0.0
    spread_min: float = 0.0
    spread_max: float = 0.0
    spread_std: float = 0.0

    skew_mean: float = 0.0
    skew_median: float = 0.0

    quantity_mean: float = 0.0
    quantity_median: float = 0.0

    leverage_mean: float = 0.0
    leverage_median: float = 0.0

    confidence_mean: float = 0.0
    confidence_min: float = 0.0
    confidence_max: float = 0.0


@dataclass
class StrategyConsensus:
    """Strategy consensus analysis"""

    consensus_strategy: str = ""
    consensus_count: int = 0
    total_models: int = 0

    strategy_votes: Dict[str, int] = field(default_factory=dict)
    strategy_percentages: Dict[str, float] = field(default_factory=dict)

    consensus_level: str = "none"
    consensus_ratio: float = 0.0

    providers_by_strategy: Dict[str, List[str]] = field(default_factory=dict)

    def is_unanimous(self) -> bool:
        return self.consensus_count == self.total_models and self.total_models > 0

    def has_majority(self) -> bool:
        return self.consensus_ratio > 0.5


@dataclass
class AggregatedResult:
    """Aggregated evaluation result from all models"""

    strategy_consensus: StrategyConsensus = field(default_factory=StrategyConsensus)
    parameter_stats: ParameterStatistics = field(default_factory=ParameterStatistics)

    consensus_confidence: float = 0.0
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)

    consensus_proposal: Optional[StrategyProposal] = None

    individual_results: List[EvaluationResult] = field(default_factory=list)
    successful_evaluations: int = 0
    failed_evaluations: int = 0

    avg_pnl: float = 0.0
    avg_sharpe: float = 0.0
    avg_win_rate: float = 0.0
    avg_latency_ms: float = 0.0

    timestamp: datetime = field(default_factory=datetime.now)

    def to_summary(self) -> dict:
        return {
            "consensus_strategy": self.strategy_consensus.consensus_strategy,
            "consensus_level": self.strategy_consensus.consensus_level,
            "consensus_ratio": f"{self.strategy_consensus.consensus_ratio:.1%}",
            "consensus_confidence": f"{self.consensus_confidence:.1%}",
            "successful_models": self.successful_evaluations,
            "failed_models": self.failed_evaluations,
            "avg_pnl": f"${self.avg_pnl:,.2f}",
            "avg_sharpe": f"{self.avg_sharpe:.2f}",
            "avg_win_rate": f"{self.avg_win_rate:.1%}",
            "parameter_spread_range": f"{self.parameter_stats.spread_min:.4f}-{self.parameter_stats.spread_max:.4f}",
        }

    def get_recommendation_strength(self) -> str:
        if self.strategy_consensus.is_unanimous():
            return "strong"
        elif self.strategy_consensus.has_majority():
            return "moderate"
        else:
            return "weak"

