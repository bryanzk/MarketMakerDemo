# Error Handling Improvement Plan / 错误处理改进计划

## Overview / 概览

This document outlines the implementation plan to improve debugging experience by standardizing error handling across the trading engine, API endpoints, and frontend templates.

本文档概述了通过标准化交易引擎、API 端点和前端模板中的错误处理来改进调试体验的实施计划。

## Current State Analysis / 当前状态分析

### ✅ What's Already Working / 已实现的功能

1. **Strategy Instance Error Tracking / 策略实例错误追踪**
   - `alert` field in `StrategyInstance` and `AlphaLoop`
   - `error_history` deque (maxlen=200) for historical errors
   - Error suggestions via `_get_error_suggestion()` method
   - Error types: `insufficient_funds`, `invalid_order`, `exchange_error`, `cycle_error`

2. **Hyperliquid Client Exceptions / Hyperliquid 客户端异常**
   - Custom exception classes: `AuthenticationError`, `ConnectionError`, `OrderNotFoundError`, `InsufficientBalanceError`, `InvalidOrderError`
   - Bilingual error messages (English/Chinese)

3. **Frontend Error Display / 前端错误显示**
   - `evaluationErrorBox` and `controlMessage` elements in templates
   - Some API calls check `data.error` and display messages

### ❌ What Needs Improvement / 需要改进的地方

1. **Inconsistent Error Format / 错误格式不一致**
   - API endpoints return errors in different formats
   - Some return `{"error": "message"}`, others return `{"status": "error", "message": "..."}`
   - Error messages not always bilingual

2. **Incomplete Frontend Error Handling / 前端错误处理不完整**
   - Not all API calls check for errors
   - Error display inconsistent across templates
   - Missing error context (which API call failed, timestamp, etc.)

3. **Limited Error Context / 错误上下文有限**
   - Errors don't always include actionable suggestions
   - Missing error codes for programmatic handling
   - No error severity levels

4. **Strategy Instance Errors Not Exposed / 策略实例错误未暴露**
   - `alert` and `error_history` not always included in API responses
   - Frontend can't easily access strategy instance error history

## Implementation Plan / 实施计划

### Phase 1: Standardize Error Response Format / 阶段 1：标准化错误响应格式

#### 1.1 Create Standard Error Response Schema / 创建标准错误响应模式

**File**: `src/shared/errors.py` (new file)

```python
"""
Standard Error Response Schema / 标准错误响应模式
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ErrorSeverity(str, Enum):
    """Error severity levels / 错误严重程度级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorType(str, Enum):
    """Standard error types / 标准错误类型"""
    # Authentication / 认证
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    
    # Connection / 连接
    CONNECTION_ERROR = "connection_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    
    # Trading / 交易
    INSUFFICIENT_FUNDS = "insufficient_funds"
    INVALID_ORDER = "invalid_order"
    ORDER_NOT_FOUND = "order_not_found"
    RATE_LIMIT_ERROR = "rate_limit_error"
    
    # Exchange / 交易所
    EXCHANGE_ERROR = "exchange_error"
    EXCHANGE_MAINTENANCE = "exchange_maintenance"
    
    # Strategy / 策略
    STRATEGY_ERROR = "strategy_error"
    CYCLE_ERROR = "cycle_error"
    
    # Validation / 验证
    VALIDATION_ERROR = "validation_error"
    INVALID_PARAMETER = "invalid_parameter"
    
    # System / 系统
    INTERNAL_ERROR = "internal_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class StandardErrorResponse:
    """
    Standard error response format / 标准错误响应格式
    
    All API endpoints should return errors in this format.
    所有 API 端点应以此格式返回错误。
    """
    error: bool = True
    error_type: str
    error_code: Optional[str] = None
    message: str  # English message / 英文消息
    message_zh: str  # Chinese message / 中文消息
    severity: str = ErrorSeverity.ERROR
    suggestion: Optional[str] = None  # English suggestion / 英文建议
    suggestion_zh: Optional[str] = None  # Chinese suggestion / 中文建议
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response / 转换为字典用于 JSON 响应"""
        import time
        return {
            "error": self.error,
            "error_type": self.error_type,
            "error_code": self.error_code,
            "message": self.message,
            "message_zh": self.message_zh,
            "severity": self.severity,
            "suggestion": self.suggestion,
            "suggestion_zh": self.suggestion_zh,
            "details": self.details,
            "timestamp": self.timestamp or time.time(),
        }
```

