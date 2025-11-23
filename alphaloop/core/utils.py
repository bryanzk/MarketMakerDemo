from decimal import ROUND_DOWN, ROUND_FLOOR, Decimal


def round_step_size(quantity, step_size):
    """
    Rounds a quantity to the nearest step size (down).
    """
    quantity = Decimal(str(quantity))
    step_size = Decimal(str(step_size))
    return float((quantity // step_size) * step_size)


def round_tick_size(price, tick_size):
    """
    Rounds a price to the nearest tick size.
    """
    price = Decimal(str(price))
    tick_size = Decimal(str(tick_size))
    return float(
        (price / tick_size).quantize(Decimal("1"), rounding=ROUND_FLOOR) * tick_size
    )
