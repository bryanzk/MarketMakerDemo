# Manual Volatility Calculator / 手动波动率计算器

Tools for manually calculating volatility from price data.
从价格数据手动计算波动率的工具。

## Tools / 工具

### 1. Interactive Calculator / 交互式计算器

**File**: `manual_volatility_calculator.py`

Interactive tool with step-by-step calculation display.
交互式工具，显示逐步计算过程。

**⚠️ Note**: This tool does NOT fetch data from exchanges. It only accepts manual input.
**⚠️ 注意**: 此工具不从交易所获取数据，仅接受手动输入。

**Usage / 用法**:
```bash
python3 manual_volatility_calculator.py
```

**Features / 功能**:
- ✅ Step-by-step calculation display / 逐步计算显示
- ✅ Manual price input or example data / 手动输入价格或使用示例数据
- ✅ Optional annualization / 可选年化
- ✅ Detailed formula explanations / 详细公式说明
- ❌ Does NOT fetch from exchange / 不从交易所获取数据

**Example / 示例**:
```
Select option (1/2/3): 2
✅ Using example prices / 使用示例价格:
   [100.0, 101.5, 99.8, 102.3, 101.0, 103.5, 102.0, 104.2, 103.8, 105.0]

📊 Annualization / 年化:
Annualize volatility? (y/n, default: n): n
```

### 2. Command Line Calculator / 命令行计算器

**File**: `calculate_volatility.py`

Quick command-line tool for calculating volatility.
快速命令行波动率计算工具。

**⚠️ Note**: This tool does NOT fetch data from exchanges. It only accepts command-line input.
**⚠️ 注意**: 此工具不从交易所获取数据，仅接受命令行输入。

**Usage / 用法**:

```bash
# Basic usage / 基本用法
python3 calculate_volatility.py 100 101.5 99.8 102.3 101.0

# Comma-separated prices / 逗号分隔价格
python3 calculate_volatility.py --prices 100,101.5,99.8,102.3,101.0

# With verbose output / 详细输出
python3 calculate_volatility.py 100 101.5 99.8 102.3 101.0 --verbose

# Annualized volatility / 年化波动率
python3 calculate_volatility.py 100 101.5 99.8 102.3 101.0 --annualized --periods 365
```

**Options / 选项**:
- `--prices`: Comma-separated price values / 逗号分隔的价格值
- `--annualized`: Annualize the volatility / 年化波动率
- `--periods`: Periods per year for annualization (default: 365) / 年化周期数（默认: 365）
- `--verbose`: Show detailed calculation steps / 显示详细计算步骤

**Example Output / 示例输出**:
```
Volatility / 波动率: 0.017505 (1.7505%)
```

### 3. Exchange Data Calculator / 交易所数据计算器

**File**: `calculate_volatility_from_exchange.py`

Fetch historical prices from exchange and calculate volatility.
从交易所获取历史价格并计算波动率。

**✅ Note**: This tool DOES fetch real data from exchanges.
**✅ 注意**: 此工具从交易所获取实际数据。

**Usage / 用法**:

```bash
# Basic usage / 基本用法
python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol BTC/USDC:USDC --hours 24

# With custom interval / 自定义间隔
python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol ETH/USDC:USDC --hours 1 --interval 5

# Calculate both 1h and 24h / 计算 1 小时和 24 小时
python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol SOL/USDC:USDC --both

# With verbose output / 详细输出
python3 calculate_volatility_from_exchange.py --exchange hyperliquid --symbol BTC/USDC:USDC --hours 24 --verbose
```

**Options / 选项**:
- `--exchange`: Exchange name (e.g., "hyperliquid") / 交易所名称（例如："hyperliquid"）
- `--symbol`: Trading symbol (e.g., "BTC/USDC:USDC") / 交易对（例如："BTC/USDC:USDC"）
- `--hours`: Number of hours of history to fetch (default: 24) / 获取历史数据的小时数（默认: 24）
- `--interval`: Interval between price points in minutes (default: 1) / 价格点之间的间隔（分钟）（默认: 1）
- `--annualized`: Annualize volatility / 年化波动率
- `--periods`: Periods per year for annualization (default: 8760 for hourly) / 年化周期数（默认: 8760 用于小时数据）
- `--verbose`: Show detailed information / 显示详细信息
- `--both`: Calculate both 1h and 24h volatility / 计算 1 小时和 24 小时波动率

**Example Output / 示例输出**:
```
================================================================================
VOLATILITY RESULT / 波动率结果
================================================================================

Symbol / 交易对: BTC/USDC:USDC
Exchange / 交易所: hyperliquid
Hours / 小时数: 24
Interval / 间隔: 1 minutes / 分钟

Volatility / 波动率: 0.023456 (2.3456%)
================================================================================
```

