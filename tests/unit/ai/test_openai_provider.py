#!/usr/bin/env python3
"""
Test OpenAI Response / 测试 OpenAI 响应

Display raw response from OpenAI to debug JSON parsing issues
显示 OpenAI 的原始响应以调试 JSON 解析问题
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.ai.evaluation.schemas import MarketContext
from src.ai.evaluation.prompts import StrategyAdvisorPrompt
from src.ai.llm import OpenAIProvider

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

def main():
    """Main function to test OpenAI response"""
    print("=" * 80)
    print("OpenAI Response Test / OpenAI 响应测试")
    print("=" * 80)
    print()
    
    # Create sample market context
    context = create_sample_market_context()
    prompt = StrategyAdvisorPrompt.generate(context)
    
    print("📝 Prompt length:", len(prompt), "characters")
    print()
    
    # Initialize OpenAI provider
    try:
        provider = OpenAIProvider()
        print(f"✅ OpenAI provider initialized: {provider.name}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI provider: {e}")
        return
    
    # Call OpenAI
    print("🚀 Calling OpenAI API...")
    try:
        raw_response = provider.generate(prompt)
        print(f"✅ Received response (length: {len(raw_response)} characters)")
        print()
        print("=" * 80)
        print("Raw Response / 原始响应")
        print("=" * 80)
        print(raw_response)
        print()
        print("=" * 80)
        print("Response Analysis / 响应分析")
        print("=" * 80)
        print(f"Total length: {len(raw_response)} characters")
        print(f"First 200 chars: {raw_response[:200]}")
        print(f"Last 200 chars: {raw_response[-200:]}")
        
        # Check for JSON markers
        if "```" in raw_response:
            print("\n⚠️  Response contains markdown code blocks")
        if "{" in raw_response and "}" in raw_response:
            print("✅ Response contains JSON-like structure")
            # Try to find JSON
            import json
            import re
            # Try to extract JSON
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_response, re.DOTALL)
            if json_match:
                print(f"Found JSON-like structure (length: {len(json_match.group())} chars)")
                try:
                    parsed = json.loads(json_match.group())
                    print("✅ Extracted JSON is valid!")
                    print(f"Keys: {list(parsed.keys())}")
                except json.JSONDecodeError as e:
                    print(f"❌ Extracted JSON is invalid: {e}")
                    print(f"Extracted text: {json_match.group()[:500]}")
        
    except Exception as e:
        print(f"❌ OpenAI API call failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()




