import json

from alphaloop.core.llm import GeminiProvider, LLMGateway
from alphaloop.core.logger import setup_logger

logger = setup_logger("QuantAgent")


class QuantAgent:
    def __init__(self, gateway=None):
        self.gateway = gateway
        if not self.gateway:
            try:
                self.gateway = LLMGateway(GeminiProvider())
            except Exception as e:
                logger.warning(
                    f"LLM Gateway initialization failed: {e}. Using rule-based fallback."
                )
                self.gateway = None

    def analyze_and_propose(self, current_strategy_config, performance_stats):
        """
        Analyzes performance and proposes changes to the strategy.
        Uses LLM if available, otherwise falls back to rule-based logic.
        """
        if self.gateway:
            try:
                return self._analyze_with_llm(
                    current_strategy_config, performance_stats
                )
            except Exception as e:
                logger.error(f"LLM analysis failed: {e}. Falling back to rules.")

        return self._analyze_rule_based(current_strategy_config, performance_stats)

    def _analyze_with_llm(self, config, stats):
        prompt = f"""
        Act as a Quantitative Analyst. Analyze the following trading performance:
        Current Config: {config}
        Performance: {stats}
        
        Propose a new 'spread' value to optimize Sharpe Ratio.
        Return ONLY a JSON object with keys: "spread" (float), "reasoning" (string).
        Example: {{"spread": 0.015, "reasoning": "High volatility detected"}}
        """
        response = self.gateway.generate(prompt)
        # Clean response (remove markdown code blocks if any)
        clean_response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)

        new_spread = float(data["spread"])
        logger.info(
            f"LLM Proposal: Spread {new_spread:.4f}. Reason: {data.get('reasoning')}"
        )
        return {"spread": new_spread}

    def _analyze_rule_based(self, current_strategy_config, performance_stats):
        win_rate = performance_stats.get("win_rate", 0)
        sharpe = performance_stats.get("sharpe_ratio", 0)
        current_spread = current_strategy_config.get("spread", 0.01)

        logger.info(
            f"Analyzing performance (Rule-Based)",
            extra={
                "extra_data": {
                    "win_rate": win_rate,
                    "sharpe": sharpe,
                    "current_spread": current_spread,
                }
            },
        )

        new_spread = current_spread

        # Logic:
        # 1. If Sharpe is low (< 1.0), strategy is struggling. Widen spread to increase PnL per trade.
        # 2. If Win Rate is high (> 55%), we can afford to tighten spread to get more volume.

        if sharpe < 1.0 or win_rate < 45:
            new_spread = current_spread * 1.1  # Widen by 10%
            logger.info(
                f"Metrics low (Sharpe < 1.0 or WR < 45%). Proposing WIDER spread",
                extra={"extra_data": {"new_spread": new_spread}},
            )
        elif win_rate > 55 and sharpe > 2.0:
            new_spread = current_spread * 0.9  # Tighten by 10%
            logger.info(
                f"Metrics high (Sharpe > 2.0 and WR > 55%). Proposing TIGHTER spread",
                extra={"extra_data": {"new_spread": new_spread}},
            )
        else:
            logger.info("Performance acceptable. No change proposed.")
            return None

        return {"spread": new_spread}