#### 1.2 Create Error Mapper / 创建错误映射器

**File**: `src/shared/error_mapper.py` (new file)

```python
"""
Error Mapper for Standardizing Exceptions / 用于标准化异常的错误映射器
"""

from typing import Optional, Dict, Any
from src.shared.errors import (
    StandardErrorResponse,
    ErrorType,
    ErrorSeverity,
)
from src.trading.hyperliquid_client import (
    AuthenticationError,
    ConnectionError,
    OrderNotFoundError,
    InsufficientBalanceError,
    InvalidOrderError,
)


class ErrorMapper:
    """Map exceptions to standard error responses / 将异常映射为标准错误响应"""
    
    # Error type mapping / 错误类型映射
    EXCEPTION_TO_ERROR_TYPE = {
        AuthenticationError: ErrorType.AUTHENTICATION_ERROR,
        ConnectionError: ErrorType.CONNECTION_ERROR,
        OrderNotFoundError: ErrorType.ORDER_NOT_FOUND,
        InsufficientBalanceError: ErrorType.INSUFFICIENT_FUNDS,
        InvalidOrderError: ErrorType.INVALID_ORDER,
        ValueError: ErrorType.VALIDATION_ERROR,
        KeyError: ErrorType.INVALID_PARAMETER,
    }
    
    # Error suggestions / 错误建议
    ERROR_SUGGESTIONS = {
        ErrorType.AUTHENTICATION_ERROR: {
            "en": "Check your API credentials and ensure they are correct.",
            "zh": "检查您的 API 凭证，确保它们正确。",
        },
        ErrorType.CONNECTION_ERROR: {
            "en": "Check your internet connection and exchange API status.",
            "zh": "检查您的网络连接和交易所 API 状态。",
        },
        ErrorType.INSUFFICIENT_FUNDS: {
            "en": "Check your account balance and margin. Consider reducing order quantity or closing existing positions.",
            "zh": "检查您的账户余额和保证金。考虑减少订单数量或关闭现有仓位。",
        },
        ErrorType.INVALID_ORDER: {
            "en": "Order parameters may be invalid. Check price, quantity, and symbol settings.",
            "zh": "订单参数可能无效。检查价格、数量和交易对设置。",
        },
        ErrorType.ORDER_NOT_FOUND: {
            "en": "The order may have been filled or canceled. Refresh the order list.",
            "zh": "订单可能已被成交或取消。刷新订单列表。",
        },
        ErrorType.RATE_LIMIT_ERROR: {
            "en": "Too many requests. Please wait a moment and try again.",
            "zh": "请求过多。请稍等片刻后重试。",
        },
        ErrorType.EXCHANGE_ERROR: {
            "en": "Exchange API error occurred. This may be temporary - the system will retry in the next cycle.",
            "zh": "交易所 API 错误。这可能是暂时的 - 系统将在下一个周期重试。",
        },
    }
    
    @classmethod
    def map_exception(
        cls,
        exception: Exception,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> StandardErrorResponse:
        """
        Map an exception to a standard error response / 将异常映射为标准错误响应
        
        Args:
            exception: The exception to map
            error_code: Optional error code for programmatic handling
            details: Optional additional error details
            
        Returns:
            StandardErrorResponse
        """
        error_type = cls.EXCEPTION_TO_ERROR_TYPE.get(
            type(exception),
            ErrorType.UNKNOWN_ERROR
        )
        
        # Get bilingual messages / 获取双语消息
        message = str(exception)
        message_zh = cls._translate_message(message, error_type)
        
        # Get suggestions / 获取建议
        suggestions = cls.ERROR_SUGGESTIONS.get(error_type, {})
        suggestion = suggestions.get("en")
        suggestion_zh = suggestions.get("zh")
        
        # Determine severity / 确定严重程度
        severity = cls._determine_severity(error_type, exception)
        
        return StandardErrorResponse(
            error_type=error_type.value,
            error_code=error_code,
            message=message,
            message_zh=message_zh,
            severity=severity.value,
            suggestion=suggestion,
            suggestion_zh=suggestion_zh,
            details=details,
        )
    
    @classmethod
    def _translate_message(cls, message: str, error_type: ErrorType) -> str:
        """Translate error message to Chinese / 将错误消息翻译为中文"""
        # Simple translation mapping / 简单翻译映射
        translations = {
            "authentication": "认证",
            "connection": "连接",
            "insufficient": "不足",
            "invalid": "无效",
            "not found": "未找到",
            "rate limit": "速率限制",
            "timeout": "超时",
        }
        
        # If message already contains Chinese, return as is / 如果消息已包含中文，原样返回
        if any('\u4e00' <= char <= '\u9fff' for char in message):
            return message
        
        # Simple translation / 简单翻译
        message_zh = message
        for en, zh in translations.items():
            if en.lower() in message.lower():
                message_zh = message.replace(en, zh)
                break
        
        return message_zh or message
    
    @classmethod
    def _determine_severity(
        cls, error_type: ErrorType, exception: Exception
    ) -> ErrorSeverity:
        """Determine error severity / 确定错误严重程度"""
        if error_type in [
            ErrorType.AUTHENTICATION_ERROR,
            ErrorType.INSUFFICIENT_FUNDS,
            ErrorType.INTERNAL_ERROR,
        ]:
            return ErrorSeverity.ERROR
        elif error_type in [
            ErrorType.RATE_LIMIT_ERROR,
            ErrorType.EXCHANGE_ERROR,
        ]:
            return ErrorSeverity.WARNING
        else:
            return ErrorSeverity.ERROR
```