**Requirements / 要求**:
- Exchange API credentials configured (if needed) / 交易所 API 凭证已配置（如需要）
- Network connection to exchange / 到交易所的网络连接
- Exchange client initialized / 交易所客户端已初始化

## Tool Comparison / 工具对比

| Feature / 功能 | Manual Calculator | CLI Calculator | Exchange Calculator |
|---------------|-------------------|----------------|---------------------|
| Fetch from exchange / 从交易所获取 | ❌ | ❌ | ✅ |
| Manual input / 手动输入 | ✅ | ✅ | ❌ |
| Step-by-step display / 逐步显示 | ✅ | Optional / 可选 | ❌ |
| Real-time data / 实时数据 | ❌ | ❌ | ✅ |
| Use case / 使用场景 | Learning / 学习 | Quick calc / 快速计算 | Production / 生产环境 |

## Calculation Formula / 计算公式

### Step 1: Calculate Returns / 步骤 1: 计算收益率

For each price pair, calculate the return:
对于每对价格，计算收益率：

```
r_t = (P_t - P_{t-1}) / P_{t-1}
```

Where:
- `P_t`: Current price / 当前价格
- `P_{t-1}`: Previous price / 前一价格
- `r_t`: Return / 收益率

### Step 2: Calculate Mean Return / 步骤 2: 计算平均收益率

```
μ = (1/n) * Σ r_i
```

Where:
- `n`: Number of returns / 收益率数量
- `μ`: Mean return / 平均收益率

### Step 3: Calculate Variance / 步骤 3: 计算方差

```
σ² = (1/(n-1)) * Σ (r_i - μ)²
```

Where:
- `σ²`: Variance / 方差
- `(n-1)`: Bessel's correction for sample variance / 样本方差的贝塞尔校正

### Step 4: Calculate Volatility / 步骤 4: 计算波动率

```
σ = √σ²
```

Where:
- `σ`: Volatility (standard deviation) / 波动率（标准差）

### Step 5: Annualize (Optional) / 步骤 5: 年化（可选）

```
σ_annual = σ * √(periods_per_year)
```

Where:
- `periods_per_year`: Number of periods per year (e.g., 365 for daily, 8760 for hourly)
- `periods_per_year`: 每年周期数（例如，日数据为 365，小时数据为 8760）

## Example Calculation / 计算示例

### Input / 输入:
```
Prices: [100.0, 101.5, 99.8, 102.3, 101.0, 103.5, 102.0, 104.2, 103.8, 105.0]
```

### Step-by-Step / 逐步计算:

1. **Returns / 收益率**:
   - r₁ = (101.5 - 100.0) / 100.0 = 0.015000 (1.50%)
   - r₂ = (99.8 - 101.5) / 101.5 = -0.016749 (-1.67%)
   - r₃ = (102.3 - 99.8) / 99.8 = 0.025050 (2.51%)
   - ...

2. **Mean Return / 平均收益率**:
   - μ = (0.015000 + (-0.016749) + 0.025050 + ...) / 9 = 0.005572 (0.56%)

3. **Variance / 方差**:
   - σ² = (1/8) * Σ (r_i - 0.005572)² = 0.00030643

4. **Volatility / 波动率**:
   - σ = √0.00030643 = 0.017505 (1.75%)

5. **Annualized (if daily data) / 年化（如果是日数据）**:
   - σ_annual = 0.017505 * √365 = 0.334436 (33.44%)

## Notes / 注意事项

1. **Minimum Data Points / 最小数据点**: Need at least 2 prices to calculate returns / 至少需要 2 个价格才能计算收益率
2. **Sample vs Population / 样本 vs 总体**: Uses sample variance (n-1) for better estimation / 使用样本方差 (n-1) 以获得更好的估计
3. **Annualization / 年化**: Only meaningful if data frequency matches periods_per_year / 仅当数据频率与 periods_per_year 匹配时才有意义
4. **Price Order / 价格顺序**: Prices must be in chronological order (oldest to newest) / 价格必须按时间顺序（从旧到新）

## Integration with Trading System / 与交易系统集成

These tools use the same calculation logic as `src/trading/volatility.py`:
这些工具使用与 `src/trading/volatility.py` 相同的计算逻辑：

```python
from src.trading.volatility import calculate_returns, calculate_volatility

prices = [100.0, 101.5, 99.8, 102.3, 101.0]
returns = calculate_returns(prices)
volatility = calculate_volatility(returns, annualized=False)
```

## References / 参考

- **Volatility Module**: `src/trading/volatility.py`
- **Tests**: `tests/unit/trading/test_volatility.py`
- **Smoke Tests**: `tests/smoke/test_volatility_smoke.py`

