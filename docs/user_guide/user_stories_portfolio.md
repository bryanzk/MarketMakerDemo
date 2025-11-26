# User Stories: Portfolio Management / 用户故事：组合管理

## 概述

本文档从用户指南中提取用户故事，用于驱动测试和开发。

---

## Epic 1: Portfolio Overview / 组合概览

### US-1.1: 查看组合总盈亏

**As a** 交易员  
**I want to** 在页面顶部看到所有策略的总盈亏 (Total PnL)  
**So that** 我可以快速了解整体交易表现

**Acceptance Criteria:**
- [ ] Total PnL 显示在 Portfolio Overview 区域
- [ ] Total PnL = Σ(各策略 Realized PnL)
- [ ] 正数显示绿色，负数显示红色
- [ ] 数据每秒自动刷新

**Test Cases:**
```python
def test_total_pnl_calculation():
    """Total PnL 应等于所有策略 PnL 之和"""
    
def test_total_pnl_display_color():
    """正 PnL 绿色，负 PnL 红色"""
```

---

### US-1.2: 查看组合夏普比率

**As a** 交易员  
**I want to** 看到组合整体的夏普比率 (Portfolio Sharpe)  
**So that** 我可以评估整体的风险调整后收益

**Acceptance Criteria:**
- [ ] Portfolio Sharpe 显示在 Portfolio Overview 区域
- [ ] 值 > 2.0 显示绿色，1.0-2.0 显示黄色，< 1.0 显示红色
- [ ] 当没有足够交易数据时显示 "N/A"

**Test Cases:**
```python
def test_portfolio_sharpe_calculation():
    """Portfolio Sharpe 基于组合整体收益率计算"""

def test_portfolio_sharpe_insufficient_data():
    """交易数少于 10 时返回 N/A"""
```

---

### US-1.3: 查看活跃策略数量

**As a** 交易员  
**I want to** 看到当前有多少策略正在运行  
**So that** 我知道系统的运行状态

**Acceptance Criteria:**
- [ ] 显示格式为 "X / Y"（活跃数 / 总数）
- [ ] 只有 status = "live" 的策略计入活跃数
- [ ] 总数包含所有已配置的策略

**Test Cases:**
```python
def test_active_strategies_count():
    """只计算 status=live 的策略"""

def test_active_strategies_format():
    """格式为 'X / Y'"""
```

---

### US-1.4: 查看组合风险等级

**As a** 交易员  
**I want to** 看到组合的整体风险等级  
**So that** 我可以在风险过高时及时采取行动

**Acceptance Criteria:**
- [ ] 风险等级分为：Low, Medium, High, Critical
- [ ] 基于以下因素计算：
  - Max Drawdown > 10% → High
  - 任一策略健康度 < 40 → Medium
  - 所有策略正常 → Low
- [ ] 不同等级使用不同颜色和图标

**Test Cases:**
```python
def test_risk_level_low():
    """所有指标正常时返回 Low"""

def test_risk_level_high_drawdown():
    """Max Drawdown > 10% 时返回 High"""

def test_risk_level_medium_health():
    """任一策略健康度 < 40 时返回 Medium"""
```

---

## Epic 2: Strategy Comparison Table / 策略对比表

### US-2.1: 查看策略列表

**As a** 交易员  
**I want to** 在表格中看到所有策略的关键指标  
**So that** 我可以快速对比各策略表现

**Acceptance Criteria:**
- [ ] 表格包含列：Strategy, Status, PnL, Sharpe, Health, Allocation, ROI, Actions
- [ ] 每行代表一个策略
- [ ] 默认按 PnL 降序排列

**Test Cases:**
```python
def test_strategy_list_columns():
    """API 返回包含所有必需字段"""

def test_strategy_list_sorted_by_pnl():
    """默认按 PnL 降序排列"""
```

---

### US-2.2: 查看策略状态

**As a** 交易员  
**I want to** 看到每个策略的运行状态  
**So that** 我知道哪些策略正在实盘运行

**Acceptance Criteria:**
- [ ] 状态包括：live, paper, paused, stopped
- [ ] 每种状态有对应的颜色和图标
- [ ] live = 🟢, paper = 🟡, paused = 🔴, stopped = ⚫

**Test Cases:**
```python
def test_strategy_status_values():
    """状态只能是 live/paper/paused/stopped"""

def test_strategy_status_display():
    """各状态有正确的图标"""
```

---

### US-2.3: 查看策略健康度

**As a** 交易员  
**I want to** 看到每个策略的健康度评分  
**So that** 我可以识别表现不佳的策略

**Acceptance Criteria:**
- [ ] 健康度为 0-100 的整数
- [ ] 计算公式：
  - 盈利能力 (40%): min(100, max(0, 50 + pnl / 100))
  - 风险调整收益 (30%): min(100, sharpe * 40)
  - 执行质量 (20%): fill_rate * 100 - slippage * 10
  - 稳定性 (10%): max(0, 100 - max_drawdown * 1000)
- [ ] 80-100 显示绿色，60-79 显示黄色，< 60 显示红色

**Test Cases:**
```python
def test_health_score_calculation():
    """健康度计算正确"""

def test_health_score_range():
    """健康度在 0-100 范围内"""

def test_health_score_weights():
    """各因素权重正确"""
```

---

### US-2.4: 查看策略资金分配

**As a** 交易员  
**I want to** 看到每个策略分配的资金比例  
**So that** 我了解资金分布情况