### Phase 2: Update API Endpoints / 阶段 2：更新 API 端点

#### 2.1 Create Error Response Helper / 创建错误响应辅助函数

**File**: `server.py` (add to existing file)

```python
from src.shared.errors import StandardErrorResponse
from src.shared.error_mapper import ErrorMapper

def create_error_response(
    exception: Exception,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create standardized error response / 创建标准化错误响应
    
    Usage / 用法:
        try:
            # ... API logic ...
        except Exception as e:
            return create_error_response(e).to_dict()
    """
    error_response = ErrorMapper.map_exception(exception, error_code, details)
    return error_response.to_dict()
```

#### 2.2 Update Hyperliquid API Endpoints / 更新 Hyperliquid API 端点

**Example**: Update `/api/hyperliquid/status` endpoint

```python
@app.get("/api/hyperliquid/status")
async def get_hyperliquid_status():
    """Get Hyperliquid connection status / 获取 Hyperliquid 连接状态"""
    try:
        exchange = get_exchange_by_name("hyperliquid")
        if not exchange:
            return create_error_response(
                ValueError("Hyperliquid exchange not initialized"),
                error_code="EXCHANGE_NOT_INITIALIZED"
            )
        
        # ... existing logic ...
        
        return status
    except Exception as e:
        logger.error(f"Error getting Hyperliquid status: {e}", exc_info=True)
        return create_error_response(
            e,
            error_code="STATUS_FETCH_ERROR",
            details={"endpoint": "/api/hyperliquid/status"}
        )
```

### Phase 3: Expose Strategy Instance Errors / 阶段 3：暴露策略实例错误

#### 3.1 Update Status API to Include Errors / 更新状态 API 以包含错误

**File**: `server.py` (update `/api/bot/status` endpoint)

```python
@app.get("/api/bot/status")
async def get_bot_status():
    """Get bot status including errors / 获取 Bot 状态（包括错误）"""
    try:
        status = bot_engine.get_status()
        
        # Add error information / 添加错误信息
        status["errors"] = {
            "global_alert": bot_engine.alert,
            "global_error_history": list(bot_engine.error_history)[-10:],  # Last 10 errors
            "instance_errors": {}
        }
        
        # Add instance-specific errors / 添加实例特定错误
        for instance_id, instance in bot_engine.strategy_instances.items():
            status["errors"]["instance_errors"][instance_id] = {
                "alert": instance.alert,
                "error_history": list(instance.error_history)[-10:],  # Last 10 errors
            }
        
        return status
    except Exception as e:
        logger.error(f"Error getting bot status: {e}", exc_info=True)
        return create_error_response(e, error_code="STATUS_FETCH_ERROR")
```

### Phase 4: Standardize Frontend Error Handling / 阶段 4：标准化前端错误处理

#### 4.1 Create Frontend Error Handler Utility / 创建前端错误处理工具

**File**: `templates/js/error_handler.js` (new file)

