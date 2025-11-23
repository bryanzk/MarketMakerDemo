from alphaloop.core.config import MAX_POSITION


class RiskManager:
    def check_position_limits(self, position_amt):
        """
        Checks if position is within limits.
        Returns: list of allowed sides ['buy', 'sell']
        """
        allowed_sides = ["buy", "sell"]

        if position_amt >= MAX_POSITION:
            if "buy" in allowed_sides:
                allowed_sides.remove("buy")
        elif position_amt <= -MAX_POSITION:
            if "sell" in allowed_sides:
                allowed_sides.remove("sell")

        return allowed_sides
