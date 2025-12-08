#!/usr/bin/env python3
"""
Manual LLM Evaluation Test Script / 手动 LLM 评估测试脚本

Run evaluation with all available LLM providers and display scoring results
运行所有可用 LLM providers 的评估并显示打分结果
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ai.evaluation.schemas import MarketContext
from src.ai.evaluation.evaluator import MultiLLMEvaluator
from src.ai.llm import create_all_providers


def create_sample_market_context() -> MarketContext:
    """Create sample market context for testing"""
    return MarketContext(
        symbol="ETHUSDT",
        mid_price=2500.0,
        best_bid=2499.5,
        best_ask=2500.5,
        spread_bps=4.0,
        volatility_24h=0.035,
        volatility_1h=0.012,
        funding_rate=0.0001,
        funding_rate_trend="rising",
        current_position=0.0,
        position_side="neutral",
        unrealized_pnl=0.0,
        available_balance=10000.0,
        current_leverage=1.0,
        win_rate=0.52,
        sharpe_ratio=1.2,
        recent_pnl=100.0,
    )


def format_result(result) -> str:
    """Format evaluation result for display"""
    proposal = result.proposal
    simulation = result.simulation
    
    status = "✅ Success" if proposal.parse_success else "❌ Failed"
    if not proposal.parse_success:
        error_info = f"\n   Error: {proposal.parse_error}" if proposal.parse_error else ""
        return f"""
{result.provider_name} - {status}
   Rank: {result.rank}
   Score: {result.score:.2f}
   Latency: {result.latency_ms:.0f}ms{error_info}
"""
    
    return f"""
{result.provider_name} - {status}
   Rank: {result.rank}
   Score: {result.score:.2f}
   Latency: {result.latency_ms:.0f}ms
   
   Strategy: {proposal.recommended_strategy}
   Spread: {proposal.spread:.4f} ({proposal.spread * 10000:.2f} bps)
   Skew Factor: {proposal.skew_factor:.0f}
   Quantity: {proposal.quantity:.2f}
   Leverage: {proposal.leverage:.1f}x
   Confidence: {proposal.confidence:.1%}
   
   Simulation Results:
   - PnL: ${simulation.realized_pnl:,.2f}
   - Win Rate: {simulation.win_rate:.1%}
   - Sharpe Ratio: {simulation.sharpe_ratio:.2f}
   - Max Drawdown: {simulation.max_drawdown:.2%}
   
   Reasoning: {proposal.reasoning[:100]}...
"""


def main():
    """Main function to run evaluation"""
    print("=" * 80)
    print("Multi-LLM Evaluation Test / 多 LLM 评估测试")
    print("=" * 80)
    print()
    
    # Create sample market context
    print("📊 Creating sample market context...")
    context = create_sample_market_context()
    print(f"   Symbol: {context.symbol}")
    print(f"   Mid Price: ${context.mid_price:,.2f}")
    print(f"   Spread: {context.spread_bps:.2f} bps")
    print(f"   Funding Rate: {context.funding_rate:.4%}")
    print()
    
    # Get all available providers
    print("🔌 Initializing LLM providers...")
    try:
        providers = create_all_providers()
        print(f"   ✅ Found {len(providers)} provider(s):")
        for p in providers:
            print(f"      - {p.name}")
        print()
    except Exception as e:
        print(f"   ❌ Failed to initialize providers: {e}")
        return
    
    if not providers:
        print("   ❌ No providers available. Please check your API keys.")
        return
    
    # Create evaluator
    print("🚀 Starting evaluation...")
    evaluator = MultiLLMEvaluator(
        providers=providers,
        simulation_steps=500,
        parallel=True,
    )
    
    # Run evaluation
    try:
        print("   Running evaluation (this may take a while)...")
        results = evaluator.evaluate(context)
        print(f"   ✅ Evaluation completed with {len(results)} result(s)")
        print()
    except Exception as e:
        print(f"   ❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("=" * 80)
    print("Evaluation Results / 评估结果")
    print("=" * 80)
    
    for result in results:
        print(format_result(result))
        print("-" * 80)
    
    # Display summary
    print()
    print("=" * 80)
    print("Summary / 摘要")
    print("=" * 80)
    
    successful = [r for r in results if r.proposal.parse_success]
    failed = [r for r in results if not r.proposal.parse_success]
    
    print(f"Total Providers: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print()
    
    if successful:
        print("Ranking (by score):")
        for i, result in enumerate(successful, 1):
            print(f"  {i}. {result.provider_name}: Score {result.score:.2f}")
    
    if failed:
        print("\nFailed Providers:")
        for result in failed:
            error = result.proposal.parse_error or "Unknown error"
            print(f"  - {result.provider_name}: {error}")
    
    # Aggregate results if we have successful ones
    if len(successful) > 1:
        print()
        print("=" * 80)
        print("Aggregated Results / 聚合结果")
        print("=" * 80)
        try:
            aggregated = evaluator.aggregate_results(results)
            print(f"Consensus Strategy: {aggregated.strategy_consensus.consensus_strategy}")
            print(f"Consensus Level: {aggregated.strategy_consensus.consensus_level}")
            print(f"Consensus Confidence: {aggregated.consensus_confidence:.1%}")
            print()
            print("Average Performance:")
            print(f"  - Avg PnL: ${aggregated.avg_pnl:,.2f}")
            print(f"  - Avg Win Rate: {aggregated.avg_win_rate:.1%}")
            print(f"  - Avg Sharpe: {aggregated.avg_sharpe:.2f}")
            print(f"  - Avg Latency: {aggregated.avg_latency_ms:.0f}ms")
        except Exception as e:
            print(f"Failed to aggregate results: {e}")


if __name__ == "__main__":
    main()

