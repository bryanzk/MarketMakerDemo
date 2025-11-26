"""
Strategy Health Score Calculator / 策略健康度评分计算器

基于用户故事 US-2.3 实现健康度评分计算。
健康度是一个 0-100 的综合评分，基于以下因素计算：
- 盈利能力 (权重 40%)
- 风险调整收益 (权重 30%)
- 执行质量 (权重 20%)
- 稳定性 (权重 10%)
"""

from typing import Dict, Any


# 健康度各因素权重
HEALTH_WEIGHTS = {
    "profitability": 0.4,  # 盈利能力
    "risk_adjusted": 0.3,  # 风险调整收益
    "execution": 0.2,  # 执行质量
    "stability": 0.1,  # 稳定性
}


def calculate_strategy_health(metrics: Dict[str, Any]) -> float:
    """
    计算策略健康度评分 (0-100)

    Args:
        metrics: 策略指标字典，包含:
            - pnl: 净盈亏 (float)
            - sharpe: 夏普比率 (float)
            - fill_rate: 成交率 (0-1)
            - slippage: 滑点 (bps)
            - max_drawdown: 最大回撤 (0-1)

    Returns:
        float: 健康度评分 (0-100)

    Example:
        >>> metrics = {
        ...     "pnl": 100,
        ...     "sharpe": 2.0,
        ...     "fill_rate": 0.85,
        ...     "slippage": 2.0,
        ...     "max_drawdown": 0.02,
        ... }
        >>> score = calculate_strategy_health(metrics)
        >>> 0 <= score <= 100
        True
    """
    scores = {}

    # 1. 盈利能力评分 (0-100)
    # 公式: min(100, max(0, 50 + pnl / 100))
    # pnl = 0 → 50分, pnl = 5000 → 100分, pnl = -5000 → 0分
    pnl = metrics.get("pnl", 0)
    scores["profitability"] = min(100, max(0, 50 + pnl / 100))

    # 2. 风险调整收益评分 (0-100)
    # 公式: min(100, sharpe * 40)
    # sharpe = 0 → 0分, sharpe = 2.5 → 100分
    sharpe = metrics.get("sharpe", 0) or 0
    scores["risk_adjusted"] = min(100, sharpe * 40)

    # 3. 执行质量评分 (0-100)
    # 公式: fill_rate * 100 - slippage * 10
    # fill_rate = 1.0, slippage = 0 → 100分
    # fill_rate = 0.85, slippage = 2 → 65分
    fill_rate = metrics.get("fill_rate", 0.8)
    slippage = metrics.get("slippage", 0)
    scores["execution"] = max(0, min(100, fill_rate * 100 - slippage * 10))

    # 4. 稳定性评分 (0-100)
    # 公式: max(0, 100 - max_drawdown * 1000)
    # max_drawdown = 0 → 100分, max_drawdown = 0.1 → 0分
    max_drawdown = metrics.get("max_drawdown", 0)
    scores["stability"] = max(0, min(100, 100 - max_drawdown * 1000))

    # 加权计算总分
    health = sum(scores[factor] * weight for factor, weight in HEALTH_WEIGHTS.items())

    return round(health, 1)


def get_health_status(health_score: float) -> str:
    """
    根据健康度评分返回状态描述

    Args:
        health_score: 健康度评分 (0-100)

    Returns:
        str: 状态描述 ("excellent", "good", "fair", "poor")
    """
    if health_score >= 80:
        return "excellent"
    elif health_score >= 60:
        return "good"
    elif health_score >= 40:
        return "fair"
    else:
        return "poor"


def get_health_color(health_score: float) -> str:
    """
    根据健康度评分返回颜色代码

    Args:
        health_score: 健康度评分 (0-100)

    Returns:
        str: 颜色十六进制代码
    """
    if health_score >= 80:
        return "#10b981"  # 绿色
    elif health_score >= 60:
        return "#f59e0b"  # 黄色
    elif health_score >= 40:
        return "#f97316"  # 橙色
    else:
        return "#ef4444"  # 红色
