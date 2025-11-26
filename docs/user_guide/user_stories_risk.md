# User Stories - Risk Indicators / 风险指标用户故事

## Epic: Risk Monitoring and Alerts / 风险监控与预警

As a trader, I need to understand trading risk status in real-time so I can take timely action to prevent significant losses.

作为交易员，我需要实时了解交易风险状况，以便及时采取行动防止重大亏损。

---

## US-R1: View Liquidation Buffer / 查看强平缓冲

### US-R1.1 View Current Liquidation Buffer Value / 查看当前强平缓冲值

**As a** trader / 交易员  
**I want to** see the current Liquidation Buffer percentage on the Dashboard / 在 Dashboard 上看到当前的 Liquidation Buffer 百分比  
**So that** I know how much safety margin I have before forced liquidation / 我可以知道距离强制平仓还有多少安全空间

**Acceptance Criteria / 验收标准:**
1. Dashboard displays Liquidation Buffer card / Dashboard 显示 Liquidation Buffer 卡片
2. Shows percentage value (e.g., "15.2%") / 显示百分比值（如 "15.2%"）
3. Shows different color status based on threshold / 根据阈值显示不同颜色状态：
   - > 20%: Green (Safe) / 绿色（安全）
   - 10-20%: Yellow (Warning) / 黄色（警告）
   - 5-10%: Orange (Danger) / 橙色（危险）
   - < 5%: Red (Critical) / 红色（紧急）
4. Shows "N/A" when no position / 无持仓时显示 "N/A"

**Test Cases / 测试用例:**
```python
def test_liquidation_buffer_display():
    # Given: Current price 100, liquidation price 80, long position
    # 给定: 当前价格 100, 强平价格 80, 多头仓位
    # When: Calculate Liquidation Buffer / 计算 Liquidation Buffer
    # Then: Return 20% ((100-80)/100) / 返回 20%
    
def test_liquidation_buffer_no_position():
    # Given: No position / 无持仓
    # When: Get Liquidation Buffer / 获取 Liquidation Buffer
    # Then: Return None or "N/A" / 返回 None 或 "N/A"
```

---

### US-R1.2 Liquidation Buffer Alert / 强平缓冲预警

**As a** trader / 交易员  
**I want to** receive visual alerts when Liquidation Buffer falls below threshold / 当 Liquidation Buffer 低于阈值时收到视觉预警  
**So that** I can take timely action to avoid liquidation / 我可以及时采取行动避免爆仓

**Acceptance Criteria / 验收标准:**
1. Below 10%: Card border turns yellow / 低于 10% 时，卡片边框变黄色
2. Below 5%: Card border turns red + blinking animation / 低于 5% 时，卡片边框变红色 + 闪烁动画
3. Status text clearly shows risk level / 状态文字明确显示风险等级

**Test Cases / 测试用例:**
```python
def test_liquidation_buffer_warning_threshold():
    # Given: Liquidation Buffer = 8%
    # When: Get status / 获取状态
    # Then: Return "danger" status / 返回 "danger" 状态

def test_liquidation_buffer_critical_threshold():
    # Given: Liquidation Buffer = 3%
    # When: Get status / 获取状态
    # Then: Return "critical" status / 返回 "critical" 状态
```

---

## US-R2: View Inventory Drift / 查看库存偏移

### US-R2.1 View Current Inventory Drift Value / 查看当前库存偏移值

**As a** market maker / 做市商  
**I want to** see the current Inventory Drift percentage on the Dashboard / 在 Dashboard 上看到当前的 Inventory Drift 百分比  
**So that** I can understand directional risk of my positions / 我可以了解持仓的方向性风险

**Acceptance Criteria / 验收标准:**
1. Dashboard displays Inventory Drift card / Dashboard 显示 Inventory Drift 卡片
2. Shows signed percentage value (e.g., "+32.5%" or "-15.0%") / 显示带符号的百分比值（如 "+32.5%" 或 "-15.0%"）
3. Positive means net long, negative means net short / 正值表示净多头，负值表示净空头
4. Shows different color status based on absolute value / 根据绝对值显示不同颜色状态：
   - |drift| < 20%: Green (Balanced) / 绿色（平衡）
   - |drift| 20-50%: Yellow (Offset) / 黄色（偏移）
   - |drift| 50-80%: Orange (Severe) / 橙色（严重偏移）
   - |drift| > 80%: Red (Extreme) / 红色（极端偏移）

