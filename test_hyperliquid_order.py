#!/usr/bin/env python3
"""
Test script to place an order on Hyperliquid testnet
向 Hyperliquid testnet 发送订单的测试脚本

Usage / 用法:
    python test_hyperliquid_order.py
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables / 加载环境变量
load_dotenv()

# Add src to path / 添加 src 到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.trading.hyperliquid_client import HyperliquidClient

def test_place_order():
    """Test placing an order on Hyperliquid testnet / 测试在 Hyperliquid testnet 上下单"""
    
    print("=" * 60)
    print("Hyperliquid Testnet Order Placement Test")
    print("Hyperliquid 测试网订单下单测试")
    print("=" * 60)
    
    # Check environment variables / 检查环境变量
    # Support both old and new variable names / 支持新旧变量名
    wallet_address = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
    api_key = os.getenv("HYPERLIQUID_API_KEY") or wallet_address
    api_secret = os.getenv("HYPERLIQUID_API_SECRET")
    testnet = os.getenv("HYPERLIQUID_TESTNET", "true").lower() == "true"
    
    if not api_secret:
        print("❌ Error: HYPERLIQUID_API_SECRET must be set")
        print("❌ 错误：必须设置 HYPERLIQUID_API_SECRET")
        return False
    
    if not api_key and not wallet_address:
        print("❌ Error: HYPERLIQUID_WALLET_ADDRESS or HYPERLIQUID_API_KEY must be set")
        print("❌ 错误：必须设置 HYPERLIQUID_WALLET_ADDRESS 或 HYPERLIQUID_API_KEY")
        return False
    
        print(f"\n📋 Configuration / 配置:")
        if wallet_address:
            print(f"  Wallet Address: {wallet_address}")
            print(f"  (from HYPERLIQUID_WALLET_ADDRESS)")
        if api_key:
            print(f"  API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
        print(f"  API Secret: {'*' * 20}...{api_secret[-10:] if len(api_secret) > 30 else '*' * 10}")
        print(f"  Testnet: {testnet}")
        print(f"  Base URL: {'https://api.hyperliquid-testnet.xyz' if testnet else 'https://api.hyperliquid.xyz'}")
        
        # Show expected account address / 显示期望的账户地址
        expected_address = "0x662097117457B21F935E187cAff2d4E30D708627"
        print(f"\n📌 Expected Account Address / 期望的账户地址:")
        print(f"  {expected_address}")
    
    try:
        # Initialize client / 初始化客户端
        print("\n🔌 Initializing Hyperliquid client...")
        print("🔌 正在初始化 Hyperliquid 客户端...")
        client = HyperliquidClient(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True,  # Force testnet / 强制使用测试网
            symbol="ETH/USDT:USDT"
        )
        
        print(f"✅ Client initialized successfully")
        print(f"✅ 客户端初始化成功")
        print(f"  - Connected: {client.is_connected}")
        print(f"  - Symbol: {client.symbol}")
        print(f"  - Account initialized: {client._account is not None}")
        if client._account:
            account_addr = client._account.address
            expected_addr = "0x662097117457B21F935E187cAff2d4E30D708627"
            print(f"  - Account address: {account_addr}")
            print(f"  - Expected address: {expected_addr}")
            if account_addr.lower() != expected_addr.lower():
                print(f"  ⚠️  WARNING: Address mismatch!")
                print(f"  ⚠️  警告：地址不匹配！")
                print(f"     The account address from private key doesn't match the expected address.")
                print(f"     从私钥派生的账户地址与期望的地址不匹配。")
                print(f"     Make sure HYPERLIQUID_API_SECRET matches the private key for {expected_addr}")
                print(f"     确保 HYPERLIQUID_API_SECRET 与 {expected_addr} 的私钥匹配")
            else:
                print(f"  ✅ Address matches expected address")
                print(f"  ✅ 地址与期望地址匹配")
        
        # Fetch meta data to get asset index / 获取 meta 数据以获取资产索引
        print("\n📊 Fetching meta data...")
        print("📊 正在获取 meta 数据...")
        meta_data = client._fetch_meta_data()
        if meta_data:
            universe_size = len(meta_data.get("universe", []))
            spot_size = len(meta_data.get("spotMeta", {}).get("universe", [])) if meta_data.get("spotMeta") else 0
            print(f"✅ Meta data fetched:")
            print(f"✅ Meta 数据已获取:")
            print(f"  - Perpetual universe size: {universe_size}")
            print(f"  - Spot universe size: {spot_size}")
            print(f"  - Asset index map size: {len(client._asset_index_map)}")
        
        # Get asset index for ETH / 获取 ETH 的资产索引
        eth_asset_index = client._get_asset_index("ETH")
        print(f"\n📈 Asset Index for ETH: {eth_asset_index}")
        print(f"📈 ETH 的资产索引: {eth_asset_index}")
        
        if eth_asset_index is None:
            print("⚠️  Warning: Could not get asset index for ETH. Order may fail.")
            print("⚠️  警告：无法获取 ETH 的资产索引。订单可能会失败。")
        
        # Fetch current market price / 获取当前市场价格
        print("\n💰 Fetching current market price...")
        print("💰 正在获取当前市场价格...")
        market_data = client.fetch_market_data()
        if market_data and market_data.get("mid_price"):
            mid_price = market_data["mid_price"]
            print(f"✅ Current mid price: ${mid_price:.2f}")
            print(f"✅ 当前中间价: ${mid_price:.2f}")
        else:
            print("⚠️  Could not fetch market price. Using default.")
            print("⚠️  无法获取市场价格。使用默认值。")
            mid_price = 3000.0
        
        # Calculate order parameters / 计算订单参数
        # Use a small order size to ensure it meets minimum $10 requirement
        # 使用小订单数量以确保满足最小 $10 要求
        order_value_usd = 20.0  # $20 order to be safe / $20 订单以确保安全
        quantity = order_value_usd / mid_price
        # Round to 4 decimal places / 四舍五入到 4 位小数
        quantity = round(quantity, 4)
        
        # Set price slightly below market for limit order / 限价单价格略低于市场价格
        limit_price = mid_price * 0.99  # 1% below market / 低于市场 1%
        limit_price = round(limit_price, 2)
        
        print(f"\n📝 Order Details / 订单详情:")
        print(f"  Side: BUY")
        print(f"  Type: LIMIT")
        print(f"  Symbol: ETH")
        print(f"  Asset Index: {eth_asset_index}")
        print(f"  Quantity: {quantity} ETH")
        print(f"  Price: ${limit_price:.2f}")
        print(f"  Order Value: ${quantity * limit_price:.2f} USD")
        print(f"  Min Order Value: $10.00 USD")
        
        # Validate order value / 验证订单价值
        if quantity * limit_price < 10.0:
            print(f"\n❌ Error: Order value ${quantity * limit_price:.2f} is below minimum $10.00")
            print(f"❌ 错误：订单价值 ${quantity * limit_price:.2f} 低于最小值 $10.00")
            return False
        
        # Build order / 构建订单
        order = {
            "side": "buy",
            "type": "limit",
            "price": limit_price,
            "quantity": quantity,
        }
        
        # Validate order / 验证订单
        print("\n🔍 Validating order...")
        print("🔍 正在验证订单...")
        validation_error = client._validate_order(order)
        if validation_error:
            print(f"❌ Validation failed: {validation_error}")
            print(f"❌ 验证失败: {validation_error}")
            return False
        
        print("✅ Order validation passed")
        print("✅ 订单验证通过")
        
        # Build order payload / 构建订单负载
        print("\n📦 Building order payload...")
        print("📦 正在构建订单负载...")
        payload = client._build_order_payload(order)
        
        print(f"✅ Order payload built:")
        print(f"✅ 订单负载已构建:")
        print(f"  - Action type: {payload.get('action', {}).get('type')}")
        print(f"  - Orders count: {len(payload.get('action', {}).get('orders', []))}")
        print(f"  - Nonce: {payload.get('nonce')}")
        print(f"  - Has signature: {'signature' in payload and payload['signature'] is not None}")
        if 'signature' in payload and payload['signature']:
            sig = payload['signature']
            print(f"  - Signature type: {'real' if client._account else 'placeholder'}")
            if isinstance(sig, dict):
                print(f"  - Signature r: {sig.get('r', 'N/A')[:30]}...")
                print(f"  - Signature s: {sig.get('s', 'N/A')[:30]}...")
                print(f"  - Signature v: {sig.get('v', 'N/A')}")
        
        # Show order details from payload / 显示负载中的订单详情
        if payload.get('action', {}).get('orders'):
            order_obj = payload['action']['orders'][0]
            print(f"\n📋 Order object in payload:")
            print(f"📋 负载中的订单对象:")
            print(f"  - a (asset): {order_obj.get('a')}")
            print(f"  - b (isBuy): {order_obj.get('b')}")
            print(f"  - s (size): {order_obj.get('s')}")
            print(f"  - p (price): {order_obj.get('p', 'N/A')}")
            print(f"  - r (reduceOnly): {order_obj.get('r')}")
            print(f"  - t (type): {order_obj.get('t')}")
        
        # Ask for confirmation / 请求确认
        print("\n" + "=" * 60)
        print("⚠️  READY TO PLACE ORDER / 准备下单")
        print("=" * 60)
        print(f"This will place a BUY limit order for {quantity} ETH at ${limit_price:.2f}")
        print(f"这将下一个买入限价单：{quantity} ETH @ ${limit_price:.2f}")
        print(f"\nOrder value: ${quantity * limit_price:.2f} USD")
        print(f"订单价值: ${quantity * limit_price:.2f} USD")
        
        # Check for --auto flag / 检查 --auto 标志
        auto_mode = '--auto' in sys.argv or '-y' in sys.argv
        if not auto_mode:
            try:
                response = input("\nProceed? (yes/no): ")
                if response.lower() not in ['yes', 'y', '是']:
                    print("❌ Order placement cancelled")
                    print("❌ 订单下单已取消")
                    return False
            except EOFError:
                print("\n⚠️  No input available. Use --auto flag for non-interactive mode.")
                print("⚠️  无输入可用。使用 --auto 标志进行非交互模式。")
                print("Skipping order placement...")
                print("跳过订单下单...")
                return False
        else:
            print("\n✅ Auto mode enabled. Proceeding with order placement...")
            print("✅ 自动模式已启用。继续下单...")
        
        # Place order / 下单
        print("\n🚀 Placing order...")
        print("🚀 正在下单...")
        orders = [order]
        result = client.place_orders(orders)
        
        if result and len(result) > 0:
            order_result = result[0]
            print("\n✅ Order placed successfully!")
            print("✅ 订单下单成功!")
            print(f"  Order ID: {order_result.get('order_id', 'N/A')}")
            print(f"  Status: {order_result.get('status', 'N/A')}")
            print(f"  Symbol: {order_result.get('symbol', 'N/A')}")
            print(f"  Side: {order_result.get('side', 'N/A')}")
            print(f"  Quantity: {order_result.get('quantity', 'N/A')}")
            print(f"  Price: {order_result.get('price', 'N/A')}")
            return True
        else:
            print("\n❌ Order placement failed")
            print("❌ 订单下单失败")
            
            # Check for errors / 检查错误
            if client.last_order_error:
                print(f"\nError details / 错误详情:")
                print(f"  Type: {client.last_order_error.get('type', 'N/A')}")
                print(f"  Message: {client.last_order_error.get('message', 'N/A')}")
            
            if client.last_api_error:
                print(f"\nAPI error / API 错误:")
                print(f"  Type: {client.last_api_error.get('type', 'N/A')}")
                print(f"  Status code: {client.last_api_error.get('status_code', 'N/A')}")
                print(f"  Error detail: {client.last_api_error.get('error_detail', 'N/A')[:200]}")
                if client.last_api_error.get('response_body'):
                    print(f"  Response body: {client.last_api_error.get('response_body')[:300]}")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"❌ 错误: {e}")
        
        # Check for common errors / 检查常见错误
        error_str = str(e).lower()
        if "does not exist" in error_str or "user" in error_str:
            print("\n💡 Note / 提示:")
            print("  This error usually means the account address needs to be created on Hyperliquid.")
            print("  此错误通常意味着账户地址需要在 Hyperliquid 上创建。")
            print("  For testnet, you may need to:")
            print("  对于测试网，您可能需要：")
            print("  1. Visit https://app.hyperliquid-testnet.xyz and connect your wallet")
            print("  1. 访问 https://app.hyperliquid-testnet.xyz 并连接您的钱包")
            print("  2. Create an account on the testnet")
            print("  2. 在测试网上创建账户")
            print(f"  3. Ensure HYPERLIQUID_API_KEY matches your wallet address")
            print(f"  3. 确保 HYPERLIQUID_API_KEY 与您的钱包地址匹配")
            if client._account:
                print(f"\n  Current account address: {client._account.address}")
                print(f"  当前账户地址: {client._account.address}")
        
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_place_order()
    sys.exit(0 if success else 1)

