# User Stories - Risk Indicators / 风险指标用户故事

## Epic: 风险监控与预警

作为交易员，我需要实时了解交易风险状况，以便及时采取行动防止重大亏损。

---

## US-R1: 查看强平缓冲

### US-R1.1 查看当前强平缓冲值

**As a** 交易员
**I want to** 在 Dashboard 上看到当前的 Liquidation Buffer 百分比
**So that** 我可以知道距离强制平仓还有多少安全空间

**Acceptance Criteria:**
1. Dashboard 显示 Liquidation Buffer 卡片
2. 显示百分比值（如 "15.2%"）
3. 根据阈值显示不同颜色状态：
   - > 20%: 绿色 (Safe)
   - 10-20%: 黄色 (Warning)
   - 5-10%: 橙色 (Danger)
   - < 5%: 红色 (Critical)
4. 无持仓时显示 "N/A"

**测试用例:**
```python
def test_liquidation_buffer_display():
    # Given: 当前价格 100, 强平价格 80, 多头仓位
    # When: 计算 Liquidation Buffer
    # Then: 返回 20% ((100-80)/100)
    
def test_liquidation_buffer_no_position():
    # Given: 无持仓
    # When: 获取 Liquidation Buffer
    # Then: 返回 None 或 "N/A"
```

---

### US-R1.2 强平缓冲预警

**As a** 交易员
**I want to** 当 Liquidation Buffer 低于阈值时收到视觉预警
**So that** 我可以及时采取行动避免爆仓

**Acceptance Criteria:**
1. 低于 10% 时，卡片边框变黄色
2. 低于 5% 时，卡片边框变红色 + 闪烁动画
3. 状态文字明确显示风险等级

**测试用例:**
```python
def test_liquidation_buffer_warning_threshold():
    # Given: Liquidation Buffer = 8%
    # When: 获取状态
    # Then: 返回 "danger" 状态

def test_liquidation_buffer_critical_threshold():
    # Given: Liquidation Buffer = 3%
    # When: 获取状态
    # Then: 返回 "critical" 状态
```

---

## US-R2: 查看库存偏移

### US-R2.1 查看当前库存偏移值

**As a** 做市商
**I want to** 在 Dashboard 上看到当前的 Inventory Drift 百分比
**So that** 我可以了解持仓的方向性风险

**Acceptance Criteria:**
1. Dashboard 显示 Inventory Drift 卡片
2. 显示带符号的百分比值（如 "+32.5%" 或 "-15.0%"）
3. 正值表示净多头，负值表示净空头
4. 根据绝对值显示不同颜色状态：
   - |drift| < 20%: 绿色 (Balanced)
   - |drift| 20-50%: 黄色 (Offset)
   - |drift| 50-80%: 橙色 (Severe)
   - |drift| > 80%: 红色 (Extreme)

**测试用例:**
```python
def test_inventory_drift_long_position():
    # Given: 持仓 0.5 ETH, 最大允许持仓 1.0 ETH
    # When: 计算 Inventory Drift
    # Then: 返回 +50%

def test_inventory_drift_short_position():
    # Given: 持仓 -0.3 ETH, 最大允许持仓 1.0 ETH
    # When: 计算 Inventory Drift
    # Then: 返回 -30%
```

---

### US-R2.2 库存偏移方向指示

**As a** 做市商
**I want to** 清楚看到库存偏移的方向
**So that** 我知道价格往哪个方向波动会导致亏损

**Acceptance Criteria:**
1. 正偏移显示 "↑ Long" 或箭头向上
2. 负偏移显示 "↓ Short" 或箭头向下
3. 鼠标悬停显示风险提示

**测试用例:**
```python
def test_inventory_drift_direction_long():
    # Given: Inventory Drift = +45%
    # When: 获取方向
    # Then: 返回 "long", 风险提示 "价格下跌时亏损"
```

---

## US-R3: 查看最大回撤

### US-R3.1 查看组合级最大回撤

**As a** 交易员
**I want to** 在 Dashboard 上看到组合的 Max Drawdown
**So that** 我可以了解整体策略的最大亏损幅度

