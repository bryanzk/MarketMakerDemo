import json
from alphaloop.core.logger import setup_logger

logger = setup_logger("QuantAgent")

class QuantAgent:
    def analyze_and_propose(self, current_strategy_config, performance_stats):
        """
        Analyzes performance and proposes changes to the strategy.
        
        Args:
            current_strategy_config: dict, e.g. {'spread': 0.01}
            performance_stats: dict, e.g. {'win_rate': 55.0, 'realized_pnl': 100}
            
        Returns:
            dict: Proposed new configuration, or None if no change needed.
        """
        win_rate = performance_stats.get('win_rate', 0)
        sharpe = performance_stats.get('sharpe_ratio', 0)
        current_spread = current_strategy_config.get('spread', 0.01)
        
        logger.info(f"Analyzing performance", extra={'extra_data': {'win_rate': win_rate, 'sharpe': sharpe, 'current_spread': current_spread}})
        
        new_spread = current_spread
        
        # Logic:
        # 1. If Sharpe is low (< 1.0), strategy is struggling. Widen spread to increase PnL per trade.
        # 2. If Win Rate is high (> 55%), we can afford to tighten spread to get more volume.
        
        if sharpe < 1.0 or win_rate < 45:
            new_spread = current_spread * 1.1 # Widen by 10%
            logger.info(f"Metrics low (Sharpe < 1.0 or WR < 45%). Proposing WIDER spread", extra={'extra_data': {'new_spread': new_spread}})
        elif win_rate > 55 and sharpe > 2.0:
            new_spread = current_spread * 0.9 # Tighten by 10%
            logger.info(f"Metrics high (Sharpe > 2.0 and WR > 55%). Proposing TIGHTER spread", extra={'extra_data': {'new_spread': new_spread}})
        else:
            logger.info("Performance acceptable. No change proposed.")
            return None
            
        return {'spread': new_spread}