```javascript
/**
 * Standardized Frontend Error Handler / 标准化前端错误处理
 * 
 * Usage / 用法:
 *   import { handleApiError, displayError } from './error_handler.js';
 *   
 *   try {
 *     const data = await fetch('/api/endpoint');
 *     if (data.error) {
 *       handleApiError(data, errorBox);
 *       return;
 *     }
 *     // ... success handling ...
 *   } catch (err) {
 *     displayError(err, errorBox);
 *   }
 */

/**
 * Handle API error response / 处理 API 错误响应
 * @param {Object} errorResponse - Standard error response from API
 * @param {HTMLElement} errorBox - Element to display error in
 * @param {Object} options - Additional options
 */
export function handleApiError(errorResponse, errorBox, options = {}) {
    if (!errorResponse || !errorResponse.error) {
        return;
    }
    
    const {
        error_type,
        message,
        message_zh,
        severity = 'error',
        suggestion,
        suggestion_zh,
        details,
        timestamp
    } = errorResponse;
    
    // Determine language / 确定语言
    const lang = options.language || detectLanguage();
    const displayMessage = lang === 'zh' ? message_zh : message;
    const displaySuggestion = lang === 'zh' ? suggestion_zh : suggestion;
    
    // Build error HTML / 构建错误 HTML
    let errorHtml = `
        <div class="error-message" data-severity="${severity}">
            <strong>${getSeverityIcon(severity)} ${displayMessage}</strong>
    `;
    
    if (displaySuggestion) {
        errorHtml += `
            <div class="error-suggestion">
                💡 ${displaySuggestion}
            </div>
        `;
    }
    
    if (details && options.showDetails) {
        errorHtml += `
            <div class="error-details">
                <details>
                    <summary>Details / 详情</summary>
                    <pre>${JSON.stringify(details, null, 2)}</pre>
                </details>
            </div>
        `;
    }
    
    if (timestamp) {
        const date = new Date(timestamp * 1000);
        errorHtml += `
            <div class="error-timestamp">
                ${date.toLocaleString()}
            </div>
        `;
    }
    
    errorHtml += `</div>`;
    
    // Display error / 显示错误
    if (errorBox) {
        errorBox.innerHTML = errorHtml;
        errorBox.style.display = 'block';
        errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Log to console / 记录到控制台
    console.error(`[${error_type}] ${displayMessage}`, {
        severity,
        suggestion: displaySuggestion,
        details,
        timestamp
    });
}

/**
 * Display generic error / 显示通用错误
 * @param {Error|string} error - Error object or message
 * @param {HTMLElement} errorBox - Element to display error in
 */
export function displayError(error, errorBox) {
    const message = error instanceof Error ? error.message : String(error);
    const errorResponse = {
        error: true,
        error_type: 'unknown_error',
        message: message,
        message_zh: message, // Fallback to same message
        severity: 'error',
    };
    
    handleApiError(errorResponse, errorBox);
}

/**
 * Get severity icon / 获取严重程度图标
 */
function getSeverityIcon(severity) {
    const icons = {
        info: 'ℹ️',
        warning: '⚠️',
        error: '❌',
        critical: '🚨',
    };
    return icons[severity] || '❌';
}

/**
 * Detect user language / 检测用户语言
 */
function detectLanguage() {
    const lang = navigator.language || navigator.userLanguage;
    return lang.startsWith('zh') ? 'zh' : 'en';
}

/**
 * Clear error display / 清除错误显示
 * @param {HTMLElement} errorBox - Element to clear
 */
export function clearError(errorBox) {
    if (errorBox) {
        errorBox.innerHTML = '';
        errorBox.style.display = 'none';
    }
}
```

#### 4.2 Update Templates to Use Error Handler / 更新模板以使用错误处理程序

**File**: `templates/HyperliquidTrade.html` (update existing error handling)

