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
    Rounds a price to the nearest tick size (down).
    
    Always rounds down to ensure the price is divisible by tick_size.
    Uses Decimal arithmetic to ensure exact divisibility.
    将价格舍入到最近的 tick size（向下舍入）。
    
    始终向下舍入以确保价格可被 tick_size 整除。
    使用 Decimal 算术确保精确可整除性。

    Args:
        price: The price to round
        tick_size: The tick size to round to

    Returns:
        Rounded price that is divisible by tick_size (as float)
    """
    if tick_size <= 0:
        return price
    
    # Convert to Decimal for precise arithmetic / 转换为 Decimal 以进行精确算术
    price_decimal = Decimal(str(price))
    tick_size_decimal = Decimal(str(tick_size))
    
    # Calculate number of ticks and round down (floor) / 计算 tick 数量并向下舍入
    # Use floor division to always round down, consistent with round_step_size
    # 使用向下整除以始终向下舍入，与 round_step_size 保持一致
    ticks_rounded = (price_decimal // tick_size_decimal)
    
    # Calculate rounded price / 计算舍入后的价格
    rounded = ticks_rounded * tick_size_decimal
    
    # Convert back to float
    # Since we've already ensured divisibility using Decimal arithmetic,
    # the float conversion should be safe
    # 转换回 float
    # 由于我们已经使用 Decimal 算术确保了可整除性，float 转换应该是安全的
    return float(rounded)
