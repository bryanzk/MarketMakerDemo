/**
 * Error History Display Component / 错误历史显示组件
 * 
 * Displays strategy instance errors from /api/status endpoint.
 * 显示来自 /api/status 端点的策略实例错误。
 */

class ErrorHistoryPanel {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            autoRefresh: options.autoRefresh !== false, // Default: true
            refreshInterval: options.refreshInterval || 5000, // Default: 5 seconds
            maxDisplayErrors: options.maxDisplayErrors || 20, // Default: 20
            showTraceId: options.showTraceId !== false, // Default: true
            language: options.language || detectLanguage(),
            ...options
        };
        this.refreshTimer = null;
        this.init();
    }

    init() {
        if (!this.container) {
            console.error(`ErrorHistoryPanel: Container #${this.containerId} not found`);
            return;
        }

        // Create panel structure / 创建面板结构
        this.container.innerHTML = `
            <div class="error-history-panel">
                <div class="error-history-header">
                    <h3>Error History / 错误历史</h3>
                    <div class="error-history-controls">
                        <button id="errorHistoryRefresh" class="btn-refresh" title="Refresh / 刷新">🔄</button>
                        <button id="errorHistoryToggle" class="btn-toggle" title="Toggle Auto-Refresh / 切换自动刷新">⏸️</button>
                    </div>
                </div>
                <div id="errorHistoryContent" class="error-history-content">
                    <div class="error-history-loading">Loading error history... / 加载错误历史中...</div>
                </div>
            </div>
        `;

        // Event listeners / 事件监听器
        const refreshBtn = document.getElementById('errorHistoryRefresh');
        const toggleBtn = document.getElementById('errorHistoryToggle');
        
        if (refreshBtn) {
            refreshBtn.onclick = () => this.refresh();
        }
        
        if (toggleBtn) {
            toggleBtn.onclick = () => this.toggleAutoRefresh();
        }

        // Initial load / 初始加载
        this.refresh();

        // Start auto-refresh if enabled / 如果启用则开始自动刷新
        if (this.options.autoRefresh) {
            this.startAutoRefresh();
        }
    }

    async refresh() {
        const contentEl = document.getElementById('errorHistoryContent');
        if (!contentEl) return;

        try {
            // Use diagnosticFetch if available / 如果可用则使用 diagnosticFetch
            const fetchFn = window.diagnosticFetch || window.fetch;
            const response = await fetchFn('/api/status');
            const data = await response.json();

            if (data.error || !data.ok) {
                contentEl.innerHTML = `
                    <div class="error-history-error">
                        ${this.options.language === 'zh' 
                            ? '加载错误历史失败' 
                            : 'Failed to load error history'}
                    </div>
                `;
                return;
            }

            const errors = data.errors || {};
            this.renderErrors(errors, contentEl);

        } catch (error) {
            console.error('Error fetching error history:', error);
            contentEl.innerHTML = `
                <div class="error-history-error">
                    ${this.options.language === 'zh' 
                        ? '加载错误历史时出错' 
                        : 'Error loading error history'}
                </div>
            `;
        }
    }

    renderErrors(errors, container) {
        const lang = this.options.language;
        let html = '';

        // Global Alert / 全局警报
        if (errors.global_alert) {
            html += this.renderAlert(errors.global_alert, 'global', lang);
        }

        // Global Error History / 全局错误历史
        if (errors.global_error_history && errors.global_error_history.length > 0) {
            html += `
                <div class="error-history-section">
                    <h4>Global Errors / 全局错误</h4>
                    <div class="error-history-list">
                        ${errors.global_error_history
                            .slice(0, this.options.maxDisplayErrors)
                            .map(err => this.renderErrorItem(err, 'global', lang))
                            .join('')}
                    </div>
                </div>
            `;
        }

        // Instance Errors / 实例错误
        if (errors.instance_errors && Object.keys(errors.instance_errors).length > 0) {
            for (const [instanceId, instanceData] of Object.entries(errors.instance_errors)) {
                if (instanceData.alert || (instanceData.error_history && instanceData.error_history.length > 0)) {
                    html += `
                        <div class="error-history-section">
                            <h4>Instance: ${instanceId}</h4>
                            ${instanceData.alert ? this.renderAlert(instanceData.alert, instanceId, lang) : ''}
                            ${instanceData.error_history && instanceData.error_history.length > 0 ? `
                                <div class="error-history-list">
                                    ${instanceData.error_history
                                        .slice(0, this.options.maxDisplayErrors)
                                        .map(err => this.renderErrorItem(err, instanceId, lang))
                                        .join('')}
                                </div>
                            ` : ''}
                        </div>
                    `;
                }
            }
        }

        if (!html) {
            html = `
                <div class="error-history-empty">
                    ${lang === 'zh' 
                        ? '暂无错误记录' 
                        : 'No errors recorded'}
                </div>
            `;
        }

        container.innerHTML = html;
    }

    renderAlert(alert, context, lang) {
        const alertType = alert.type || 'info';
        const message = alert.message || '';
        const suggestion = alert.suggestion || '';
        
        return `
            <div class="error-alert error-alert-${alertType}" data-context="${context}">
                <div class="error-alert-header">
                    <strong>${lang === 'zh' ? '警报' : 'Alert'}</strong>
                    <span class="error-alert-type">${alertType}</span>
                </div>
                <div class="error-alert-message">${escapeHtml(message)}</div>
                ${suggestion ? `<div class="error-alert-suggestion">${escapeHtml(suggestion)}</div>` : ''}
            </div>
        `;
    }

    renderErrorItem(error, context, lang) {
        const timestamp = error.timestamp ? new Date(error.timestamp * 1000).toLocaleString() : 'N/A';
        const type = error.type || 'unknown';
        const message = error.message || '';
        const symbol = error.symbol || '';
        const traceId = error.trace_id || '';
        const details = error.details || null;

        return `
            <div class="error-item" data-type="${type}" data-context="${context}">
                <div class="error-item-header">
                    <span class="error-item-time">${timestamp}</span>
                    <span class="error-item-type error-type-${type}">${type}</span>
                </div>
                <div class="error-item-content">
                    ${symbol ? `<div class="error-item-symbol">${lang === 'zh' ? '交易对' : 'Symbol'}: ${escapeHtml(symbol)}</div>` : ''}
                    <div class="error-item-message">${escapeHtml(message)}</div>
                    ${this.options.showTraceId && traceId ? `
                        <div class="error-item-trace-id">
                            ${lang === 'zh' ? '追踪ID' : 'Trace ID'}: 
                            <code>${traceId}</code>
                            <button class="btn-copy-trace" onclick="copyToClipboard('${traceId}')" title="${lang === 'zh' ? '复制' : 'Copy'}">📋</button>
                        </div>
                    ` : ''}
                    ${details ? `
                        <details class="error-item-details">
                            <summary>${lang === 'zh' ? '详情' : 'Details'}</summary>
                            <pre>${escapeHtml(JSON.stringify(details, null, 2))}</pre>
                        </details>
                    ` : ''}
                </div>
            </div>
        `;
    }

    startAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        this.refreshTimer = setInterval(() => {
            this.refresh();
        }, this.options.refreshInterval);
        
        const toggleBtn = document.getElementById('errorHistoryToggle');
        if (toggleBtn) {
            toggleBtn.textContent = '⏸️';
            toggleBtn.title = this.options.language === 'zh' ? '暂停自动刷新' : 'Pause Auto-Refresh';
        }
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
        
        const toggleBtn = document.getElementById('errorHistoryToggle');
        if (toggleBtn) {
            toggleBtn.textContent = '▶️';
            toggleBtn.title = this.options.language === 'zh' ? '恢复自动刷新' : 'Resume Auto-Refresh';
        }
    }

    toggleAutoRefresh() {
        if (this.refreshTimer) {
            this.stopAutoRefresh();
        } else {
            this.startAutoRefresh();
        }
    }

    destroy() {
        this.stopAutoRefresh();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

/**
 * Detect user language / 检测用户语言
 */
function detectLanguage() {
    const lang = navigator.language || navigator.userLanguage;
    return lang.startsWith('zh') ? 'zh' : 'en';
}

/**
 * Escape HTML to prevent XSS / 转义 HTML 以防止 XSS
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

/**
 * Copy to clipboard / 复制到剪贴板
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show feedback / 显示反馈
        const event = new CustomEvent('showMessage', {
            detail: { message: 'Copied! / 已复制!', type: 'success' }
        });
        document.dispatchEvent(event);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Make ErrorHistoryPanel available globally / 使 ErrorHistoryPanel 全局可用
window.ErrorHistoryPanel = ErrorHistoryPanel;

// Auto-initialize when DOM is ready / DOM 就绪时自动初始化
document.addEventListener('DOMContentLoaded', () => {
    // ErrorHistoryPanel will be initialized by individual pages
    // 错误历史面板将由各个页面初始化
});

