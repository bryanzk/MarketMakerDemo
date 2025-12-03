# User Story Standards / 用户故事标准

**Source / 来源**: Classic Software Development Literature / 经典软件开发文献  
**Last Updated / 最后更新**: 2025-11-30  
**Maintained by / 维护者**: Agent PO

---

## 📚 经典标准概览 / Classic Standards Overview

### 1. INVEST 原则 / INVEST Principle

**Origin / 来源**: Bill Wake (2003) - "INVEST in Good Stories, and SMART Tasks"

INVEST 是评估用户故事质量的六个标准：

| 标准 | 英文 | 中文 | 说明 |
|------|------|------|------|
| **I** | **Independent** | **独立性** | 用户故事应当能够独立存在和实现，避免与其他故事过度依赖 |
| **N** | **Negotiable** | **可协商性** | 用户故事应当是简洁的需求描述，具体细节可通过讨论确定 |
| **V** | **Valuable** | **有价值性** | 每个用户故事都应为用户或客户提供明确的价值 |
| **E** | **Estimable** | **可估算性** | 用户故事应当足够清晰，以便团队能够对其工作量进行合理估算 |
| **S** | **Small** | **小型化** | 用户故事的规模应当适中，通常能够在一个迭代内完成 |
| **T** | **Testable** | **可测试性** | 用户故事应当包含明确的验收标准，以便于测试和验证 |

---

### 2. 3Cs 原则 / 3Cs Principle

**Origin / 来源**: Ron Jeffries (2001) - "Essential XP: Card, Conversation, Confirmation"

用户故事包含三个核心要素：

| C | 英文 | 中文 | 说明 |
|---|------|------|------|
| **Card** | Card | 卡片 | 用户故事的简短书面描述（通常写在索引卡上） |
| **Conversation** | Conversation | 对话 | 开发团队与利益相关者之间的讨论，澄清需求细节 |
| **Confirmation** | Confirmation | 确认 | 明确的验收标准，用于确认故事已完成 |

---

### 3. 标准格式 / Standard Format

**Origin / 来源**: Mike Cohn (2004) - "User Stories Applied"

经典的用户故事格式：

```
As a {role},
I want {functionality},
So that {benefit}.
```

**中文格式**：
```
作为 {角色}，
我想要 {功能}，
以便 {收益}。
```

---

## ✅ 好的用户故事的特征 / Characteristics of Good User Stories

### 1. 清晰简洁 / Clear and Concise

- ✅ 使用简单明了的语言
- ✅ 避免技术术语
- ✅ 使所有团队成员都能理解

**Example / 示例**:
```
✅ Good: "As a trader, I want to switch between Binance and Hyperliquid, so that I can trade on different exchanges."

❌ Bad: "As a trader, I want to implement a polymorphic exchange client factory pattern with dependency injection, so that I can abstract exchange-specific implementations."
```

---

### 2. 用户导向 / User-Oriented

- ✅ 从用户的角度描述需求
- ✅ 明确谁是用户
- ✅ 明确用户的目标
- ✅ 明确用户希望获得的价值

**Example / 示例**:
```
✅ Good: "As a quantitative trader, I want to see real-time PnL metrics, so that I can monitor my trading performance."

❌ Bad: "The system should display PnL calculations in the database."
```

---

### 3. 可测试性 / Testable

- ✅ 包含明确的验收标准
- ✅ 验收标准可验证
- ✅ 有明确的成功/失败条件

**Example / 示例**:
```
✅ Good:
- [ ] Connection retries up to 3 times with exponential backoff (1s, 2s, 4s)
- [ ] Health check endpoint returns 200 OK when connected, 503 when disconnected

❌ Bad:
- [ ] Connection should be reliable (too vague)
- [ ] System should work well (not measurable)
```

---

### 4. 独立性 / Independent

- ✅ 尽量使每个用户故事独立存在
- ✅ 减少与其他故事的依赖
- ✅ 方便单独开发和测试

**Example / 示例**:
```
✅ Good: "As a trader, I want to place limit orders, so that I can control my entry price."

❌ Bad: "As a trader, I want to place limit orders (depends on US-001: Exchange Connection), so that I can control my entry price."
```

**Note / 注意**: 如果存在依赖，应在验收标准中明确说明，但尽量设计为可独立测试。

---

### 5. 可估算性 / Estimable