**Test Cases / 测试用例:**
```python
def test_inventory_drift_long_position():
    # Given: Position 0.5 ETH, max allowed 1.0 ETH
    # 给定: 持仓 0.5 ETH, 最大允许持仓 1.0 ETH
    # When: Calculate Inventory Drift / 计算 Inventory Drift
    # Then: Return +50% / 返回 +50%

def test_inventory_drift_short_position():
    # Given: Position -0.3 ETH, max allowed 1.0 ETH
    # 给定: 持仓 -0.3 ETH, 最大允许持仓 1.0 ETH
    # When: Calculate Inventory Drift / 计算 Inventory Drift
    # Then: Return -30% / 返回 -30%
```

---

### US-R2.2 Inventory Drift Direction Indicator / 库存偏移方向指示

**As a** market maker / 做市商  
**I want to** clearly see the direction of inventory drift / 清楚看到库存偏移的方向  
**So that** I know which price direction would cause losses / 我知道价格往哪个方向波动会导致亏损

**Acceptance Criteria / 验收标准:**
1. Positive drift shows "↑ Long" or up arrow / 正偏移显示 "↑ Long" 或箭头向上
2. Negative drift shows "↓ Short" or down arrow / 负偏移显示 "↓ Short" 或箭头向下
3. Hover shows risk tooltip / 鼠标悬停显示风险提示

**Test Cases / 测试用例:**
```python
def test_inventory_drift_direction_long():
    # Given: Inventory Drift = +45%
    # When: Get direction / 获取方向
    # Then: Return "long", risk tip "Loss when price falls"
    # 返回 "long", 风险提示 "价格下跌时亏损"
```

---

## US-R3: View Max Drawdown / 查看最大回撤

### US-R3.1 View Portfolio-level Max Drawdown / 查看组合级最大回撤

**As a** trader / 交易员  
**I want to** see the portfolio's Max Drawdown on the Dashboard / 在 Dashboard 上看到组合的 Max Drawdown  
**So that** I can understand the overall strategy's maximum loss extent / 我可以了解整体策略的最大亏损幅度

**Acceptance Criteria / 验收标准:**
1. Dashboard displays Max Drawdown card / Dashboard 显示 Max Drawdown 卡片
2. Shows negative percentage value (e.g., "-4.8%") / 显示负百分比值（如 "-4.8%"）
3. Shows different color status based on absolute value / 根据绝对值显示不同颜色状态：
   - |dd| < 5%: Green (Excellent) / 绿色（优秀）
   - |dd| 5-10%: Yellow (Normal) / 黄色（正常）
   - |dd| 10-20%: Orange (Warning) / 橙色（警告）
   - |dd| > 20%: Red (Danger) / 红色（危险）

**Test Cases / 测试用例:**
```python
def test_max_drawdown_calculation():
    # Given: PnL history [0, 100, 150, 120, 180]
    # 给定: PnL 历史 [0, 100, 150, 120, 180]
    # When: Calculate Max Drawdown / 计算 Max Drawdown
    # Then: Return -20% ((150-120)/150) / 返回 -20%
    
def test_max_drawdown_no_drawdown():
    # Given: PnL history [0, 50, 100, 150] (monotonically increasing)
    # 给定: PnL 历史 [0, 50, 100, 150] (单调递增)
    # When: Calculate Max Drawdown / 计算 Max Drawdown
    # Then: Return 0% / 返回 0%
```

---

### US-R3.2 View Strategy-level Max Drawdown / 查看策略级最大回撤

**As a** trader / 交易员  
**I want to** see each strategy's Max Drawdown in the comparison table / 在策略对比表中看到每个策略的 Max Drawdown  
**So that** I can identify which strategy has the highest risk / 我可以识别哪个策略风险最高

**Acceptance Criteria / 验收标准:**
1. Strategy comparison table adds "Max DD" column / 策略对比表新增 "Max DD" 列
2. Each strategy shows its individual max drawdown / 每个策略显示其独立的最大回撤
3. Can sort by Max Drawdown / 可按 Max Drawdown 排序
4. Strategy with highest drawdown is highlighted / 回撤最大的策略高亮显示