**Acceptance Criteria:**
1. Dashboard 显示 Max Drawdown 卡片
2. 显示负百分比值（如 "-4.8%"）
3. 根据绝对值显示不同颜色状态：
   - |dd| < 5%: 绿色 (Excellent)
   - |dd| 5-10%: 黄色 (Normal)
   - |dd| 10-20%: 橙色 (Warning)
   - |dd| > 20%: 红色 (Danger)

**测试用例:**
```python
def test_max_drawdown_calculation():
    # Given: PnL 历史 [0, 100, 150, 120, 180]
    # When: 计算 Max Drawdown
    # Then: 返回 -20% ((150-120)/150)
    
def test_max_drawdown_no_drawdown():
    # Given: PnL 历史 [0, 50, 100, 150] (单调递增)
    # When: 计算 Max Drawdown
    # Then: 返回 0%
```

---

### US-R3.2 查看策略级最大回撤

**As a** 交易员
**I want to** 在策略对比表中看到每个策略的 Max Drawdown
**So that** 我可以识别哪个策略风险最高

**Acceptance Criteria:**
1. 策略对比表新增 "Max DD" 列
2. 每个策略显示其独立的最大回撤
3. 可按 Max Drawdown 排序
4. 回撤最大的策略高亮显示

**测试用例:**
```python
def test_strategy_level_drawdown():
    # Given: 策略A回撤5%, 策略B回撤12%
    # When: 获取策略列表
    # Then: 每个策略包含 max_drawdown 字段
```

---

## US-R4: 综合风险等级

### US-R4.1 查看综合风险等级

**As a** 交易员
**I want to** 看到一个综合的风险等级评估
**So that** 我可以快速判断整体风险状况

**Acceptance Criteria:**
1. 根据三个指标计算综合风险等级
2. 显示 "Low" / "Medium" / "High" / "Critical"
3. 任一指标达到红色，综合等级为 "High" 或 "Critical"

**计算规则:**
```
if any indicator is Critical:
    overall = "Critical"
elif any indicator is Danger:
    overall = "High"
elif any indicator is Warning:
    overall = "Medium"
else:
    overall = "Low"
```

**测试用例:**
```python
def test_overall_risk_level_critical():
    # Given: Liquidation Buffer = 3% (Critical)
    # When: 计算综合风险
    # Then: 返回 "Critical"

def test_overall_risk_level_low():
    # Given: 所有指标都在绿色范围
    # When: 计算综合风险
    # Then: 返回 "Low"
```

---

## US-R5: API 接口

### US-R5.1 获取风险指标 API

**As a** 前端开发者
**I want to** 通过 API 获取所有风险指标
**So that** 我可以在 Dashboard 上展示

**API Specification:**
```
GET /api/risk-indicators

Response:
{
  "liquidation_buffer": 15.2,
  "liquidation_buffer_status": "warning",  // safe/warning/danger/critical
  "inventory_drift": 32.5,
  "inventory_drift_status": "offset",      // balanced/offset/severe/extreme
  "max_drawdown": -4.8,
  "max_drawdown_status": "excellent",      // excellent/normal/warning/danger
  "overall_risk_level": "medium"           // low/medium/high/critical
}
```

**测试用例:**
```python
def test_risk_indicators_api():
    # Given: 服务器运行中，有持仓
    # When: GET /api/risk-indicators
    # Then: 返回 200, 包含所有指标字段
```

---

## 验收测试场景

### 场景1：正常市场监控
1. 用户打开 Dashboard
2. 看到三个风险指标卡片
3. 所有指标显示绿色
4. 综合风险显示 "Low"

### 场景2：风险预警触发
1. 市场剧烈波动
2. Liquidation Buffer 降至 8%
3. 卡片变为黄色警告状态
4. 综合风险升至 "Medium"

### 场景3：紧急风险状态
1. Liquidation Buffer 降至 3%
2. 卡片变为红色 + 闪烁
3. 综合风险升至 "Critical"
4. 用户决定暂停策略

---

## 非功能需求

| 需求 | 描述 |
|------|------|
| **性能** | 指标计算 < 100ms |
| **刷新频率** | 默认 3 秒刷新一次 |
| **准确性** | 使用交易所实时数据 |
| **可用性** | 交易所 API 失败时显示 "N/A" |


