#!/usr/bin/env python3
"""
Manual Volatility Calculator / 手动波动率计算器

Interactive tool to manually calculate volatility from price data.
从价格数据手动计算波动率的交互式工具。

Usage / 用法:
    python3 manual_volatility_calculator.py
"""

import math
import sys
from typing import List, Tuple


def calculate_returns(prices: List[float]) -> List[float]:
    """
    Calculate returns from price series / 从价格序列计算收益率
    
    Formula: r_t = (P_t - P_{t-1}) / P_{t-1}
    公式: r_t = (P_t - P_{t-1}) / P_{t-1}
    
    Args:
        prices: List of prices in chronological order
        
    Returns:
        List of returns (percentage changes)
    """
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] > 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        else:
            print(f"⚠️  Warning: Zero or negative price at index {i-1}: {prices[i-1]}")
    
    return returns


def calculate_volatility(
    returns: List[float], 
    annualized: bool = False, 
    periods_per_year: int = 365
) -> Tuple[float, dict]:
    """
    Calculate volatility (standard deviation) from returns / 从收益率计算波动率（标准差）
    
    Formula:
    1. Mean return: μ = (1/n) * Σ r_i
    2. Variance: σ² = (1/(n-1)) * Σ (r_i - μ)²
    3. Volatility: σ = √σ²
    4. Annualized: σ_annual = σ * √(periods_per_year)
    
    公式:
    1. 平均收益率: μ = (1/n) * Σ r_i
    2. 方差: σ² = (1/(n-1)) * Σ (r_i - μ)²
    3. 波动率: σ = √σ²
    4. 年化: σ_annual = σ * √(periods_per_year)
    
    Args:
        returns: List of returns (percentage changes)
        annualized: Whether to annualize the volatility
        periods_per_year: Number of periods per year for annualization
        
    Returns:
        Tuple of (volatility, calculation_details)
    """
    if len(returns) < 2:
        return 0.0, {}
    
    n = len(returns)
    
    # Step 1: Calculate mean return / 步骤 1: 计算平均收益率
    mean_return = sum(returns) / n
    
    # Step 2: Calculate variance / 步骤 2: 计算方差
    squared_deviations = [(r - mean_return) ** 2 for r in returns]
    variance = sum(squared_deviations) / (n - 1)  # Sample variance (Bessel's correction)
    
    # Step 3: Calculate standard deviation (volatility) / 步骤 3: 计算标准差（波动率）
    volatility = math.sqrt(variance)
    
    # Step 4: Annualize if requested / 步骤 4: 如果需要，进行年化
    volatility_annualized = volatility * math.sqrt(periods_per_year) if annualized else None
    
    # Prepare detailed calculation / 准备详细计算
    details = {
        "n": n,
        "mean_return": mean_return,
        "squared_deviations": squared_deviations,
        "variance": variance,
        "volatility": volatility,
        "volatility_annualized": volatility_annualized,
        "periods_per_year": periods_per_year if annualized else None,
    }
    
    return volatility, details


def print_calculation_steps(prices: List[float], returns: List[float], details: dict, annualized: bool = False):
    """
    Print detailed calculation steps / 打印详细计算步骤
    """
    print("\n" + "=" * 80)
    print("VOLATILITY CALCULATION STEPS / 波动率计算步骤")
    print("=" * 80)
    
    # Step 1: Prices / 步骤 1: 价格
    print("\n📊 Step 1: Price Data / 价格数据")
    print("-" * 80)
    print(f"Number of prices: {len(prices)}")
    print(f"价格数量: {len(prices)}")
    print("\nPrice series / 价格序列:")
    for i, price in enumerate(prices):
        print(f"  P_{i} = {price:.4f}")
    
    # Step 2: Returns / 步骤 2: 收益率
    print("\n📈 Step 2: Calculate Returns / 计算收益率")
    print("-" * 80)
    print("Formula: r_t = (P_t - P_{t-1}) / P_{t-1}")
    print("公式: r_t = (P_t - P_{t-1}) / P_{t-1}")
    print("\nReturns / 收益率:")
    for i, ret in enumerate(returns):
        if i + 1 < len(prices):
            print(f"  r_{i+1} = (P_{i+1} - P_{i}) / P_{i} = ({prices[i+1]:.4f} - {prices[i]:.4f}) / {prices[i]:.4f} = {ret:.6f} ({ret*100:.4f}%)")
    
    # Step 3: Mean Return / 步骤 3: 平均收益率
    print("\n📊 Step 3: Calculate Mean Return / 计算平均收益率")
    print("-" * 80)
    print(f"Formula: μ = (1/n) * Σ r_i")
    print(f"公式: μ = (1/n) * Σ r_i")
    print(f"\nμ = (1/{details['n']}) * ({' + '.join([f'{r:.6f}' for r in returns])})")
    print(f"μ = {details['mean_return']:.6f} ({details['mean_return']*100:.4f}%)")
    
    # Step 4: Variance / 步骤 4: 方差
    print("\n📊 Step 4: Calculate Variance / 计算方差")
    print("-" * 80)
    print(f"Formula: σ² = (1/(n-1)) * Σ (r_i - μ)²")
    print(f"公式: σ² = (1/(n-1)) * Σ (r_i - μ)²")
    print("\nSquared deviations / 平方偏差:")
    for i, (ret, sq_dev) in enumerate(zip(returns, details['squared_deviations'])):
        print(f"  (r_{i+1} - μ)² = ({ret:.6f} - {details['mean_return']:.6f})² = {sq_dev:.8f}")
    
    sum_sq_dev = sum(details['squared_deviations'])
    print(f"\nΣ (r_i - μ)² = {sum_sq_dev:.8f}")
    print(f"σ² = (1/({details['n']}-1)) * {sum_sq_dev:.8f} = {details['variance']:.8f}")
    
    # Step 5: Volatility / 步骤 5: 波动率
    print("\n📊 Step 5: Calculate Volatility (Standard Deviation) / 计算波动率（标准差）")
    print("-" * 80)
    print(f"Formula: σ = √σ²")
    print(f"公式: σ = √σ²")
    print(f"σ = √{details['variance']:.8f} = {details['volatility']:.6f} ({details['volatility']*100:.4f}%)")
    
    # Step 6: Annualized (if requested) / 步骤 6: 年化（如果需要）
    if annualized and details['volatility_annualized']:
        print("\n📊 Step 6: Annualize Volatility / 年化波动率")
        print("-" * 80)
        print(f"Formula: σ_annual = σ * √(periods_per_year)")
        print(f"公式: σ_annual = σ * √(periods_per_year)")
        print(f"σ_annual = {details['volatility']:.6f} * √{details['periods_per_year']} = {details['volatility_annualized']:.6f} ({details['volatility_annualized']*100:.4f}%)")
    
    print("\n" + "=" * 80)


