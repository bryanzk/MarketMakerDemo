# Strategy Development Guide / 策略开发指南

This guide outlines the steps required to add a new trading strategy to the AlphaLoop Market Maker system.

本指南概述了向 AlphaLoop 做市商系统添加新交易策略所需的步骤。

## Overview / 概述

Adding a new strategy involves changes across the backend (logic), API (configuration), and frontend (UI).

添加新策略涉及后端（逻辑）、API（配置）和前端（UI）的更改。

## Step-by-Step Implementation / 分步实施

### 1. Create Strategy Logic / 创建策略逻辑
Create a new file in `src/trading/strategies/` (e.g., `my_strategy.py`) and define your strategy class.

在 `src/trading/strategies/` 中创建新文件（例如 `my_strategy.py`）并定义策略类。

```python
# src/trading/strategies/my_strategy.py

class MyNewStrategy:
    def __init__(self):
        self.spread = 0.002
        self.quantity = 0.01
        # Add custom parameters / 添加自定义参数
        self.my_param = 10

    def calculate_target_orders(self, market_data, funding_rate=0.0):
        """
        Calculate bid and ask orders based on market data.
        根据市场数据计算买卖订单。
        Returns: list of dicts with 'side', 'price', 'quantity'
        返回：包含 'side', 'price', 'quantity' 的字典列表
        """
        # Implement your logic here / 在此实现你的逻辑
        pass
```

### 2. Update Configuration (Optional) / 更新配置（可选）
If your strategy needs global configuration constants, add them to `src/shared/config.py`.

如果策略需要全局配置常量，将它们添加到 `src/shared/config.py`。

```python
# src/shared/config.py
MY_PARAM_DEFAULT = 10
```

### 3. Integrate with Main Loop / 集成到主循环
Update `src/trading/engine.py` to import your strategy and handle switching.

更新 `src/trading/engine.py` 以导入策略并处理切换。

```python
# src/trading/engine.py
from src.strategies.my_strategy import MyNewStrategy

class AlphaLoop:
    def set_strategy(self, strategy_type):
        if strategy_type == "my_strategy":
            new_strategy = MyNewStrategy()
            # ... preserve common params / 保留通用参数 ...
            self.strategy = new_strategy
            return True
        # ... handle other strategies / 处理其他策略 ...
```

### 4. Update Risk Engine / 更新风险引擎
If your strategy introduces new parameters that need validation, update `src/ai/agents/risk.py`.

如果策略引入了需要验证的新参数，更新 `src/ai/agents/risk.py`。

```python
# src/ai/agents/risk.py

class RiskAgent:
    def validate_proposal(self, proposed_config):
        # ... existing checks / 现有检查 ...
        
        my_param = proposed_config.get("my_param")
        if my_param is not None and my_param > 100:
            return False, "My Param too high"
            
        return True, "Approved"
```

### 5. Update API / 更新 API
Update `server.py` to expose your strategy and its parameters.

更新 `server.py` 以暴露策略及其参数。

```python
# server.py
from src.strategies.my_strategy import MyNewStrategy

class ConfigUpdate(BaseModel):
    # ...
    strategy_type: str
    my_param: float = None  # Add optional param / 添加可选参数

@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    # ...
    if config.strategy_type == "my_strategy":
        bot_engine.strategy.my_param = config.my_param
    # ...
```

### 6. Update UI / 更新用户界面
Update `templates/index.html` to allow selecting the strategy and configuring its parameters.

更新 `templates/index.html` 以允许选择策略并配置其参数。

- Add an option to the **Strategy** dropdown. / 在**策略**下拉菜单中添加选项。
- Add input fields for your new parameters (hidden by default). / 为新参数添加输入字段（默认隐藏）。
- Update JavaScript `toggleStrategyParams` to show/hide inputs. / 更新 JavaScript `toggleStrategyParams` 以显示/隐藏输入。
- Update JavaScript `updateConfig` and `fetchStatus` to handle the new parameters. / 更新 JavaScript `updateConfig` 和 `fetchStatus` 以处理新参数。

## Verification / 验证

1.  **Unit Tests / 单元测试**: Create tests in `tests/` to verify your strategy logic and risk validation. / 在 `tests/` 中创建测试以验证策略逻辑和风险验证。
2.  **Manual Test / 手动测试**: Start the server, switch to your strategy, and verify that orders are generated correctly and parameters can be updated. / 启动服务器，切换到你的策略，并验证订单是否正确生成以及参数是否可以更新。
