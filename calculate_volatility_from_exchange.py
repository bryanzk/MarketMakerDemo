#!/usr/bin/env python3
"""
Volatility Calculator from Exchange Data / 从交易所数据计算波动率

Fetch historical prices from exchange and calculate volatility.
从交易所获取历史价格并计算波动率。

Usage / 用法:
    python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol BTC/USDC:USDC --hours 24
    python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol ETH/USDC:USDC --hours 1 --interval 5
"""

import argparse
import os
import sys
from typing import Optional

# Add project root to path / 将项目根目录添加到路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.trading.volatility import (
        calculate_volatility_1h_24h,
        fetch_and_calculate_volatility,
        VolatilityCalculator,
    )
    from src.trading.hyperliquid_client import HyperliquidClient
    from src.trading.exchange import get_exchange_by_name
except ImportError as e:
    print(f"❌ Error importing modules: {e}", file=sys.stderr)
    print("Make sure you're running from the project root directory.", file=sys.stderr)
    print("确保从项目根目录运行。", file=sys.stderr)
    sys.exit(1)


def get_exchange_client(exchange_name: str, symbol: str):
    """
    Get exchange client instance / 获取交易所客户端实例
    
    Args:
        exchange_name: Exchange name (e.g., "hyperliquid")
        symbol: Trading symbol
        
    Returns:
        Exchange client instance
    """
    exchange_name_lower = exchange_name.lower()
    
    if exchange_name_lower == "hyperliquid":
        # Initialize HyperliquidClient / 初始化 HyperliquidClient
        client = HyperliquidClient(symbol=symbol)
        return client
    else:
        # Try to get from exchange factory / 尝试从交易所工厂获取
        exchange = get_exchange_by_name(exchange_name_lower)
        if exchange:
            return exchange
        else:
            raise ValueError(f"Unsupported exchange: {exchange_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate volatility from exchange data / 从交易所数据计算波动率",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / 示例:
  %(prog)s --exchange hyperliquid --symbol BTC/USDC:USDC --hours 24
  %(prog)s --exchange hyperliquid --symbol ETH/USDC:USDC --hours 1 --interval 5
  %(prog)s --exchange hyperliquid --symbol SOL/USDC:USDC --hours 24 --annualized
        """
    )
    
    parser.add_argument(
        '--exchange',
        type=str,
        required=True,
        help='Exchange name (e.g., "hyperliquid") / 交易所名称（例如："hyperliquid"）'
    )
    
    parser.add_argument(
        '--symbol',
        type=str,
        required=True,
        help='Trading symbol (e.g., "BTC/USDC:USDC") / 交易对（例如："BTC/USDC:USDC"）'
    )
    
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Number of hours of history to fetch (default: 24) / 获取历史数据的小时数（默认: 24）'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=1,
        help='Interval between price points in minutes (default: 1) / 价格点之间的间隔（分钟）（默认: 1）'
    )
    
    parser.add_argument(
        '--annualized',
        action='store_true',
        help='Annualize volatility / 年化波动率'
    )
    
    parser.add_argument(
        '--periods',
        type=int,
        default=8760,
        help='Periods per year for annualization (default: 8760 for hourly) / 年化周期数（默认: 8760 用于小时数据）'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed information / 显示详细信息'
    )
    
    parser.add_argument(
        '--both',
        action='store_true',
        help='Calculate both 1h and 24h volatility / 计算 1 小时和 24 小时波动率'
    )
    
    args = parser.parse_args()
    
    try:
        # Get exchange client / 获取交易所客户端
        if args.verbose:
            print(f"🔌 Connecting to {args.exchange}...")
            print(f"🔌 连接到 {args.exchange}...")
        
        exchange = get_exchange_client(args.exchange, args.symbol)
        
        if args.verbose:
            print(f"✅ Connected to {args.exchange}")
            print(f"✅ 已连接到 {args.exchange}")
            print(f"📊 Symbol: {args.symbol}")
            print(f"📊 交易对: {args.symbol}")
        
        # Calculate volatility / 计算波动率
        if args.both:
            # Calculate both 1h and 24h / 计算 1 小时和 24 小时
            calculator = VolatilityCalculator(cache_ttl=300)
            volatility_1h, volatility_24h = calculate_volatility_1h_24h(
                exchange, args.symbol, calculator=calculator
            )
            
            print("\n" + "=" * 80)
            print("VOLATILITY RESULTS / 波动率结果")
            print("=" * 80)
            print(f"\n1-hour volatility / 1 小时波动率: {volatility_1h:.6f} ({volatility_1h*100:.4f}%)")
            print(f"24-hour volatility / 24 小时波动率: {volatility_24h:.6f} ({volatility_24h*100:.4f}%)")
            
            if args.annualized:
                periods_1h = 24 * 365  # Hourly periods per year
                periods_24h = 1 * 365   # Daily periods per year
                vol_1h_annual = volatility_1h * (periods_1h ** 0.5)
                vol_24h_annual = volatility_24h * (periods_24h ** 0.5)
                print(f"\n1-hour annualized / 1 小时年化: {vol_1h_annual:.6f} ({vol_1h_annual*100:.4f}%)")
                print(f"24-hour annualized / 24 小时年化: {vol_24h_annual:.6f} ({vol_24h_annual*100:.4f}%)")
            
            print("=" * 80)
        else:
            # Calculate single volatility / 计算单个波动率
            calculator = VolatilityCalculator(cache_ttl=300)
            volatility = fetch_and_calculate_volatility(
                exchange, args.symbol, hours=args.hours, default=0.02, calculator=calculator
            )
            
            print("\n" + "=" * 80)
            print("VOLATILITY RESULT / 波动率结果")
            print("=" * 80)
            print(f"\nSymbol / 交易对: {args.symbol}")
            print(f"Exchange / 交易所: {args.exchange}")
            print(f"Hours / 小时数: {args.hours}")
            print(f"Interval / 间隔: {args.interval} minutes / 分钟")
            print(f"\nVolatility / 波动率: {volatility:.6f} ({volatility*100:.4f}%)")
            
            if args.annualized:
                volatility_annualized = volatility * (args.periods ** 0.5)
                print(f"Annualized volatility / 年化波动率: {volatility_annualized:.6f} ({volatility_annualized*100:.4f}%)")
                print(f"(Using {args.periods} periods per year / 使用每年 {args.periods} 个周期)")
            
            print("=" * 80)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye! / 用户中断。再见！")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

