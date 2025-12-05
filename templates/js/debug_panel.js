/**
 * Frontend Debug Panel Component / 前端调试面板组件
 * 
 * Displays all API calls with full context for debugging.
 * 显示所有 API 调用及其完整上下文，用于调试。
 */

class DebugPanel {
    constructor(apiDiagnostics) {
        this.apiDiagnostics = apiDiagnostics;
        this.isVisible = false;
        this.filter = 'all'; // 'all' or 'errors'
        this.panel = null;
        this.isPaused = false; // Pause state for auto-refresh / 自动刷新暂停状态
        this.init();
    }

    /**
     * Initialize debug panel / 初始化调试面板
     */
    init() {
        // Create panel HTML / 创建面板 HTML
        const panelHTML = `
            <div id="debugPanel" class="debug-panel" style="display: none;">
                <div class="debug-panel-header">
                    <h3>🔍 Debug Panel / 调试面板</h3>
                    <div class="debug-panel-controls">
                        <label>
                            <input type="radio" name="debugFilter" value="all" checked>
                            All / 全部
                        </label>
                        <label>
                            <input type="radio" name="debugFilter" value="errors">
                            Errors Only / 仅错误
                        </label>
                        <button id="debugPanelPauseBtn" class="btn-pause" onclick="debugPanel.togglePause()" title="Pause/Resume auto-refresh / 暂停/继续自动刷新">
                            ⏸️ Pause / 暂停
                        </button>
                        <button class="btn-clear" onclick="debugPanel.clear()">Clear / 清除</button>
                        <button class="btn-close" onclick="debugPanel.toggle()">✕</button>
                    </div>
                </div>
                <div class="debug-panel-content" id="debugPanelContent">
                    <p class="debug-empty">No API calls recorded yet. / 尚未记录 API 调用。</p>
                </div>
            </div>
        `;

        // Insert panel into body / 将面板插入 body
        document.body.insertAdjacentHTML('beforeend', panelHTML);
        this.panel = document.getElementById('debugPanel');

        // Setup filter listeners / 设置过滤器监听器
        const filterInputs = this.panel.querySelectorAll('input[name="debugFilter"]');
        filterInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.filter = e.target.value;
                this.render();
            });
        });
        
        // Initialize pause button state / 初始化暂停按钮状态
        this.updatePauseButton();
    }

    /**
     * Toggle panel visibility / 切换面板可见性
     */
    toggle() {
        this.isVisible = !this.isVisible;
        if (this.panel) {
            this.panel.style.display = this.isVisible ? 'block' : 'none';
            if (this.isVisible) {
                this.render();
            }
        }
    }

    /**
     * Show panel / 显示面板
     */
    show() {
        if (!this.isVisible) {
            this.toggle();
        }
    }

    /**
     * Hide panel / 隐藏面板
     */
    hide() {
        if (this.isVisible) {
            this.toggle();
        }
    }

    /**
     * Clear call history / 清除调用历史
     */
    clear() {
        if (this.apiDiagnostics) {
            this.apiDiagnostics.clear();
        }
        this.render();
    }

    /**
     * Render panel content / 渲染面板内容
     */
    render() {
        if (!this.panel) return;

        const content = this.panel.querySelector('#debugPanelContent');
        if (!content) return;

        // Get calls based on filter / 根据过滤器获取调用
        const filters = this.filter === 'errors' ? { errorsOnly: true } : {};
        const calls = this.apiDiagnostics ? this.apiDiagnostics.getRecentCalls(filters) : [];

        if (calls.length === 0) {
            content.innerHTML = '<p class="debug-empty">No API calls recorded yet. / 尚未记录 API 调用。</p>';
            return;
        }

        // Render calls / 渲染调用
        const callsHTML = calls.map(call => this.renderCall(call)).join('');
        content.innerHTML = callsHTML;
    }

    /**
     * Render a single API call / 渲染单个 API 调用
     */
    renderCall(call) {
        const timestamp = new Date(call.timestamp).toLocaleTimeString();
        const statusClass = call.status >= 400 || call.error ? 'error' : 
                           call.status >= 300 ? 'warning' : 'success';
        const latencyColor = call.latency > 1000 ? '#ef4444' : 
                            call.latency > 500 ? '#f59e0b' : '#22c55e';

        return `
            <div class="debug-call-item ${statusClass}" data-call-id="${call.id}">
                <div class="debug-call-header">
                    <span class="debug-call-method">${call.method}</span>
                    <span class="debug-call-url">${this.escapeHtml(call.url)}</span>
                    <span class="debug-call-status status-${statusClass}">${call.status}</span>
                    <span class="debug-call-latency" style="color: ${latencyColor}">
                        ${call.latency}ms
                    </span>
                </div>
                <div class="debug-call-details">
                    <div class="debug-call-row">
                        <strong>Time / 时间:</strong> ${timestamp}
                    </div>
                    ${call.traceId ? `
                        <div class="debug-call-row">
                            <strong>Trace ID / 追踪ID:</strong> 
                            <code>${this.escapeHtml(call.traceId)}</code>
                            <button class="btn-copy-trace" onclick="debugPanel.copyTraceId('${this.escapeHtml(call.traceId)}')" title="Copy / 复制">📋</button>
                        </div>
                    ` : ''}
                    ${call.statusText ? `
                        <div class="debug-call-row">
                            <strong>Status / 状态:</strong> ${this.escapeHtml(call.statusText)}
                        </div>
                    ` : ''}
                    ${call.payloadHash ? `
                        <div class="debug-call-row">
                            <strong>Payload Hash / 负载哈希:</strong> 
                            <code>${this.escapeHtml(call.payloadHash)}</code>
                        </div>
                    ` : ''}
                    ${call.error ? `
                        <div class="debug-call-row error">
                            <strong>Error / 错误:</strong> ${this.escapeHtml(call.error)}
                        </div>
                    ` : ''}
                    ${call.payload ? `
                        <div class="debug-call-row">
                            <details>
                                <summary>
                                    Payload / 负载
                                    <button class="btn-copy-payload" onclick="debugPanel.copyPayload('${call.id}')" title="Copy payload / 复制负载">📋</button>
                                </summary>
                                <pre id="payload-${call.id}">${this.escapeHtml(JSON.stringify(call.payload, null, 2))}</pre>
                            </details>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Copy trace ID to clipboard / 复制追踪ID到剪贴板
     */
    copyTraceId(traceId) {
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

    /**
     * Copy payload to clipboard / 复制负载到剪贴板
     */
    copyPayload(callId) {
        const calls = this.apiDiagnostics ? this.apiDiagnostics.getRecentCalls({}) : [];
        const call = calls.find(c => c.id === callId);
        
        if (!call || !call.payload) {
            console.error('Call or payload not found');
            return;
        }
        
        const payloadText = JSON.stringify(call.payload, null, 2);
        navigator.clipboard.writeText(payloadText).then(() => {
            // Show feedback / 显示反馈
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = '✓';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 1000);
        }).catch(err => {
            console.error('Failed to copy payload:', err);
        });
    }

    /**
     * Escape HTML to prevent XSS / 转义 HTML 以防止 XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Toggle pause state / 切换暂停状态
     */
    togglePause() {
        this.isPaused = !this.isPaused;
        this.updatePauseButton();
        
        if (this.isPaused) {
            this.stopAutoRefresh();
        } else {
            this.startAutoRefresh(1000);
        }
    }

    /**
     * Update pause button text and style / 更新暂停按钮文本和样式
     */
    updatePauseButton() {
        const btn = document.getElementById('debugPanelPauseBtn');
        if (!btn) return;
        
        if (this.isPaused) {
            btn.innerHTML = '▶️ Resume / 继续';
            btn.classList.remove('btn-pause');
            btn.classList.add('btn-resume');
            btn.title = 'Resume auto-refresh / 继续自动刷新';
        } else {
            btn.innerHTML = '⏸️ Pause / 暂停';
            btn.classList.remove('btn-resume');
            btn.classList.add('btn-pause');
            btn.title = 'Pause auto-refresh / 暂停自动刷新';
        }
    }

    /**
     * Auto-refresh panel / 自动刷新面板
     */
    startAutoRefresh(interval = 1000) {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        // Only start if not paused / 仅在未暂停时启动
        if (!this.isPaused) {
            this.autoRefreshInterval = setInterval(() => {
                if (this.isVisible && !this.isPaused) {
                    this.render();
                }
            }, interval);
        }
    }

    /**
     * Stop auto-refresh / 停止自动刷新
     */
    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }
}

