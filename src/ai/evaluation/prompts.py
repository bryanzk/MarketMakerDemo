"""
Prompt Templates for Multi-LLM Strategy Evaluation
多 LLM 策略评估 Prompt 模板

Owner: Agent AI
"""

from src.ai.evaluation.schemas import MarketContext


class StrategyAdvisorPrompt:
    """策略顾问 Prompt 生成器"""

    TEMPLATE = """You are an expert quantitative trading analyst specializing in cryptocurrency perpetual futures market making.

Analyze the following market data and recommend optimal trading strategy parameters.

{market_context}

【策略 / Strategy】
FixedSpread - 固定价差做市策略，适合低波动市场
Note: Only FixedSpread strategy is supported in simulation.

【你的任务 / Your Task】
Based on the market conditions, recommend optimal parameters for FixedSpread strategy:
1. Optimal spread (价差)
2. Optimal quantity (数量)
3. Optimal leverage (杠杆)
4. Your confidence level in this recommendation (置信度)

【输出格式要求 / Output Format】
Return ONLY a valid JSON object with the following structure:

{{
    "recommended_strategy": "FixedSpread",
    "spread": 0.01,
    "skew_factor": 100,
    "quantity": 0.1,
    "leverage": 1.0,
    "reasoning": "Your reasoning here",
    "confidence": 0.85,
    "risk_level": "low" or "medium" or "high",
    "expected_return": 0.05
}}

Now analyze and provide your recommendation:"""

    @classmethod
    def generate(cls, context: MarketContext) -> str:
        return cls.TEMPLATE.format(market_context=context.to_prompt_string())


class RiskAdvisorPrompt:
    """风险顾问 Prompt 生成器"""

    TEMPLATE = """You are a risk management expert for cryptocurrency perpetual futures trading.

Analyze the following position and market conditions to provide risk assessment.

{market_context}

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
        return cls.TEMPLATE.format(market_context=context.to_prompt_string())


class MarketDiagnosisPrompt:
    """市场诊断 Prompt 生成器"""

    TEMPLATE = """You are a market analyst specializing in cryptocurrency perpetual futures.

Analyze the current market conditions and provide a diagnosis.

{market_context}

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
        return cls.TEMPLATE.format(market_context=context.to_prompt_string())