**Test Cases / 测试用例:**
```python
def test_strategy_level_drawdown():
    # Given: Strategy A drawdown 5%, Strategy B drawdown 12%
    # 给定: 策略A回撤5%, 策略B回撤12%
    # When: Get strategy list / 获取策略列表
    # Then: Each strategy includes max_drawdown field / 每个策略包含 max_drawdown 字段
```

---

## US-R4: Overall Risk Level / 综合风险等级

### US-R4.1 View Overall Risk Level / 查看综合风险等级

**As a** trader / 交易员  
**I want to** see a comprehensive risk level assessment / 看到一个综合的风险等级评估  
**So that** I can quickly judge the overall risk situation / 我可以快速判断整体风险状况

**Acceptance Criteria / 验收标准:**
1. Calculate overall risk level from three indicators / 根据三个指标计算综合风险等级
2. Display "Low" / "Medium" / "High" / "Critical" / 显示 "Low" / "Medium" / "High" / "Critical"
3. If any indicator is red, overall level is "High" or "Critical" / 任一指标达到红色，综合等级为 "High" 或 "Critical"

**Calculation Rules / 计算规则:**
```python
if any indicator is Critical:
    overall = "Critical"
elif any indicator is Danger:
    overall = "High"
elif any indicator is Warning:
    overall = "Medium"
else:
    overall = "Low"
```

**Test Cases / 测试用例:**
```python
def test_overall_risk_level_critical():
    # Given: Liquidation Buffer = 3% (Critical)
    # 给定: Liquidation Buffer = 3% (Critical)
    # When: Calculate overall risk / 计算综合风险
    # Then: Return "Critical" / 返回 "Critical"

def test_overall_risk_level_low():
    # Given: All indicators in green range / 所有指标都在绿色范围
    # When: Calculate overall risk / 计算综合风险
    # Then: Return "Low" / 返回 "Low"
```

---

## US-R5: API Interface / API 接口

### US-R5.1 Get Risk Indicators API / 获取风险指标 API

**As a** frontend developer / 前端开发者  
**I want to** get all risk indicators via API / 通过 API 获取所有风险指标  
**So that** I can display them on the Dashboard / 我可以在 Dashboard 上展示

**API Specification / API 规范:**
```
GET /api/risk-indicators

Response / 响应:
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

**Test Cases / 测试用例:**
```python
def test_risk_indicators_api():
    # Given: Server running, has position / 服务器运行中，有持仓
    # When: GET /api/risk-indicators
    # Then: Return 200, includes all indicator fields / 返回 200, 包含所有指标字段
```

---

## Acceptance Test Scenarios / 验收测试场景

### Scenario 1: Normal Market Monitoring / 场景1：正常市场监控
1. User opens Dashboard / 用户打开 Dashboard
2. Sees three risk indicator cards / 看到三个风险指标卡片
3. All indicators show green / 所有指标显示绿色
4. Overall risk shows "Low" / 综合风险显示 "Low"

### Scenario 2: Risk Alert Triggered / 场景2：风险预警触发
1. Market fluctuates violently / 市场剧烈波动
2. Liquidation Buffer drops to 8% / Liquidation Buffer 降至 8%
3. Card turns yellow warning state / 卡片变为黄色警告状态
4. Overall risk rises to "Medium" / 综合风险升至 "Medium"

### Scenario 3: Emergency Risk State / 场景3：紧急风险状态
1. Liquidation Buffer drops to 3% / Liquidation Buffer 降至 3%
2. Card turns red + blinking / 卡片变为红色 + 闪烁
3. Overall risk rises to "Critical" / 综合风险升至 "Critical"
4. User decides to pause strategy / 用户决定暂停策略

---

## Non-Functional Requirements / 非功能需求

| Requirement / 需求 | Description / 描述 |
|------|------|
| **Performance / 性能** | Indicator calculation < 100ms / 指标计算 < 100ms |
| **Refresh Rate / 刷新频率** | Default 3 second refresh / 默认 3 秒刷新一次 |
| **Accuracy / 准确性** | Uses exchange real-time data / 使用交易所实时数据 |
| **Availability / 可用性** | Shows "N/A" when exchange API fails / 交易所 API 失败时显示 "N/A" |