- ✅ 足够具体，使开发团队能够估算实现所需的时间和资源
- ✅ 规模适中，通常能够在一个迭代内完成
- ✅ 避免过于庞大或过于细碎

**Example / 示例**:
```
✅ Good: "As a trader, I want to cancel all open orders, so that I can quickly exit all positions."

❌ Bad: "As a trader, I want a complete trading platform with all features." (too large)
❌ Bad: "As a trader, I want a button to click." (too small, missing context)
```

---

### 6. 可协商性 / Negotiable

- ✅ 提供足够的信息以引发团队与利益相关者之间的讨论
- ✅ 不应过于详细，以保留灵活性
- ✅ 具体细节通过对话确定

**Example / 示例**:
```
✅ Good: "As a trader, I want to see my portfolio balance, so that I can monitor my capital."

❌ Bad: "As a trader, I want to see my portfolio balance displayed in a 12px Arial font, centered on the page, with a blue background, updated every 100ms, so that I can monitor my capital." (too prescriptive)
```

---

## 📋 验收标准最佳实践 / Acceptance Criteria Best Practices

### 特征 / Characteristics

根据经典文献和项目实践，良好的验收标准应具备：

| 特征 | 英文 | 中文 | 说明 |
|------|------|------|------|
| **Testable** | Testable | 可测试 | 可以通过测试验证 |
| **Measurable** | Measurable | 可衡量 | 有明确的成功/失败条件 |
| **Specific** | Specific | 具体 | 不模糊或含糊不清 |
| **Independent** | Independent | 独立 | 可以单独验证 |

---

### 格式 / Format

**Given-When-Then 格式** (BDD - Behavior Driven Development):

```
Given {precondition}
When {action}
Then {expected result}
```

**中文格式**:
```
Given {前置条件}
When {操作}
Then {预期结果}
```

**Example / 示例**:
```
### AC-1: Connection Retry Logic / 连接重试逻辑

**Given** the exchange API is temporarily unavailable  
**When** the system attempts to connect  
**Then** it should retry up to 3 times with exponential backoff (1s, 2s, 4s)

**Given** 交易所 API 暂时不可用  
**When** 系统尝试连接  
**Then** 应该重试最多 3 次，使用指数退避（1秒、2秒、4秒）
```

---

## 🔍 评估检查清单 / Evaluation Checklist

### 用户故事质量检查 / User Story Quality Check

- [ ] **Independent / 独立性**: 故事可以独立实现，不依赖其他未完成的故事
- [ ] **Negotiable / 可协商性**: 故事简洁，细节可通过讨论确定
- [ ] **Valuable / 有价值性**: 故事为用户提供明确的价值
- [ ] **Estimable / 可估算性**: 团队能够估算工作量
- [ ] **Small / 小型化**: 可以在一个迭代内完成（通常 1-3 天）
- [ ] **Testable / 可测试性**: 有明确的验收标准

### 格式检查 / Format Check

- [ ] 遵循 "As a... I want... So that..." 格式
- [ ] 角色（Persona）清晰明确
- [ ] 功能描述具体
- [ ] 收益陈述清晰

### 验收标准检查 / Acceptance Criteria Check

- [ ] 每个验收标准可测试
- [ ] 每个验收标准可衡量
- [ ] 每个验收标准具体明确
- [ ] 验收标准独立可验证
- [ ] 使用 Given-When-Then 格式（推荐）

---

## 📊 项目中的实践 / Project Practice

### 与经典标准的对比 / Comparison with Classic Standards

| 标准 | 经典要求 | 项目要求 | 状态 |
|------|---------|---------|------|
| **INVEST** | 6 个标准 | ✅ 全部采用 | ✅ 一致 |
| **3Cs** | Card, Conversation, Confirmation | ✅ 采用（Card + Confirmation） | ✅ 一致 |
| **格式** | "As a... I want... So that..." | ✅ 完全一致 | ✅ 一致 |
| **验收标准** | Given-When-Then | ✅ 推荐使用 | ✅ 一致 |
| **双语** | 通常单语 | ✅ 要求双语 | ⭐ 增强 |

---

### 项目特殊要求 / Project-Specific Requirements

根据 `.cursorrules` 和 `docs/agents/AGENT_PO.md`，项目对用户故事有额外要求：

1. **双语文档 / Bilingual Documentation**
   - 所有文档必须中英文双语
   - 格式：`## Title / 标题`

