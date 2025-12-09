#!/usr/bin/env python3
"""
Quick Volatility Calculator / 快速波动率计算器

Calculate volatility from command line arguments.
从命令行参数计算波动率。

Usage / 用法:
    python3 calculate_volatility.py 100 101.5 99.8 102.3 101.0
    python3 calculate_volatility.py --prices 100,101.5,99.8,102.3,101.0
    python3 calculate_volatility.py --annualized --periods 365
"""

import argparse
import math
import sys
from typing import List, Tuple


def calculate_returns(prices: List[float]) -> List[float]:
    """Calculate returns from price series / 从价格序列计算收益率"""
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] > 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
    
    return returns


def calculate_volatility(
    returns: List[float], 
    annualized: bool = False, 
    periods_per_year: int = 365
) -> float:
    """Calculate volatility from returns / 从收益率计算波动率"""
    if len(returns) < 2:
        return 0.0
    
    n = len(returns)
    mean_return = sum(returns) / n
    variance = sum((r - mean_return) ** 2 for r in returns) / (n - 1)
    volatility = math.sqrt(variance)
    
    if annualized:
        volatility = volatility * math.sqrt(periods_per_year)
    
    return volatility


def main():
    parser = argparse.ArgumentParser(
        description="Calculate volatility from price data / 从价格数据计算波动率",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / 示例:
  %(prog)s 100 101.5 99.8 102.3 101.0
  %(prog)s --prices 100,101.5,99.8,102.3,101.0
  %(prog)s --prices 100,101.5,99.8 --annualized --periods 365
        """
    )
    
    parser.add_argument(
        'prices',
        nargs='*',
        type=float,
        help='Price values (space-separated) / 价格值（空格分隔）'
    )
    
    parser.add_argument(
        '--prices',
        type=str,
        help='Price values (comma-separated) / 价格值（逗号分隔）'
    )
    
    parser.add_argument(
        '--annualized',
        action='store_true',
        help='Annualize volatility / 年化波动率'
    )
    
    parser.add_argument(
        '--periods',
        type=int,
        default=365,
        help='Periods per year for annualization (default: 365) / 年化周期数（默认: 365）'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed calculation steps / 显示详细计算步骤'
    )
    
    args = parser.parse_args()
    
    # Get prices / 获取价格
    prices = []
    if args.prices and isinstance(args.prices, str):
        # Comma-separated / 逗号分隔
        prices = [float(x.strip()) for x in args.prices.split(',')]
    elif len(args.prices) > 0:
        # Space-separated / 空格分隔 (from positional arguments)
        prices = args.prices
    elif len(sys.argv) > 1:
        # Try to parse from command line / 尝试从命令行解析
        try:
            prices = [float(x) for x in sys.argv[1:] if not x.startswith('--')]
        except ValueError:
            parser.print_help()
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    if len(prices) < 2:
        print("❌ Error: Need at least 2 prices. / 错误: 至少需要 2 个价格。", file=sys.stderr)
        sys.exit(1)
    
    # Calculate / 计算
    returns = calculate_returns(prices)
    if len(returns) < 1:
        print("❌ Error: Could not calculate returns. / 错误: 无法计算收益率。", file=sys.stderr)
        sys.exit(1)
    
    volatility = calculate_volatility(returns, annualized=args.annualized, periods_per_year=args.periods)
    
    # Print results / 打印结果
    if args.verbose:
        print("=" * 80)
        print("VOLATILITY CALCULATION / 波动率计算")
        print("=" * 80)
        print(f"\nPrices / 价格: {prices}")
        print(f"Returns / 收益率: {[f'{r:.6f}' for r in returns]}")
        mean_return = sum(returns) / len(returns)
        print(f"Mean return / 平均收益率: {mean_return:.6f} ({mean_return*100:.4f}%)")
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        print(f"Variance / 方差: {variance:.8f}")
        print(f"Standard deviation / 标准差: {math.sqrt(variance):.6f}")
        if args.annualized:
            print(f"Annualization factor / 年化因子: √{args.periods} = {math.sqrt(args.periods):.4f}")
        print("=" * 80)
    
    # Output result / 输出结果
    print(f"\n{'Annualized ' if args.annualized else ''}Volatility / {'年化 ' if args.annualized else ''}波动率: {volatility:.6f} ({volatility*100:.4f}%)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

