"""
Data schemas for Multi-LLM Strategy Evaluation
多 LLM 策略评估数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class MarketContext:
    """
    市场上下文数据 - 作为 LLM 输入
    Market context data - used as LLM input
    """

    # 价格数据 / Price data
    symbol: str
    mid_price: float
    best_bid: float
    best_ask: float
    spread_bps: float  # 当前市场价差 (基点)

    # 波动性 / Volatility
    volatility_24h: float  # 24小时波动率
    volatility_1h: float  # 1小时波动率

    # 资金费率 / Funding rate
    funding_rate: float  # 当前资金费率
    funding_rate_trend: str  # "rising" | "falling" | "stable"
    next_funding_time: Optional[datetime] = None

    # 持仓信息 / Position info
    current_position: float = 0.0
    position_side: str = "neutral"  # "long" | "short" | "neutral"
    unrealized_pnl: float = 0.0

    # 账户信息 / Account info
    available_balance: float = 10000.0
    current_leverage: float = 1.0

    # 历史绩效 / Historical performance
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
    """
    策略参数建议 - LLM 输出
    Strategy parameter proposal - LLM output
    """

    # 策略选择 / Strategy selection
    recommended_strategy: str  # "FixedSpread" | "FundingRate"

    # 参数建议 / Parameter suggestions
    spread: float  # 价差百分比 (e.g., 0.01 = 1%)
    skew_factor: float = 100.0  # 资金费率倾斜因子
    quantity: float = 0.1  # 交易数量
    leverage: float = 1.0  # 杠杆倍数

    # 分析 / Analysis
    reasoning: str = ""  # 决策理由
    confidence: float = 0.0  # 置信度 (0-1)
    risk_level: str = "medium"  # "low" | "medium" | "high"
    expected_return: float = 0.0  # 预期收益率

    # 元数据 / Metadata
    provider_name: str = ""
    raw_response: str = ""
    parse_success: bool = True
    parse_error: str = ""


@dataclass
class SimulationResult:
    """
    模拟交易结果
    Simulation trading result
    """

    # 绩效指标 / Performance metrics
    realized_pnl: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    win_rate: float = 0.0
    max_drawdown: float = 0.0

    # 执行质量 / Execution quality
    avg_slippage_bps: float = 0.0
    fill_rate: float = 0.0

    # 风险指标 / Risk metrics
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    volatility: float = 0.0

    # 元数据 / Metadata
    simulation_steps: int = 0
    pnl_history: list = field(default_factory=list)


@dataclass
class EvaluationResult:
    """
    完整的评估结果 - 包含 LLM 建议 + 模拟结果
    Complete evaluation result - includes LLM proposal + simulation result
    """

    # LLM 信息 / LLM info
    provider_name: str
    proposal: StrategyProposal
    simulation: SimulationResult

    # 评分 / Scoring
    score: float = 0.0  # 综合评分 (0-100)
    rank: int = 0  # 排名

    # 时间戳 / Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0.0  # LLM 响应延迟

    def to_summary(self) -> dict:
        """Return a summary dict for comparison"""
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
