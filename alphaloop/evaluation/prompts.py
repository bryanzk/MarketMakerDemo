"""
Prompt Templates for Multi-LLM Strategy Evaluation
多 LLM 策略评估 Prompt 模板
"""

from alphaloop.evaluation.schemas import MarketContext


class StrategyAdvisorPrompt:
    """策略顾问 Prompt 生成器"""

    TEMPLATE = """You are an expert quantitative trading analyst specializing in cryptocurrency perpetual futures market making.

Analyze the following market data and recommend optimal trading strategy parameters.

{market_context}

【可选策略 / Available Strategies】
1. FixedSpread - 固定价差做市策略，适合低波动市场
2. FundingRate - 资金费率倾斜策略，适合捕获资金费率套利

【你的任务 / Your Task】
Based on the market conditions, recommend:
1. Which strategy to use
2. Optimal parameters for the strategy
3. Your confidence level in this recommendation

【输出格式要求 / Output Format】
Return ONLY a valid JSON object with the following structure (no markdown, no explanation outside JSON):

{{
    "recommended_strategy": "FixedSpread" or "FundingRate",
    "spread": 0.01,
    "skew_factor": 100,
    "quantity": 0.1,
    "leverage": 1.0,
    "reasoning": "Your reasoning here",
    "confidence": 0.85,
    "risk_level": "low" or "medium" or "high",
    "expected_return": 0.05
}}

Parameter Guidelines:
- spread: 0.005 to 0.03 (0.5% to 3%)
- skew_factor: 50 to 200 (how aggressively to skew based on funding)
- quantity: 0.05 to 0.5 (trade size in base currency)
- leverage: 1 to 5 (conservative to aggressive)
- confidence: 0.0 to 1.0 (your confidence in this recommendation)

Now analyze and provide your recommendation:"""

    @classmethod
    def generate(cls, context: MarketContext) -> str:
        """Generate the strategy advisor prompt with market context"""
        return cls.TEMPLATE.format(market_context=context.to_prompt_string())


class RiskAdvisorPrompt:
    """风险顾问 Prompt 生成器"""

    TEMPLATE = """You are a risk management expert for cryptocurrency perpetual futures trading.

Analyze the following position and market conditions to provide risk assessment and recommendations.

{market_context}

【风险评估任务 / Risk Assessment Task】
1. Evaluate current position risk
2. Check liquidation proximity
3. Recommend position adjustments if needed

【输出格式要求 / Output Format】
Return ONLY a valid JSON object:

{{
    "risk_score": 0.0 to 1.0,
    "risk_level": "low" or "medium" or "high" or "critical",
    "liquidation_risk": 0.0 to 1.0,
    "recommended_action": "hold" or "reduce" or "close" or "hedge",
    "position_adjustment": 0.0,
    "reasoning": "Your risk assessment here",
    "warnings": ["warning1", "warning2"]
}}

Provide your risk assessment:"""

    @classmethod
    def generate(cls, context: MarketContext) -> str:
        """Generate the risk advisor prompt with market context"""
        return cls.TEMPLATE.format(market_context=context.to_prompt_string())


class MarketDiagnosisPrompt:
    """市场诊断 Prompt 生成器"""

    TEMPLATE = """You are a market analyst specializing in cryptocurrency perpetual futures.

Analyze the current market conditions and provide a diagnosis.

{market_context}

【诊断任务 / Diagnosis Task】
1. Identify the current market regime (trending, ranging, volatile)
2. Predict short-term direction (bullish, bearish, neutral)
3. Identify key risk factors

【输出格式要求 / Output Format】
Return ONLY a valid JSON object:

{{
    "market_regime": "trending" or "ranging" or "volatile",
    "short_term_bias": "bullish" or "bearish" or "neutral",
    "confidence": 0.0 to 1.0,
    "key_factors": ["factor1", "factor2"],
    "recommended_strategy_type": "momentum" or "mean_reversion" or "market_making",
    "reasoning": "Your market analysis here"
}}

Provide your market diagnosis:"""

    @classmethod
    def generate(cls, context: MarketContext) -> str:
        """Generate the market diagnosis prompt with market context"""
        return cls.TEMPLATE.format(market_context=context.to_prompt_string())
