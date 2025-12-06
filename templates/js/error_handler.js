/**
 * Standardized Frontend Error Handler / 标准化前端错误处理
 * 
 * Usage / 用法:
 *   handleApiError(data, errorBox);
 *   displayError(err, errorBox);
 *   clearError(errorBox);
 */

/**
 * Handle API error response / 处理 API 错误响应
 * @param {Object} errorResponse - Standard error response from API
 * @param {HTMLElement} errorBox - Element to display error in
 * @param {Object} options - Additional options
 */
function handleApiError(errorResponse, errorBox, options = {}) {
    if (!errorResponse || (!errorResponse.error && !errorResponse.error_type)) {
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
    const displayMessage = (lang === 'zh' && message_zh) ? message_zh : (message || errorResponse.error || 'Unknown error');
    const displaySuggestion = (lang === 'zh' && suggestion_zh) ? suggestion_zh : suggestion;
    const displayRemediation = (lang === 'zh' && remediation_zh) ? remediation_zh : remediation;
    
    // Build error HTML / 构建错误 HTML
    let errorHtml = `
        <div class="error-message" data-severity="${severity}">
            <strong>${getSeverityIcon(severity)} ${escapeHtml(displayMessage)}</strong>
    `;
    
    if (displaySuggestion) {
        errorHtml += `
            <div class="error-suggestion">
                💡 ${escapeHtml(displaySuggestion)}
            </div>
        `;
    }
    
    if (displayRemediation) {
        errorHtml += `
            <div class="error-remediation">
                🔧 ${escapeHtml(displayRemediation)}
            </div>
        `;
    }
    
    if (details && options.showDetails) {
        errorHtml += `
            <div class="error-details">
                <details>
                    <summary>Details / 详情</summary>
                    <pre>${escapeHtml(JSON.stringify(details, null, 2))}</pre>
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
                <strong>Trace ID / 追踪ID:</strong> <code>${escapeHtml(trace_id)}</code>
                <button class="copy-trace-id-btn" onclick="copyTraceId('${escapeHtml(trace_id)}')" title="Copy / 复制">📋</button>
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
    console.error(`[${error_type || 'error'}] ${displayMessage}`, {
        severity,
        suggestion: displaySuggestion,
        remediation: displayRemediation,
        details,
        timestamp,
        trace_id,
    });
}

/**
 * Display generic error / 显示通用错误
 * @param {Error|string} error - Error object or message
 * @param {HTMLElement} errorBox - Element to display error in
 */
function displayError(error, errorBox) {
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
function clearError(errorBox) {
    if (errorBox) {
        errorBox.innerHTML = '';
        errorBox.style.display = 'none';
    }
}

/**
 * Escape HTML to prevent XSS / 转义 HTML 以防止 XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Copy trace ID to clipboard / 复制追踪ID到剪贴板
 */
function copyTraceId(traceId) {
    navigator.clipboard.writeText(traceId).then(() => {
        // Show feedback / 显示反馈
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 1000);
    }).catch(err => {
        console.error('Failed to copy trace ID:', err);
    });
}

// Make functions available globally / 使函数全局可用
window.handleApiError = handleApiError;
window.displayError = displayError;
window.clearError = clearError;
window.copyTraceId = copyTraceId;

