"""
Utility Functions / 工具函数

Common helper functions used across modules.
跨模块使用的通用辅助函数。

Owner: Agent ARCH
"""

from decimal import ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_UP, Decimal


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
    
    Uses standard rounding (nearest) to ensure price is divisible by tick_size.
    使用标准四舍五入（最近值）确保价格可被 tick_size 整除。

    Args:
        price: The price to round
        tick_size: The tick size to round to

    Returns:
        Rounded price that is divisible by tick_size
    """
    if tick_size <= 0:
        return price
    
    price = Decimal(str(price))
    tick_size = Decimal(str(tick_size))
    
    # Round to nearest tick_size / 四舍五入到最近的 tick_size
    rounded = (price / tick_size).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * tick_size
    
    # Verify the result is divisible by tick_size / 验证结果可被 tick_size 整除
    remainder = rounded % tick_size
    if remainder != 0:
        # If not divisible, round down to ensure divisibility / 如果不可整除，向下舍入以确保可整除
        rounded = (price / tick_size).quantize(Decimal("1"), rounding=ROUND_FLOOR) * tick_size
    
    return float(rounded)
