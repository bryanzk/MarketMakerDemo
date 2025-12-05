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
    All responses (success and error) should include trace_id for correlation.
    所有 API 端点应以此格式返回错误。
    所有响应（成功和错误）都应包含 trace_id 用于关联。
    """
    error: bool = True
    error_type: str
    error_code: Optional[str] = None
    message: str  # English message / 英文消息
    message_zh: str  # Chinese message / 中文消息
    severity: str = ErrorSeverity.ERROR
    suggestion: Optional[str] = None  # English suggestion / 英文建议
    suggestion_zh: Optional[str] = None  # Chinese suggestion / 中文建议
    remediation: Optional[str] = None  # English remediation steps / 英文修复步骤
    remediation_zh: Optional[str] = None  # Chinese remediation steps / 中文修复步骤
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    trace_id: Optional[str] = None  # Request trace ID for correlation / 请求追踪ID用于关联
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response / 转换为字典用于 JSON 响应"""
        import time
        return {
            "ok": not self.error,  # Success flag / 成功标志
            "error": self.error,
            "error_type": self.error_type,
            "error_code": self.error_code,
            "message": self.message,
            "message_zh": self.message_zh,
            "severity": self.severity,
            "suggestion": self.suggestion,
            "suggestion_zh": self.suggestion_zh,
            "remediation": self.remediation,
            "remediation_zh": self.remediation_zh,
            "details": self.details,
            "timestamp": self.timestamp or time.time(),
            "trace_id": self.trace_id,
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

### Phase 2: Request Tracing & Correlation / 阶段 2：请求追踪与关联

#### 2.1 Create Trace ID Middleware / 创建追踪ID中间件

**File**: `src/shared/tracing.py` (new file)

```python
"""
Request Tracing Utilities / 请求追踪工具

Provides trace_id generation and correlation across requests, logs, and responses.
提供跨请求、日志和响应的 trace_id 生成和关联。
"""

import uuid
import time
from typing import Optional, Dict, Any
from contextvars import ContextVar

# Context variable for trace_id / 用于 trace_id 的上下文变量
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)


def generate_trace_id() -> str:
    """
    Generate a unique trace ID / 生成唯一的追踪ID
    
    Returns:
        Trace ID string (e.g., "req_abc123def456")
    """
    return f"req_{uuid.uuid4().hex[:12]}"


def get_trace_id() -> Optional[str]:
    """Get current trace ID from context / 从上下文获取当前追踪ID"""
    return trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    """Set trace ID in context / 在上下文中设置追踪ID"""
    trace_id_var.set(trace_id)


def create_request_context(
    endpoint: str,
    method: str = "GET",
    payload_hash: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create minimal request context for logging / 创建用于日志记录的最小请求上下文
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        payload_hash: Hash of request payload (for repro without secrets)
        
    Returns:
        Context dictionary
    """
    return {
        "endpoint": endpoint,
        "method": method,
        "payload_hash": payload_hash,
        "trace_id": get_trace_id(),
    }
```

#### 2.2 Add Trace ID Middleware to FastAPI / 为 FastAPI 添加追踪ID中间件

**File**: `server.py` (add middleware)

```python
from fastapi import Request
from src.shared.tracing import generate_trace_id, set_trace_id, get_trace_id

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    """
    Add trace_id to all requests / 为所有请求添加 trace_id
    
    Trace ID is included in:
    - Request context (for logging)
    - Response headers
    - Error responses
    - Strategy instance error_history entries
    
    追踪ID包含在：
    - 请求上下文（用于日志记录）
    - 响应头
    - 错误响应
    - 策略实例 error_history 条目
    """
    trace_id = generate_trace_id()
    set_trace_id(trace_id)
    
    # Add trace_id to request state / 将 trace_id 添加到请求状态
    request.state.trace_id = trace_id
    
    response = await call_next(request)
    
    # Add trace_id to response headers / 将 trace_id 添加到响应头
    response.headers["X-Trace-ID"] = trace_id
    
    return response
```

#### 2.3 Create Error Response Helper / 创建错误响应辅助函数

**File**: `server.py` (add to existing file)

```python
from src.shared.errors import StandardErrorResponse
from src.shared.error_mapper import ErrorMapper
from src.shared.tracing import get_trace_id

def create_error_response(
    exception: Exception,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create standardized error response / 创建标准化错误响应
    
    Automatically includes trace_id from request context.
    自动包含来自请求上下文的 trace_id。
    
    Usage / 用法:
        try:
            # ... API logic ...
        except Exception as e:
            return create_error_response(e).to_dict()
    """
    error_response = ErrorMapper.map_exception(exception, error_code, details)
    error_response.trace_id = get_trace_id()  # Add trace_id / 添加 trace_id
    return error_response.to_dict()
```

#### 2.4 Update Hyperliquid API Endpoints / 更新 Hyperliquid API 端点

**Example**: Update `/api/hyperliquid/status` endpoint

```python
from src.shared.tracing import get_trace_id, create_request_context
import hashlib
import json

@app.get("/api/hyperliquid/status")
async def get_hyperliquid_status(request: Request):
    """Get Hyperliquid connection status / 获取 Hyperliquid 连接状态"""
    trace_id = get_trace_id()
    request_context = create_request_context("/api/hyperliquid/status", "GET")
    
    try:
        exchange = get_exchange_by_name("hyperliquid")
        if not exchange:
            return create_error_response(
                ValueError("Hyperliquid exchange not initialized"),
                error_code="EXCHANGE_NOT_INITIALIZED",
                details=request_context
            )
        
        # ... existing logic ...
        
        # Add trace_id to success response / 将 trace_id 添加到成功响应
        status["trace_id"] = trace_id
        status["ok"] = True
        
        return status
    except Exception as e:
        logger.error(
            "Error getting Hyperliquid status",
            exc_info=True,
            extra={
                "trace_id": trace_id,
                **request_context,
                "error": str(e),
            }
        )
        return create_error_response(
            e,
            error_code="STATUS_FETCH_ERROR",
            details=request_context
        )
```

#### 2.5 Add Pre-flight Connection Endpoint / 添加预检连接端点

**File**: `server.py` (add new endpoint)

```python
@app.get("/api/hyperliquid/connection")
async def check_hyperliquid_connection(request: Request):
    """
    Pre-flight connection check / 预检连接检查
    
    Returns market-data freshness, auth status, and warnings.
    Returns / 返回：市场数据新鲜度、认证状态和警告。
    """
    trace_id = get_trace_id()
    request_context = create_request_context("/api/hyperliquid/connection", "GET")
    
    try:
        exchange = get_exchange_by_name("hyperliquid")
        if not exchange:
            return {
                "ok": False,
                "connected": False,
                "error": "Exchange not initialized / 交易所未初始化",
                "trace_id": trace_id,
            }
        
        # Check connection status / 检查连接状态
        is_connected = exchange.is_connected if hasattr(exchange, "is_connected") else False
        
        # Check market data freshness / 检查市场数据新鲜度
        market_data = None
        data_freshness = None
        if is_connected:
            try:
                market_data = exchange.fetch_market_data()
                # Calculate freshness (time since last update) / 计算新鲜度（自上次更新以来的时间）
                if market_data and "timestamp" in market_data:
                    data_freshness = time.time() - market_data.get("timestamp", 0)
            except Exception as e:
                logger.warning(f"Failed to fetch market data: {e}", extra={"trace_id": trace_id})
        
        # Check auth status / 检查认证状态
        auth_status = "authenticated" if is_connected else "not_authenticated"
        
        # Collect warnings / 收集警告
        warnings = []
        if not is_connected:
            warnings.append({
                "type": "connection",
                "message": "Not connected to exchange / 未连接到交易所",
                "message_zh": "未连接到交易所",
            })
        if data_freshness and data_freshness > 60:  # Stale if > 60 seconds / 超过60秒视为过期
            warnings.append({
                "type": "stale_data",
                "message": f"Market data is stale ({data_freshness:.1f}s old) / 市场数据已过期（{data_freshness:.1f}秒）",
                "message_zh": f"市场数据已过期（{data_freshness:.1f}秒）",
            })
        
        return {
            "ok": True,
            "connected": is_connected,
            "auth_status": auth_status,
            "data_freshness": data_freshness,
            "warnings": warnings,
            "trace_id": trace_id,
        }
    except Exception as e:
        logger.error(
            "Error checking connection",
            exc_info=True,
            extra={
                "trace_id": trace_id,
                **request_context,
                "error": str(e),
            }
        )
        return create_error_response(
            e,
            error_code="CONNECTION_CHECK_ERROR",
            details=request_context
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

#### 4.1 Create Frontend Diagnostic Helper / 创建前端诊断辅助工具

**File**: `templates/js/api_diagnostics.js` (new file)

```javascript
/**
 * API Call Diagnostics Helper / API 调用诊断辅助工具
 * 
 * Wraps all fetch calls to log: URL, status, latency, payload, and errors.
 * 包装所有 fetch 调用以记录：URL、状态、延迟、负载和错误。
 */

class ApiDiagnostics {
    constructor(maxCalls = 50) {
        this.calls = [];
        this.maxCalls = maxCalls;
    }
    
    /**
     * Wrap fetch call with diagnostics / 用诊断包装 fetch 调用
     * @param {string} url - API endpoint URL
     * @param {Object} options - Fetch options
     * @returns {Promise<Response>}
     */
    async fetch(url, options = {}) {
        const startTime = performance.now();
        const callId = `call_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Hash payload for logging (without secrets) / 为日志记录哈希负载（不含密钥）
        const payloadHash = options.body 
            ? this.hashPayload(options.body) 
            : null;
        
        try {
            const response = await fetch(url, options);
            const latency = performance.now() - startTime;
            
            // Clone response for reading body / 克隆响应以读取正文
            const clonedResponse = response.clone();
            let parsedPayload = null;
            
            try {
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.includes("application/json")) {
                    parsedPayload = await clonedResponse.json();
                }
            } catch (e) {
                // Ignore parse errors / 忽略解析错误
            }
            
            // Record call / 记录调用
            this.recordCall({
                id: callId,
                url,
                method: options.method || "GET",
                status: response.status,
                statusText: response.statusText,
                latency: Math.round(latency),
                payloadHash,
                payload: parsedPayload,
                timestamp: Date.now(),
                traceId: response.headers.get("X-Trace-ID"),
                error: parsedPayload?.error || null,
            });
            
            return response;
        } catch (error) {
            const latency = performance.now() - startTime;
            
            // Record failed call / 记录失败的调用
            this.recordCall({
                id: callId,
                url,
                method: options.method || "GET",
                status: 0,
                statusText: "Network Error",
                latency: Math.round(latency),
                payloadHash,
                payload: null,
                timestamp: Date.now(),
                traceId: null,
                error: error.message,
            });
            
            throw error;
        }
    }
    
    /**
     * Hash payload for logging / 为日志记录哈希负载
     * @param {string} payload - Request payload
     * @returns {string} Hash string
     */
    hashPayload(payload) {
        // Simple hash function / 简单哈希函数
        let hash = 0;
        const str = typeof payload === "string" ? payload : JSON.stringify(payload);
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer / 转换为32位整数
        }
        return Math.abs(hash).toString(36);
    }
    
    /**
     * Record API call / 记录 API 调用
     * @param {Object} callData - Call data
     */
    recordCall(callData) {
        this.calls.unshift(callData); // Add to beginning / 添加到开头
        if (this.calls.length > this.maxCalls) {
            this.calls.pop(); // Remove oldest / 移除最旧的
        }
    }
    
    /**
     * Get recent calls / 获取最近的调用
     * @param {Object} filters - Filter options
     * @returns {Array} Filtered calls
     */
    getRecentCalls(filters = {}) {
        let calls = this.calls;
        
        // Filter by errors only / 仅按错误过滤
        if (filters.errorsOnly) {
            calls = calls.filter(call => call.error || call.status >= 400);
        }
        
        // Filter by endpoint / 按端点过滤
        if (filters.endpoint) {
            calls = calls.filter(call => call.url.includes(filters.endpoint));
        }
        
        // Limit results / 限制结果
        if (filters.limit) {
            calls = calls.slice(0, filters.limit);
        }
        
        return calls;
    }
    
    /**
     * Clear call history / 清除调用历史
     */
    clear() {
        this.calls = [];
    }
}

// Global instance / 全局实例
const apiDiagnostics = new ApiDiagnostics();

// Export for use in templates / 导出供模板使用
if (typeof module !== "undefined" && module.exports) {
    module.exports = { ApiDiagnostics, apiDiagnostics };
}
```

#### 4.2 Create Frontend Error Handler Utility / 创建前端错误处理工具

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
        remediation,
        remediation_zh,
        details,
        timestamp,
        trace_id
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
    
    // Add trace_id for log correlation / 添加 trace_id 用于日志关联
    if (trace_id) {
        errorHtml += `
            <div class="error-trace-id">
                <strong>Trace ID / 追踪ID:</strong> <code>${trace_id}</code>
                <button onclick="navigator.clipboard.writeText('${trace_id}')" title="Copy / 复制">📋</button>
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
        timestamp,
        trace_id,  // Include trace_id for log correlation / 包含 trace_id 用于日志关联
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
- [ ] Add `trace_id` field to `StandardErrorResponse`
- [ ] Add `remediation` fields for detailed recovery steps
- [ ] Create `src/shared/error_mapper.py` with `ErrorMapper` class
- [ ] Add error type mappings for all custom exceptions
- [ ] Add bilingual error suggestions for all error types
- [ ] Test error mapping with sample exceptions

### Phase 2: Request Tracing & Correlation / 阶段 2：请求追踪与关联
- [ ] Create `src/shared/tracing.py` with trace_id utilities
- [ ] Add trace_id middleware to FastAPI
- [ ] Update `create_error_response()` to include trace_id
- [ ] Add trace_id to all API responses (success and error)
- [ ] Update `/api/hyperliquid/status` endpoint with trace_id
- [ ] Add `/api/hyperliquid/connection` pre-flight endpoint
- [ ] Include trace_id in strategy instance error_history entries
- [ ] Test trace_id generation and correlation

### Phase 3: Structured Logging & Observability / 阶段 3：结构化日志与可观测性
- [ ] Update `src/shared/logger.py` with JSON formatter
- [ ] Add trace_id to all log entries
- [ ] Implement structured logging for API requests
- [ ] Implement structured logging for exchange calls
- [ ] Add `/metrics` endpoint for exchange health
- [ ] Track latency buckets and error rates
- [ ] Test structured logging output

### Phase 4: Standardize Frontend Error Handling / 阶段 4：标准化前端错误处理
- [ ] Create `templates/js/api_diagnostics.js` for API call tracking
- [ ] Create `templates/js/error_handler.js` utility
- [ ] Update error handler to display trace_id
- [ ] Wrap all fetch calls with diagnostics
- [ ] Update `HyperliquidTrade.html` to use error handler
- [ ] Update `LLMTrade.html` to use error handler
- [ ] Update `index.html` to use error handler
- [ ] Add error display styling (CSS)
- [ ] Test error display in all templates

### Phase 5: Frontend Debug Panel / 阶段 5：前端调试面板
- [ ] Create `templates/js/debug_panel.js` component
- [ ] Add debug panel to `HyperliquidTrade.html`
- [ ] Add debug panel to `LLMTrade.html`
- [ ] Add debug panel to `index.html`
- [ ] Implement filters (errors only / all)
- [ ] Add debug panel styling (CSS)
- [ ] Test debug panel functionality

### Phase 6: Client-Side Validation / 阶段 6：客户端验证
- [ ] Create `templates/js/validation.js` validation layer
- [ ] Validate order parameters before submission
- [ ] Validate symbol format
- [ ] Validate quantity and price
- [ ] Validate leverage range
- [ ] Display validation errors in UI
- [ ] Test validation prevents invalid orders

### Phase 7: Expose Strategy Instance Errors / 阶段 7：暴露策略实例错误
- [ ] Update `/api/bot/status` to include error information
- [ ] Add `errors` field with `global_alert`, `global_error_history`, `instance_errors`
- [ ] Include trace_id in error_history entries
- [ ] Limit error history to last 10-20 entries for performance
- [ ] Test error exposure in API responses

### Phase 8: Add Error History Display / 阶段 8：添加错误历史显示
- [ ] Add error history panel to `HyperliquidTrade.html`
- [ ] Add error history panel to `LLMTrade.html`
- [ ] Add error history panel to `index.html`
- [ ] Display trace_id in error history
- [ ] Implement auto-refresh for error history
- [ ] Add error history styling (CSS)
- [ ] Test error history display

### Phase 9: Testing / 阶段 9：测试
- [ ] Write contract tests for error envelope structure
- [ ] Write fixture-driven exchange failure simulations
- [ ] Write E2E tests for error display
- [ ] Write E2E tests for debug panel
- [ ] Write unit tests for trace_id generation
- [ ] Write integration tests for structured logging
- [ ] Run full test suite

## Testing Plan / 测试计划

### 1. Contract Tests / 契约测试

**File**: `tests/contract/test_error_envelope.py` (new file)

```python
"""
Contract tests to assert error envelopes per endpoint / 契约测试以断言每个端点的错误信封
"""

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_error_envelope_structure():
    """Test that all error responses follow standard envelope / 测试所有错误响应遵循标准信封"""
    # Trigger an error / 触发错误
    response = client.get("/api/hyperliquid/status")
    
    if not response.json().get("ok", True):
        data = response.json()
        assert "error" in data
        assert "error_type" in data
        assert "message" in data
        assert "message_zh" in data
        assert "trace_id" in data
        assert "timestamp" in data

def test_success_envelope_structure():
    """Test that success responses include trace_id / 测试成功响应包含 trace_id"""
    # Mock successful response / 模拟成功响应
    response = client.get("/api/bot/status")
    
    if response.status_code == 200:
        data = response.json()
        assert "trace_id" in data or "X-Trace-ID" in response.headers
```

### 2. Fixture-Driven Exchange Failure Simulations / 基于 Fixture 的交易所失败模拟

**File**: `tests/integration/test_exchange_failures.py` (new file)

```python
"""
Fixture-driven simulations for exchange failures / 交易所失败的基于 Fixture 的模拟
"""

import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_network_timeout():
    """Simulate network timeout / 模拟网络超时"""
    with patch("src.trading.hyperliquid_client.requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        yield mock_post

@pytest.fixture
def mock_rate_limit():
    """Simulate rate limit error / 模拟速率限制错误"""
    with patch("src.trading.hyperliquid_client.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_post.return_value = mock_response
        yield mock_post

def test_network_timeout_handling(mock_network_timeout):
    """Test handling of network timeout / 测试网络超时的处理"""
    from src.trading.hyperliquid_client import HyperliquidClient
    
    client = HyperliquidClient()
    result = client.fetch_market_data()
    
    assert result is None or "error" in result

def test_rate_limit_handling(mock_rate_limit):
    """Test handling of rate limit / 测试速率限制的处理"""
    from src.trading.hyperliquid_client import HyperliquidClient
    
    client = HyperliquidClient()
    result = client.place_order({})
    
    assert "error" in result or result is None
```

### 3. E2E Tests / 端到端测试

**File**: `tests/e2e/test_error_display.py` (new file)

```python
"""
E2E tests to verify error banners render correctly / 端到端测试以验证错误横幅正确渲染
"""

import pytest
from playwright.sync_api import Page, expect

def test_error_banner_displays_trace_id(page: Page):
    """Test that error banner displays trace_id / 测试错误横幅显示 trace_id"""
    # Navigate to page / 导航到页面
    page.goto("http://localhost:3000/hyperliquid")
    
    # Trigger an error / 触发错误
    page.click("button:has-text('Connect')")
    
    # Wait for error to appear / 等待错误出现
    error_banner = page.locator(".error-message")
    expect(error_banner).to_be_visible()
    
    # Check trace_id is displayed / 检查 trace_id 是否显示
    trace_id_element = page.locator(".error-trace-id")
    expect(trace_id_element).to_be_visible()
    
    # Check trace_id is copyable / 检查 trace_id 可复制
    copy_button = trace_id_element.locator("button")
    expect(copy_button).to_be_visible()

def test_debug_panel_records_failing_call(page: Page):
    """Test that debug panel records failing API call / 测试调试面板记录失败的 API 调用"""
    page.goto("http://localhost:3000/hyperliquid")
    
    # Open debug panel / 打开调试面板
    page.click("#debugPanelToggle")
    
    # Trigger an error / 触发错误
    page.click("button:has-text('Connect')")
    
    # Check debug panel shows the call / 检查调试面板显示调用
    debug_panel = page.locator("#debugPanel")
    expect(debug_panel).to_be_visible()
    
    # Check call is recorded / 检查调用已记录
    call_item = debug_panel.locator(".debug-call-item.error")
    expect(call_item).to_be_visible()
```

### 4. Unit Tests / 单元测试

- Test `ErrorMapper.map_exception()` with various exceptions
- Test `StandardErrorResponse.to_dict()` serialization
- Test error type and severity determination
- Test trace_id generation and context management

### 5. Integration Tests / 集成测试

- Test API endpoints return standardized error format
- Test error history is exposed correctly
- Test frontend error handler displays errors correctly
- Test trace_id is included in all responses
- Test structured logging includes trace_id

### 6. Manual Testing / 手动测试

- Trigger various error scenarios (network, auth, insufficient funds, etc.)
- Verify error messages are bilingual
- Verify error suggestions are helpful
- Verify error history is accessible in frontend
- Verify trace_id is visible in error messages
- Verify debug panel shows API calls
- Verify client-side validation prevents invalid orders

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

## Expected Impact on Debugging / 对调试的预期影响

### Faster Pinpointing / 更快定位问题

- **Trace IDs and structured entries**: Make it trivial to follow a request from UI to backend/exchange
- **追踪ID和结构化条目**：使从 UI 到后端/交易所的请求追踪变得简单
- **Correlated logs**: Backend logs become directly searchable from the UI-surfaced trace ID
- **关联日志**：后端日志可以通过 UI 显示的 trace ID 直接搜索

### Actionable UI Errors / 可操作的 UI 错误

- **Specific codes/messages**: Users see specific error codes and human-readable messages
- **特定代码/消息**：用户看到特定的错误代码和人类可读的消息
- **Suggested remediation**: Each error includes suggested remediation steps
- **建议的修复**：每个错误都包含建议的修复步骤
- **Reduced back-and-forth**: Clear error context reduces need for additional debugging
- **减少来回沟通**：清晰的错误上下文减少额外调试的需要

### Lower Reproduction Cost / 降低重现成本

- **Captured context**: Request context (endpoint, payload hash, latency) captured for reproduction
- **捕获的上下文**：捕获请求上下文（端点、负载哈希、延迟）用于重现
- **Fixture-driven simulations**: Allow engineers to replay failure modes locally
- **基于 Fixture 的模拟**：允许工程师在本地重放失败模式
- **Debug panel**: Frontend debug panel shows all API calls with full context
- **调试面板**：前端调试面板显示所有 API 调用及其完整上下文

### Removed Ambiguity / 消除歧义

- **"Which call failed?" ambiguity removed**: Debug panel clearly shows which API call failed
- **"哪个调用失败？"歧义已消除**：调试面板清楚地显示哪个 API 调用失败
- **Frontend vs backend vs exchange**: Structured signals make it clear where the failure occurred
- **前端 vs 后端 vs 交易所**：结构化信号清楚地显示失败发生的位置
- **Logs and UI messages correlated**: Trace IDs connect UI errors to backend logs
- **日志和 UI 消息关联**：追踪ID将 UI 错误连接到后端日志

## Summary / 总结

This plan provides a comprehensive approach to improving debugging experience:

1. **Standardized Error Format**: All errors follow the same structure with trace_id for correlation
2. **标准化错误格式**：所有错误遵循相同的结构，包含用于关联的 trace_id
3. **Bilingual Support**: All error messages in English and Chinese
4. **双语支持**：所有错误消息均为英文和中文
5. **Actionable Suggestions**: Each error includes recovery suggestions and remediation steps
6. **可操作的建议**：每个错误都包含恢复建议和修复步骤
7. **Request Tracing**: Trace IDs enable end-to-end request correlation
8. **请求追踪**：追踪ID支持端到端请求关联
9. **Frontend Debug Panel**: Real-time visibility into API calls with full context
10. **前端调试面板**：实时查看 API 调用及其完整上下文
11. **Structured Logging**: JSON logs with trace_id for easy searching and correlation
12. **结构化日志**：包含 trace_id 的 JSON 日志，便于搜索和关联
13. **Client-Side Validation**: Prevent invalid orders before sending to backend
14. **客户端验证**：在发送到后端之前防止无效订单
15. **Exchange Health Metrics**: Monitor exchange latency and error rates
16. **交易所健康指标**：监控交易所延迟和错误率
17. **Comprehensive Testing**: Contract tests, fixture-driven simulations, and E2E tests
18. **全面测试**：契约测试、基于 Fixture 的模拟和端到端测试

The implementation should be done in phases to minimize disruption and allow for testing at each stage.

实施应分阶段进行，以最小化干扰并在每个阶段进行测试。