**Acceptance Criteria:**
- [ ] 显示为百分比格式（如 60%）
- [ ] 所有策略的分配比例之和 = 100%
- [ ] 分配比例来自策略配置

**Test Cases:**
```python
def test_allocation_sum():
    """所有策略分配之和为 100%"""

def test_allocation_format():
    """显示为百分比格式"""
```

---

### US-2.5: 查看策略 ROI

**As a** 交易员  
**I want to** 看到每个策略的投资回报率  
**So that** 我可以评估资金使用效率

**Acceptance Criteria:**
- [ ] ROI = PnL / Allocated Capital
- [ ] 显示为百分比格式
- [ ] 正数绿色，负数红色

**Test Cases:**
```python
def test_roi_calculation():
    """ROI = PnL / Allocated Capital"""

def test_roi_format():
    """显示为百分比格式"""
```

---

### US-2.6: 暂停策略

**As a** 交易员  
**I want to** 点击按钮暂停某个策略  
**So that** 我可以在风险较高时停止该策略下单

**Acceptance Criteria:**
- [ ] 每行有 [暂停] 按钮
- [ ] 点击后弹出确认对话框
- [ ] 确认后策略状态变为 "paused"
- [ ] 暂停后按钮变为 [恢复]

**Test Cases:**
```python
def test_pause_strategy():
    """暂停策略后状态变为 paused"""

def test_pause_strategy_confirmation():
    """需要确认才能暂停"""
```

---

### US-2.7: 按列排序

**As a** 交易员  
**I want to** 点击表头按该列排序  
**So that** 我可以快速找到表现最好/最差的策略

**Acceptance Criteria:**
- [ ] 点击表头触发排序
- [ ] 第一次点击降序，再次点击升序
- [ ] 当前排序列显示排序图标

**Test Cases:**
```python
def test_sort_by_pnl():
    """按 PnL 排序正确"""

def test_sort_toggle():
    """点击切换升序/降序"""
```

---

## Epic 3: Data Refresh / 数据刷新

### US-3.1: 自动刷新

**As a** 交易员  
**I want to** 数据自动刷新  
**So that** 我不需要手动刷新就能看到最新数据

**Acceptance Criteria:**
- [ ] Portfolio Overview 每秒刷新
- [ ] Strategy Table 每 2 秒刷新
- [ ] 健康度每 5 秒重新计算

**Test Cases:**
```python
def test_auto_refresh_interval():
    """刷新间隔正确"""
```

---

### US-3.2: 手动刷新

**As a** 交易员  
**I want to** 点击刷新按钮立即获取最新数据  
**So that** 我可以在需要时立即看到最新状态

**Acceptance Criteria:**
- [ ] 有刷新按钮
- [ ] 点击后立即请求最新数据
- [ ] 刷新期间显示加载状态

**Test Cases:**
```python
def test_manual_refresh():
    """点击刷新按钮触发数据请求"""
```

---

## 测试用例汇总

### 后端 API 测试 (test_portfolio_api.py)

| 测试函数 | 描述 | 对应 US |
|----------|------|---------|
| `test_get_portfolio_success` | 成功获取组合数据 | US-1.1 |
| `test_portfolio_total_pnl` | Total PnL 计算正确 | US-1.1 |
| `test_portfolio_sharpe` | Sharpe 计算正确 | US-1.2 |
| `test_portfolio_sharpe_insufficient_data` | 数据不足时返回 None | US-1.2 |
| `test_portfolio_active_count` | 活跃策略计数正确 | US-1.3 |
| `test_portfolio_risk_level` | 风险等级计算正确 | US-1.4 |
| `test_portfolio_strategies_list` | 策略列表完整 | US-2.1 |
| `test_strategy_health_calculation` | 健康度计算正确 | US-2.3 |
| `test_strategy_allocation_sum` | 分配之和为 100% | US-2.4 |
| `test_strategy_roi` | ROI 计算正确 | US-2.5 |
| `test_pause_strategy` | 暂停策略功能 | US-2.6 |

### 前端测试（手动/E2E）

| 测试场景 | 描述 | 对应 US |
|----------|------|---------|
| Portfolio Overview 显示 | 页面顶部显示组合概览 | US-1.x |
| Strategy Table 显示 | 表格正确显示所有策略 | US-2.x |
| 颜色编码 | PnL/Sharpe/Health 颜色正确 | US-1.1, US-2.3 |
| 排序功能 | 点击表头排序 | US-2.7 |
| 暂停按钮 | 点击暂停策略 | US-2.6 |
| 自动刷新 | 数据定时更新 | US-3.1 |

---

## 优先级排序

| 优先级 | User Story | 说明 |
|--------|------------|------|
| P0 | US-1.1 | 核心功能：总盈亏 |
| P0 | US-1.3 | 核心功能：活跃策略数 |
| P0 | US-2.1 | 核心功能：策略列表 |
| P0 | US-2.2 | 核心功能：策略状态 |
| P1 | US-1.2 | 重要：组合 Sharpe |
| P1 | US-2.3 | 重要：健康度 |
| P1 | US-2.5 | 重要：ROI |
| P2 | US-1.4 | 增强：风险等级 |
| P2 | US-2.4 | 增强：资金分配 |
| P2 | US-2.6 | 增强：暂停功能 |
| P3 | US-2.7 | 优化：排序功能 |
| P3 | US-3.x | 优化：刷新机制 |


