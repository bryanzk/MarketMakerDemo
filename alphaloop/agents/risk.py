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
        spread = proposed_config.get("spread")

        logger.info(f"Validating proposal", extra={"extra_data": {"spread": spread}})

        # Risk Limits
        min_spread = RISK_LIMITS["MIN_SPREAD"]
        max_spread = RISK_LIMITS["MAX_SPREAD"]

        if spread < min_spread:
            reason = (
                f"Spread {spread*100:.2f}% is too tight (Min {min_spread*100:.2f}%)"
            )
            logger.warning(
                f"REJECTED: {reason}",
                extra={"extra_data": {"spread": spread, "min": min_spread}},
            )
            return False, reason

        if spread > max_spread:
            reason = f"Spread {spread*100:.2f}% is too wide (Max {max_spread*100:.2f}%)"
            logger.warning(
                f"REJECTED: {reason}",
                extra={"extra_data": {"spread": spread, "max": max_spread}},
            )
            return False, reason

        # Validate Skew Factor if present
        skew_factor = proposed_config.get("skew_factor")
        if skew_factor is not None:
            max_skew = 500.0 # Hardcoded limit for now, could be in config
            if skew_factor < 0:
                reason = f"Skew Factor {skew_factor} cannot be negative"
                return False, reason
            if skew_factor > max_skew:
                reason = f"Skew Factor {skew_factor} is too high (Max {max_skew})"
                return False, reason

        logger.info("APPROVED")
        return True, "Approved"