def interactive_calculator():
    """
    Interactive volatility calculator / 交互式波动率计算器
    """
    print("=" * 80)
    print("MANUAL VOLATILITY CALCULATOR / 手动波动率计算器")
    print("=" * 80)
    print("\nThis tool helps you manually calculate volatility from price data.")
    print("此工具帮助您从价格数据手动计算波动率。")
    
    # Get input method / 获取输入方法
    print("\n📝 Input Method / 输入方法:")
    print("1. Enter prices manually / 手动输入价格")
    print("2. Use example data / 使用示例数据")
    print("3. Exit / 退出")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == "3":
        print("Goodbye! / 再见！")
        return
    
    # Get prices / 获取价格
    if choice == "2":
        # Example data / 示例数据
        prices = [100.0, 101.5, 99.8, 102.3, 101.0, 103.5, 102.0, 104.2, 103.8, 105.0]
        print(f"\n✅ Using example prices / 使用示例价格:")
        print(f"   {prices}")
    else:
        # Manual input / 手动输入
        print("\n📝 Enter prices (comma-separated or one per line, empty line to finish):")
        print("输入价格（逗号分隔或每行一个，空行结束）:")
        prices_input = []
        while True:
            line = input().strip()
            if not line:
                break
            # Try to parse as comma-separated or single value
            # 尝试解析为逗号分隔或单个值
            if ',' in line:
                prices_input.extend([float(x.strip()) for x in line.split(',')])
            else:
                try:
                    prices_input.append(float(line))
                except ValueError:
                    print(f"⚠️  Invalid input: {line}. Skipping. / 无效输入: {line}。跳过。")
        
        if len(prices_input) < 2:
            print("❌ Error: Need at least 2 prices. / 错误: 至少需要 2 个价格。")
            return
        
        prices = prices_input
    
    # Calculate returns / 计算收益率
    returns = calculate_returns(prices)
    
    if len(returns) < 1:
        print("❌ Error: Could not calculate returns. / 错误: 无法计算收益率。")
        return
    
    # Ask for annualization / 询问是否年化
    print("\n📊 Annualization / 年化:")
    annualize_choice = input("Annualize volatility? (y/n, default: n): ").strip().lower()
    annualized = annualize_choice == 'y'
    
    periods_per_year = 365
    if annualized:
        period_choice = input("Periods per year (default: 365 for daily, 8760 for hourly): ").strip()
        if period_choice:
            try:
                periods_per_year = int(period_choice)
            except ValueError:
                print(f"⚠️  Invalid input. Using default: {periods_per_year}")
    
    # Calculate volatility / 计算波动率
    volatility, details = calculate_volatility(returns, annualized=annualized, periods_per_year=periods_per_year)
    
    # Print results / 打印结果
    print_calculation_steps(prices, returns, details, annualized=annualized)
    
    # Summary / 摘要
    print("\n" + "=" * 80)
    print("SUMMARY / 摘要")
    print("=" * 80)
    print(f"Number of prices: {len(prices)}")
    print(f"价格数量: {len(prices)}")
    print(f"Number of returns: {len(returns)}")
    print(f"收益率数量: {len(returns)}")
    print(f"\nMean return: {details['mean_return']:.6f} ({details['mean_return']*100:.4f}%)")
    print(f"平均收益率: {details['mean_return']:.6f} ({details['mean_return']*100:.4f}%)")
    print(f"Variance: {details['variance']:.8f}")
    print(f"方差: {details['variance']:.8f}")
    print(f"\n{'Annualized ' if annualized else ''}Volatility: {details['volatility_annualized'] if annualized else details['volatility']:.6f} ({(details['volatility_annualized'] if annualized else details['volatility'])*100:.4f}%)")
    print(f"{'年化 ' if annualized else ''}波动率: {details['volatility_annualized'] if annualized else details['volatility']:.6f} ({(details['volatility_annualized'] if annualized else details['volatility'])*100:.4f}%)")
    print("=" * 80)
    
    # Ask if user wants to calculate again / 询问用户是否要再次计算
    again = input("\nCalculate again? (y/n): ").strip().lower()
    if again == 'y':
        interactive_calculator()


if __name__ == "__main__":
    try:
        interactive_calculator()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye! / 用户中断。再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