```javascript
// Import error handler (if using modules) or include inline
// import { handleApiError, displayError, clearError } from './js/error_handler.js';

// Update existing API calls / 更新现有 API 调用
async function checkConnection() {
    const statusEl = document.getElementById('connectionStatus');
    const errorBox = document.getElementById('evaluationErrorBox');
    
    try {
        clearError(errorBox);
        const response = await fetch('/api/hyperliquid/status');
        const data = await response.json();
        
        // Use standardized error handler / 使用标准化错误处理程序
        if (data.error) {
            handleApiError(data, errorBox, { showDetails: true });
            return;
        }
        
        // ... success handling ...
    } catch (err) {
        displayError(err, errorBox);
    }
}

// Apply to all API calls / 应用于所有 API 调用
async function updateStrategyConfig() {
    const controlMessage = document.getElementById('controlMessage');
    const errorBox = document.getElementById('evaluationErrorBox');
    
    try {
        clearError(errorBox);
        const response = await fetch('/api/hyperliquid/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ spread, quantity, leverage })
        });
        const data = await response.json();
        
        if (data.error) {
            handleApiError(data, errorBox);
            return;
        }
        
        // Success / 成功
        showMessage(controlMessage, 'Strategy config updated. / 策略配置已更新。');
    } catch (err) {
        displayError(err, errorBox);
    }
}
```

### Phase 5: Add Error History Display / 阶段 5：添加错误历史显示

#### 5.1 Add Error History Panel to Frontend / 添加错误历史面板到前端

**File**: `templates/HyperliquidTrade.html` (add new section)

