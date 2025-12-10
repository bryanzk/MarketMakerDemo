# Exchange Volatility Calculator Test Guide / 交易所波动率计算器测试指南

## Test Scripts / 测试脚本

### 1. `test_hyperliquid_api_direct.py`

**Purpose / 目的**: Direct API test without project dependencies / 无需项目依赖的直接 API 测试

**Tests / 测试**:
- ✅ Public info endpoint (allMids) / 公共信息端点 (allMids)
- ✅ Candle snapshot endpoint / K 线快照端点
- ✅ Request/response format / 请求/响应格式

**Usage / 用法**:
```bash
# Install dependencies first / 首先安装依赖
pip install requests

# Run test / 运行测试
python3 test_hyperliquid_api_direct.py
```

**Expected Output / 预期输出**:
```
✅ Success! Response keys: ['mid_prices']
✅ Success! Received 60 candles
```

### 2. `test_exchange_volatility.py`

**Purpose / 目的**: Full integration test with project modules / 使用项目模块的完整集成测试

**Tests / 测试**:
- ✅ Module imports / 模块导入
- ✅ Client initialization / 客户端初始化
- ✅ Historical price fetching / 历史价格获取
- ✅ Volatility calculation / 波动率计算

**Usage / 用法**:
```bash
# Install all project dependencies / 安装所有项目依赖
pip install -r requirements.txt

# Run test / 运行测试
python3 test_exchange_volatility.py
```

### 3. `calculate_volatility_from_exchange.py`

**Purpose / 目的**: Production tool for calculating volatility from exchange / 从交易所计算波动率的生产工具

**Usage / 用法**:
```bash
# Install all project dependencies / 安装所有项目依赖
pip install -r requirements.txt

# Basic usage / 基本用法
python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol BTC/USDC:USDC --hours 24

# With verbose output / 详细输出
python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol BTC/USDC:USDC --hours 24 --verbose

# Calculate both 1h and 24h / 计算 1 小时和 24 小时
python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol BTC/USDC:USDC --both
```

## Current Status / 当前状态

### ✅ Completed / 已完成

1. **Script Creation / 脚本创建**:
   - ✅ `calculate_volatility_from_exchange.py` - Main tool / 主工具
   - ✅ `test_hyperliquid_api_direct.py` - Direct API test / 直接 API 测试
   - ✅ `test_exchange_volatility.py` - Integration test / 集成测试

2. **Documentation / 文档**:
   - ✅ Usage guide / 使用指南
   - ✅ Test guide / 测试指南

### ⚠️ Pending / 待处理

1. **Dependencies / 依赖**:
   - ⚠️ Need to install: `requests`, `python-dotenv`, `certifi`
   - ⚠️ 需要安装: `requests`, `python-dotenv`, `certifi`
   - ⚠️ May need: `eth-account`, `hyperliquid-python-sdk`
   - ⚠️ 可能需要: `eth-account`, `hyperliquid-python-sdk`

2. **Testing / 测试**:
   - ⚠️ Need to run tests with dependencies installed / 需要安装依赖后运行测试
   - ⚠️ Verify API connectivity / 验证 API 连接
   - ⚠️ Test with real exchange data / 使用真实交易所数据测试

## Installation Steps / 安装步骤

### Step 1: Install Basic Dependencies / 步骤 1: 安装基本依赖

```bash
pip install requests python-dotenv certifi
```

### Step 2: Install Project Dependencies / 步骤 2: 安装项目依赖

```bash
pip install -r requirements.txt
```

### Step 3: Run Direct API Test / 步骤 3: 运行直接 API 测试

```bash
python3 test_hyperliquid_api_direct.py
```

**Expected / 预期**:
- ✅ Should connect to Hyperliquid testnet API / 应该连接到 Hyperliquid 测试网 API
- ✅ Should fetch allMids data / 应该获取 allMids 数据
- ✅ Should fetch candle snapshot data / 应该获取 K 线快照数据

### Step 4: Run Integration Test / 步骤 4: 运行集成测试

```bash
python3 test_exchange_volatility.py
```

**Expected / 预期**:
- ✅ Should import all modules / 应该导入所有模块
- ✅ Should initialize HyperliquidClient / 应该初始化 HyperliquidClient
- ✅ Should fetch historical prices / 应该获取历史价格
- ✅ Should calculate volatility / 应该计算波动率

### Step 5: Test Production Tool / 步骤 5: 测试生产工具

```bash
python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol BTC/USDC:USDC --hours 1 --verbose
```

**Expected / 预期**:
- ✅ Should connect to exchange / 应该连接到交易所
- ✅ Should fetch 1 hour of data / 应该获取 1 小时数据
- ✅ Should calculate and display volatility / 应该计算并显示波动率

## Troubleshooting / 故障排除

### Issue: "No module named 'dotenv'"

**Solution / 解决方案**:
```bash
pip install python-dotenv
```

### Issue: "No module named 'requests'"

**Solution / 解决方案**:
```bash
pip install requests
```

### Issue: "422 Unprocessable Entity"

**Possible Causes / 可能原因**:
1. Invalid coin name / 无效币种名称
2. Invalid time range / 无效时间范围
3. Unsupported interval / 不支持的间隔

**Solution / 解决方案**:
- Check coin name format (e.g., "BTC" not "BTC/USDC:USDC") / 检查币种名称格式（例如，"BTC" 而不是 "BTC/USDC:USDC"）
- Verify time range is within 5000 candles limit / 验证时间范围在 5000 根 K 线限制内
- Use supported intervals: "1m", "3m", "5m", "15m", "30m", "1h", etc. / 使用支持的间隔: "1m", "3m", "5m", "15m", "30m", "1h" 等

### Issue: "Connection timeout"

**Possible Causes / 可能原因**:
1. Network issue / 网络问题
2. API endpoint down / API 端点不可用
3. Firewall blocking / 防火墙阻止

**Solution / 解决方案**:
- Check internet connection / 检查互联网连接
- Try testnet endpoint / 尝试测试网端点
- Check firewall settings / 检查防火墙设置

## Next Steps / 下一步

1. **Install Dependencies / 安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Tests / 运行测试**:
   ```bash
   python3 test_hyperliquid_api_direct.py
   python3 test_exchange_volatility.py
   ```

3. **Test Production Tool / 测试生产工具**:
   ```bash
   python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol BTC/USDC:USDC --hours 24 --verbose
   ```

4. **Verify Results / 验证结果**:
   - Check if data is fetched successfully / 检查数据是否成功获取
   - Verify volatility calculation / 验证波动率计算
   - Compare with manual calculation / 与手动计算比较