2. **Metadata / 元数据**
   - `parent_feature`: 父级 Feature 或 Epic 的引用
   - `parent_feature_zh`: 父级 Feature 或 Epic 的中文名称
   - `module`: 所属模块
   - `owner_agent`: 负责的开发 Agent

3. **层级关系 / Hierarchy**
   - 支持 Epic → Story 层级
   - 支持 Feature → Story 层级
   - 通过 `parent_feature` 字段建立关系

---

## 🎯 实际应用示例 / Practical Examples

### Example 1: Good User Story / 好的用户故事示例

```markdown
# US-CORE-004: Hyperliquid Exchange Support / Hyperliquid 交易所支持

## Metadata / 元数据

- **id**: "US-CORE-004"
- **parent_feature**: "CORE-004: Hyperliquid Exchange Integration"
- **parent_feature_zh**: "CORE-004: Hyperliquid 交易所集成"
- **module**: "trading"
- **owner_agent**: "Agent TRADING"

## User Story / 用户故事

**As a** quantitative trader  
**I want** to switch between Binance and Hyperliquid exchanges  
**So that** I can trade on different exchanges and diversify my trading options

**作为** 量化交易员  
**我希望** 能够在 Binance 和 Hyperliquid 交易所之间切换  
**以便** 我可以在不同交易所交易并分散交易选择

## Acceptance Criteria / 验收标准

### AC-1: Exchange Selection / 交易所选择

**Given** the system is configured with both Binance and Hyperliquid credentials  
**When** I select Hyperliquid from the exchange dropdown  
**Then** the system should connect to Hyperliquid API and display connection status

**Given** 系统配置了 Binance 和 Hyperliquid 凭证  
**When** 我从交易所下拉菜单中选择 Hyperliquid  
**Then** 系统应该连接到 Hyperliquid API 并显示连接状态

### AC-2: Order Placement / 订单下单

**Given** I am connected to Hyperliquid  
**When** I place a limit order  
**Then** the order should be placed on Hyperliquid and I should receive order confirmation

**Given** 我已连接到 Hyperliquid  
**When** 我下一个限价单  
**Then** 订单应该在 Hyperliquid 上执行，我应该收到订单确认

### AC-3: Error Handling / 错误处理

**Given** Hyperliquid API returns an error  
**When** the system processes the error  
**Then** it should display a user-friendly error message in Chinese and English

**Given** Hyperliquid API 返回错误  
**When** 系统处理错误  
**Then** 应该显示中英文用户友好的错误消息
```

**评估 / Evaluation**:
- ✅ Independent: 可以独立实现
- ✅ Negotiable: 简洁，细节可讨论
- ✅ Valuable: 为用户提供价值（多交易所支持）
- ✅ Estimable: 团队可以估算工作量
- ✅ Small: 可以在一个迭代内完成
- ✅ Testable: 有明确的验收标准

---

### Example 2: Bad User Story / 不好的用户故事示例

```markdown
# US-BAD-001: Trading System / 交易系统

## User Story / 用户故事

**As a** user  
**I want** a trading system  
**So that** I can trade

**作为** 用户  
**我希望** 一个交易系统  
**以便** 我可以交易

## Acceptance Criteria / 验收标准

- [ ] System should work
- [ ] 系统应该工作
```

**问题 / Problems**:
- ❌ 角色不明确（"user" 太泛）
- ❌ 功能描述不具体（"trading system" 太宽泛）
- ❌ 收益不清晰（"can trade" 没有说明价值）
- ❌ 验收标准不可测试（"should work" 太模糊）
- ❌ 规模太大（整个交易系统）

---

## 📚 参考文献 / References

1. **INVEST Principle**
   - Wake, Bill (2003). "INVEST in Good Stories, and SMART Tasks"
   - XP 2003 Conference

2. **3Cs Principle**
   - Jeffries, Ron (2001). "Essential XP: Card, Conversation, Confirmation"
   - Extreme Programming Explained

3. **User Stories Applied**
   - Cohn, Mike (2004). "User Stories Applied: For Agile Software Development"
   - Addison-Wesley Professional

4. **Agile Estimating and Planning**
   - Cohn, Mike (2005). "Agile Estimating and Planning"
   - Prentice Hall

---

**Last Updated / 最后更新**: 2025-11-30  
**Maintained by / 维护者**: Agent PO