```html
<!-- Error History Panel / 错误历史面板 -->
<div class="panel">
    <h2>Error History / 错误历史</h2>
    <button onclick="refreshErrorHistory()">🔄 Refresh / 刷新</button>
    <div id="errorHistory" class="error-history">
        <p>Loading error history... / 加载错误历史中...</p>
    </div>
</div>

<script>
async function refreshErrorHistory() {
    const errorHistoryEl = document.getElementById('errorHistory');
    
    try {
        const response = await fetch('/api/bot/status');
        const data = await response.json();
        
        if (data.error) {
            errorHistoryEl.innerHTML = `<p class="error">Failed to load error history / 加载错误历史失败</p>`;
            return;
        }
        
        const errors = data.errors || {};
        const instanceErrors = errors.instance_errors || {};
        
        let html = '<div class="error-history-list">';
        
        // Display global errors / 显示全局错误
        if (errors.global_alert) {
            html += `
                <div class="error-item global">
                    <strong>Global Alert / 全局警报:</strong>
                    ${formatError(errors.global_alert)}
                </div>
            `;
        }
        
        // Display instance errors / 显示实例错误
        for (const [instanceId, instanceError] of Object.entries(instanceErrors)) {
            if (instanceError.alert) {
                html += `
                    <div class="error-item instance" data-instance="${instanceId}">
                        <strong>${instanceId} Alert / 警报:</strong>
                        ${formatError(instanceError.alert)}
                    </div>
                `;
            }
            
            if (instanceError.error_history && instanceError.error_history.length > 0) {
                html += `
                    <div class="error-item history" data-instance="${instanceId}">
                        <strong>${instanceId} Error History / 错误历史:</strong>
                        <ul>
                            ${instanceError.error_history.map(err => `
                                <li>
                                    <span class="error-time">${new Date(err.timestamp * 1000).toLocaleString()}</span>
                                    <span class="error-type">[${err.type}]</span>
                                    <span class="error-message">${err.message}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            }
        }
        
        html += '</div>';
        errorHistoryEl.innerHTML = html;
    } catch (err) {
        errorHistoryEl.innerHTML = `<p class="error">Error: ${err.message}</p>`;
    }
}

function formatError(alert) {
    if (!alert) return '';
    if (typeof alert === 'string') return alert;
    
    return `
        <div class="alert-content">
            <span class="alert-type">[${alert.type}]</span>
            <span class="alert-message">${alert.message}</span>
            ${alert.suggestion ? `<div class="alert-suggestion">💡 ${alert.suggestion}</div>` : ''}
        </div>
    `;
}

// Auto-refresh error history every 30 seconds / 每 30 秒自动刷新错误历史
setInterval(refreshErrorHistory, 30000);
</script>
```

## Implementation Checklist / 实施清单

### Phase 1: Standardize Error Response Format / 阶段 1：标准化错误响应格式
- [ ] Create `src/shared/errors.py` with `StandardErrorResponse` and enums
- [ ] Create `src/shared/error_mapper.py` with `ErrorMapper` class
- [ ] Add error type mappings for all custom exceptions
- [ ] Add bilingual error suggestions for all error types
- [ ] Test error mapping with sample exceptions

### Phase 2: Update API Endpoints / 阶段 2：更新 API 端点
- [ ] Add `create_error_response()` helper to `server.py`
- [ ] Update all Hyperliquid API endpoints (`/api/hyperliquid/*`)
- [ ] Update bot control endpoints (`/api/bot/*`)
- [ ] Update evaluation endpoints (`/api/evaluation/*`)
- [ ] Update portfolio endpoints (`/api/portfolio/*`)
- [ ] Test all endpoints return standardized error format

### Phase 3: Expose Strategy Instance Errors / 阶段 3：暴露策略实例错误
- [ ] Update `/api/bot/status` to include error information
- [ ] Add `errors` field with `global_alert`, `global_error_history`, `instance_errors`
- [ ] Limit error history to last 10-20 entries for performance
- [ ] Test error exposure in API responses

### Phase 4: Standardize Frontend Error Handling / 阶段 4：标准化前端错误处理
- [ ] Create `templates/js/error_handler.js` utility
- [ ] Update `HyperliquidTrade.html` to use error handler
- [ ] Update `LLMTrade.html` to use error handler
- [ ] Update `index.html` to use error handler
- [ ] Add error display styling (CSS)
- [ ] Test error display in all templates

### Phase 5: Add Error History Display / 阶段 5：添加错误历史显示
- [ ] Add error history panel to `HyperliquidTrade.html`
- [ ] Add error history panel to `LLMTrade.html`
- [ ] Add error history panel to `index.html`
- [ ] Implement auto-refresh for error history
- [ ] Add error history styling (CSS)
- [ ] Test error history display

## Testing Plan / 测试计划

1. **Unit Tests / 单元测试**
   - Test `ErrorMapper.map_exception()` with various exceptions
   - Test `StandardErrorResponse.to_dict()` serialization
   - Test error type and severity determination

2. **Integration Tests / 集成测试**
   - Test API endpoints return standardized error format
   - Test error history is exposed correctly
   - Test frontend error handler displays errors correctly

3. **Manual Testing / 手动测试**
   - Trigger various error scenarios (network, auth, insufficient funds, etc.)
   - Verify error messages are bilingual
   - Verify error suggestions are helpful
   - Verify error history is accessible in frontend

## Additional Recommendations / 额外建议

### 1. Error Logging Enhancement / 错误日志增强

Add structured logging for all errors:

```python
import structlog

logger = structlog.get_logger()

# Log errors with context / 记录带上下文的错误
logger.error(
    "API error occurred",
    error_type=error_type,
    error_code=error_code,
    endpoint=endpoint,
    user_id=user_id,
    exc_info=True
)
```

### 2. Error Monitoring / 错误监控

Consider integrating error monitoring service (e.g., Sentry):

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)

# Automatically capture exceptions / 自动捕获异常
```

### 3. Error Recovery Suggestions / 错误恢复建议

Enhance `_get_error_suggestion()` to provide more specific recovery steps:

```python
def _get_error_suggestion(self, error_type: str, error_details: dict) -> str:
    """Get user-friendly suggestion with recovery steps / 获取带恢复步骤的用户友好建议"""
    base_suggestion = self._get_base_suggestion(error_type)
    recovery_steps = self._get_recovery_steps(error_type, error_details)
    return f"{base_suggestion}\n\nRecovery steps:\n{recovery_steps}"
```

### 4. Error Rate Limiting / 错误速率限制

Add rate limiting for error display to avoid flooding:

```javascript
class ErrorRateLimiter {
    constructor(maxErrorsPerMinute = 10) {
        this.errors = [];
        this.maxErrors = maxErrorsPerMinute;
    }
    
    shouldDisplay(error) {
        const now = Date.now();
        this.errors = this.errors.filter(time => now - time < 60000);
        
        if (this.errors.length >= this.maxErrors) {
            return false;
        }
        
        this.errors.push(now);
        return true;
    }
}
```

## Summary / 总结

This plan provides a comprehensive approach to improving debugging experience:

1. **Standardized Error Format**: All errors follow the same structure
2. **Bilingual Support**: All error messages in English and Chinese
3. **Actionable Suggestions**: Each error includes recovery suggestions
4. **Frontend Integration**: Errors are visible in the UI with context
5. **Error History**: Users can see recent errors and their history

The implementation should be done in phases to minimize disruption and allow for testing at each stage.

