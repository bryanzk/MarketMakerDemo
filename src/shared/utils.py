"""
Utility Functions / 工具函数

Common helper functions used across modules.
跨模块使用的通用辅助函数。

Owner: Agent ARCH
"""

from decimal import ROUND_DOWN, ROUND_FLOOR, Decimal


def round_step_size(quantity: float, step_size: float) -> float:
    """
    Rounds a quantity to the nearest step size (down).

    Args:
        quantity: The quantity to round
        step_size: The step size to round to

    Returns:
        Rounded quantity
    """
    quantity = Decimal(str(quantity))
    step_size = Decimal(str(step_size))
    return float((quantity // step_size) * step_size)


def round_tick_size(price: float, tick_size: float) -> float:
    """
    Rounds a price to the nearest tick size.

    Args:
        price: The price to round
        tick_size: The tick size to round to

    Returns:
        Rounded price
    """
    price = Decimal(str(price))
    tick_size = Decimal(str(tick_size))
    return float(
        (price / tick_size).quantize(Decimal("1"), rounding=ROUND_FLOOR) * tick_size
    )
