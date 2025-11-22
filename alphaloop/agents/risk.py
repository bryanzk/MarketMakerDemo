from alphaloop.core.config import RISK_LIMITS
from alphaloop.core.logger import setup_logger

logger = setup_logger("RiskAgent")

class RiskAgent:
    def validate_proposal(self, proposed_config):
        """
        Validates a proposed configuration against risk limits.
        
        Args:
            proposed_config: dict, e.g. {'spread': 0.009}
            
        Returns:
            bool: True if approved, False if rejected.
        """
        spread = proposed_config.get('spread')
        
        logger.info(f"Validating proposal", extra={'extra_data': {'spread': spread}})
        
        # Risk Limits
        min_spread = RISK_LIMITS['MIN_SPREAD']
        max_spread = RISK_LIMITS['MAX_SPREAD']
        
        if spread < min_spread:
            logger.warning(f"REJECTED: Spread too tight", extra={'extra_data': {'spread': spread, 'min': min_spread}})
            return False
            
        if spread > max_spread:
            logger.warning(f"REJECTED: Spread too wide", extra={'extra_data': {'spread': spread, 'max': max_spread}})
            return False
            
        logger.info("APPROVED")
        return True