// Initialize debug panel when API diagnostics is available / 当 API 诊断可用时初始化调试面板
let debugPanel = null;

// Wait for apiDiagnostics to be available / 等待 apiDiagnostics 可用
function initDebugPanel() {
    if (window.apiDiagnostics && !debugPanel) {
        debugPanel = new DebugPanel(window.apiDiagnostics);
        debugPanel.startAutoRefresh(1000); // Refresh every second / 每秒刷新
        
        // Make debugPanel globally available / 使 debugPanel 全局可用
        window.debugPanel = debugPanel;
        
        // Add toggle button to page / 添加切换按钮到页面
        addDebugPanelToggle();
    } else if (!window.apiDiagnostics) {
        // Retry after a short delay / 短暂延迟后重试
        setTimeout(initDebugPanel, 100);
    }
}

/**
 * Add toggle button to page / 添加切换按钮到页面
 */
function addDebugPanelToggle() {
    // Check if toggle button already exists / 检查切换按钮是否已存在
    if (document.getElementById('debugPanelToggle')) {
        return;
    }

    const toggleButton = document.createElement('button');
    toggleButton.id = 'debugPanelToggle';
    toggleButton.className = 'debug-panel-toggle';
    toggleButton.innerHTML = '🔍 Debug';
    toggleButton.title = 'Toggle Debug Panel / 切换调试面板';
    toggleButton.onclick = () => {
        if (debugPanel) {
            debugPanel.toggle();
        }
    };

    // Add to page (fixed position) / 添加到页面（固定位置）
    document.body.appendChild(toggleButton);
}

// Initialize when DOM is ready / DOM 就绪时初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDebugPanel);
} else {
    initDebugPanel();
}

